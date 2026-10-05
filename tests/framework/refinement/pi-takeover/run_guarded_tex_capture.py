"""Freeze and run one guarded TeX roundtrip;preserve earlier file-control workers."""
import hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent
PRIVATE=pathlib.Path('/tmp/solpi-guarded-tex-launch-v1')
def main():
 PRIVATE.mkdir(mode=0o700,exist_ok=False)
 template=R/'run_file_capture_control.py';code=template.read_text()
 code='import sys\nsys.path.insert(0,'+repr(str(R))+')\nfrom protected_inputs import check_protected_inputs\n'+code
 code=code.replace("R=pathlib.Path(__file__).resolve().parent","R=pathlib.Path("+repr(str(R))+")")
 code=code.replace("OUTPUTS={'regex-log'","OUTPUTS={'overfull-hbox':'/app/input.tex','regex-log'")
 code=code.replace("'scope':'Negative original-image control", "'protected_inputs':['/app/main.tex','/app/synonyms.txt'],'guard_module_sha256':sha(R/'protected_inputs.py'),'worker_sha256':sha(pathlib.Path(__file__)),'scope':'Guarded TeX original-image control")
 helper=''' def capture_guard(name,label):
  records={}
  for path in plan['protected_inputs']:
   artifact=root/(label+'-'+pathlib.PurePosixPath(path).name)
   with (root/(label+'-'+pathlib.PurePosixPath(path).name+'-stderr.log')).open('wb') as errors:
    p=subprocess.Popen(['docker','cp',name+':'+path,'-'],stdout=subprocess.PIPE,stderr=errors);timer=threading.Timer(60,p.kill);timer.start()
    try:
     records[path]=capture_file(p.stdout,artifact,pathlib.PurePosixPath(path).name,33554432);p.stdout.close()
     if p.wait(timeout=5)!=0:raise RuntimeError('guard capture failed')
    finally:
     timer.cancel()
     if p.poll() is None:p.kill();p.wait(timeout=5)
     p.stdout.close()
  return records
'''
 assert code.count(' def grade(role,artifact=None):')==1;code=code.replace(' def grade(role,artifact=None):',helper+' def grade(role,artifact=None):')
 needle="  oracle=create('oracle',['-v',str(source/'solution')+':/solution:ro'])"
 assert code.count(needle)==1;code=code.replace(needle,needle+"\n  out['protected_before']=capture_guard(oracle,'before')")
 needle="  artifact=root/'captured-output'"
 insertion="""  out['protected_after']=capture_guard(oracle,'after')
  out['protected_check']=check_protected_inputs(out['protected_before'],out['protected_after'],plan['protected_inputs'])
  tampered={k:dict(v) for k,v in out['protected_after'].items()}
  tamper_file=root/'synthetic-tampered-main.tex';tamper_file.write_bytes((root/'after-main.tex').read_bytes()+b'\\n% forbidden edit\\n')
  tampered['/app/main.tex']={'capture_complete':True,'bytes':tamper_file.stat().st_size,'sha256':sha(tamper_file)}
  out['synthetic_tamper_check']=check_protected_inputs(out['protected_before'],tampered,plan['protected_inputs'])
"""
 assert code.count(needle)==1;code=code.replace(needle,insertion+needle)
 needle="  out['valid_output_replay']=out['baseline']['reward']=='0'"
 assert code.count(needle)==1;code=code.replace(needle,"  out['valid_output_replay']=out['protected_check']['unchanged'] and not out['synthetic_tamper_check']['unchanged'] and out['baseline']['reward']=='0'")
 worker=PRIVATE/'worker.py';worker.write_text(code);compile(code,str(worker),'exec')
 plan={'task':'overfull-hbox','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(worker.read_bytes()).hexdigest(),'original_input_paths':['/app/main.tex','/app/synonyms.txt'],'maximum_worker_seconds':2700,'retry':0,'model_POSTs':0,'candidate_changes':False,'scope':'Guarded original-image replay only;synthetic tamper is not an actor or scoring attempt'}
 (R/'guarded-tex-execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (PRIVATE/'worker.log').open('wb') as log:p=subprocess.run([sys.executable,str(worker),'--task','overfull-hbox'],stdout=log,stderr=subprocess.STDOUT,timeout=2700)
 print(json.dumps({'worker_exit':p.returncode,'model_POSTs':0,'log':str(PRIVATE/'worker.log')}))
if __name__=='__main__':main()
