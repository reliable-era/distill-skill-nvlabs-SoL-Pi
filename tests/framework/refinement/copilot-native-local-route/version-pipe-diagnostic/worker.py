import os,pathlib,subprocess,json,hashlib,shutil,threading,signal,time
out=pathlib.Path('/output');env={'PATH':os.environ['PATH'],'HOME':'/tmp/fresh-home','XDG_CONFIG_HOME':'/tmp/fresh-home/config','XDG_CACHE_HOME':'/tmp/fresh-home/cache','COPILOT_OFFLINE':'true','COPILOT_PROVIDER_BASE_URL':'http://provider.example:8000/v1','COPILOT_PROVIDER_TYPE':'openai','COPILOT_PROVIDER_WIRE_API':'completions','COPILOT_MODEL':'mock-routing-only'}
def capture(pipe,path):
 h=hashlib.sha256();total=0;kept=0
 with open(path,'wb') as f:
  while True:
   b=pipe.read(8192)
   if not b:break
   h.update(b);total+=len(b);part=b[:max(0,65536-kept)];f.write(part);kept+=len(part)
 pipe.close();return {'total_bytes':total,'retained_bytes':kept,'sha256_full_stream':h.hexdigest()}
if __name__=='__main__':
 pathlib.Path(env['HOME']).mkdir(mode=0o700)
 loader=pathlib.Path(shutil.which('copilot')).resolve();binary=loader.parent/'node_modules/@github/copilot-linux-x64/copilot'
 r={'runtime_hashes':{'loader_sha256':hashlib.sha256(loader.read_bytes()).hexdigest(),'native_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()},'prompt_starts':0,'streams':{}}
 p=subprocess.Popen(['copilot','--no-auto-update','--version'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 def reader(name,pipe):r['streams'][name]=capture(pipe,out/('private-version.'+name))
 threads=[threading.Thread(target=reader,args=(n,s),daemon=True) for n,s in [('stdout',p.stdout),('stderr',p.stderr)]]
 for t in threads:t.start()
 try:p.wait(timeout=5);r['timeout']=False
 except subprocess.TimeoutExpired:
  r['timeout']=True;os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=1)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2)
 r['returncode']=p.returncode;r['owned_process_terminal']=p.poll() is not None
 for t in threads:t.join(timeout=1)
 r['reader_threads_terminal']=all(not t.is_alive() for t in threads)
 (out/'version-result.json').write_text(json.dumps(r,indent=2)+'\n')
