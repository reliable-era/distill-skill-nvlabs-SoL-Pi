"""Oneboundedgrader-onlyrepair ofsavedKcapture;NO actor/modelretry."""
import json,pathlib,subprocess,uuid,hashlib
from task_replay import replay_capture,verify_payload
from task_artifacts import descriptor
from tex_grader_setup import prepare,grade_argv
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def docker(*args):return subprocess.check_output(['docker',*args],stderr=subprocess.PIPE,text=True,timeout=60).strip()
if __name__=='__main__':
 assert not (R/'16k-tex-K-grade-repair.json').exists(),'one repaironly'
 plan=json.loads((R/'16k-tex-r2-plan.json').read_text());digest=sha(R/'16k-tex-r2-plan.json');old=json.loads((R/'16k-tex-r2-result.json').read_text());assert old['plan_sha256']==digest and len(old['rows'])==3 and old['errors'][0]['type']=='TimeoutExpired' and old['starts']==4;assert not pathlib.Path('/proc/1462373').exists()
 src=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/overfull-hbox');assert all(sha(src/n)==h for n,h in plan['task_source_manifest'].items());assert all(sha(R/n)==h for n,h in plan['prospective_module_hashes'].items());saved=pathlib.Path('/tmp/solpi-t16-'+digest[:18])/'K';cap=json.loads((saved/'captured/capture.json').read_text());assert cap['protected_input_gate_passed'] and cap['stopped_actor_verified'] and cap['image_id']==plan['actor_image_id']
 for item in descriptor('overfull-hbox'):verify_payload(saved/'captured'/cap['artifacts'][item['path']]['local_payload'],cap['artifacts'][item['path']])
 pins={str(p.relative_to(saved/'captured')):sha(p) for p in (saved/'captured').rglob('*') if p.is_file()};root=pathlib.Path('/tmp/solpi-tex-grade-repair-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);logs=root/'logs';(logs/'verifier').mkdir(parents=True);name=root.name;out={'plan_sha256':digest,'saved_capture':str(saved/'captured'),'capture_hashes_before':pins,'private_root':str(root),'arm':'K','native_starts':0,'model_POST':0,'grader_repair_attempt':1,'source_unchanged':True,'original_setup_failure_retained':True,'original_setup_failure_log_sha256':sha(saved/'trusted-setup.log'),'actor_wall_seconds':'unavailable:notdurablyrecordedbeforegraderfailure','grader_setup_seconds_cap':300,'grader_seconds_cap':600};created=False
 try:
  spec=plan['public_recipe'];docker('create','--name',name,'--network','bridge','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(src/'tests')+':/tests:ro','-v',str(logs)+':/logs:rw','-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro','--entrypoint','/bin/sh',plan['image_id'],'-c','sleep infinity');created=True;out['replay']=replay_capture('overfull-hbox',saved/'captured',name,plan['image_id'],actor_image_id=plan['actor_image_id']);out['dependency_setup']=prepare(name,plan['image_id'],root)
  with (root/'verifier.log').open('wb') as f:p=subprocess.run(grade_argv(name),stdout=f,stderr=subprocess.STDOUT,timeout=600)
  out['verifier_exit']=p.returncode;tests=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];out['reward']=(logs/'verifier/reward.txt').read_text().strip();out['test_results']=[{'name':t['name'],'status':t['status']} for t in tests];assert len(tests)==4 and {t['name'] for t in tests}==set(json.loads((R/'tex-wiring-probe.json').read_text())['collected_original_tests']);out['solved']=out['reward']=='1' and all(t['status']=='passed' for t in tests);out['grade_available']=True
 except Exception as e:out.update(grade_available=False,error={'type':type(e).__name__,'message':str(e)[:500]})
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  out['cleanup_verified']=subprocess.run(['docker','inspect',name],capture_output=True,timeout=10).returncode!=0;out['capture_hashes_after']={str(p.relative_to(saved/'captured')):sha(p) for p in (saved/'captured').rglob('*') if p.is_file()};assert out['capture_hashes_after']==pins;out['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'16k-tex-K-grade-repair.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
