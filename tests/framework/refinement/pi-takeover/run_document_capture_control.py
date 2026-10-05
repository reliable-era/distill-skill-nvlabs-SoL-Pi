"""One prospective directory-state control using the established fresh-image runner."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;PRIVATE=pathlib.Path('/tmp/solpi-document-capture-launch-v2')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False);template=R/'run_file_capture_control.py';code=template.read_text().replace("'-v1'","'-v2'").replace("'file-capture-'","'document-capture-v2-'")
 code='import sys\nsys.path.insert(0,'+repr(str(R))+')\nfrom directory_capture import capture_directory\nfrom collections import Counter\n'+code
 code=code.replace('R=pathlib.Path(__file__).resolve().parent','R=pathlib.Path('+repr(str(R))+')')
 code=code.replace("OUTPUTS={'regex-log'","OUTPUTS={'financial-document-processor':'/app/documents','regex-log'")
 code=code.replace(" contract=json.loads((R/'selected-artifact-contracts.json').read_text())['task_contracts'][task]"," contract={'max_file_bytes':536870912}")
 code=code.replace("'scope':'Negative original-image control","'directory_module_sha256':sha(R/'directory_capture.py'),'worker_sha256':sha(pathlib.Path(__file__)),'max_directory_entries':10000,'scope':'Directory-state original-image control")
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
   subprocess.run(['docker','exec',name,'sh','-c','rm -rf /app/documents /app/invoices /app/other'],capture_output=True,check=True,timeout=15)
   for folder in ['documents','invoices','other']:
    subprocess.run(['docker','cp',str(artifact/folder),name+':/app/'],capture_output=True,check=True,timeout=60)
"""
 assert code.count(needle)==1;code=code.replace(needle,replacement)
 needle="  oracle=create('oracle',['-v',str(source/'solution')+':/solution:ro'])"
 assert code.count(needle)==1;code=code.replace(needle,needle+"\n  out['original_documents']=capture_dir(oracle,'/app/documents','before')")
 start=code.index("  artifact=root/'captured-output'");end=code.index("  out['replay']=grade('replay',artifact)",start)
 code=code[:start]+'''  artifact=root/'after';out['directory_capture']={}
  for folder in ['documents','invoices','other']:
   out['directory_capture'][folder]=capture_dir(oracle,'/app/'+folder,'after')
  def identities(files):return Counter((pathlib.PurePosixPath(k).name,v['bytes'],v['sha256']) for k,v in files.items())
  original=identities(out['original_documents']['files']);moved=Counter()
  for folder in ['invoices','other']:
   files={k:v for k,v in out['directory_capture'][folder]['files'].items() if not(folder=='invoices' and k=='summary.csv')};moved.update(identities(files))
  out['move_state_check']={'documents_empty':not out['directory_capture']['documents']['files'],'original_file_identities_preserved_exactly':all(moved[k]==v for k,v in original.items()),'additional_output_files':sum((moved-original).values()),'original_files':sum(original.values()),'moved_files':sum(moved.values())}
'''+code[end:]
 code=code.replace("  out['valid_output_replay']=out['baseline']['reward']=='0'","  out['valid_output_replay']=out['move_state_check']['documents_empty'] and out['move_state_check']['original_file_identities_preserved_exactly'] and out['baseline']['reward']=='0'")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'financial-document-processor','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'max_directory_bytes':536870912,'max_directory_entries':10000,'maximum_worker_seconds':3000,'model_POSTs':0,'actor_runs':0,'retry':0,'scope':'Capture/replay exact document move-state plus public-contract identity witness;not scored skill inference'}
 (R/'document-capture-v2-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as log:p=subprocess.run([sys.executable,str(worker),'--task','financial-document-processor'],stdout=log,stderr=subprocess.STDOUT,timeout=3000)
 print(json.dumps({'worker_exit':p.returncode,'log':str(PRIVATE/'worker.log'),'model_POSTs':0}))
if __name__=='__main__':main()
