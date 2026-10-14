"""Final supervisor correction:ONLY official resolved fields,no more reruns."""
import collections,csv,json
from common import H,private_root,save,sha,verify_preregistration
from official_control_rule import pair

def main():
 root=private_root();verify_preregistration();assert not (root/'models-launch.json').exists();c=json.loads((root/'controls-complete.json').read_text());assert c['control_session']=='controls-official-v2';template=json.loads((root/'grader-template.json').read_text());rows=[];restored=[]
 for f in sorted((root/c['control_session']).glob('*/final-control.json')):
  old=json.loads(f.read_text());iid=old['task'];v=pair(old['official_report_roots'],iid,template['official_source']);v.update(official_report_roots=old['official_report_roots'],image_lease=old['image_lease'],infra_pair_retry=old['infra_pair_retry'],previous_decision_sha256=sha(f));save(root/'controls-resolved-only-v3'/iid/'final-control.json',v);rows.append(v)
  if v['valid_pair'] and not old['valid_pair']:restored.append(iid)
 assert len(rows)==500 and sum(v['valid_pair'] for v in rows)==444 and len(restored)==22,'Supervisor444/56 expectation must match actual reports'
 summary=[dict(task=v['task'],eligible=v['valid_pair'],category=v['category'],infra_pair_retry=v['infra_pair_retry'],private_result_sha256=sha(root/'controls-resolved-only-v3'/v['task']/'final-control.json')) for v in rows]
 (root/'control-summary-log-heuristic-v2.csv').write_bytes((H/'control-summary.csv').read_bytes());save(root/'controls-complete-log-heuristic-v2.json',c)
 with (H/'control-summary.csv').open('w',newline='') as out:w=csv.DictWriter(out,fieldnames=list(summary[0]),lineterminator='\n');w.writeheader();w.writerows(summary)
 save(root/'controls-complete.json',dict(control_session='controls-resolved-only-v3',completed_issues=500,eligible_tasks=[v['task'] for v in rows if v['valid_pair']],failed_tasks=[v['task'] for v in rows if not v['valid_pair']],model_calls=0,summary_sha256=sha(H/'control-summary.csv')));save(H/'control-rule-correction-summary.json',dict(eligibility_rule='ONLY official gold resolved True AND official no-op resolved False',final_categories=dict(collections.Counter(v['category'] for v in rows)),eligible=444,excluded=56,log_heuristic_exclusions_reversed=22,restored_issue_ids=restored,infra_issues_retried_once=sum(v['infra_pair_retry'] for v in rows),additional_regrading=0,model_calls=0,csv_line_endings='LF;git diff --cached --check required'));print('500 official resolved-only decisions:444 eligible/56 excluded;22 restored;zero additional regrades/model calls.')
if __name__=='__main__':main()
