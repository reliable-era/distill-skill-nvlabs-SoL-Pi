"""Prepared-only launch requires exact root authorization; fake provider only."""
import argparse,hashlib,http.server,json,os,pathlib,socketserver,subprocess,threading,time
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def validate(p):
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
 return h['NetworkMode']=='none' and h['NanoCpus']==1000000000 and h['Memory']==536870912 and h['ReadonlyRootfs'] and h['PidsLimit']==128 and mounts=={'/probe':(str(R),False),'/broker':(str(private/'socket'),False),'/output':(str(private/'output'),True)}
class Broker(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
 daemon_threads=True;block_on_close=False
 def __init__(self,path,root):
  self.root=root;self.lock=threading.Lock();self.posts=0;self.records=[];self.workers=0;self.sockets=set();super().__init__(path,Handler)
 def persist(self):
  (self.root/'broker-ledger.json').write_text(json.dumps({'POST':self.posts,'records':self.records,'workers':self.workers},indent=2)+'\n')
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  s=self.server;self.connection.settimeout(3)
  with s.lock:
   s.workers+=1;s.sockets.add(self.connection)
  try:
   with s.lock:
    if s.posts>=2:
     self.close_connection=True;return
    s.posts+=1;num=s.posts
   n=int(self.headers.get('Content-Length','-1'))
   allowed=num<=2 and self.path=='/v1/chat/completions' and 0<=n<=262144 and not self.headers.get('Transfer-Encoding')
   body=self.rfile.read(n) if allowed else b''
   record={'ordinal':num,'path':self.path,'accepted':allowed and len(body)==n,'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'status':400 if allowed else 429,'inference_calls':0}
   with s.lock:s.records.append(record);s.persist()
   payload=b'{"error":{"message":"Frozen routing-only mock; no model execution","type":"invalid_request_error","code":"mock_no_inference"}}'
   self.send_response(record['status']);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
  finally:
   with s.lock:s.workers-=1;s.sockets.discard(self.connection);s.persist()
 def do_GET(self):self.send_error(403)
def main():
 a=argparse.ArgumentParser();a.add_argument('--launch',action='store_true');x=a.parse_args()
 p=json.loads((R/'plan.json').read_text());validate(p)
 if not x.launch:print('prepared; zero runtime calls');return
 digest=sha(R/'plan.json');auth=json.loads((R/'execution-authorization.json').read_text())
 if auth.get('authorized') is not True or auth.get('plan_sha256')!=digest:raise RuntimeError('exact authorization missing')
 private=pathlib.Path('/tmp/solpi-copilot-native-mock-'+digest);private.mkdir(mode=0o700)
 (private/'launch-marker').open('x').close();(private/'socket').mkdir(mode=0o700);(private/'output').mkdir(mode=0o700)
 result={'plan_sha256':digest,'model_calls':0,'errors':[]};broker=None;proc=None;name='solpi-copilot-mock-'+digest[:12];created=False
 try:
  if not absent(name):raise RuntimeError('existing owned name')
  info=json.loads(docker('image','inspect',p['image_id']))[0]
  if info['Id']!=p['image_id']:raise RuntimeError('image binding')
  broker=Broker(str(private/'socket/broker.sock'),private);os.chmod(private/'socket/broker.sock',0o600)
  thread=threading.Thread(target=broker.serve_forever,daemon=True);thread.start()
  docker('create','--name',name,'--network','none','--cpus','1','--memory','512m','--pids-limit','128','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=128m','--mount','type=bind,src='+str(R)+',dst=/probe,readonly','--mount','type=bind,src='+str(private/'socket')+',dst=/broker,readonly','--mount','type=bind,src='+str(private/'output')+',dst=/output','--entrypoint','python3',p['image_id'],'/probe/worker.py');created=True
  actual=json.loads(docker('inspect',name))[0];(private/'container-before-start.json').write_text(json.dumps(actual))
  if not caps(actual,p,private):raise RuntimeError('actual caps/mount/network mismatch')
  with open(private/'private-container.log','wb') as log:
   proc=subprocess.Popen(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:proc.wait(timeout=45)
   except subprocess.TimeoutExpired:raise RuntimeError('outer timeout')
  result['container_exit_code']=json.loads(docker('inspect',name))[0]['State']['ExitCode']
  worker=json.loads((private/'output/worker-result.json').read_text());result['worker']=worker
  result['routing_pass']=worker.get('native_starts')==1 and worker.get('native_process_terminal') is True and worker.get('proxy_workers_remaining')==0 and 1<=broker.posts<=2 and all(r['accepted'] for r in broker.records) and not worker['errors']
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
  (private/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'private_result':str(private/'result.json'),'routing_pass':result.get('routing_pass',False),'errors':result['errors']}))
if __name__=='__main__':main()
