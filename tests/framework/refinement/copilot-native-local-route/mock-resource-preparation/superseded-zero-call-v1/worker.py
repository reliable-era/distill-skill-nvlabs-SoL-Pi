"""Single native CLI attempt against an owned fake provider; no inference."""
import hashlib,json,os,pathlib,signal,subprocess,threading,time,shutil
from tunnel_proxy import TunnelProxy
from server import OwnedServer
OUT=pathlib.Path('/output')
SAFE={'PATH':os.environ['PATH'],'HOME':'/tmp/fresh-home','XDG_CONFIG_HOME':'/tmp/fresh-home/config','XDG_CACHE_HOME':'/tmp/fresh-home/cache','COPILOT_OFFLINE':'true','COPILOT_PROVIDER_BASE_URL':'http://provider.example:8000/v1','COPILOT_PROVIDER_TYPE':'openai','COPILOT_PROVIDER_WIRE_API':'completions','COPILOT_MODEL':'mock-routing-only','HTTP_PROXY':'http://127.0.0.1:8080','HTTPS_PROXY':'http://127.0.0.1:8080','http_proxy':'http://127.0.0.1:8080','https_proxy':'http://127.0.0.1:8080','NO_PROXY':'','no_proxy':''}
def capture(pipe,path):
 h=hashlib.sha256();total=0;kept=0
 with open(path,'wb') as f:
  while True:
   b=pipe.read(8192)
   if not b:break
   h.update(b);total+=len(b);part=b[:max(0,65536-kept)];f.write(part);kept+=len(part)
 pipe.close();return {'total_bytes':total,'retained_bytes':kept,'sha256_full_stream':h.hexdigest()}

def terminal(p):
 try:p.wait(timeout=30)
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=2)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2)
 return p.poll() is not None
if __name__=='__main__':
 result={'native_starts':0,'errors':[]};proxy=None;p=None
 try:
  pathlib.Path(SAFE['HOME']).mkdir(mode=0o700)
  plan=json.loads(pathlib.Path('/probe/plan.json').read_text())
  loader=pathlib.Path(shutil.which('copilot')).resolve()
  binary=loader.parent/'node_modules/@github/copilot-linux-x64/copilot'
  actual={'loader_sha256':hashlib.sha256(loader.read_bytes()).hexdigest(),'native_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
  result['runtime_hashes']=actual
  if actual!=plan['runtime_hashes']:raise RuntimeError('native loader/ELF mismatch')
  v=subprocess.run(['copilot','--no-auto-update','--version'],env=SAFE,capture_output=True,text=True,timeout=5)
  (OUT/'private-version.stdout').write_text(v.stdout[:65536]);(OUT/'private-version.stderr').write_text(v.stderr[:65536]);result['version_returncode']=v.returncode
  if v.returncode or 'GitHub Copilot CLI 1.0.91.' not in v.stdout:raise RuntimeError('native version mismatch')
  result['version']='1.0.91';result['env_keys']=sorted(SAFE)
  proxy=OwnedServer(('127.0.0.1',8080),TunnelProxy);thread=threading.Thread(target=proxy.serve_forever,daemon=True);thread.start()
  p=subprocess.Popen(['copilot','--no-auto-update','--no-custom-instructions','--no-ask-user','--disable-builtin-mcps','-p','Reply OK. Do not use tools.','--allow-all-tools','--output-format','json','--usage-output-file','/output/private-usage.json'],env=SAFE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  result['native_starts']=1;result['native_pid']=p.pid;result['streams']={}
  def reader(name,pipe):result['streams'][name]=capture(pipe,OUT/('private-native.'+name))
  readers=[threading.Thread(target=reader,args=(n,s),daemon=True) for n,s in [('stdout',p.stdout),('stderr',p.stderr)]]
  for t in readers:t.start()
  result['native_process_terminal']=terminal(p);result['native_exit_code']=p.returncode
  for t in readers:t.join(timeout=1)
  result['native_readers_terminal']=all(not t.is_alive() for t in readers)
 except Exception as e:result['errors'].append(type(e).__name__+': '+str(e))
 finally:
  if p is not None and p.poll() is None:result['native_process_terminal']=terminal(p)
  if proxy is not None:
   try:proxy.cleanup();result['proxy_workers_remaining']=proxy.workers
   except Exception as e:result['errors'].append('proxy cleanup: '+str(e))
  result['proxy_counts']=TunnelProxy.stats.copy()
  result['usage_present']=(OUT/'private-usage.json').exists()
  (OUT/'worker-result.json').write_text(json.dumps(result,indent=2)+'\n')
