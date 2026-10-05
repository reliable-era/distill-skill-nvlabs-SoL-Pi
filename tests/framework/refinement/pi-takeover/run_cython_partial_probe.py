"""New synthetic source-only -> original official grader gate;zero model calls."""
import hashlib,json,pathlib,subprocess,uuid
from actor_public_inputs import recipe,docker_options,verify_actor_inspect
from cython_partial_output import capture_partial,replay_partial
from cython_grader_inputs import inputs,docker_options as grader_options,prepare
R=pathlib.Path(__file__).resolve().parent
TASK=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-cython-ext')
def docker(*args,**kwargs):return subprocess.run(['docker',*args],capture_output=True,check=True,timeout=kwargs.pop('timeout',30),**kwargs)
def main():
 token=uuid.uuid4().hex[:10];root=pathlib.Path('/tmp/solpi-cython-partial-'+token);root.mkdir(mode=0o700);logs=root/'logs';logs.mkdir(mode=0o700);(logs/'verifier').mkdir();actor='solpi-cyp-'+token+'-actor';grader='solpi-cyp-'+token+'-grader';owned=[];result={'private_root':str(root),'native_starts':0,'provider_POST':0,'synthetic_helper_containers':1,'trusted_grader_calls':0,'protocol':'cython-source-only-probe-v1','scope':'new missing-installation/source transfer integration;not skill comparison or repeated gold control'}
 try:
  spec=recipe('build-cython-ext');g=inputs();image=spec['actor_image_id'];assert image==g['image_id']
  docker('create','--name',actor,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128',*docker_options(spec),'--entrypoint','/bin/sh',image,'-c','sleep infinity');owned.append(actor)
  metadata=json.loads(docker('inspect',actor,text=True).stdout)[0];result['actor_isolation']=verify_actor_inspect(metadata,spec,'none',{})
  docker('start',actor);docker('exec',actor,'/bin/sh','-c','mkdir -p /app/pyknotid; printf "%s" "synthetic source-only output;target never installed" > /app/pyknotid/README.synthetic');docker('stop','-t','0',actor)
  result['capture']=capture_partial(actor,image,root/'captured');docker('rm',actor);owned.remove(actor)
  docker('create','--name',grader,'--network','none','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128','-v',str(TASK/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw',*grader_options(g),'--entrypoint','/bin/sh',image,'-c','sleep infinity');owned.append(grader)
  result['replay']=replay_partial(root/'captured',grader,image);result['dependency_setup']=prepare(grader,image,installation_absent=True)
  readback=docker('exec',grader,'cat','/app/pyknotid/README.synthetic').stdout;original=(root/'captured/payload-0/README.synthetic').read_bytes();assert readback==original;result['source_readback_sha256']=hashlib.sha256(readback).hexdigest()
  result['trusted_grader_calls']=1
  with (root/'verifier.log').open('wb') as out:p=subprocess.run(['docker','exec',grader,'bash','/tests/test.sh'],stdout=out,stderr=subprocess.STDOUT,timeout=600)
  result['verifier_exit']=p.returncode;result['reward']=(logs/'verifier/reward.txt').read_text().strip();tests=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];result['test_events']=len(tests);result['passed_test_names']=[t['name'] for t in tests if t['status']=='passed'];result['failed_test_names']=[t['name'] for t in tests if t['status']=='failed'];assert result['reward']=='0' and len(tests)==11;assert docker('exec',grader,'cat','/app/pyknotid/README.synthetic').stdout==original;result['passed']=True
 except Exception as e:result['passed']=False;result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  result['cleanup_verified']=all(subprocess.run(['docker','inspect',n],capture_output=True,text=True,timeout=10).returncode!=0 for n in [actor,grader])
  result['module_hashes']={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['cython_partial_output.py','stopped_cython_output.py','cython_grader_inputs.py','run_cython_partial_probe.py']};result['evidence_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()};(R/'cython-partial-probe-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
