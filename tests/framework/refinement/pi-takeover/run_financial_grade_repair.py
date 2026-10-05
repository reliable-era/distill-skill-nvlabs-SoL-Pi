"""Same successfulmissingcapture,new trustedgrader;no helper/modelrerun."""
import hashlib,json,pathlib,subprocess,uuid
from financial_output import replay,verify
from financial_grader_setup import prepare,grade_argv
from actor_public_inputs import recipe
R=pathlib.Path(__file__).resolve().parent;SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def docker(*a):return subprocess.run(['docker',*a],capture_output=True,text=True,check=True,timeout=60)
if __name__=='__main__':
 old=json.loads((R/'financial-missing-v2-setup-failure.json').read_text());capture=pathlib.Path(old['private_root'])/'captured';spec=recipe(SOURCE.name);verify(capture,spec['actor_image_id']);root=pathlib.Path('/tmp/solpi-financial-grade-repair-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);logs=root/'logs';(logs/'verifier').mkdir(parents=True);name=root.name+'-grader';report={'private_root':str(root),'reused_capture':str(capture),'native_starts':0,'provider_POST':0,'helper_reruns':0,'grader_calls':0,'capture_manifest_sha256':sha(capture/'capture.json'),'test_script_sha256':sha(SOURCE/'tests/test.sh'),'tests_sha256':sha(SOURCE/'tests/test_outputs.py')}
 try:
  docker('create','--name',name,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SOURCE/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw','-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro','--entrypoint','/bin/sh',spec['grader_image_id'],'-c','sleep infinity');report['replay']=replay(capture,name,spec['grader_image_id']);report['setup']=prepare(name,spec['grader_image_id'],root);report['grader_calls']=1
  with (root/'verifier.log').open('wb') as out:p=subprocess.run(grade_argv(name),stdout=out,stderr=subprocess.STDOUT,timeout=600)
  tests=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];reward=(logs/'verifier/reward.txt').read_text().strip();report.update(verifier_exit=p.returncode,reward=reward,test_results=[{'name':t['name'],'status':t['status']} for t in tests]);assert len(tests)==7 and all(t['status']=='failed' for t in tests) and reward=='0'
  for path in ['/app/documents','/app/invoices','/app/other']:docker('exec',name,'test','!','-e',path)
  assert sha(SOURCE/'tests/test.sh')==report['test_script_sha256'] and sha(capture/'capture.json')==report['capture_manifest_sha256'];report['all_missing_paths_preserved']=True;report['passed']=True
 except Exception as e:report['passed']=False;report['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);report['cleanup_verified']=subprocess.run(['docker','inspect',name],capture_output=True,timeout=10).returncode!=0;report['evidence_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};report['module_hashes']={n:sha(R/n) for n in ['financial_output.py','financial_grader_setup.py','run_financial_grade_repair.py']};(R/'financial-missing-grade-repair.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
