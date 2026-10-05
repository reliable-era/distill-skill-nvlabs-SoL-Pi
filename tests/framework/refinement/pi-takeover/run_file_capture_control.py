"""Prospective stopped-oracle artifact replay into fresh trusted images;0modelcalls."""
import argparse,datetime,json,pathlib,shutil,subprocess,threading,time,uuid
from artifact_capture import capture_file
from run_first_terminal_controls import sha,tree
R=pathlib.Path(__file__).resolve().parent
OUTPUTS={'regex-log':'/app/regex.txt','sparql-university':'/app/solution.sparql','train-fasttext':'/app/model.bin'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',choices=OUTPUTS,required=True);a=parser.parse_args();task=a.task
 root=pathlib.Path('/tmp/solpi-file-capture-'+task+'-v1');root.mkdir(mode=0o700,exist_ok=False)
 source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2')/task
 spec=next(t for t in json.loads((R/'terminal-readiness-inventory.json').read_text())['tasks'] if t['id']==task)
 image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']==task)
 contract=json.loads((R/'selected-artifact-contracts.json').read_text())['task_contracts'][task]
 candidate=R.parent/'development/pi-takeover-qwen-incremental-coverage/frozen/candidate/SKILL.md'
 plan={'task':task,'image_id':image,'source_hashes':tree(source),'candidate_sha256':sha(candidate),'capture_module_sha256':sha(R/'artifact_capture.py'),'contract_sha256':sha(R/'selected-artifact-contracts.json'),'oracle_seconds':300,'verifier_seconds':600,'capture_seconds':60,'max_file_bytes':contract['max_file_bytes'],'retry':0,'model_POSTs':0,'actor_runs':0,'scope':'Negative original-image control plus stopped-oracle output-only replay;not skill scoring'}
 (root/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');(R/('file-capture-'+task+'-plan.json')).write_text(json.dumps(plan,indent=2)+'\n')
 owned=[];out={'task':task,'model_POSTs':0,'actor_runs':0,'plan_sha256':sha(root/'plan.json')}
 def create(role,mounts):
  name='solpi-capture-control-'+uuid.uuid4().hex[:12]
  subprocess.run(['docker','create','--name',name,'--pull=never','--cpus',str(spec['declared_cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges',*mounts,'--entrypoint','sh',image,'-c','sleep infinity'],capture_output=True,check=True,timeout=15);owned.append(name)
  subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15);return name
 def grade(role,artifact=None):
  d=root/role;d.mkdir();logs=d/'logs';(logs/'verifier').mkdir(parents=True)
  tests=source/'tests'
  if task=='train-fasttext':tests=d/'tests-copy';shutil.copytree(source/'tests',tests)
  name=create(role,['-v',str(tests)+':/tests'+('' if task=='train-fasttext' else ':ro'),'-v',str(logs)+':/logs'])
  if artifact:subprocess.run(['docker','cp',str(artifact),name+':'+OUTPUTS[task]],capture_output=True,check=True,timeout=60)
  with (d/'verifier.log').open('wb') as f:p=subprocess.run(['docker','exec',name,'bash','/tests/test.sh'],stdout=f,stderr=subprocess.STDOUT,timeout=600)
  events=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests']
  return {'verifier_exit':p.returncode,'reward':(logs/'verifier/reward.txt').read_text().strip(),'tests':[{k:e.get(k) for k in ('name','status')} for e in events]}
 try:
  out['baseline']=grade('baseline')
  oracle=create('oracle',['-v',str(source/'solution')+':/solution:ro'])
  with (root/'oracle.log').open('wb') as f:p=subprocess.run(['docker','exec',oracle,'bash','/solution/solve.sh'],stdout=f,stderr=subprocess.STDOUT,timeout=300)
  out['oracle_exit']=p.returncode
  if p.returncode:raise RuntimeError('oracle failed;no retry')
  subprocess.run(['docker','stop','-t','1',oracle],capture_output=True,check=True,timeout=15)
  artifact=root/'captured-output'
  with (root/'capture-stderr.log').open('wb') as errors:
   p=subprocess.Popen(['docker','cp',oracle+':'+OUTPUTS[task],'-'],stdout=subprocess.PIPE,stderr=errors);timer=threading.Timer(60,p.kill);timer.start()
   try:
    out['capture']=capture_file(p.stdout,artifact,pathlib.PurePosixPath(OUTPUTS[task]).name,contract['max_file_bytes']);p.stdout.close()
    if p.wait(timeout=5)!=0:raise RuntimeError('Docker capture failed')
   finally:
    timer.cancel()
    if p.poll() is None:p.kill();p.wait(timeout=5)
    p.stdout.close()
  out['replay']=grade('replay',artifact)
  out['same_test_collection']=sorted(e['name'] for e in out['baseline']['tests'])==sorted(e['name'] for e in out['replay']['tests'])
  out['valid_output_replay']=out['baseline']['reward']=='0' and out['replay']['reward']=='1' and out['same_test_collection'] and bool(out['replay']['tests'])
 except Exception as e:out.update(error_type=type(e).__name__,error=str(e),valid_output_replay=False)
 finally:
  cleanup=[]
  for name in owned:
   subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);cleanup.append(p.returncode!=0 and 'No such' in p.stderr)
  out['cleanup_verified']=all(cleanup);out['source_unchanged']=tree(source)==plan['source_hashes'];out['candidate_unchanged']=sha(candidate)==plan['candidate_sha256'];out['artifact_hashes']=tree(root)
  (R/('file-capture-'+task+'-result.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
