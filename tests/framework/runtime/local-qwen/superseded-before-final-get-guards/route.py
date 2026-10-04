"""Exclusive root-reviewed GET-only routing controls; no native model starts."""
import pathlib,json,subprocess,uuid,threading,http.server,importlib.util,hashlib,fcntl,argparse,time
R=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('broker',R/'broker.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def validate(p):
 if p['model_starts']!=0 or p['post_requests']!=0 or p['routing_deadline_seconds']!=45:raise RuntimeError('zero-inference guard')
 for f,h in p['source_hashes'].items():
  target=(R/f).resolve()
  if hashlib.sha256(target.read_bytes()).hexdigest()!=h:raise RuntimeError('source mismatch')
def absence(returncode,stderr):return returncode!=0 and ('No such' in stderr)
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-get-only',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args()
 digest=hashlib.sha256((R/'plan.json').read_bytes()).hexdigest()
 if not x.execute_get_only or x.plan_sha256!=digest:raise SystemExit('explicit authorization/hash required')
 p=json.loads((R/'plan.json').read_text());validate(p)
 private=pathlib.Path('/tmp')/('solpi-qwenroute-'+digest);private.mkdir(mode=0o700,exist_ok=False)
 (private/'launch.json').write_text(json.dumps({'plan':digest,'native_starts':0,'POST':0}))
 prefix='solpi-qwenroute-'+uuid.uuid4().hex[:10];nets=[];owned=[];server=None;locks=[];errors=[];result=None;start=time.monotonic()
 def cmd(*args,cleanup=False):
  budget=8 if cleanup else min(8,45-(time.monotonic()-start))
  if budget<=0:raise RuntimeError('routing deadline')
  return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.PIPE,timeout=budget).strip()
 def remove(name):
  z=subprocess.run(['docker','rm','-f',name],capture_output=True,text=True,timeout=5)
  q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=3)
  if not absence(q.returncode,q.stderr):raise RuntimeError('owned container absence unverified')
 try:
  for item in p['shared_inference_locks']:
   path=pathlib.Path(item['path']);s=path.stat()
   if (s.st_dev,s.st_ino)!=(item['device'],item['inode']):raise RuntimeError('lock identity changed')
   lock=path.open('r');locks.append(lock);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if cmd('image','inspect','--format','{{.Id}}',p['image_id'])!=p['image_id']:raise RuntimeError('image mismatch')
  for part in ['actor','provider']:
   n=prefix+'-'+part;nets.append(n);opts=['--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated'] if part=='actor' else []
   cmd('network','create','--internal','--ipv6=false',*opts,n)
  netdata=[json.loads(cmd('network','inspect',n))[0] for n in nets]
  if any(not n['Internal'] or n['EnableIPv6'] for n in netdata) or netdata[0]['IPAM']['Config'][0].get('Gateway'):raise RuntimeError('network isolation mismatch')
  gateway=netdata[1]['IPAM']['Config'][0]['Gateway']
  server=http.server.ThreadingHTTPServer((gateway,0),b.Broker);server.daemon_threads=True;threading.Thread(target=server.serve_forever,daemon=True).start();port=server.server_address[1]
  proxy=prefix+'-proxy';owned.append(proxy)
  cmd('run','-d','--pull=never','--name',proxy,'--network',nets[0],'--network-alias','proxy','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-e','EGRESS_ALLOWLIST='+json.dumps({'provider.example:'+str(port):gateway}),'-v',str(R.parent/'egress')+':/app:ro',p['image_id'],'/app/proxy.py');cmd('network','connect',nets[1],proxy)
  z=json.loads(cmd('inspect',proxy))[0]
  if set(z['NetworkSettings']['Networks'])!=set(nets):raise RuntimeError('proxy attachments mismatch')
  code='''import urllib.request,socket,json
p=urllib.request.build_opener(urllib.request.ProxyHandler({'http':'http://proxy:8080'}));r={}
r['models']=json.load(p.open('http://provider.example:PORT/v1/models',timeout=5))['data'][0]['id']
for name,url in [('authority','http://blocked.example:PORT/v1/models'),('path','http://provider.example:PORT/solution')]:
 try:p.open(url,timeout=3);r[name]=False
 except urllib.error.HTTPError as e:r[name]=e.code==403
try:socket.create_connection(('GATEWAY',PORT),timeout=2);r['direct_host_blocked']=False
except OSError:r['direct_host_blocked']=True
print(json.dumps(r))'''.replace('PORT',str(port)).replace('GATEWAY',gateway)
  probe=prefix+'-probe';owned.append(probe)
  result=json.loads(cmd('run','--pull=never','--name',probe,'--network',nets[0],'--cap-drop','ALL','--entrypoint','python3',p['image_id'],'-c',code))
  z=json.loads(cmd('inspect',probe))[0]
  if set(z['NetworkSettings']['Networks'])!={nets[0]}:raise RuntimeError('probe attachment mismatch')
  if result.get('models')!=p['model'] or not all(result.get(k) for k in ['authority','path','direct_host_blocked']):raise RuntimeError('routing control failed')
 except Exception as e:errors.append(type(e).__name__+': '+str(e)[:120])
 finally:
  if server:
   t=threading.Thread(target=server.shutdown,daemon=True);t.start();t.join(2)
   if t.is_alive():errors.append('broker shutdown unverified')
   server.server_close()
  for n in reversed(owned):
   try:remove(n)
   except Exception:errors.append('owned container cleanup uncertain '+n)
  for n in reversed(nets):
   try:
    cmd('network','rm',n,cleanup=True)
    q=subprocess.run(['docker','network','inspect',n],capture_output=True,text=True,timeout=3)
    if not absence(q.returncode,q.stderr):errors.append('owned network remains')
   except Exception:errors.append('owned network cleanup uncertain '+n)
  for lock in locks:lock.close()
  if b.Broker.posts:errors.append('POST attempted')
  report={'routing':result,'POST':b.Broker.posts,'native_starts':0,'errors':errors,'elapsed':time.monotonic()-start,'idleness':'Not certified; no models authorized'}
  (private/'final-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
 if errors:raise SystemExit('routing failed; private evidence retained')
 print(json.dumps(report))
if __name__=='__main__':main()
