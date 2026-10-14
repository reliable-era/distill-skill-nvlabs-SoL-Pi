"""All-original official gold/no-op checks, G4C semantics, zero models.
Separate worker process per issue avoids os.chdir races in official harness.
"""
import json,pathlib,sys
from common import save,sha
from grade_swe import grade

def validate(entry,spec,statuses,found,kind,resolve,classification):
 if not found or classification is not None or entry.get('infra_failure') is not False or entry.get('infra_failure_reason'):raise RuntimeError('Official control infrastructure/collection failure')
 coverage={}
 for category,expected in [('FAIL_TO_PASS',spec.FAIL_TO_PASS),('PASS_TO_PASS',spec.PASS_TO_PASS)]:
  detail=entry['tests_status'][category];reported=detail['success']+detail['failure']
  if len(reported)!=len(expected) or set(reported)!=set(expected):raise RuntimeError('Original expected-test coverage mismatch')
  keys=[resolve(x,statuses) for x in expected]
  if any(k is None for k in keys):raise RuntimeError('Missing/ambiguous original test statuses')
  values=[statuses[k] for k in keys]
  if any(v not in ('PASSED','FAILED') for v in values):raise RuntimeError('Incomplete original tests')
  coverage[category]=dict(expected=len(expected),passed=values.count('PASSED'),failed=values.count('FAILED'))
 if not spec.FAIL_TO_PASS or coverage['PASS_TO_PASS']['failed']:raise RuntimeError('No original F2P or original P2P regression')
 if kind=='gold':
  if entry.get('patch_successfully_applied') is not True or entry.get('resolved') is not True or coverage['FAIL_TO_PASS']['failed']:raise RuntimeError('Original gold did not resolve')
 elif entry.get('resolved') is not False or not coverage['FAIL_TO_PASS']['failed']:raise RuntimeError('No-op did not demonstrate original F2P failure')
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
