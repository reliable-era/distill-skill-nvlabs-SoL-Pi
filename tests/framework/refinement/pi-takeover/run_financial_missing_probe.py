"""New absent-directory negative capture/grader gate,not goldcontrolrepeat."""
import hashlib,json,pathlib,subprocess,uuid
from financial_output import capture_stopped,replay,verify
from financial_grader_setup import prepare,grade_argv
from actor_public_inputs import recipe,docker_options,verify_actor_inspect
R=pathlib.Path(__file__).resolve().parent;SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def docker(*args):return subprocess.run(['docker',*args],capture_output=True,text=True,check=True,timeout=60)
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-financial-missing-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);spec=recipe(SOURCE.name);actor=root.name+'-actor';grader=root.name+'-grader';owned=[];logs=root/'logs';(logs/'verifier').mkdir(parents=True);report={'private_root':str(root),'native_starts':0,'provider_POST':0,'grader_calls':0,'helper_attempts':1,'test_script_sha256':sha(SOURCE/'tests/test.sh'),'tests_sha256':sha(SOURCE/'tests/test_outputs.py'),'scope':'new all-absent directory-state capture/replay negative;not repeat of originalbaseline/gold controls or completedpositive transfers'}
 try:
  docker('create','--name',actor,'--network','none','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges',*docker_options(spec),'--entrypoint','/bin/sh',spec['actor_image_id'],'-c','sleep infinity');owned.append(actor);report['actor_isolation']=verify_actor_inspect(json.loads(docker('inspect',actor).stdout)[0],spec,'none',{});docker('start',actor);docker('exec',actor,'rm','-rf','--','/app/documents','/app/invoices','/app/other');docker('stop','-t','0',actor);report['capture']=capture_stopped(actor,spec['actor_image_id'],root/'captured');docker('rm',actor);owned.remove(actor)
  docker('create','--name',grader,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SOURCE/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw','-v','/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro','--entrypoint','/bin/sh',spec['grader_image_id'],'-c','sleep infinity');owned.append(grader);report['replay']=replay(root/'captured',grader,spec['grader_image_id']);report['setup']=prepare(grader,spec['grader_image_id'],root);report['grader_calls']=1
  with (root/'verifier.log').open('wb') as out:p=subprocess.run(grade_argv(grader),stdout=out,stderr=subprocess.STDOUT,timeout=600)
  tests=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];reward=(logs/'verifier/reward.txt').read_text().strip();report.update(verifier_exit=p.returncode,reward=reward,test_results=[{'name':t['name'],'status':t['status']} for t in tests]);assert len(tests)==7 and all(t['status']=='failed' for t in tests) and reward=='0';assert len(report['replay']['absent_paths_preserved'])==3
  for path in ['/app/documents','/app/invoices','/app/other']:docker('exec',grader,'test','!','-e',path)
  assert sha(SOURCE/'tests/test.sh')==report['test_script_sha256'];report['all_missing_paths_preserved']=True;report['passed']=True
 except Exception as e:report['passed']=False;report['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  report['cleanup_verified']=all(subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in [actor,grader]);report['evidence_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};report['module_hashes']={n:sha(R/n) for n in ['financial_output.py','financial_grader_setup.py','run_financial_missing_probe.py']};(R/'financial-missing-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
