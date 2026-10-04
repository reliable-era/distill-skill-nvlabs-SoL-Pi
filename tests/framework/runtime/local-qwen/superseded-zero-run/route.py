"""Root-reviewed routing-only preparation; no native model starts in this entrypoint."""
import pathlib,json,subprocess,uuid,threading,http.server,importlib.util,hashlib,fcntl,contextlib
R=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('broker',R/'broker.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def main():
 p=json.loads((R/'plan.json').read_text())
 if p['model_starts']!=0:raise RuntimeError('routing entrypoint permits zero model starts')
 for f,h in p['source_hashes'].items():
  if hashlib.sha256((R/f).read_bytes()).hexdigest()!=h:raise RuntimeError('source mismatch')
 locks=[]
 for item in p['shared_inference_locks']:
  path=pathlib.Path(item['path']);info=path.stat()
  if (info.st_dev,info.st_ino)!=(item['device'],item['inode']):raise RuntimeError('shared lock identity changed')
  lock=path.open('r');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(lock)
 prefix='solpi-qwenroute-'+uuid.uuid4().hex[:10];nets=[];owned=[];server=None;errors=[]
 def cmd(*args):return subprocess.check_output(['docker',*args],text=True,timeout=12).strip()
 try:
  for part in ['actor','provider']:
   n=prefix+'-'+part;opts=['--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated'] if part=='actor' else []
   cmd('network','create','--internal','--ipv6=false',*opts,n);nets.append(n)
  info=json.loads(cmd('network','inspect',nets[1]))[0];gateway=info['IPAM']['Config'][0]['Gateway']
  server=http.server.ThreadingHTTPServer((gateway,0),b.Broker);threading.Thread(target=server.serve_forever,daemon=True).start();port=server.server_address[1]
  proxy=prefix+'-proxy';owned.append(proxy)
  cmd('run','-d','--name',proxy,'--network',nets[0],'--network-alias','proxy','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-e','EGRESS_ALLOWLIST='+json.dumps({'provider.example:'+str(port):gateway}),'-v',str(R.parent/'egress')+':/app:ro',p['image_id'],'/app/proxy.py');cmd('network','connect',nets[1],proxy)
  code='''import urllib.request,socket,json
p=urllib.request.build_opener(urllib.request.ProxyHandler({'http':'http://proxy:8080'}));r={}
r['models']=json.load(p.open('http://provider.example:PORT/v1/models',timeout=5))['data'][0]['id']
for name,url in [('authority','http://blocked.example:PORT/v1/models'),('path','http://provider.example:PORT/solution')]:
 try:p.open(url,timeout=3);r[name]=False
 except urllib.error.HTTPError as e:r[name]=e.code==403
try:socket.create_connection(('GATEWAY',PORT),timeout=2);r['direct_host_blocked']=False
except OSError:r['direct_host_blocked']=True
print(json.dumps(r))'''.replace('PORT',str(port)).replace('GATEWAY',gateway)
  result=json.loads(cmd('run','--rm','--network',nets[0],'--entrypoint','python3',p['image_id'],'-c',code))
  if result.get('models')!=p['model'] or not all(result.get(k) for k in ['authority','path','direct_host_blocked']):raise RuntimeError('routing control failed')
 finally:
  if server:server.shutdown();server.server_close()
  for n in reversed(owned):
   try:cmd('rm','-f',n)
   except Exception:errors.append('owned container cleanup uncertain')
  for n in reversed(nets):
   try:cmd('network','rm',n)
   except Exception:errors.append('owned network cleanup uncertain')
  for lock in locks:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  if errors:raise RuntimeError(';'.join(errors))
 # Scope: zero POST/native starts; not a server-idleness certification.
 print(json.dumps({'routing':result,'posts':b.Broker.count,'native_starts':0,'cleanup_errors':errors}))
if __name__=='__main__':main()
