"""Bounded transport components; no standalone execution entrypoint."""
from usage_normalization import normalize_request
import datetime,contextlib,fcntl,hashlib,http.client,json,os,pathlib,socket,threading,time
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
PATHS=frozenset(['/v1/chat/completions'])
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
 return isinstance(load,list) and bool(load) and all(isinstance(r,dict) and type(r.get('num_reqs')) is int and type(r.get('num_waiting_reqs')) is int and r['num_reqs']==0 and r['num_waiting_reqs']==0 for r in load)
def fetch_idle(artifact=None):
 deadline=time.monotonic()+2
 c=http.client.HTTPConnection('127.0.0.1',8000,timeout=2);timer=None
 try:
  c.connect();sock=c.sock
  def cutoff():
   try:sock.shutdown(socket.SHUT_RDWR)
   except OSError:pass
  remaining=deadline-time.monotonic()
  if remaining<=0:raise TimeoutError('loadabsolute2sdeadline')
  sock.settimeout(remaining);timer=threading.Timer(remaining,cutoff);timer.start()
  c.request('GET','/get_load');z=c.getresponse();body=z.read(65537)
  if artifact is not None:
   f=pathlib.Path(artifact);f.write_bytes(body[:65536]);f.chmod(0o600)
   meta=f.with_suffix('.metadata.json');meta.write_text(json.dumps({'status':z.status,'bytes':len(body),'truncated':len(body)>65536}));meta.chmod(0o600)
  if z.status!=200 or len(body)>65536:raise RuntimeError('load unavailable')
  load=json.loads(body)
  if not idle(load):raise RuntimeError('scheduler busy or ambiguous')
  return load
 finally:
  if timer:timer.cancel();timer.join(timeout=1)
  c.close()
def idle_grace(private,maximum_seconds=300,maximum_GET=61):
 if maximum_seconds!=300 or maximum_GET!=61:raise ValueError('frozenidlegracecap')
 private=pathlib.Path(private);private.mkdir(mode=0o700,exist_ok=False);start=time.monotonic();records=[]
 for index in range(maximum_GET):
  if time.monotonic()-start>298:break
  path=private/(str(index)+'.json');success=False
  try:load=fetch_idle(path);success=True
  except Exception as error:
   records.append({'GET':index+1,'idle':False,'error_type':type(error).__name__,'body_sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None})
  else:records.append({'GET':index+1,'idle':True,'body_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  (private/'grace.json').write_text(json.dumps({'GETs':len(records),'elapsed_seconds':time.monotonic()-start,'records':records,'models_during_grace':0}));(private/'grace.json').chmod(0o600)
  if success:return load
  if index+1<maximum_GET:time.sleep(min(5,max(0,298-(time.monotonic()-start))))
 raise RuntimeError('boundedidlegraceexhausted, no nextactor')
class Session:
 def __init__(self,private,topology):
  required={'verified':True,'image_id':IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True}
  if any(topology.get(k)!=v for k,v in required.items()) or not topology.get('actor_network'):raise RuntimeError('reviewed topology required')
  self.root=pathlib.Path(private);self.root.mkdir(mode=0o700,exist_ok=False);self.topology=topology;self.starts=0;self.posts=0;self.per_actor={};self.active=None;self.deadline=0;self.records=[];self.denials=[];self.lock=threading.Lock();self.connections={}
  self.persist()
 def persist(self):
  data={'native_starts':self.starts,'provider_POST':self.posts,'per_actor':self.per_actor,'records':self.records,'local_budget_denials':self.denials,'usage_complete':None,'model_backend_pooling':False}
  f=self.root/'ledger.json';f.write_text(json.dumps(data,indent=2)+'\n');f.chmod(0o600)
 def begin(self,actor,load):
  with self.lock:
   if not isinstance(actor,str) or self.active or self.starts>=12 or actor in self.per_actor or not idle(load):raise RuntimeError('start/idleness guard')
   self.starts+=1;self.per_actor[actor]=0;self.active=actor;self.deadline=time.monotonic()+600;self.persist()
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
  parsed=json.loads(body)
  if parsed.get('model')!='Qwen3.8-27B-FP8' or parsed.get('stream') is not True:raise ValueError('fixed streaming model required')
  with self.lock:
   actor=self.active
   if actor is None:raise RuntimeError('no active actor')
   if self.posts>=192 or self.per_actor[actor]>=16:
    self.denials.append({'actor':actor,'reason':'local_request_budget_exhausted','before_forward':True,'forwarded':0,'actor_POST':self.per_actor[actor],'total_POST':self.posts,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    self.persist()
    raise RuntimeError('local request budget exhausted')
   if self.deadline-time.monotonic()<=10:raise RuntimeError('actor remaining deadline')
   self.posts+=1;self.per_actor[actor]+=1;number=self.posts;self.persist()
  request_start=time.monotonic();started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
  timeout=min(590,self.deadline-time.monotonic()-10);c=connect('127.0.0.1',8000,timeout=timeout);timer=None;deadline_fired=threading.Event();size=0;complete=False;error=None;usage=[];status=None;error_body_sha=None;error_body_bytes=0;terminal=False;events=[]
  request=self.root/f'request-{number}.json';request.write_bytes(body);request.chmod(0o600)
  dest=self.root/f'response-{number}.sse'
  try:
   with self.lock:self.connections[c]=None
   c.connect();sock=c.sock
   with self.lock:self.connections[c]=sock
   def cutoff():
    deadline_fired.set()
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   timer=threading.Timer(timeout,cutoff);timer.start();c.request('POST',path,body,{'Content-Type':'application/json'});z=c.getresponse()
   status=z.status
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
     if size>2097152 or time.monotonic()>self.deadline:raise RuntimeError('response bytes/time cap')
     raw.write(chunk);raw.flush();emit(chunk)
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
   self.records.append({'started_utc':started_utc,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-request_start,'provider_status':status,'private_error_body_sha256':error_body_sha,'private_error_body_bytes':min(error_body_bytes,65536),'error_body_truncated':error_body_bytes>65536,'local_deadline_fired':deadline_fired.is_set(),'request':number,'actor':actor,'path':path,'request_bytes':len(body),'request_sha256':hashlib.sha256(body).hexdigest(),'bytes':size,'stream_eof':complete,'usage_observed':bool(usage),'usage_complete':normalize_request(events,'chat',complete)['gross_usage_complete'],'usage_audit':normalize_request(events,'chat',complete),'error':error,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None})
   # Exact usage remains private and unnormalized until observed provider schema is audited.
   if usage:
    f=self.root/f'usage-{number}.json';f.write_text(json.dumps(usage));f.chmod(0o600)
   self.persist()
if __name__=='__main__':raise SystemExit('No execution: routing pass and root-reviewed orchestration required')
