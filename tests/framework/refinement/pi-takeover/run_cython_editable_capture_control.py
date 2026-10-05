"""Versioned editable-install capture;retain failedv1 and reuse its dependencylock."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;PRIVATE=pathlib.Path('/tmp/solpi-cython-capture-launch-v2')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False);template=pathlib.Path('/tmp/solpi-cython-capture-launch-v1/worker.py');code=template.read_text()
 code=code.replace("'-v1'","'-v2'").replace("'file-capture-'","'cython-capture-v2-'")
 oldlock=pathlib.Path('/tmp/solpi-file-capture-build-cython-ext-v1/trusted-dependencies-lock.txt');assert oldlock.exists()
 needle="root.mkdir(mode=0o700,exist_ok=False)"
 assert code.count(needle)==1;code=code.replace(needle,needle+";shutil.copyfile("+repr(str(oldlock))+",root/'trusted-dependencies-lock.txt')")
 needle="   program=\"import json,numpy,pyknotid;"
 insertion="""   for path in out['capture_files']:
    subprocess.run(['docker','cp',str(root/'sidecars'/pathlib.PurePosixPath(path).name),name+':'+path],capture_output=True,check=True,timeout=60)
"""
 assert code.count(needle)==1;code=code.replace(needle,insertion+needle)
 code=code.replace("import json,numpy,pyknotid;from pyknotid", "import json,numpy,pyknotid,importlib.metadata as metadata;from pyknotid")
 code=code.replace("{'numpy':numpy.__version__,'package':pyknotid.__file__", "{'numpy':numpy.__version__,'installed_version':metadata.version('pyknotid'),'package':pyknotid.__file__")
 site='/usr/local/lib/python3.13/site-packages'
 needle="  out['capture_paths']=['/app/pyknotid','/usr/local/lib/python3.13/site-packages'+'/pyknotid',distributions[0]]"
 replacement="""  (root/'docker-diff.log').write_text(diff)
  top=set(line.split(' ',1)[1] for line in diff.splitlines() if line.startswith(('A ','C ')) and line.split(' ',1)[1].startswith(SITE+'/') and line.split(' ',1)[1].count('/')==SITE.count('/')+1)
  sidecars=sorted(path for path in top if pathlib.PurePosixPath(path).name.startswith('__editable__') and 'pyknotid' in pathlib.PurePosixPath(path).name and (path.endswith('.pth') or path.endswith('_finder.py')))
  normal_package=SITE+'/pyknotid' in top
  if not normal_package and not(any(p.endswith('.pth') for p in sidecars) and any(p.endswith('_finder.py') for p in sidecars)):raise RuntimeError('unsupported installation layout')
  out['installation_layout']='normal' if normal_package else 'editable'
  out['capture_paths']=['/app/pyknotid',distributions[0]]+([SITE+'/pyknotid'] if normal_package else [])
  out['capture_files']=sidecars
  (root/'sidecars').mkdir(mode=0o700);out['sidecar_capture']={}
  for path in sidecars:
   with (root/(pathlib.PurePosixPath(path).name+'-stderr.log')).open('wb') as errors:
    p=subprocess.Popen(['docker','cp',oracle+':'+path,'-'],stdout=subprocess.PIPE,stderr=errors);timer=threading.Timer(60,p.kill);timer.start()
    try:
     out['sidecar_capture'][path]=capture_file(p.stdout,root/'sidecars'/pathlib.PurePosixPath(path).name,pathlib.PurePosixPath(path).name,1048576);p.stdout.close()
     if p.wait(timeout=5)!=0:raise RuntimeError('editable sidecar capture failed')
    finally:
     timer.cancel()
     if p.poll() is None:p.kill();p.wait(timeout=5)
     p.stdout.close()
""".replace('SITE',repr(site))
 assert code.count(needle)==1;code=code.replace(needle,replacement)
 code=code.replace(".startswith('/usr/local/lib/python3.13/site-packages/pyknotid/')", ".startswith(('/usr/local/lib/python3.13/site-packages/pyknotid/','/app/pyknotid/pyknotid/'))")
 code=code.replace("  out['valid_output_replay']=out['global_import_witness']['numpy']", "  out['trusted_dependency_lock_sha256']=sha(root/'trusted-dependencies-lock.txt')\n  out['valid_output_replay']=out['global_import_witness']['installed_version']=='0.5.3' and out['global_import_witness']['numpy']")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'build-cython-ext','v1_worker_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'reused_dependency_lock_sha256':hashlib.sha256(oldlock.read_bytes()).hexdigest(),'retry':0,'maximum_worker_seconds':4800,'model_POSTs':0,'actor_runs':0,'scope':'Newprotocol for demonstrated editablelayout;v1failure retained;globalimportoutsidecwd;no rebuild or PYTHONPATH fallback'}
 (R/'cython-capture-v2-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as f:p=subprocess.run([sys.executable,str(worker),'--task','build-cython-ext'],stdout=f,stderr=subprocess.STDOUT,timeout=4800)
 print(json.dumps({'worker_exit':p.returncode,'model_POSTs':0,'log':str(PRIVATE/'worker.log')}))
if __name__=='__main__':main()
