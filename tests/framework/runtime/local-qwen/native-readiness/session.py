"""Bounded transport components; no standalone execution entrypoint."""
import datetime,contextlib,fcntl,hashlib,http.client,json,os,pathlib,socket,threading,time
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
PATHS=frozenset(['/v1/responses','/v1/chat/completions'])
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
def fetch_idle():
 c=http.client.HTTPConnection('127.0.0.1',8000,timeout=2);timer=None
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
def usage_audit(usage,eof,terminal):
 if not eof or not terminal or not usage:return None
 u=usage[-1]
 if not isinstance(u,dict):return None
 fields=('input_tokens','output_tokens','total_tokens') if 'input_tokens' in u else ('prompt_tokens','completion_tokens','total_tokens')
 if any(type(u.get(k)) is not int or u[k]<0 for k in fields):return None
 if u[fields[0]]+u[fields[1]]!=u['total_tokens']:return None
 return {'complete':True,'provider_fields':list(fields),'input':u[fields[0]],'output':u[fields[1]],'total':u['total_tokens']}
class Session:
 def __init__(self,private,topology):
  required={'verified':True,'image_id':IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True}
  if any(topology.get(k)!=v for k,v in required.items()) or not topology.get('actor_network'):raise RuntimeError('reviewed topology required')
  self.root=pathlib.Path(private);self.root.mkdir(mode=0o700,exist_ok=False);self.topology=topology;self.starts=0;self.posts=0;self.per_actor={};self.active=None;self.deadline=0;self.records=[];self.lock=threading.Lock();self.connections={}
  self.persist()
 def persist(self):
  data={'native_starts':self.starts,'provider_POST':self.posts,'per_actor':self.per_actor,'records':self.records,'usage_complete':None,'model_backend_pooling':False}
  f=self.root/'ledger.json';f.write_text(json.dumps(data,indent=2)+'\n');f.chmod(0o600)
 def begin(self,actor,load):
  with self.lock:
   if actor not in ['codex','pi'] or self.active or self.starts>=2 or actor in self.per_actor or not idle(load):raise RuntimeError('start/idleness guard')
   self.starts+=1;self.per_actor[actor]=0;self.active=actor;self.deadline=time.monotonic()+90;self.persist()
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
   if actor is None or self.posts>=8 or self.per_actor[actor]>=4 or self.deadline<=time.monotonic():raise RuntimeError('request budget')
   self.posts+=1;self.per_actor[actor]+=1;number=self.posts;self.persist()
  request_start=time.monotonic();started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
  timeout=min(40,self.deadline-time.monotonic());c=connect('127.0.0.1',8000,timeout=timeout);timer=None;size=0;complete=False;error=None;usage=[];status=None;error_body_sha=None;error_body_bytes=0;terminal=False
  request=self.root/f'request-{number}.json';request.write_bytes(body);request.chmod(0o600)
  dest=self.root/f'response-{number}.sse'
  try:
   with self.lock:self.connections[c]=None
   c.connect();sock=c.sock
   with self.lock:self.connections[c]=sock
   def cutoff():
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
    if line==b'data: [DONE]':terminal=True
    if line.startswith(b'data: '):
     try:
      event=json.loads(line[6:]);terminal=terminal or event.get('type')=='response.completed';u=event.get('usage') or event.get('response',{}).get('usage')
      if u is not None:usage.append(u)
     except (ValueError,AttributeError):pass
  except BaseException as e:error=type(e).__name__;raise
  finally:
   if timer:timer.cancel();timer.join(timeout=1)
   c.close()
   with self.lock:self.connections.pop(c,None)
   self.records.append({'started_utc':started_utc,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-request_start,'provider_status':status,'private_error_body_sha256':error_body_sha,'private_error_body_bytes':min(error_body_bytes,65536),'error_body_truncated':error_body_bytes>65536,'request':number,'actor':actor,'path':path,'request_bytes':len(body),'request_sha256':hashlib.sha256(body).hexdigest(),'bytes':size,'stream_eof':complete,'usage_observed':bool(usage),'usage_complete':True if usage_audit(usage,complete,terminal) else None,'usage_audit':usage_audit(usage,complete,terminal),'error':error,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None})
   # Exact usage remains private and unnormalized until observed provider schema is audited.
   if usage:
    f=self.root/f'usage-{number}.json';f.write_text(json.dumps(usage));f.chmod(0o600)
   self.persist()
if __name__=='__main__':raise SystemExit('No execution: routing pass and root-reviewed orchestration required')
