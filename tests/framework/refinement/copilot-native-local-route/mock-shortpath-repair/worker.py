"""Single native CLI attempt against an owned fake provider; no inference."""
import hashlib,json,os,pathlib,signal,subprocess,threading,time,resource,shutil
from tunnel_proxy import TunnelProxy
from server import OwnedServer
OUT=pathlib.Path('/output')
SAFE={'PATH':os.environ['PATH'],'HOME':'/tmp/fresh-home','XDG_CONFIG_HOME':'/tmp/fresh-home/config','XDG_CACHE_HOME':'/tmp/fresh-home/cache','COPILOT_OFFLINE':'true','COPILOT_PROVIDER_BASE_URL':'http://provider.example:8000/v1','COPILOT_PROVIDER_TYPE':'openai','COPILOT_PROVIDER_WIRE_API':'completions','COPILOT_MODEL':'mock-routing-only','HTTP_PROXY':'http://127.0.0.1:8080','HTTPS_PROXY':'http://127.0.0.1:8080','http_proxy':'http://127.0.0.1:8080','https_proxy':'http://127.0.0.1:8080','NO_PROXY':'','no_proxy':''}
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
  if v.returncode or 'GitHub Copilot CLI 1.0.91.' not in v.stdout:raise RuntimeError('native version mismatch')
  result['version']='1.0.91';result['env_keys']=sorted(SAFE)
  proxy=OwnedServer(('127.0.0.1',8080),TunnelProxy);thread=threading.Thread(target=proxy.serve_forever,daemon=True);thread.start()
  with open(OUT/'private-native.log','wb') as log:
   resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
   p=subprocess.Popen(['copilot','--no-auto-update','--no-custom-instructions','--no-ask-user','--disable-builtin-mcps','-p','Reply OK. Do not use tools.','--allow-all-tools','--output-format','json','--usage-output-file','/output/private-usage.json'],env=SAFE,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   result['native_starts']=1;result['native_pid']=p.pid
   result['native_process_terminal']=terminal(p);result['native_exit_code']=p.returncode
 except Exception as e:result['errors'].append(type(e).__name__+': '+str(e))
 finally:
  if p is not None and p.poll() is None:result['native_process_terminal']=terminal(p)
  if proxy is not None:
   try:proxy.cleanup();result['proxy_workers_remaining']=proxy.workers
   except Exception as e:result['errors'].append('proxy cleanup: '+str(e))
  result['proxy_counts']=TunnelProxy.stats.copy()
  result['usage_present']=(OUT/'private-usage.json').exists()
  (OUT/'worker-result.json').write_text(json.dumps(result,indent=2)+'\n')
