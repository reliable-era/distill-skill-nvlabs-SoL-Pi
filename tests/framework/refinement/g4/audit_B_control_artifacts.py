"""Retained original B pairs plus neutral tmux/Python control rechecks.
Local immutable logs/tests/resources and actual owned absence; no reruns/models.
Original tmux exit127 remains invalid despite reward1, never silently repaired.
"""
import json,pathlib,subprocess
from native import H,sha
from transport import save

def main():
 plan=json.loads((H/'preregistration.json').read_text());original=json.loads((H/'B-controls-result.json').read_text());tmux=json.loads((H/'B-tmux-result.json').read_text());python=json.loads((H/'B-python-result.json').read_text());campaigns=[('original',original['rows']),('neutral_tmux',[tmux['control_pair']]),('neutral_python',[r['pair'] for r in python['rows']])];proofs=[];errors=[];latest={}
 assert len(original['rows'])==9 and len(python['rows'])==5 and tmux['original_failed_pair_retained'] and tmux['no_test_or_oracle_edits'];assert all(r['no_task_test_or_gold_edits'] for r in python['rows'])
 for campaign,rows in campaigns:
  for row in rows:
   bad=[];metadata=plan['terminal_tasks'][row['task']];source=pathlib.Path(plan['terminal_source'])/row['task'];valid=[]
   if row['model_calls']!=0 or len(row['controls'])!=2 or {c['mode'] for c in row['controls']}!={'nop','gold'}:bad.append('original pair/model-free identity')
   for relative,digest in metadata['source_hashes'].items():
    if sha(source/relative)!=digest:bad.append('original task/test/oracle changed')
   for c in row['controls']:
    directory=pathlib.Path(c['private_root']);ins=json.loads((directory/'container-inspect.json').read_text());host=ins['HostConfig'];env=metadata['environment'];name=c['container_name']
    if sha(directory/'container-inspect.json')!=c['inspect_sha256'] or ins['Image']!=row['image_id'] or host['NanoCpus']!=int(env['cpus']*1e9) or host['Memory']!=env['memory_mb']*1024**2 or host['PidsLimit']!=512 or host['Privileged'] or host.get('DeviceRequests'):bad.append('control inspect/image/resources')
    if not any(m['Destination']=='/tests' and m['Source']==str(source/'tests') and not m['RW'] for m in ins['Mounts']):bad.append('readonly original tests')
    if sha(directory/'verifier.private.log')!=c['verifier']['log_sha256']:bad.append('original verifier log')
    if c.get('oracle') and sha(directory/'oracle.private.log')!=c['oracle']['log_sha256']:bad.append('original oracle log')
    ctrf=directory/'logs/verifier/ctrf.json';reward=(directory/'logs/verifier/reward.txt').read_text().strip();tests=json.loads(ctrf.read_text())['results']['tests']
    if sha(ctrf)!=c['ctrf_sha256'] or len(tests)!=c['test_events'] or any(t['status'] not in ('passed','failed') for t in tests):bad.append('original test collection/artifact')
    expected='1' if c['mode']=='gold' else '0';ok=reward==expected and reward==c['reward'] and c['verifier']['exit_code']==0 and (c['mode']!='gold' or c['oracle']['exit_code']==0)
    if c['mode']=='gold' and reward=='1' and not all(t['status']=='passed' for t in tests):bad.append('original reward/CTRF mismatch')
    if c['mode']=='nop' and reward=='0' and all(t['status']=='passed' for t in tests):bad.append('original no-op failure missing')
    if c['valid_expected_reward']!=ok:bad.append('oracle/verifier/reward eligibility disagreement')
    valid.append(ok)
    if not name.startswith('solpi-g4-B-control-'):bad.append('unowned control name')
    else:
     gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
     if gone.returncode==0 or 'No such' not in gone.stderr:bad.append('actual owned control absence')
   if row['valid_pair']!=all(valid):bad.append('pair validity')
   latest[row['task']]=row
   if bad:errors.append(dict(campaign=campaign,task=row['task'],checks=bad))
   proofs.append(dict(campaign=campaign,task=row['task'],image_id=row['image_id'],valid_pair=row['valid_pair'],original_oracle_exits={c['mode']:c.get('oracle',{}).get('exit_code') for c in row['controls']},owned_containers=len(row['controls']),all_checks_passed=not bad))
 for task,row in latest.items():
  if not row['valid_pair'] or row['image_id']!=plan['terminal_tasks'][task]['image_id']:errors.append(dict(task=task,checks=['effective frozen image lacks valid original controls']))
 assert len(latest)==9;result=dict(proofs=proofs,errors=errors,all_original_control_evidence_verified=not errors,effective_control_valid_tasks=9,original_invalid_pairs=sum(not r['valid_pair'] for r in original['rows']),model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/'B-control-artifact-audit.json',result);print('Original/neutral control pairs',len(proofs),'owned containers',sum(r['owned_containers'] for r in proofs),'errors',errors)
if __name__=='__main__':main()
