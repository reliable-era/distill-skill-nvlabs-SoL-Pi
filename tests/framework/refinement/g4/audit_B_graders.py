"""Independent B original verifier/capture/resource/absence checks, no reruns.
Only recorded owned grader names; raw reward/CTRF remain authoritative.
"""
import argparse,json,pathlib,subprocess
from native import H,sha
from transport import save

def audit(window):
 plan=json.loads((H/'preregistration.json').read_text());launch=json.loads((H/f'window-{window}-launch.json').read_text());root=pathlib.Path(launch['root']);cells=[i for i in json.loads((H/f'windows/{window}.json').read_text())['cells'] if i.startswith('g4-B-')];proofs=[];pending=[];errors=[]
 for cell in cells:
  path=root/(cell+'-attempts.json')
  if not path.exists():pending.append(cell);continue
  for row in json.loads(path.read_text()):
   directory=pathlib.Path(row['root'])/'grade';result=directory/'grade-result.json'
   if not result.exists():pending.append(cell);continue
   g=json.loads(result.read_text());metadata=plan['terminal_tasks'][row['task']];bad=[];env=metadata['environment'];ins=json.loads((directory/'container-inspect.json').read_text());host=ins['HostConfig']
   if g['image_id']!=row['capture_image_id'] or ins['Image']!=row['capture_image_id']:bad.append('captured filesystem image mismatch')
   if not (host['NanoCpus']==int(env['cpus']*1e9) and host['Memory']==env['memory_mb']*1024**2 and host['PidsLimit']==512 and not host['Privileged'] and not host.get('DeviceRequests')):bad.append('original resources')
   source=pathlib.Path(plan['terminal_source'])/row['task'];mounts=ins['Mounts']
   if not any(m['Source']==str(source/'tests') and m['Destination']=='/tests' and m['RW'] is False for m in mounts):bad.append('original readonly verifier mount')
   for relative,digest in metadata['source_hashes'].items():
    if sha(source/relative)!=digest:bad.append('original task changed')
   for relative,digest in g['artifacts'].items():
    if sha(directory/relative)!=digest:bad.append('raw artifact changed:'+relative)
   tests=json.loads((directory/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(directory/'logs/verifier/reward.txt').read_text().strip();solved=reward=='1'
   if len(tests)!=metadata['gold_original_test_events'] or any(t.get('status') not in ('passed','failed') for t in tests):bad.append('original test coverage/status')
   if reward not in ('0','1') or solved!=all(t['status']=='passed' for t in tests) or solved!=g['solved'] or not g['grade_valid'] or g['timeout'] or g.get('verifier_exit')!=0:bad.append('reward/verifier consistency; explicit unavailable if infrastructure')
   name=g['container_name']
   if not name.startswith('solpi-g4-B-grade-'):bad.append('owned grader name')
   else:
    p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
    if p.returncode==0 or 'No such' not in p.stderr:bad.append('actual grader absence')
   if bad:errors.append(dict(cell_id=cell,attempt=row['attempt'],checks=bad))
   proofs.append(dict(cell_id=cell,attempt=row['attempt'],grade_sha256=sha(result),image_id=g['image_id'],test_events=len(tests),solved=g['solved'],all_checks_passed=not bad))
 r=dict(window=window,proofs=proofs,pending_cells=pending,errors=errors,original_grader_capture_evidence_verified=not errors and not pending,model_calls=0,not_a_completion_audit=True);save(H/f'window-{window}-B-grader-audit.json',r);return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('B grader proofs',len(r['proofs']),'pending',r['pending_cells'],'errors',r['errors'])
