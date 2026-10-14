"""Create compact stage3 allowance only after actual all500 artifact audit.
No model, image, or grader execution; caller must commit this before launch.
"""
import json,pathlib,subprocess,sys
from common import H,R,private_root,verify_preregistration,sha,save

def freeze():
 root=private_root();p=verify_preregistration();c=json.loads((root/'controls-complete.json').read_text());assert c['completed_issues']==500 and c['model_calls']==0;assert not (root/'models-launch.json').exists();assert sha(H/'control-summary.csv')==c['summary_sha256'];raw=[json.loads(line) for line in (R/'tests/eval/swebench_verified.jsonl').read_text().splitlines()];enriched=json.loads((root/'dataset.json').read_text());lookup={t['instance_id']:t for t in enriched};assert len(raw)==len(lookup)==500
 for row in raw:
  for key,value in row.items():assert lookup[row['instance_id']][key]==value,'Original issue/test/source metadata altered'
 run=subprocess.run(['/tmp/solpi-refinement-harbor-venv/bin/python',str(H/'audit_controls.py'),'--require-complete'],check=True,capture_output=True,text=True,timeout=300);audit=json.loads(run.stdout);assert audit['all500_verified'] and audit['completed_pairs']==500 and audit['eligible_pairs']==len(c['eligible_tasks']);assert set(c['eligible_tasks']).isdisjoint(c['failed_tasks']) and set(c['eligible_tasks'])|set(c['failed_tasks'])==set(lookup)
 for iid in lookup:
  v=json.loads((root/c['control_session']/iid/'final-control.json').read_text());assert v['valid_pair']==(iid in c['eligible_tasks'])
 m=dict(contract='fed9674',stage='eligible model runs',control_summary_sha256=c['summary_sha256'],eligible_tasks_sha256=sha(root/'controls-complete.json'),all500_control_audit=audit,private_enriched_dataset_sha256=sha(root/'dataset.json'),private_full_queue_sha256=p['queue_sha256'],eligible_issues=len(c['eligible_tasks']),excluded_only_failed_controls=len(c['failed_tasks']),planned_cells=4*len(c['eligible_tasks']),source_sha256={f.name:sha(f) for f in sorted(H.glob('*.py'))},caps=p['caps'],route='127.0.0.1:8000',rolling_slots=16,metadata_gating=False,model_calls_before_allowance=0,not_complete=True)
 save(H/'model-stage.json',m);print('Model-stage allowance prepared; commit before launching with --allowance-commit. No model calls.')
if __name__=='__main__':freeze()
