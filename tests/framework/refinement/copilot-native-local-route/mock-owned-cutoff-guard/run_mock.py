"""Prepared-only launch requires exact root authorization; fake provider only."""
import argparse,hashlib,http.server,json,os,pathlib,socketserver,subprocess,threading,time
from stream_session import FixtureSession
R=pathlib.Path(__file__).resolve().parent
import sys,types
sys.path.insert(0,str(R.parent.parent/'pi-takeover'))
from copilot_host_cutoff_controller import HostCutoffController
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def validate(p):
 if p['host_uid']!=os.getuid() or p['host_gid']!=os.getgid():raise ValueError('host UID/GID mismatch')
 if (p['native_starts_cap'],p['POST_cap'],p['native_seconds'],p['models'],p['retries'])!=(1,1,30,0,0):raise ValueError('budget mismatch')
 for n,h in p['source_hashes'].items():
  if sha(R/n)!=h:raise ValueError('source mismatch')
def docker(*a,timeout=5):
 z=subprocess.run(['docker',*a],capture_output=True,text=True,timeout=timeout)
 if z.returncode:raise RuntimeError('docker '+a[0]+' failed')
 return z.stdout.strip()
def absent(name):
 z=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
 return z.returncode!=0 and z.stderr.strip() in ['Error: No such object: '+name,'Error response from daemon: No such container: '+name]
def caps(a,p,private):
 h=a['HostConfig'];mounts={m['Destination']:(m['Source'],m['RW']) for m in a['Mounts']}
 return a['Config']['User']==str(p['host_uid'])+':'+str(p['host_gid']) and h['NetworkMode']=='none' and h['NanoCpus']==1000000000 and h['Memory']==2147483648 and h['Tmpfs']=={'/tmp':'rw,exec,nosuid,size=512m'} and h['ReadonlyRootfs'] and h['PidsLimit']==128 and h['CapDrop']==['ALL'] and h['SecurityOpt']==['no-new-privileges'] and mounts=={'/probe':(str(R),False),'/broker':(str(private/'socket'),False),'/output':(str(private/'output'),True)}
class Broker(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
 daemon_threads=True;block_on_close=False
 def __init__(self,path,root):
  self.controller=None;self.fixture=FixtureSession();self.root=root;self.lock=threading.Lock();self.posts=0;self.POST_headers=0;self.connections=0;self.denied_connections=0;self.records=[];self.workers=0;self.sockets=set();self.slots=threading.Semaphore(4);super().__init__(path,Handler)
 def persist(self):
  (self.root/'broker-ledger.json').write_text(json.dumps({'accepted_body_POST':self.posts,'all_POST_headers':self.POST_headers,'accepted_connections':self.connections,'denied_connections':self.denied_connections,'records':self.records,'workers':self.workers},indent=2)+'\n')
 def get_request(self):
  sock,addr=super().get_request();sock.settimeout(3)
  return sock,addr
 def process_request(self,sock,addr):
  with self.lock:
   allowed=self.connections<16 and self.slots.acquire(False)
   if allowed:self.connections+=1;self.workers+=1;self.sockets.add(sock)
   else:self.denied_connections+=1
   self.persist()
  if not allowed:self.shutdown_request(sock);return
  try:super().process_request(sock,addr)
  except BaseException:
   with self.lock:self.workers-=1;self.sockets.discard(sock);self.persist()
   self.slots.release();self.shutdown_request(sock);raise
 def process_request_thread(self,sock,addr):
  try:super().process_request_thread(sock,addr)
  finally:
   with self.lock:self.workers-=1;self.sockets.discard(sock);self.persist()
   self.slots.release()
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def deny(self,verb):
  with self.server.lock:self.server.records.append({'verb':verb,'path':self.path,'accepted':False,'status':403,'inference_calls':0});self.server.persist()
  self.send_error(403)
 def do_POST(self):
  s=self.server
  with s.lock:s.POST_headers+=1;ordinal=s.POST_headers
  try:n=int(self.headers.get('Content-Length','-1'))
  except ValueError:n=-1
  with s.lock:
   allowed=s.controller.guard.admit() and s.posts<1 and self.path=='/v1/chat/completions' and 0<=n<=262144 and not self.headers.get('Transfer-Encoding') and self.headers.get('Host')=='provider.example:8000'
   if allowed:s.posts+=1
  body=self.rfile.read(n) if allowed else b''
  payload=b'';status=429;fixture_error=None;guard_code=None;shape=None
  if allowed and len(body)==n:
   try:
    obj=json.loads(body)
    from guard_metadata import describe
    shape=describe(obj)
    with s.lock:payload=s.fixture.response(obj);status=200
   except Exception as e:status=422;fixture_error=type(e).__name__;guard_code=getattr(e,'guard_code','UNCLASSIFIED_EXCEPTION')
  record={'verb':'POST','ordinal':ordinal,'authority':self.headers.get('Host'),'path':self.path,'accepted':allowed and len(body)==n,'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'status':status,'inference_calls':0,'synthetic_ONLY':True,'fixture_error_type':fixture_error,'tool_result_seen':False,'guard_code':guard_code,'shape_metadata':shape}
  with s.lock:s.records.append(record);s.persist()
  if status!=200:payload=b'{"error":{"message":"Synthetic fixture guard rejected request"}}'
  from response_receipt import inspect_response
  if len(payload)>65536:raise ValueError('response receipt cap')
  response_name='response-'+str(ordinal)+'.sse'
  (s.root/response_name).write_bytes(payload)
  record['response_receipt']={'deliberate_transport_cutoff':status==200,'promised_content_length':len(payload)+128 if status==200 else len(payload),'file':response_name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'prepared_NOT_delivery':True,'write_completed':False,'inspection':inspect_response(payload) if status==200 else None}
  with s.lock:s.persist()
  try:
   self.send_response(status);self.send_header('Content-Type','text/event-stream' if status==200 else 'application/json');self.send_header('Content-Length',str(len(payload)+128 if status==200 else len(payload)));self.end_headers();written=self.wfile.write(payload);self.wfile.flush()
   if status==200:
    startup=s.root/'output/worker-start.json'
    if not startup.exists():raise RuntimeError('startup witness unavailable; no inferred native starts')
    record['startup_witness_sha256']=sha(startup)
    s.controller.journal_partial(payload,len(payload)+128)
    s.controller.stop_before_eof()
    record['verified_owned_stop_before_EOF']=True
    self.close_connection=True
    self.connection.shutdown(1)
   record['response_receipt']['write_completed']=written==len(payload)
   record['response_receipt']['bytes_written']=written
  except Exception as e:record['response_receipt']['write_error_type']=type(e).__name__;raise
  finally:
   with s.lock:s.persist()
 def do_GET(self):self.deny('GET')
 def do_CONNECT(self):self.deny('CONNECT')
 def do_PUT(self):self.deny('PUT')
def final_pass(result):
 return bool(result.get('routing_candidate') and result.get('container_absent') and result.get('docker_client_terminal') and result.get('broker_workers_remaining')==0 and result.get('socket_absent') and not result['errors'])
def socket_path_ok(path):
 return len(os.fsencode(path))<=100
def main():
 a=argparse.ArgumentParser();a.add_argument('--launch',action='store_true');x=a.parse_args()
 p=json.loads((R/'plan.json').read_text());validate(p)
 if not x.launch:print('prepared; zero runtime calls');return
 digest=sha(R/'plan.json');auth=json.loads((R/'execution-authorization.json').read_text())
 if auth.get('authorized') is not True or auth.get('plan_sha256')!=digest:raise RuntimeError('exact authorization missing')
 private=pathlib.Path('/tmp/solpi-cpguard-'+digest[:16]);private.mkdir(mode=0o700)
 (private/'launch-marker').open('x').close();(private/'launch.json').write_text(json.dumps({'plan_sha256':digest})+'\n');(private/'socket').mkdir(mode=0o700);(private/'output').mkdir(mode=0o700)
 result={'plan_sha256':digest,'model_calls':0,'errors':[]};broker=None;proc=None;name='solpi-copilot-owned-guard-'+digest[:12];created=False
 try:
  if not absent(name):raise RuntimeError('existing owned name')
  info=json.loads(docker('image','inspect',p['image_id']))[0]
  if info['Id']!=p['image_id']:raise RuntimeError('image binding')
  if not socket_path_ok(private/'socket/broker.sock'):raise RuntimeError('Unix socket path exceeds100bytes')
  broker=Broker(str(private/'socket/broker.sock'),private);os.chmod(private/'socket/broker.sock',0o600)
  thread=threading.Thread(target=broker.serve_forever,daemon=True);thread.start()
  docker('create','--name',name,'--user',str(p['host_uid'])+':'+str(p['host_gid']),'--network','none','--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,exec,nosuid,size=512m','--mount','type=bind,src='+str(R)+',dst=/probe,readonly','--mount','type=bind,src='+str(private/'socket')+',dst=/broker,readonly','--mount','type=bind,src='+str(private/'output')+',dst=/output','--entrypoint','python3',p['image_id'],'/probe/worker.py');created=True
  actual=json.loads(docker('inspect',name))[0];(private/'container-before-start.json').write_text(json.dumps(actual))
  if not caps(actual,p,private):raise RuntimeError('actual caps/mount/network mismatch')
  session=types.SimpleNamespace(active='probe',deadline=time.monotonic()+30)
  context={'arm':'probe','deadline':session.deadline,'container_id':actual['Id'],'name':name,'image':p['image_id'],'row':{'phase':'owned_guard_prepared'},'path':private/'guard-row.json'}
  broker.controller=HostCutoffController(session,context,docker,{name},private,cap=1)
  with open(private/'private-container.log','wb') as log:
   proc=subprocess.Popen(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:proc.wait(timeout=75)
   except subprocess.TimeoutExpired:raise RuntimeError('outer timeout')
  result['container_exit_code']=json.loads(docker('inspect',name))[0]['State']['ExitCode']
  # A verified whole-container stop can prevent final worker/usage writes.
  for filename,key in [('worker-start.json','startup'),('worker-result.json','worker'),('private-usage.json','native_usage')]:
   path=private/'output'/filename
   result[key]=json.loads(path.read_text()) if path.exists() else None
  row=json.loads((private/'guard-row.json').read_text())
  result['guard_row']=row
  result['routing_candidate']=False
  result['guard_candidate']=bool(row.get('issuer_stop_receipt',{}).get('owned_stop_verified') and broker.posts==1 and broker.POST_headers==1 and result['startup'] and result['startup']['native_starts']==1 and all(x.get('verified_owned_stop_before_EOF') for x in broker.records))

 except Exception as e:result['errors'].append(type(e).__name__+': '+str(e))
 finally:
  if created:
   try:docker('rm','-f',name,timeout=10);result['container_absent']=absent(name)
   except Exception as e:result['errors'].append('container cleanup '+str(e))
  if proc is not None:
   try:proc.wait(timeout=3);result['docker_client_terminal']=True
   except subprocess.TimeoutExpired:
    import signal
    os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3);result['docker_client_terminal']=True
  if broker is not None:
   stop=threading.Thread(target=broker.shutdown,daemon=True);stop.start();stop.join(timeout=2)
   if stop.is_alive():result['errors'].append('broker shutdown uncertain')
   for sock in list(broker.sockets):
    try:sock.shutdown(2)
    except OSError:pass
   broker.server_close();thread.join(timeout=3)
   end=time.monotonic()+3
   while broker.workers and time.monotonic()<end:time.sleep(.01)
   result['broker_workers_remaining']=broker.workers;broker.persist()
   pathlib.Path(broker.server_address).unlink(missing_ok=True)
   result['socket_absent']=not pathlib.Path(broker.server_address).exists()
  result['routing_pass']=final_pass(result)
  result['owned_guard_pass']=bool(result.get('guard_candidate') and result.get('container_absent') and result.get('docker_client_terminal') and result.get('broker_workers_remaining')==0 and result.get('socket_absent') and not result['errors'])
  (private/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'private_result':str(private/'result.json'),'routing_pass':result.get('routing_pass',False),'owned_guard_pass':result.get('owned_guard_pass',False),'errors':result['errors']}))
if __name__=='__main__':main()
