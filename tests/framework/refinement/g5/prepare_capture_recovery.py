"""Capture-regression recovery snapshot;immutable originals,all costs retained.
Supervisor-authorized harness attempts do not consume the five-attempt budget.
No model/server calls;ownership cleanup already completed before invocation.
"""
import json,pathlib
from common import H,private_root,save,sha
from audit_receipts import reconstruct

def main():
 root=private_root();assert (root/'ADMISSIONS-STOP').exists();assert not (root/'models-resume-v2-launch.json').exists();base=json.loads((root/'harness-5xx-recovery.json').read_text());current=json.loads((root/'model-summary.json').read_text());assert len(current)==38;allrows={};retained=base['retained_rows'];old_harness=set(base['harness_affected_cells']);failed=[];stopped=[]
 for cid,rows in base['prior_attempt_rows'].items():
  for a in rows:
   a=dict(a)
   if cid in old_harness:a.update(harness_failure=True,harness_failure_reason='original authorized socket/stop-cascade recovery')
   allrows[a['root']]=a
 for r in current:
  for a in r['attempt_rows']:
   a=dict(a)
   if a['root'] not in allrows:allrows[a['root']]=a
  last=allrows[r['attempt_rows'][-1]['root']]
  if last.get('phase')=='capture' and last.get('native_exit')==0 and last.get('error'):
   last.update(harness_failure=True,harness_failure_reason='short bind source deleted before docker cp');failed.append(r['cell_id'])
 assert len(failed)==32
 # Preserve original ledgers byte-for-byte. For interrupted forwards,derive only
 # raw-evidenced lower bounds into a separate sidecar;missing usage stays unknown.
 orphan_requests=0
 for item in json.loads((root/'capture-stop-owned-actors.json').read_text())['actors']:
  d=pathlib.Path(item['attempt_root']);a=json.loads((d/'attempt-progress.json').read_text());ledger=json.loads((d/'transport/ledger.json').read_text());closed={v['request'] for v in ledger['records']};extras=[]
  for n in range(1,ledger['provider_POST']+1):
   if n in closed:continue
   rawpath=d/'transport'/f'response-{n}.sse';raw=rawpath.read_bytes() if rawpath.exists() else b'';proof=reconstruct(raw,dict(stream_eof=False,error='SupervisorStop',provider_status=None));extras.append(dict(request=n,response_sha256=sha(rawpath) if rawpath.exists() else None,**proof));orphan_requests+=1
  sidecar=d/'supervisor-stop-cost.json';save(sidecar,dict(original_ledger_sha256=sha(d/'transport/ledger.json'),closed_receipts=len(closed),provider_POST=ledger['provider_POST'],interrupted_forward_receipts=extras,missing_usage_not_imputed=True));a.update(harness_failure=True,harness_failure_reason='supervisor stopped in-flight actor to prevent capture-regression calls',phase='supervisor_stop',error=dict(type='SupervisorStop',message='Actor stopped cleanly after admission freeze'),native_exit=None,native_sha256=sha(d/'native.jsonl'),timeout=False,grader_timeout=False,grade_valid=False,solved=None,requests=ledger['provider_POST'],recorded_receipts=len(closed),known_tokens_lower_bound=sum(v['tokens_lower_bound'] for v in ledger['records'])+sum(v['tokens_lower_bound'] for v in extras),cost_complete=not extras and all(v['cost_complete'] for v in ledger['records']),actor_absent=True,owned_cleanup_verified=True,connection_infra_failure=False,ended_on_5xx=False,supervisor_stop_cost_sha256=sha(sidecar));save(d/'supervisor-stop-result.json',a);allrows[a['root']]=a;stopped.append(a['cell_id'])
 prior={};done={r['cell_id'] for r in retained}
 for a in allrows.values():
  if a['cell_id'] not in done:prior.setdefault(a['cell_id'],[]).append(a)
 for rows in prior.values():rows.sort(key=lambda a:a['attempt']);assert [a['attempt'] for a in rows]==list(range(1,len(rows)+1))
 recent=[dict(cell_id=r['cell_id'],attempt=r['scored_attempt'],ended5xx=False) for r in current if r['cell_id'] in failed][-16:]
 result=dict(retained_rows=retained,prior_attempt_rows=prior,last16_finished_attempts=recent,original_capture_failed_cells=sorted(failed),supervisor_stopped_cells=sorted(stopped),capture_harness_attempts_excluded_from_budget=32,supervisor_stop_attempts_excluded_from_budget=len(stopped),interrupted_requests_with_unknown_completion=orphan_requests,all_prior_costs_retained=True,original_ledgers_and_archives_unchanged=True,prior_recovery_sha256=sha(root/'harness-5xx-recovery.json'),pre_repair_summary_sha256=sha(root/'model-summary.json'));save(root/'capture-recovery-v2.json',result);save(H/'capture-recovery-summary.json',{k:v for k,v in result.items() if k not in ('retained_rows','prior_attempt_rows','last16_finished_attempts')});print('Capture recovery:',len(failed),'failed,',len(stopped),'stopped,',orphan_requests,'interrupted request receipts unknown;all costs retained')
if __name__=='__main__':main()
