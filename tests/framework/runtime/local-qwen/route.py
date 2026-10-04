"""Exclusive root-reviewed GET-only routing controls; no native model starts."""
import pathlib,json,subprocess,uuid,threading,http.server,importlib.util,hashlib,fcntl,argparse,time,resource
R=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('broker',R/'broker.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def validate(p):
 if p['model_starts']!=0 or p['post_requests']!=0 or p['routing_deadline_seconds']!=45:raise RuntimeError('zero-inference guard')
 for f,h in p['source_hashes'].items():
  target=(R/f).resolve()
  if hashlib.sha256(target.read_bytes()).hexdigest()!=h:raise RuntimeError('source mismatch')
def absence(returncode,stderr,kind,name):
 if returncode==0:return False
 if kind=='container':return stderr.strip() in ('Error: No such object: '+name,'Error response from daemon: No such container: '+name)
 if kind=='network':return stderr.strip() in ('Error: No such network: '+name,'Error response from daemon: network '+name+' not found')
 return False

def resources_ok(row):
 h=row['HostConfig'];return h.get('NanoCpus')==1000000000 and h.get('Memory')==536870912
def actor_isolation_ok(row,network):
 return set(row['NetworkSettings']['Networks'])=={network} and not row.get('Mounts') and resources_ok(row)

def bounded_command(argv,private,sequence,seconds):
 # Child file size limit bounds stdout/stderr independently; raw files stay private.
 stdout=private/('command-'+str(sequence)+'.stdout');stderr=private/('command-'+str(sequence)+'.stderr')
 def limit():resource.setrlimit(resource.RLIMIT_FSIZE,(32768,32768))
 timed_out=False
 with stdout.open('wb') as out,stderr.open('wb') as err:
  try:result=subprocess.run(argv,stdout=out,stderr=err,timeout=seconds,preexec_fn=limit)
  except subprocess.TimeoutExpired:timed_out=True;result=None
 meta={'sequence':sequence,'operation':argv[1] if len(argv)>1 else 'unknown','exit_code':result.returncode if result else None,'timeout':timed_out,'stdout_bytes':stdout.stat().st_size,'stderr_bytes':stderr.stat().st_size,'capture_limit_bytes':32768,'stdout_sha256':hashlib.sha256(stdout.read_bytes()).hexdigest(),'stderr_sha256':hashlib.sha256(stderr.read_bytes()).hexdigest()}
 (private/('command-'+str(sequence)+'.json')).write_text(json.dumps(meta)+'\n')
 if timed_out or result.returncode:
  # Error metadata points to preserved private capture; never publishes command/raw content.
  raise RuntimeError('command_failure '+json.dumps(meta,separators=(',',':')))
 return stdout.read_text(errors='replace').strip()

def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-get-only',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args()
 digest=hashlib.sha256((R/'plan.json').read_bytes()).hexdigest()
 if not x.execute_get_only or x.plan_sha256!=digest:raise SystemExit('explicit authorization/hash required')
 p=json.loads((R/'plan.json').read_text());validate(p)
 private=pathlib.Path('/tmp')/('solpi-qwenroute-'+digest);private.mkdir(mode=0o700,exist_ok=False)
 (private/'launch.json').write_text(json.dumps({'plan':digest,'native_starts':0,'POST':0}))
 prefix='solpi-qwenroute-'+uuid.uuid4().hex[:10];nets=[];owned=[];server=None;locks=[];errors=[];result=None;start=time.monotonic();sequence=0;resource_proofs=[];absence_proofs=[];proxy=None;proxy_counters=None;proxy_health=None;direct_hop=None
 def cmd(*args,cleanup=False):
  nonlocal sequence
  sequence+=1
  budget=8 if cleanup else min(8,45-(time.monotonic()-start))
  if budget<=0:raise RuntimeError('routing deadline')
  return bounded_command(['docker',*args],private,sequence,budget)
 def remove(name):
  z=subprocess.run(['docker','rm','-f',name],capture_output=True,text=True,timeout=5)
  q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=3)
  for label,value in [('remove.stdout',z.stdout),('remove.stderr',z.stderr),('inspect.stdout',q.stdout),('inspect.stderr',q.stderr)]:
   (private/(name+'-'+label)).write_text(value[:32768])
  verified=absence(q.returncode,q.stderr,'container',name)
  absence_proofs.append({'kind':'container','name':name,'remove_exit':z.returncode,'inspect_exit':q.returncode,'absence_verified':verified})
  if not verified:raise RuntimeError('owned container absence unverified')
 try:
  for item in p['shared_inference_locks']:
   path=pathlib.Path(item['path']);s=path.stat()
   if (s.st_dev,s.st_ino)!=(item['device'],item['inode']):raise RuntimeError('lock identity changed')
   lock=path.open('r');locks.append(lock);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if cmd('image','inspect','--format','{{.Id}}',p['image_id'])!=p['image_id']:raise RuntimeError('image mismatch')
  n=prefix+'-actor';nets.append(n)
  cmd('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',n)
  netdata=json.loads(cmd('network','inspect',n))[0]
  if not netdata['Internal'] or netdata['EnableIPv6'] or netdata['IPAM']['Config'][0].get('Gateway'):raise RuntimeError('network isolation mismatch')
  socketdir=private/'socket';socketdir.mkdir(mode=0o700);socketpath=socketdir/'broker.sock'
  server=b.OwnedUnixServer(str(socketpath),b.Broker);threading.Thread(target=server.serve_forever,daemon=True).start();port=8000
  proxy=prefix+'-proxy';owned.append(proxy)
  cmd('run','-d','--pull=never','--name',proxy,'--user',str(__import__('os').getuid())+':'+str(__import__('os').getgid()),'--network',nets[0],'--network-alias','proxy','--cpus','1','--memory','512m','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-e','EGRESS_ALLOWLIST='+json.dumps({'provider.example:'+str(port):'owned-unix-broker'}),'-v',str(R)+':/app:ro','-v',str(socketdir)+':/broker:ro',p['image_id'],'/app/metadata_proxy.py')
  z=json.loads(cmd('inspect',proxy))[0]
  resource_proofs.append({'kind':'proxy','memory':z['HostConfig'].get('Memory'),'nano_cpus':z['HostConfig'].get('NanoCpus'),'verified':resources_ok(z)})
  if not resources_ok(z):raise RuntimeError('proxy resource mismatch')
  if set(z['NetworkSettings']['Networks'])!=set(nets):raise RuntimeError('proxy attachments mismatch')
  socketmounts=[m for m in z['Mounts'] if m.get('Destination')=='/broker']
  if len(socketmounts)!=1 or socketmounts[0].get('RW') or socketmounts[0].get('Source')!=str(socketdir):raise RuntimeError('proxy socketmount mismatch')
  health_code='import urllib.request;print(urllib.request.urlopen("http://127.0.0.1:8080/_health",timeout=2).read().decode())'
  proxy_health=json.loads(cmd('exec',proxy,'python3','-c',health_code))
  hop_code='import sys,json;sys.path.insert(0,"/app");from metadata_proxy import UnixHTTPConnection;c=UnixHTTPConnection("/broker/broker.sock");c.request("GET","/v1/models");print(json.loads(c.getresponse().read())["data"][0]["id"])'
  direct_hop=cmd('exec',proxy,'python3','-c',hop_code)
  if direct_hop!=p['model']:raise RuntimeError('direct proxy-to-broker metadata mismatch')
  code='''import urllib.request,socket,json
p=urllib.request.build_opener(urllib.request.ProxyHandler({'http':'http://proxy:8080'}));r={}
r['models']=json.load(p.open('http://provider.example:PORT/v1/models',timeout=5))['data'][0]['id']
for name,url in [('authority','http://blocked.example:PORT/v1/models'),('path','http://provider.example:PORT/solution')]:
 try:p.open(url,timeout=3);r[name]=False
 except urllib.error.HTTPError as e:r[name]=e.code==403
try:socket.create_connection(('GATEWAY',PORT),timeout=2);r['direct_host_blocked']=False
except OSError:r['direct_host_blocked']=True
print(json.dumps(r))'''.replace('PORT',str(port)).replace('GATEWAY','127.0.0.1')
  probe=prefix+'-probe';owned.append(probe)
  result=json.loads(cmd('run','--pull=never','--name',probe,'--network',nets[0],'--cpus','1','--memory','512m','--cap-drop','ALL','--entrypoint','python3',p['image_id'],'-c',code))
  z=json.loads(cmd('inspect',probe))[0]
  resource_proofs.append({'kind':'probe','memory':z['HostConfig'].get('Memory'),'nano_cpus':z['HostConfig'].get('NanoCpus'),'verified':resources_ok(z)})
  if not resources_ok(z):raise RuntimeError('probe resource mismatch')
  if set(z['NetworkSettings']['Networks'])!={nets[0]}:raise RuntimeError('probe attachment mismatch')
  if not actor_isolation_ok(z,nets[0]):raise RuntimeError('actorprobe isolation/resource/mount mismatch')
  if result.get('models')!=p['model'] or not all(result.get(k) for k in ['authority','path','direct_host_blocked']):raise RuntimeError('routing control failed')
 except Exception as e:errors.append(type(e).__name__+': '+str(e))
 finally:
  if proxy:
   try:proxy_counters=json.loads(cmd('exec',proxy,'python3','-c','import urllib.request;print(urllib.request.urlopen(\"http://127.0.0.1:8080/_health\",timeout=2).read().decode())',cleanup=True))
   except Exception:pass
  if server:
   t=threading.Thread(target=server.shutdown,daemon=True);t.start();t.join(2)
   if t.is_alive():errors.append('broker shutdown unverified')
   server.terminate_connections();server.server_close()
   until=time.monotonic()+6
   while (b.Broker.active or server.workers) and time.monotonic()<until:time.sleep(0.05)
   if b.Broker.active or server.workers:errors.append('broker request threads remain active')
   socketpath.unlink(missing_ok=True)
   if socketpath.exists():errors.append('broker socket absence unverified')
  for n in reversed(owned):
   try:remove(n)
   except Exception:errors.append('owned container cleanup uncertain '+n)
  for n in reversed(nets):
   try:
    cmd('network','rm',n,cleanup=True)
    q=subprocess.run(['docker','network','inspect',n],capture_output=True,text=True,timeout=3)
    verified=absence(q.returncode,q.stderr,'network',n);absence_proofs.append({'kind':'network','name':n,'inspect_exit':q.returncode,'absence_verified':verified})
    if not verified:errors.append('owned network remains')
   except Exception:errors.append('owned network cleanup uncertain '+n)
  for lock in locks:lock.close()
  if b.Broker.posts:errors.append('POST attempted')
  report={'routing':result,'POST':b.Broker.posts,'native_starts':0,'errors':errors,'elapsed':time.monotonic()-start,'idleness':'Not certified; no models authorized','resource_proofs':resource_proofs,'absence_proofs':absence_proofs,'command_captures':sequence,'broker_socket_absent':not socketpath.exists() if server else None,'broker_workers_remaining':server.workers if server else None,'proxy_startup_health':proxy_health,'proxy_counters':proxy_counters,'direct_proxy_broker_model':direct_hop,'broker_counters':{k:getattr(b.Broker,k) for k in ['get_count','upstream_connect','upstream_status','completed','upstream_error']}}
  (private/'final-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
 if errors:raise SystemExit('routing failed; private evidence retained')
 print(json.dumps(report))
if __name__=='__main__':main()
