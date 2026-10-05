"""Source/global wheel replay;trusted dependencies only;never rebuild submitted code."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;PRIVATE=pathlib.Path('/tmp/solpi-cython-capture-launch-v1')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False);template=R/'run_file_capture_control.py';code=template.read_text()
 env=json.loads((R/'cython-global-environment-paths.json').read_text());site=env['purelib'];assert site==env['platlib'] and env['numpy']=='2.3.0'
 deps=json.loads((R/'cython-public-source-dependencies.json').read_text())['install_requires']+['scipy'];deps=[d if d!='numpy' else 'numpy==2.3.0' for d in deps]
 constraint=PRIVATE/'constraints.txt';constraint.write_text('numpy==2.3.0\nplanarity==0.6\n')
 code='import sys\nsys.path.insert(0,'+repr(str(R))+')\nfrom directory_capture import capture_directory\n'+code
 code=code.replace('R=pathlib.Path(__file__).resolve().parent','R=pathlib.Path('+repr(str(R))+')')
 code=code.replace("OUTPUTS={'regex-log'","OUTPUTS={'build-cython-ext':'/app/pyknotid','regex-log'")
 code=code.replace(" contract=json.loads((R/'selected-artifact-contracts.json').read_text())['task_contracts'][task]"," contract={'max_file_bytes':536870912}")
 code=code.replace("'scope':'Negative original-image control","'directory_module_sha256':sha(R/'directory_capture.py'),'worker_sha256':sha(pathlib.Path(__file__)),'scope':'Source/global installed package original-image control")
 needle="  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15);return name"
 preparation="""  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15)
  subprocess.run(['docker','cp',CONSTRAINT,name+':/opt/replay-constraints.txt'],capture_output=True,check=True,timeout=15)
  lock=root/'trusted-dependencies-lock.txt'
  if lock.exists():
   subprocess.run(['docker','cp',str(lock),name+':/opt/trusted-dependencies-lock.txt'],capture_output=True,check=True,timeout=15)
   requirements=['-r','/opt/trusted-dependencies-lock.txt']
  else:requirements=DEPENDENCIES
  with (root/(role+'-trusted-dependencies.log')).open('wb') as f:
   p=subprocess.run(['docker','exec',name,'pip','install','-c','/opt/replay-constraints.txt',*requirements],stdout=f,stderr=subprocess.STDOUT,timeout=300)
  if p.returncode:raise RuntimeError('trusted dependency installation failed')
  if not lock.exists():
   p=subprocess.run(['docker','exec',name,'pip','freeze','--all'],capture_output=True,text=True,check=True,timeout=15)
   import re
   lines=p.stdout.splitlines()
   if any(not re.fullmatch(r'[A-Za-z0-9_.-]+==[A-Za-z0-9_.+!-]+',line) or line.lower().startswith('pyknotid==') for line in lines):raise RuntimeError('untrusted dependency lock form')
   lock.write_text(p.stdout)
   out['trusted_dependency_lock_sha256']=sha(lock)
  return name""".replace('CONSTRAINT',repr(str(constraint))).replace('DEPENDENCIES',repr(deps))
 assert code.count(needle)==1;code=code.replace(needle,preparation)
 helper=''' def capture_dir(name,path,label):
  destination=root/label/pathlib.PurePosixPath(path).name;destination.parent.mkdir(mode=0o700,exist_ok=True)
  with (root/(label+'-'+pathlib.PurePosixPath(path).name+'-stderr.log')).open('wb') as errors:
   p=subprocess.Popen(['docker','cp',name+':'+path,'-'],stdout=subprocess.PIPE,stderr=errors);timer=threading.Timer(60,p.kill);timer.start()
   try:
    result=capture_directory(p.stdout,destination,pathlib.PurePosixPath(path).name,536870912,10000);p.stdout.close()
    if p.wait(timeout=5)!=0:raise RuntimeError('directory capture failed')
    return result
   finally:
    timer.cancel()
    if p.poll() is None:p.kill();p.wait(timeout=5)
    p.stdout.close()
'''
 code=code.replace(' def grade(role,artifact=None):',helper+' def grade(role,artifact=None):')
 needle="  if artifact:subprocess.run(['docker','cp',str(artifact),name+':'+OUTPUTS[task]],capture_output=True,check=True,timeout=60)"
 replacement="""  if artifact:
   for path in out['capture_paths']:
    parent=str(pathlib.PurePosixPath(path).parent)+'/'
    subprocess.run(['docker','cp',str(artifact/pathlib.PurePosixPath(path).name),name+':'+parent],capture_output=True,check=True,timeout=60)
   program="import json,numpy,pyknotid;from pyknotid.spacecurves import chelpers,ccomplexity;from pyknotid import cinvariants;print(json.dumps({'numpy':numpy.__version__,'package':pyknotid.__file__,'extensions':[m.__file__ for m in [chelpers,ccomplexity,cinvariants]]}))"
   p=subprocess.run(['docker','exec','-w','/tmp',name,'python','-I','-c',program],capture_output=True,text=True,check=True,timeout=30)
   out['global_import_witness']=json.loads(p.stdout.splitlines()[-1])
"""
 assert code.count(needle)==1;code=code.replace(needle,replacement)
 # Preserve the known NumPy2.3.0/planarity0.6 environment also during opaque oracle execution.
 code=code.replace("['docker','exec',name,'bash','/solution/solve.sh']","['docker','exec','-e','PIP_CONSTRAINT=/opt/replay-constraints.txt','-e','UV_CONSTRAINT=/opt/replay-constraints.txt',name,'bash','/solution/solve.sh']")
 # The original runner calls its oracle with variable oracle,not name.
 code=code.replace("['docker','exec',oracle,'bash','/solution/solve.sh']","['docker','exec','-e','PIP_CONSTRAINT=/opt/replay-constraints.txt','-e','UV_CONSTRAINT=/opt/replay-constraints.txt',oracle,'bash','/solution/solve.sh']")
 start=code.index("  artifact=root/'captured-output'");end=code.index("  out['replay']=grade('replay',artifact)",start)
 capture="""  diff=subprocess.run(['docker','diff',oracle],capture_output=True,text=True,check=True,timeout=15).stdout
  distributions=sorted(set(line.split(' ',1)[1] for line in diff.splitlines() if line.startswith('A '+SITE+'/pyknotid-') and line.endswith('.dist-info') and line.split(' ',1)[1].count('/')==SITE.count('/')+1))
  if len(distributions)!=1:raise RuntimeError('unsupported global-install layout;no silent source-only fallback')
  out['capture_paths']=['/app/pyknotid',SITE+'/pyknotid',distributions[0]]
  artifact=root/'after';out['directory_capture']={}
  for path in out['capture_paths']:
   label='source' if path=='/app/pyknotid' else 'global'
   out['directory_capture'][path]=capture_dir(oracle,path,label)
  # Build a private replay bundle without rebuilding or running captured setup scripts.
  artifact.mkdir(mode=0o700)
  for path in out['capture_paths']:
   label='source' if path=='/app/pyknotid' else 'global'
   # Source and global package share a basename;retain separate payload roots.
   if path=='/app/pyknotid':continue
   shutil.copytree(root/label/pathlib.PurePosixPath(path).name,artifact/pathlib.PurePosixPath(path).name)
""".replace('SITE',repr(site))
 # Copy source separately in grader to avoid aliasing /app/pyknotid with global/pyknotid.
 code=code.replace("str(artifact/pathlib.PurePosixPath(path).name)","str((root/'source/pyknotid') if path=='/app/pyknotid' else artifact/pathlib.PurePosixPath(path).name)")
 code=code[:code.index("  artifact=root/'captured-output'")]+capture+code[code.index("  out['replay']=grade('replay',artifact)",code.index("  artifact=root/'captured-output'")):]
 code=code.replace("  out['valid_output_replay']=out['baseline']['reward']=='0'","  out['valid_output_replay']=out['global_import_witness']['numpy']=='2.3.0' and out['global_import_witness']['package'].startswith("+repr(site+'/pyknotid/')+") and all(p.endswith('.so') and p.startswith("+repr(site+'/pyknotid/')+") for p in out['global_import_witness']['extensions']) and out['baseline']['reward']=='0'")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'build-cython-ext','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'constraints_sha256':hashlib.sha256(constraint.read_bytes()).hexdigest(),'trusted_dependencies':deps,'maximum_worker_seconds':4200,'retry':0,'model_POSTs':0,'actor_runs':0,'scope':'Captured source/global package and metadata;trusted dependency lock;no submitted-code rebuild or source-only import substitution'}
 (R/'cython-capture-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as f:p=subprocess.run([sys.executable,str(worker),'--task','build-cython-ext'],stdout=f,stderr=subprocess.STDOUT,timeout=4200)
 print(json.dumps({'worker_exit':p.returncode,'model_POSTs':0,'log':str(PRIVATE/'worker.log')}))
if __name__=='__main__':main()
