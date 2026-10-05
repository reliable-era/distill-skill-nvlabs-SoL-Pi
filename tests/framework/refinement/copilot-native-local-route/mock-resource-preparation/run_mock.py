"""Prepared-only launch requires exact root authorization; fake provider only."""
import argparse,hashlib,http.server,json,os,pathlib,socketserver,subprocess,threading,time
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def validate(p):
 if p['host_uid']!=os.getuid() or p['host_gid']!=os.getgid():raise ValueError('host UID/GID mismatch')
 if (p['native_starts_cap'],p['POST_cap'],p['native_seconds'],p['models'],p['retries'])!=(1,2,30,0,0):raise ValueError('budget mismatch')
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
 return a['Config']['User']==str(p['host_uid'])+':'+str(p['host_gid']) and h['NetworkMode']=='none' and h['NanoCpus']==1000000000 and h['Memory']==2147483648 and h['Tmpfs']=={'/tmp':'rw,noexec,nosuid,size=512m'} and h['ReadonlyRootfs'] and h['PidsLimit']==128 and h['CapDrop']==['ALL'] and h['SecurityOpt']==['no-new-privileges'] and mounts=={'/probe':(str(R),False),'/broker':(str(private/'socket'),False),'/output':(str(private/'output'),True)}
class Broker(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
 daemon_threads=True;block_on_close=False
 def __init__(self,path,root):
  self.root=root;self.lock=threading.Lock();self.posts=0;self.POST_headers=0;self.connections=0;self.denied_connections=0;self.records=[];self.workers=0;self.sockets=set();self.slots=threading.Semaphore(4);super().__init__(path,Handler)
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
   allowed=s.posts<2 and self.path=='/v1/chat/completions' and 0<=n<=262144 and not self.headers.get('Transfer-Encoding') and self.headers.get('Host')=='provider.example:8000'
   if allowed:s.posts+=1
  body=self.rfile.read(n) if allowed else b''
  record={'verb':'POST','ordinal':ordinal,'authority':self.headers.get('Host'),'path':self.path,'accepted':allowed and len(body)==n,'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'status':400 if allowed else 429,'inference_calls':0}
  with s.lock:s.records.append(record);s.persist()
  payload=b'{"error":{"message":"Frozen routing-only mock; no model execution","type":"invalid_request_error","code":"mock_no_inference"}}'
  self.send_response(record['status']);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
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
 private=pathlib.Path('/tmp/solpi-cpm-'+digest[:16]);private.mkdir(mode=0o700)
 (private/'launch-marker').open('x').close();(private/'launch.json').write_text(json.dumps({'plan_sha256':digest})+'\n');(private/'socket').mkdir(mode=0o700);(private/'output').mkdir(mode=0o700)
 result={'plan_sha256':digest,'model_calls':0,'errors':[]};broker=None;proc=None;name='solpi-copilot-mock-'+digest[:12];created=False
 try:
  if not absent(name):raise RuntimeError('existing owned name')
  info=json.loads(docker('image','inspect',p['image_id']))[0]
  if info['Id']!=p['image_id']:raise RuntimeError('image binding')
  if not socket_path_ok(private/'socket/broker.sock'):raise RuntimeError('Unix socket path exceeds100bytes')
  broker=Broker(str(private/'socket/broker.sock'),private);os.chmod(private/'socket/broker.sock',0o600)
  thread=threading.Thread(target=broker.serve_forever,daemon=True);thread.start()
  docker('create','--name',name,'--user',str(p['host_uid'])+':'+str(p['host_gid']),'--network','none','--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=512m','--mount','type=bind,src='+str(R)+',dst=/probe,readonly','--mount','type=bind,src='+str(private/'socket')+',dst=/broker,readonly','--mount','type=bind,src='+str(private/'output')+',dst=/output','--entrypoint','python3',p['image_id'],'/probe/worker.py');created=True
  actual=json.loads(docker('inspect',name))[0];(private/'container-before-start.json').write_text(json.dumps(actual))
  if not caps(actual,p,private):raise RuntimeError('actual caps/mount/network mismatch')
  with open(private/'private-container.log','wb') as log:
   proc=subprocess.Popen(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:proc.wait(timeout=75)
   except subprocess.TimeoutExpired:raise RuntimeError('outer timeout')
  result['container_exit_code']=json.loads(docker('inspect',name))[0]['State']['ExitCode']
  worker=json.loads((private/'output/worker-result.json').read_text());result['worker']=worker
  result['routing_candidate']=worker.get('native_starts')==1 and worker.get('native_process_terminal') is True and worker.get('native_readers_terminal') is True and worker.get('proxy_workers_remaining')==0 and 1<=broker.posts<=2 and all(r['accepted'] and r['status']==400 and r['authority']=='provider.example:8000' and r['inference_calls']==0 for r in broker.records) and not worker['errors']
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
  (private/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'private_result':str(private/'result.json'),'routing_pass':result.get('routing_pass',False),'errors':result['errors']}))
if __name__=='__main__':main()
