"""G3 direct9012 per-attempt streaming broker; no speculative imputation.
One Unix socket per isolated actor. No configurable backend or fallback.
"""
import datetime,hashlib,http.client,http.server,json,os,pathlib,socket,socketserver,threading,time
MODEL='Qwen/Qwen3.8-27B';PEER='127.0.0.1:9012';CAP=16384
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,value):
 path=pathlib.Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');os.replace(tmp,path)
def metadata(path):
 if path not in ('/v1/models','/get_load'):raise ValueError('Metadata path not authorized')
 c=http.client.HTTPConnection('127.0.0.1',9012,timeout=10)
 try:
  c.request('GET',path);r=c.getresponse();b=r.read(1048577)
  if r.status!=200 or len(b)>1048576:raise RuntimeError('9012 metadata unavailable status='+str(r.status))
  return dict(backend=PEER,path=path,status=r.status,utc=utc(),body=json.loads(b))
 finally:c.close()
def waiting_zero(record):
 rows=record.get('body');return isinstance(rows,list) and bool(rows) and all(isinstance(r,dict) and type(r.get('num_waiting_reqs')) is int and r['num_waiting_reqs']==0 and type(r.get('num_reqs')) is int and r['num_reqs']>=0 for r in rows)
def check_model():
 r=metadata('/v1/models')
 if {x['id'] for x in r['body'].get('data',[])}!={MODEL}:raise RuntimeError('9012 model identity mismatch')
 return r

def usage_from_sse(raw,eof):
 events=[];malformed=False
 for line in raw.splitlines():
  if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
  try:events.append(json.loads(line[6:]))
  except ValueError:malformed=True
 complete=[e for e in events if e.get('type')=='response.completed'];usage=complete[-1].get('response',{}).get('usage') if complete else None
 valid=isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens','total_tokens')) and usage['total_tokens']==usage['input_tokens']+usage['output_tokens']
 return dict(cost_complete=bool(eof and not malformed and len(complete)==1 and valid),tokens_lower_bound=usage['total_tokens'] if valid else 0,usage=usage,terminal_completed=len(complete),malformed_json=malformed)

class UnixServer(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
 daemon_threads=False;block_on_close=True
class Broker:
 def __init__(self,root,deadline):
  self.root=pathlib.Path(root);self.root.mkdir(mode=0o700);self.deadline=deadline;self.records=[];self.denials=[];self.posts=0;self.active=0;self.lock=threading.RLock();self.connections=set();self.server=None;self.persist()
 def persist(self):
  with self.lock:save(self.root/'ledger.json',dict(backend=PEER,model=MODEL,provider_POST=self.posts,records=self.records,budget_denials=self.denials,active_connections=self.active))
 def start(self):
  owner=self
  class Handler(http.server.BaseHTTPRequestHandler):
   protocol_version='HTTP/1.0'
   def log_message(self,*args):pass
   def do_GET(self):self.send_error(405)
   def do_POST(self):
    try:
     size=int(self.headers.get('Content-Length','0'))
     if self.path!='/v1/responses' or not 0<size<=16777216 or self.headers.get('Transfer-Encoding'):self.send_error(400);return
     self.connection.settimeout(30);body=self.rfile.read(size)
     if len(body)!=size:raise ValueError('Incomplete request body')
     self.connection.settimeout(2);owner.forward(self.path,body,self)
    except (BrokenPipeError,ConnectionResetError):pass
    except Exception:
     try:self.send_error(502)
     except OSError:pass
  socket_dir=self.root/'socket';socket_dir.mkdir(mode=0o755)
  self.server=UnixServer(str(socket_dir/'broker.sock'),Handler);os.chmod(socket_dir/'broker.sock',0o666);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def forward(self,path,body,client,connect=http.client.HTTPConnection):
  parsed=json.loads(body)
  if parsed.get('model')!=MODEL or parsed.get('stream') is not True:raise ValueError('Fixed streaming model required')
  if 'max_output_tokens' in parsed and parsed['max_output_tokens']!=CAP:raise ValueError('Conflicting output cap')
  parsed['max_output_tokens']=CAP;forwarded=json.dumps(parsed,separators=(',',':')).encode()
  with self.lock:
   if self.posts>=60 or time.monotonic()>=self.deadline-10:
    self.denials.append(dict(utc=utc(),reason='request_cap' if self.posts>=60 else 'wall_cap',forwarded=False));self.persist();client.send_error(429);return
   self.posts+=1;n=self.posts;self.active+=1;self.persist()
  (self.root/f'request-{n}.json').write_bytes(body);(self.root/f'forwarded-request-{n}.json').write_bytes(forwarded)
  record=dict(request=n,backend=PEER,model=MODEL,path=path,started_utc=utc(),original_sha256=sha(body),forwarded_sha256=sha(forwarded),output_cap=CAP,stream_eof=False,error=None,provider_status=None,client_disconnected=False)
  try:record['load_before_request']=metadata('/get_load')
  except Exception as e:record['load_before_request']={'backend':PEER,'utc':utc(),'error':type(e).__name__,'message':str(e)}
  c=connect('127.0.0.1',9012,timeout=max(.1,self.deadline-time.monotonic()+240));timer=None;dest=self.root/f'response-{n}.sse';start=time.monotonic();connected=False
  try:
   c.connect();connected=True
   with self.lock:self.connections.add(c)
   sock=c.sock
   def cutoff():
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   timer=threading.Timer(max(.1,self.deadline-time.monotonic()+240),cutoff);timer.start()
   c.request('POST',path,forwarded,{'Content-Type':'application/json'});r=c.getresponse();record['provider_status']=r.status
   if r.status!=200:
    err=r.read(1048576);(self.root/f'provider-error-{n}.body').write_bytes(err);record['provider_error_sha256']=sha(err);client.send_error(502);return
   client.send_response(200);client.send_header('Content-Type','text/event-stream');client.send_header('Connection','close');client.end_headers()
   with dest.open('xb') as out:
    while True:
     chunk=r.read1(8192)
     if not chunk:record['stream_eof']=True;break
     out.write(chunk);out.flush()
     if not record['client_disconnected']:
      try:client.wfile.write(chunk);client.wfile.flush()
      except (OSError,TimeoutError):record['client_disconnected']=True
  except Exception as e:record.update(error=type(e).__name__,error_message=str(e),connection_infra_failure=isinstance(e,(ConnectionRefusedError,ConnectionResetError)))
  finally:
   if timer:timer.cancel()
   c.close();raw=dest.read_bytes() if dest.exists() else b'';record.update(ended_utc=utc(),seconds=time.monotonic()-start,response_sha256=sha(raw),response_bytes=len(raw));record.update(usage_from_sse(raw,record['stream_eof']));record['cost_complete']=record['cost_complete'] and record['error'] is None and record['provider_status']==200
   record['proven_zero_model_refusal']=record['error']=='ConnectionRefusedError' and not connected
   if record['proven_zero_model_refusal']:record.update(cost_complete=True,tokens_lower_bound=0)
   with self.lock:self.connections.discard(c);self.records.append(record);self.records.sort(key=lambda r:r['request']);self.active-=1;self.persist()
 def close(self):
  if self.server:self.server.shutdown();self.thread.join(timeout=5)
  until=time.monotonic()+250
  while self.active and time.monotonic()<until:time.sleep(.1)
  if self.active:raise RuntimeError('Owned provider completion uncertain')
  if self.server:self.server.server_close()
