"""NewTeXbaseline/wiring/software-collectiongate;no model/gold/officialtestredo."""
import json,pathlib,subprocess,uuid,hashlib
from actor_public_inputs import recipe,docker_options,verify_actor_inspect
from tex_protected_baseline import capture_before,compare_original
from task_artifacts import capture_stopped_actor
from task_replay import replay_capture
from tex_grader_setup import prepare,grade_argv
R=pathlib.Path(__file__).resolve().parent;SRC=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/overfull-hbox')
def docker(*a):return subprocess.check_output(['docker',*a],stderr=subprocess.PIPE,text=True,timeout=60).strip()
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-tex-wiring-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);spec=recipe(SRC.name);actor=root.name+'-actor';grade=root.name+'-grader';owned=[];logs=root/'logs';(logs/'verifier').mkdir(parents=True);out={'private_root':str(root),'native_starts':0,'model_POST':0,'gold_runs':0,'official_test_runs':0,'trusted_setup_attempts':1,'collection_only':True}
 try:
  ctrl=json.loads((R/'file-capture-overfull-hbox-result.json').read_text());assert ctrl['valid_output_replay'] and ctrl['source_unchanged'] and ctrl['cleanup_verified']
  docker('create','--name',actor,'--network','none','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges',*docker_options(spec),'--entrypoint','/bin/sh',spec['actor_image_id'],'-c','sleep infinity');owned.append(actor);verify_actor_inspect(json.loads(docker('inspect',actor))[0],spec,'none',{});baseline=capture_before(actor,spec['actor_image_id'],root/'before');out['before_baseline']=baseline;out['original_inputs']=compare_original(baseline,ctrl);out['capture']=capture_stopped_actor(SRC.name,actor,spec['actor_image_id'],root/'captured',protected_baseline=baseline['protected_baseline']);assert out['capture']['protected_input_gate_passed'];docker('rm',actor);owned.remove(actor)
  docker('create','--name',grade,'--network','bridge','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SRC/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw','-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro','--entrypoint','/bin/sh',spec['grader_image_id'],'-c','sleep infinity');owned.append(grade);out['replay']=replay_capture(SRC.name,root/'captured',grade,spec['grader_image_id'],actor_image_id=spec['actor_image_id']);assert out['replay']['restored_paths']==['/app/input.tex'];out['setup']=prepare(grade,spec['grader_image_id'],root)
  cmd=['docker','exec','-w','/app','-e','UV_OFFLINE=1','-e','UV_PYTHON_DOWNLOADS=never',grade,'/root/.local/bin/uvx','-p','3.13','-w','pytest==8.4.1','-w','pytest-json-ctrf==0.3.5','pytest','--collect-only','-q','/tests/test_outputs.py']
  with (root/'collection.log').open('wb') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=90)
  names=[l.strip() for l in (root/'collection.log').read_text().splitlines() if '::test_' in l];expected=[t['name'] for t in ctrl['replay']['tests']];assert p.returncode==0 and len(names)==4 and {n.split('/')[-1] for n in names}=={n.split('/')[-1] for n in expected};out['collected_original_tests']=names;out['unchanged_test_script_sha256']=hashlib.sha256((SRC/'tests/test.sh').read_bytes()).hexdigest();out['passed']=True
 except Exception as e:out.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:400]})
 finally:
  for n in owned:subprocess.run(['docker','rm','-f',n],capture_output=True,timeout=30)
  out['cleanup_verified']=all(subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in [actor,grade]);out['artifact_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()};(R/'tex-wiring-probe.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
