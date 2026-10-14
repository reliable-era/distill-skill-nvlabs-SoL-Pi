"""All-original official gold/no-op checks, G4C semantics, zero models.
Separate worker process per issue avoids os.chdir races in official harness.
"""
import json,pathlib,sys
from common import save,sha
from grade_swe import grade

def validate(entry,spec,statuses,found,kind,resolve,classification):
 if type(entry.get('resolved')) is not bool:raise RuntimeError('Official resolved field unavailable')
 coverage={}
 for category,expected in [('FAIL_TO_PASS',spec.FAIL_TO_PASS),('PASS_TO_PASS',spec.PASS_TO_PASS)]:
  detail=entry['tests_status'][category];reported=detail['success']+detail['failure']
  # Original per-test diagnostics are informational, not eligibility gates.
  keys=[resolve(x,statuses) for x in expected]
  values=[statuses[k] for k in keys if k is not None]
  coverage[category]=dict(expected=len(expected),passed=values.count('PASSED'),failed=values.count('FAILED'))
 if entry.get('resolved') is not (kind=='gold'):raise RuntimeError('Official gold/no-op resolved outcome failed required rule')
 return coverage

def main(root,planfile):
 root=pathlib.Path(root).resolve();plan=json.loads(pathlib.Path(planfile).read_text());task=json.loads(pathlib.Path(plan['private_dataset']).read_text())[0];iid=task['instance_id'];sys.path.insert(0,plan['official_source'])
 from swebench.harness.utils import make_test_spec
 from swebench.harness.run_evaluation import LOG_TEST_OUTPUT,LOG_INSTANCE
 from swebench.harness.grading import get_logs_eval,_resolve_case
 from swebench.harness.infra_failure import classify_logs
 spec=make_test_spec(dict(task,image=plan['images'][iid]));rows=[]
 for kind in ('nop','gold'):
  patch=root/(kind+'.patch');patch.write_text(task['patch'] if kind=='gold' else '');directory=root/kind;r=grade(directory,iid,patch,plan);c=dict(kind=kind,valid=False,grade_valid=r['grade_valid'],resolved=r['solved'],owned_containers_absent=r['owned_containers_absent'],grade_sha256=sha(directory/'grade-result.json'))
  try:
   reports=list(directory.rglob('report.json'))
   if len(reports)!=1 or not r['grade_valid'] or not r['owned_containers_absent']:raise RuntimeError('Official control result/cleanup unavailable')
   report=reports[0];entry=json.loads(report.read_text())[iid];statuses,found=get_logs_eval(spec,str(report.parent/LOG_TEST_OUTPUT));c['coverage']=validate(entry,spec,statuses,found,kind,_resolve_case,classify_logs(report.parent/LOG_TEST_OUTPUT,report.parent/LOG_INSTANCE));c['valid']=True
  except Exception as e:c['error']=dict(type=type(e).__name__,message=str(e)[:500]);c['grader_errors']=r['errors']
  rows.append(c);save(root/'control-result.json',dict(task=iid,controls=rows,valid_pair=False,model_calls=0))
 save(root/'control-result.json',dict(task=iid,controls=rows,valid_pair=all(c['valid'] for c in rows),model_calls=0,official_image_id=plan['images'][iid]))
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
