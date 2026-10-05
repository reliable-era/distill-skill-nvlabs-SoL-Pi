"""Bounded transport components; no standalone execution entrypoint."""
from usage_normalization import normalize_request
from output_policy import transform
from provider_cost import normalize_cost
import datetime,contextlib,fcntl,hashlib,http.client,json,os,pathlib,socket,threading,time
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
PATHS=frozenset(['/v1/responses'])
@contextlib.contextmanager
def inference_locks(pins):
 if len(pins)!=2 or len({(p['device'],p['inode']) for p in pins})!=2:raise ValueError('two distinct frozen locks required')
 handles=[]
 try:
  for p in pins:
   fd=os.open(p['path'],os.O_RDONLY|os.O_NOFOLLOW);handle=os.fdopen(fd,'r');handles.append(handle);st=os.fstat(fd)
   if (st.st_dev,st.st_ino)!=(p['device'],p['inode']):raise RuntimeError('lock identity changed')
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  yield
 finally:
  for h in reversed(handles):h.close()
def idle(load):
 return isinstance(load,list) and bool(load) and all(isinstance(r,dict) and type(r.get('num_reqs')) is int and type(r.get('num_waiting_reqs')) is int and r['num_waiting_reqs']==0 for r in load)
def fetch_idle():
 c=http.client.HTTPConnection('127.0.0.1',18001,timeout=2);timer=None
 try:
  c.connect();sock=c.sock
  def cutoff():
   try:sock.shutdown(socket.SHUT_RDWR)
   except OSError:pass
  timer=threading.Timer(2,cutoff);timer.start()
  c.request('GET','/get_load');z=c.getresponse();body=z.read(65537)
  if z.status!=200 or len(body)>65536:raise RuntimeError('load unavailable')
  load=json.loads(body)
  if not idle(load):raise RuntimeError('scheduler busy or ambiguous')
  return load
 finally:
  if timer:timer.cancel();timer.join(timeout=1)
  c.close()
class LocalBudgetExhaustion(RuntimeError):
 """Owned pre-forward limit; never a provider status/error."""
 def __init__(self,reason):self.reason=reason;super().__init__('owned local budget: '+reason)

class Session:
 def __init__(self,private,topology):
  required={'verified':True,'image_id':IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True}
  if any(topology.get(k)!=v for k,v in required.items()) or not topology.get('actor_network'):raise RuntimeError('reviewed topology required')
  self.root=pathlib.Path(private);self.root.mkdir(mode=0o700,exist_ok=False);self.topology=topology;self.starts=0;self.posts=0;self.per_actor={};self.active=None;self.deadline=0;self.records=[];self.budget_denials=[];self.lock=threading.Lock();self.connections={}
  self.persist()
 def persist(self):
  data={'native_starts':self.starts,'provider_POST':self.posts,'per_actor':self.per_actor,'records':self.records,'local_budget_denials':self.budget_denials,'usage_complete':None,'model_backend_pooling':False}
  f=self.root/'ledger.json';f.write_text(json.dumps(data,indent=2)+'\n');f.chmod(0o600)
 def begin(self,actor,load):
  with self.lock:
   if not isinstance(actor,str) or self.active or self.starts>=10 or self.posts>=600 or actor in self.per_actor or not idle(load):raise RuntimeError('start/idleness guard')
   self.starts+=1;self.per_actor[actor]=0;self.active=actor;self.deadline=time.monotonic()+3600;self.persist()
 def finish(self,cleanup_verified,auxiliary_events=()):
  with self.lock:
   if not cleanup_verified or auxiliary_events:raise RuntimeError('cleanup or auxiliary accounting invalid')
   self.active=None;self.persist()
 def abort_owned_connections(self):
  with self.lock:connections=list(self.connections.items())
  for c,sock in connections:
   if sock:
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   c.close()
  return len(connections)
 def forward(self,path,body,emit,connect=http.client.HTTPConnection):
  # Called only by future reviewed broker: clients cannot choose upstream host or headers.
  if path not in PATHS or not isinstance(body,bytes) or len(body)>262144:raise ValueError('endpoint/request size cap')
  forwarded_body,policy=transform(body)
  parsed=json.loads(body)
  if parsed.get('model')!='Qwen3.8-27B-FP8' or parsed.get('stream') is not True:raise ValueError('fixed streaming model required')
  with self.lock:
   actor=self.active
   if actor is None:raise RuntimeError('no active actor')
   reason=('global_POST_cap' if self.posts>=600 else 'per_actor_POST_cap' if self.per_actor[actor]>=60 else 'actor_deadline_reserve' if self.deadline-10<=time.monotonic() else None)
   if reason:
    self.budget_denials.append({'actor':actor,'reason':reason,'provider_forwarded':False,'forward_count':0,'actor_POST_count':self.per_actor[actor],'global_POST_count':self.posts,'maximum_actor_POST':60,'maximum_global_POST':600,'exception_source':'session.Session.forward local guard','exception_type':'LocalBudgetExhaustion'})
    self.persist() # Receipt must survive before the typed exception leaves this guard.
    raise LocalBudgetExhaustion(reason)
   self.posts+=1;self.per_actor[actor]+=1;number=self.posts;self.persist()
  request_start=time.monotonic();started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
  timeout=provider_seconds(self.deadline,time.monotonic());c=connect('127.0.0.1',8000,timeout=timeout);timer=None;size=0;complete=False;error=None;usage=[];status=None;error_body_sha=None;error_body_bytes=0;terminal=False;events=[];client_disconnected=False;client_disconnect_reason=None;backend=None
  request=self.root/f'request-{number}.json';request.write_bytes(body);request.chmod(0o600)
  forwarded_file=self.root/f'forwarded-request-{number}.json';forwarded_file.write_bytes(forwarded_body);forwarded_file.chmod(0o600)
  dest=self.root/f'response-{number}.sse'
  try:
   with self.lock:self.connections[c]=None
   c.connect();sock=c.sock
   with self.lock:self.connections[c]=sock
   def cutoff():
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   timer=threading.Timer(timeout,cutoff);timer.start();c.request('POST',path,forwarded_body,{'Content-Type':'application/json'});z=c.getresponse()
   status=z.status;backend=getattr(z,'getheader',lambda _:None)('X-Solpi-Upstream')
   if z.status!=200:
    raw_error=z.read(65537);error_body_bytes=len(raw_error)
    error_file=self.root/f'provider-error-{number}.body';error_file.write_bytes(raw_error[:65536]);error_file.chmod(0o600);error_body_sha=hashlib.sha256(raw_error[:65536]).hexdigest()
    raise RuntimeError('provider non200 status='+str(status))
   with dest.open('xb') as raw:
    dest.chmod(0o600)
    while True:
     chunk=z.read1(8192)
     if not chunk:complete=True;break
     size+=len(chunk)
     if size>2097152 or time.monotonic()>self.deadline-10+240:raise RuntimeError('response bytes/time cap')
     raw.write(chunk);raw.flush()
     if not client_disconnected:
      try:emit(chunk)
      except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError,TimeoutError) as e:
       client_disconnected=True;client_disconnect_reason=type(e).__name__
   for line in dest.read_bytes().splitlines():
    if line==b'data: [DONE]':terminal=True;events.append('[DONE]')
    if line.startswith(b'data: '):
     try:
      event=json.loads(line[6:]);events.append(event);terminal=terminal or event.get('type')=='response.completed';u=event.get('usage') or event.get('response',{}).get('usage')
      if u is not None:usage.append(u)
     except (ValueError,AttributeError):pass
  except BaseException as e:error=type(e).__name__;raise
  finally:
   if timer:timer.cancel();timer.join(timeout=1)
   c.close()
   with self.lock:self.connections.pop(c,None)
   self.records.append({'provider_backend':backend,'client_disconnected':client_disconnected,'client_disconnect_reason':client_disconnect_reason,'receipt_after_actor_reserve':time.monotonic()>self.deadline-10,'completion_grace_seconds':240,'started_utc':started_utc,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-request_start,'provider_status':status,'private_error_body_sha256':error_body_sha,'private_error_body_bytes':min(error_body_bytes,65536),'error_body_truncated':error_body_bytes>65536,'request':number,'actor':actor,'path':path,'payload_policy':policy,'request_bytes':len(body),'request_sha256':hashlib.sha256(body).hexdigest(),'bytes':size,'stream_eof':complete,'usage_observed':bool(usage),'usage_complete':normalize_cost(events,complete)['gross_usage_complete'],'usage_audit':normalize_cost(events,complete),'error':error,'actor_budget_exhaustion':error is not None and status in (None,200) and time.monotonic()>=self.deadline-10+240,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None})
   # Exact usage remains private and unnormalized until observed provider schema is audited.
   if usage:
    f=self.root/f'usage-{number}.json';f.write_text(json.dumps(usage));f.chmod(0o600)
   self.persist()
  return {'client_disconnected':client_disconnected}
if __name__=='__main__':raise SystemExit('No execution: routing pass and root-reviewed orchestration required')

def provider_seconds(deadline,now):
 # No new POST may pass forward() after the actor reserve. Already committed
 # requests have a finite completion-only backend grace; no actor continuation.
 remaining=deadline-now-10+240
 if remaining<=0:raise RuntimeError('provider completion grace exhausted')
 return remaining

def request_seconds(deadline,now):
 remaining=deadline-now-10
 if remaining<=0:raise RuntimeError('actor cleanup reserve reached')
 return remaining

def fetch_load_record(deadline):
 """Bounded raw GET metadata only; never infers workload ownership."""
 record={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':None,'raw_body':None,'load':None,'error':None}
 call_deadline=min(deadline,time.monotonic()+2);remaining=call_deadline-time.monotonic()
 if remaining<=0:record['error']='deadline';return record
 c=http.client.HTTPConnection('127.0.0.1',18001,timeout=remaining);timer=None
 try:
  c.connect();sock=c.sock;remaining=call_deadline-time.monotonic()
  if remaining<=0:raise TimeoutError('metadata deadline')
  sock.settimeout(remaining)
  def cutoff():
   try:sock.shutdown(socket.SHUT_RDWR)
   except OSError:pass
  timer=threading.Timer(remaining,cutoff);timer.start();c.request('GET','/get_load');z=c.getresponse();body=z.read(65537)
  record.update(status=z.status,raw_body=body[:65536].decode(errors='replace'),truncated=len(body)>65536)
  if z.status==200 and len(body)<=65536:record['load']=json.loads(body)
 except Exception as e:record['error']=type(e).__name__
 finally:
  if timer:timer.cancel();timer.join(timeout=1)
  c.close()
 record['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();return record

def wait_idle(evidence_path,seconds=300,max_gets=61,fetch=fetch_load_record,sleep=time.sleep,clock=time.monotonic):
 if seconds!=300 or max_gets!=61:raise ValueError('frozen idle grace caps')
 path=pathlib.Path(evidence_path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True);observations=[];start=clock();deadline=start+seconds
 for index in range(max_gets):
  if clock()>=deadline:break
  record=fetch(deadline);record['attempt']=index+1;observations.append(record)
  # Durable raw/status evidence precedes eligibility checks.
  path.write_text(json.dumps({'observations':observations,'elapsed_seconds':clock()-start,'GET_count':len(observations),'eligible':None,'unknown_jobs_untouched':True},indent=2)+'\n');path.chmod(0o600)
  if record.get('status')==200 and record.get('error') is None and idle(record.get('load')) and clock()<=deadline:
   result={'observations':observations,'elapsed_seconds':clock()-start,'GET_count':len(observations),'eligible':True,'unknown_jobs_untouched':True};path.write_text(json.dumps(result,indent=2)+'\n');return record['load']
  if index+1<max_gets and clock()<deadline:sleep(min(5,deadline-clock()))
 path.write_text(json.dumps({'observations':observations,'elapsed_seconds':clock()-start,'GET_count':len(observations),'eligible':False,'unknown_jobs_untouched':True},indent=2)+'\n');raise RuntimeError('scheduler idle grace exhausted or ambiguous')
