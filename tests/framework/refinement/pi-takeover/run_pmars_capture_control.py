"""Installed executable plus Debian source-directory replay;no actor/model calls."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;PRIVATE=pathlib.Path('/tmp/solpi-pmars-capture-launch-v1')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False);template=R/'run_file_capture_control.py';code=template.read_text()
 archive=pathlib.Path('/tmp/solpi-pmars-archive-probe-v1/snapshot-debian.sources');assert archive.exists()
 code='import sys\nsys.path.insert(0,'+repr(str(R))+')\nfrom executable_capture import capture_executable\nfrom directory_capture import capture_directory\n'+code
 code=code.replace('R=pathlib.Path(__file__).resolve().parent','R=pathlib.Path('+repr(str(R))+')')
 code=code.replace("OUTPUTS={'regex-log'","OUTPUTS={'build-pmars':'/usr/local/bin/pmars','regex-log'")
 code=code.replace(" contract=json.loads((R/'selected-artifact-contracts.json').read_text())['task_contracts'][task]"," contract={'max_file_bytes':33554432}")
 code=code.replace("'scope':'Negative original-image control","'executable_module_sha256':sha(R/'executable_capture.py'),'directory_module_sha256':sha(R/'directory_capture.py'),'worker_sha256':sha(pathlib.Path(__file__)),'scope':'Executable/source-state original-image control")
 code=code.replace("'no-new-privileges',*mounts","'no-new-privileges','-v','/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro',*mounts")
 needle="  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15);return name"
 assert code.count(needle)==1
 code=code.replace(needle,"  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15)\n  subprocess.run(['docker','cp',"+repr(str(archive))+",name+':/etc/apt/sources.list.d/debian.sources'],capture_output=True,check=True,timeout=15)\n  with (root/(role+'-archive-metadata.log')).open('wb') as f:\n   refresh=subprocess.run(['docker','exec',name,'apt-get','-o','Acquire::Retries=0','update'],stdout=f,stderr=subprocess.STDOUT,timeout=120)\n  if refresh.returncode:raise RuntimeError('archive metadata refresh failed')\n  return name")
 needle="  if artifact:subprocess.run(['docker','cp',str(artifact),name+':'+OUTPUTS[task]],capture_output=True,check=True,timeout=60)"
 assert code.count(needle)==1
 code=code.replace(needle,needle+"\n  if artifact:subprocess.run(['docker','cp',str(root/'source-capture'/out['source_directory_name']),name+':/app/'],capture_output=True,check=True,timeout=60)")
 code=code.replace("out['capture']=capture_file(p.stdout,artifact","out['capture']=capture_executable(p.stdout,artifact")
 needle="  out['replay']=grade('replay',artifact)"
 assert code.count(needle)==1
 replacement='''  diff=subprocess.run(['docker','diff',oracle],capture_output=True,text=True,check=True,timeout=15).stdout
  directories=sorted(set(line.split(' ',1)[1] for line in diff.splitlines() if line.startswith('A /app/pmars-') and line.split(' ',1)[1].count('/')==2))
  if len(directories)!=1:raise RuntimeError('ambiguous or missing Debian source directory')
  path=directories[0];out['source_directory_name']=pathlib.PurePosixPath(path).name
  directory=root/'source-capture'/out['source_directory_name'];directory.parent.mkdir(mode=0o700)
  with (root/'source-capture-stderr.log').open('wb') as errors:
   p=subprocess.Popen(['docker','cp',oracle+':'+path,'-'],stdout=subprocess.PIPE,stderr=errors);timer=threading.Timer(60,p.kill);timer.start()
   try:
    out['source_capture']=capture_directory(p.stdout,directory,out['source_directory_name'],536870912,10000);p.stdout.close()
    if p.wait(timeout=5)!=0:raise RuntimeError('source-directory capture failed')
   finally:
    timer.cancel()
    if p.poll() is None:p.kill();p.wait(timeout=5)
    p.stdout.close()
'''
 code=code.replace(needle,replacement+needle)
 code=code.replace("  out['valid_output_replay']=out['baseline']['reward']=='0'","  out['valid_output_replay']=out['capture']['source_executable'] and out['source_capture']['capture_complete'] and out['baseline']['reward']=='0'")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'build-pmars','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'archive_sources_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'maximum_worker_seconds':3000,'retry':0,'model_POSTs':0,'actor_runs':0,'scope':'Original-image executable/source replay;no dependency assumptions or skill scoring'}
 (R/'pmars-capture-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as f:p=subprocess.run([sys.executable,str(worker),'--task','build-pmars'],stdout=f,stderr=subprocess.STDOUT,timeout=3000)
 print(json.dumps({'worker_exit':p.returncode,'model_POSTs':0,'log':str(PRIVATE/'worker.log')}))
if __name__=='__main__':main()
