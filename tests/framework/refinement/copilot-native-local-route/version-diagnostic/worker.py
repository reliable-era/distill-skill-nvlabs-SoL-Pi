import os,pathlib,subprocess,json,hashlib,shutil,resource
out=pathlib.Path('/output');env={'PATH':os.environ['PATH'],'HOME':'/tmp/fresh-home','XDG_CONFIG_HOME':'/tmp/fresh-home/config','XDG_CACHE_HOME':'/tmp/fresh-home/cache','COPILOT_OFFLINE':'true','COPILOT_PROVIDER_BASE_URL':'http://provider.example:8000/v1','COPILOT_PROVIDER_TYPE':'openai','COPILOT_PROVIDER_WIRE_API':'completions','COPILOT_MODEL':'mock-routing-only'}
pathlib.Path(env['HOME']).mkdir(mode=0o700)
loader=pathlib.Path(shutil.which('copilot')).resolve();binary=loader.parent/'node_modules/@github/copilot-linux-x64/copilot'
r={'runtime_hashes':{'loader_sha256':hashlib.sha256(loader.read_bytes()).hexdigest(),'native_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()},'prompt_starts':0}
resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
with open(out/'private-version.stdout','wb') as stdout,open(out/'private-version.stderr','wb') as stderr:
 p=subprocess.Popen(['copilot','--no-auto-update','--version'],env=env,stdout=stdout,stderr=stderr,start_new_session=True)
 try:p.wait(timeout=5);r['timeout']=False
 except subprocess.TimeoutExpired:
  import signal
  os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2);r['timeout']=True
 r['returncode']=p.returncode
(out/'version-result.json').write_text(json.dumps(r,indent=2)+'\n')
