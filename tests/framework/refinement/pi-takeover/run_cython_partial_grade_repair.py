"""Reuse identical failed-probe capture;repair only trusted test-runner cache."""
import hashlib,json,pathlib,subprocess,uuid
from cython_partial_output import replay_partial,verify_partial
from cython_grader_inputs import inputs,docker_options,prepare
R=pathlib.Path(__file__).resolve().parent;TASK=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-cython-ext')
def docker(*args):return subprocess.run(['docker',*args],capture_output=True,check=True,timeout=60)
if __name__=='__main__':
 old=json.loads((R/'cython-partial-probe-v1-setup-failure.json').read_text());original=pathlib.Path(old['private_root']);capture=original/'captured';assert not old['passed'];spec=inputs();verify_partial(capture,spec['image_id']);root=pathlib.Path('/tmp/solpi-cython-partial-repair-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);logs=root/'logs';logs.mkdir();(logs/'verifier').mkdir();name=root.name+'-grader';result={'private_root':str(root),'reused_capture':str(capture),'reused_capture_manifest_sha256':hashlib.sha256((capture/'capture.json').read_bytes()).hexdigest(),'native_starts':0,'provider_POST':0,'actor_reruns':0,'trusted_grader_calls':0,'prior_attempt':'cython-partial-probe-v1-setup-failure.json','scope':'trusted-only runner cache repair;prior reward0 was setupfailure/noCTRF,not taskquality'}
 try:
  docker('create','--name',name,'--network','none','--cpus','1','--memory','2048m','--pids-limit','128','-v',str(TASK/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw',*docker_options(spec),'--entrypoint','/bin/sh',spec['image_id'],'-c','sleep infinity')
  result['replay']=replay_partial(capture,name,spec['image_id']);result['dependency_setup']=prepare(name,spec['image_id'],installation_absent=True);expected=(capture/'payload-0/README.synthetic').read_bytes();assert docker('exec',name,'cat','/app/pyknotid/README.synthetic').stdout==expected
  result['trusted_grader_calls']=1
  with (root/'verifier.log').open('wb') as out:p=subprocess.run(['docker','exec',name,'bash','/tests/test.sh'],stdout=out,stderr=subprocess.STDOUT,timeout=600)
  tests=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];result['reward']=(logs/'verifier/reward.txt').read_text().strip();result['test_events']=len(tests);result['test_results']=[{'name':t['name'],'status':t['status']} for t in tests];assert result['reward']=='0' and len(tests)==11 and any(t['status']=='failed' for t in tests);assert docker('exec',name,'cat','/app/pyknotid/README.synthetic').stdout==expected;result['source_byte_identity_preserved']=True;result['passed']=True
 except Exception as e:result['passed']=False;result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);result['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;result['evidence_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()};result['module_hashes']={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['cython_partial_output.py','cython_grader_inputs.py','run_cython_partial_grade_repair.py']};(R/'cython-partial-grade-repair-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
