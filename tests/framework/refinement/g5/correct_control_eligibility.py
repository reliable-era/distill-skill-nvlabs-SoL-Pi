"""User-approved official-only re-judgment and once-only infra pair reruns.
Never reruns a valid original pair, even if official outcome is exclusion.
Raw original reports/diagnostics retained; no model calls.
"""
import collections,concurrent.futures,csv,json,os,pathlib,subprocess,threading
from common import H,private_root,verify_preregistration,save,sha,disk_free
from images import Images
from model_images import ModelImages
from official_control_rule import pair

def inventory(root):
 template=json.loads((root/'grader-template.json').read_text());rows=[]
 for old in sorted((root/'controls02').glob('*/final-control.json')):
  original=json.loads(old.read_text());iid=original['task'];d={k:str(old.parent/k) for k in ('nop','gold')};r=pair(d,iid,template['official_source']);r.update(original_legacy_valid_pair=original['valid_pair'],original_final_sha256=sha(old),official_report_roots=d,image_lease=original.get('image_lease'))
  legacy_infra=bool(original.get('infrastructure_error')) or any((c.get('error') or {}).get('message') in ('Official control result/cleanup unavailable','Official control infrastructure/collection failure') for c in original['controls'])
  if legacy_infra:r.update(rejudged_original_category=r['category'],category='infrastructure',legacy_infrastructure_failure=True)
  rows.append(r)
 assert len(rows)==500;return rows

def main():
 root=private_root();verify_preregistration();assert not (root/'models-launch.json').exists();assert not (root/'control-correction-launch.json').exists(),'Do not restart existing correction; reconcile owned handle';initial=inventory(root);save(root/'control-rejudgment-originals.json',initial);save(root/'control-correction-launch.json',dict(pid=os.getpid(),model_calls=0));template=json.loads((root/'grader-template.json').read_text());tasks={t['instance_id']:t for t in json.loads((root/'dataset.json').read_text())};images=ModelImages(root);fallback=Images(root);lock=threading.RLock();final=[]
 def process(r):
  iid=r['task'];v=r;owned=images if r['image_lease'] else fallback
  if r['category']=='infrastructure':
   d=root/'controls-infra-v2'/iid;d.mkdir(parents=True,exist_ok=False)
   try:
    lease=images.acquire_control_image(iid,r['image_lease']) if r['image_lease'] else fallback.acquire(iid,'controls-infra-v2');plan=dict(template,images={iid:lease['image_id']});save(d/'task.json',[tasks[iid]]);plan.update(private_dataset=str(d/'task.json'),private_dataset_sha256=sha(d/'task.json'));save(d/'grader-plan.json',plan)
    with (d/'worker.log').open('xb') as log:p=subprocess.run(['/tmp/solpi-refinement-harbor-venv/bin/python',str(H/'control_worker.py'),str(d),str(d/'grader-plan.json')],stdout=log,stderr=subprocess.STDOUT,timeout=1800)
    assert p.returncode==0,'Corrected control runner failure; retain records and stop, not exclusion';roots={k:str(d/k) for k in ('nop','gold')};v=pair(roots,iid,template['official_source']);v.update(official_report_roots=roots,image_lease=lease,infra_pair_retry=1,original_category='infrastructure',original_final_sha256=r['original_final_sha256'])
   finally:owned.release(iid)
  else:v=dict(r,infra_pair_retry=0)
  save(root/'controls-official-v2'/iid/'final-control.json',v)
  with lock:final.append(v);save(H/'progress.json',dict(stage='control_official_rule_correction',completed_issues=len(final),total_issues=500,eligible_issues=sum(x['valid_pair'] for x in final),model_calls=0,root_free_bytes=disk_free()));print('corrected controls',len(final),'of500',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(process,r) for r in initial]
  for f in concurrent.futures.as_completed(futures):f.result()
 assert len(final)==500;rows=[dict(task=v['task'],eligible=v['valid_pair'],category=v['category'],infra_pair_retry=v['infra_pair_retry'],private_result_sha256=sha(root/'controls-official-v2'/v['task']/'final-control.json')) for v in sorted(final,key=lambda v:v['task'])]
 with (H/'control-summary.csv').open('w') as out:w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 save(root/'controls-complete-original-extra-rules.json',json.loads((root/'controls-complete.json').read_text()));save(root/'controls-complete.json',dict(control_session='controls-official-v2',completed_issues=500,eligible_tasks=[v['task'] for v in final if v['valid_pair']],failed_tasks=[v['task'] for v in final if not v['valid_pair']],model_calls=0,summary_sha256=sha(H/'control-summary.csv')));save(H/'control-rule-correction-summary.json',dict(original_categories=dict(collections.Counter(v['category'] for v in initial)),final_categories=dict(collections.Counter(v['category'] for v in final)),original_extra_rule_exclusions_reversed=sum(v['valid_pair'] and not v['original_legacy_valid_pair'] for v in initial),infra_issues_retried_once=sum(v['infra_pair_retry'] for v in final),model_calls=0));print('STAGE BOUNDARY:500 corrected official-only control decisions complete;commit summary before models.',flush=True)
if __name__=='__main__':main()
