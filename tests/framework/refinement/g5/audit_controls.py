"""Audit user-approved official-only control eligibility; no model/grader calls.
Original per-test expectations/diagnostics retained informationally, never gates.
"""
import collections,json,pathlib
from common import H,private_root,save,sha
from official_control_rule import pair

def audit(root,session=None,require_complete=False):
 root=pathlib.Path(root);complete=json.loads((root/'controls-complete.json').read_text());session=session or complete['control_session'];template=json.loads((root/'grader-template.json').read_text());tasks={t['instance_id']:t for t in json.loads((root/'dataset.json').read_text())};assert len(tasks)==500;rows=[]
 for f in sorted((root/session).glob('*/final-control.json')):
  r=json.loads(f.read_text());iid=r['task'];assert iid in tasks and r['model_calls']==0;assert 'official_report_roots' in r,'Corrected official-only decision required';derived=pair(r['official_report_roots'],iid,template['official_source']);assert derived['valid_pair']==r['valid_pair'] and derived['category']==r['category'];expected={k:len(json.loads(tasks[iid][k]) if isinstance(tasks[iid][k],str) else tasks[iid][k]) for k in ('FAIL_TO_PASS','PASS_TO_PASS')};rows.append(dict(task=iid,valid_pair=r['valid_pair'],category=r['category'],original_expected_informational=expected,final_sha256=sha(f),official_decisions=derived['controls'],infra_pair_retry=r['infra_pair_retry']))
 if require_complete:assert len(rows)==500 and set(complete['eligible_tasks'])=={r['task'] for r in rows if r['valid_pair']}
 s=dict(completed_pairs=len(rows),eligible_pairs=sum(r['valid_pair'] for r in rows),failed_pairs=sum(not r['valid_pair'] for r in rows),all500_verified=len(rows)==500,model_calls=0,eligibility_rule='Official gold resolved True AND official no-op resolved False;statuses informational only',original_expected_tests_retained=True,categories=dict(collections.Counter(r['category'] for r in rows)));path=root/'control-official-rule-audit.json';save(path,dict(summary=s,rows=rows));s['private_coverage_audit_sha256']=sha(path);return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--require-complete',action='store_true');a=p.parse_args();print(json.dumps(audit(private_root(),require_complete=a.require_complete),separators=(',',':')))
