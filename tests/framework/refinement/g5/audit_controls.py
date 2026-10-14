"""Read-only original-control artifact/coverage audit. No model/grader calls.
Run with the pinned official-grader interpreter. Partial snapshots cannot
satisfy the all500 barrier. Raw test identities/statuses remain private.
"""
import collections,hashlib,json,pathlib,sys
from common import H,private_root,save,sha

def audit(root,session='controls02',require_complete=False):
 root=pathlib.Path(root);template=json.loads((root/'grader-template.json').read_text());sys.path.insert(0,template['official_source'])
 from swebench.harness.utils import make_test_spec
 from swebench.harness.run_evaluation import LOG_TEST_OUTPUT,LOG_INSTANCE
 from swebench.harness.grading import get_logs_eval,_resolve_case
 from swebench.harness.infra_failure import classify_logs
 from control_worker import validate
 tasks={r['instance_id']:r for r in json.loads((root/'dataset.json').read_text())};assert len(tasks)==500;rows=[];reasons=collections.Counter();artifacts=[]
 for f in sorted((root/session).glob('*/final-control.json')):
  r=json.loads(f.read_text());iid=r['task'];assert iid in tasks and r['model_calls']==0;assert {c['kind'] for c in r['controls']}=={'nop','gold'};assert r['official_image_id']==r['image_lease']['image_id'];spec=make_test_spec(dict(tasks[iid],image=r['official_image_id']));proof=dict(task=iid,valid_pair=r['valid_pair'],original_expected={k:len(getattr(spec,k)) for k in ('FAIL_TO_PASS','PASS_TO_PASS')},controls=[])
  for c in r['controls']:
   d=f.parent/c['kind'];g=d/'grade-result.json';assert sha(g)==c['grade_sha256'];grade=json.loads(g.read_text());assert grade['grade_valid']==c['grade_valid'] and grade['solved']==c['resolved'] and grade['owned_containers_absent']==c['owned_containers_absent'];reports=list(d.rglob('report.json'));detail=dict(kind=c['kind'],valid=c['valid'],grade_sha256=sha(g));recomputed=False
   if len(reports)==1:
    report=reports[0];entry=json.loads(report.read_text())[iid];statuses,found=get_logs_eval(spec,str(report.parent/LOG_TEST_OUTPUT));detail['original_coverage']={k:dict(expected=len(getattr(spec,k)),missing_or_ambiguous=sum(_resolve_case(x,statuses) is None for x in getattr(spec,k)),incomplete=sum(_resolve_case(x,statuses) is not None and statuses[_resolve_case(x,statuses)] not in ('PASSED','FAILED') for x in getattr(spec,k))) for k in ('FAIL_TO_PASS','PASS_TO_PASS')};detail['report_sha256']=sha(report)
    try:
     coverage=validate(entry,spec,statuses,found,c['kind'],_resolve_case,classify_logs(report.parent/LOG_TEST_OUTPUT,report.parent/LOG_INSTANCE));recomputed=grade['grade_valid'] and grade['owned_containers_absent']
     if recomputed:assert coverage==c['coverage']
    except RuntimeError as e:detail['failure_reason']=str(e)
   else:detail['failure_reason']='Official control result/cleanup unavailable'
   assert bool(recomputed)==c['valid'],'Persisted control validity not reproduced'
   if not c['valid']:reasons[(c['kind'],detail.get('failure_reason','Official control result/cleanup unavailable'))]+=1
   proof['controls'].append(detail)
  assert r['valid_pair']==all(c['valid'] for c in proof['controls']);rows.append(proof);artifacts.append(dict(task=iid,final_control_sha256=sha(f)))
 if require_complete:assert len(rows)==500 and (root/'controls-complete.json').exists(),'All500 actual pairs required'
 summary=dict(completed_pairs=len(rows),eligible_pairs=sum(r['valid_pair'] for r in rows),failed_pairs=sum(not r['valid_pair'] for r in rows),all500_verified=len(rows)==500,model_calls=0,original_expected_tests_used=True,control_source_sha256=sha(H/'control_worker.py'),failure_taxonomy=[dict(kind=k[0],reason=k[1],count=v) for k,v in sorted(reasons.items())]);save(root/'control-coverage-audit.json',dict(summary=summary,rows=rows,artifacts=artifacts));summary['private_coverage_audit_sha256']=sha(root/'control-coverage-audit.json');return summary
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--require-complete',action='store_true');a=p.parse_args();print(json.dumps(audit(private_root(),require_complete=a.require_complete),separators=(',',':')))
