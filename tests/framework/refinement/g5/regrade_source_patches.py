"""No-model deterministic source/empty regrading,then a durable resume snapshot.
Run only after the original owned controller drains;max4 issue leases/16 graders.
Original patches,rows,grades,ledgers and archives are not modified.
"""
import concurrent.futures,json,pathlib,subprocess
from common import H,R,private_root,save,sha,verify_preregistration
from source_patch import project
from patch_outcomes import empty_result
from model_images import ModelImages

def main(audit_only=False,operation_commit=None):
 root=private_root()
 if not audit_only:
  verify_preregistration();stage=json.loads((H/'regrade-stage.json').read_text());assert operation_commit
  assert subprocess.check_output(['git','show',operation_commit+':'+str((H/'regrade-stage.json').relative_to(R))],cwd=R)==(H/'regrade-stage.json').read_bytes()
  for f,d in stage['source_sha256'].items():assert sha(H/f)==d
  for f,d in stage['private_inputs_sha256'].items():assert sha(root/f)==d
 old_pid=json.loads((root/'model-resume-v2-handle.json').read_text())['pid'];proc=pathlib.Path('/proc')/str(old_pid)
 if proc.exists() and ') Z ' not in (proc/'stat').read_text():raise RuntimeError('Owned controller must finish draining before summary projection')
 auditdir=root/'patch-audit-v1';audit=json.loads((auditdir/'audit.json').read_text());before=json.loads((root/'model-summary.json').read_text());base=json.loads((root/'capture-recovery-v2.json').read_text());allrows={}
 for rows in base['prior_attempt_rows'].values():
  for a in rows:allrows[a['root']]=dict(a)
 for r in before:
  for a in r['attempt_rows']:allrows[a['root']]=dict(a)
 for f in (root/'models-resume-v2').glob('*/g5-*-a*/attempt-result.json'):
  a=json.loads(f.read_text())
  if not a.get('native_started') and a.get('error'):a.update(harness_failure=True,harness_failure_reason='clean deployment drain before native start')
  allrows.setdefault(a['root'],a)
 bykey={pathlib.Path(a['root']).parent.parent.name+'/'+pathlib.Path(a['root']).name:a for a in allrows.values()};outcomes={};groups={};counts=dict(scanned_patches=0,patches_with_pyc=0,patches_with_binary_files_entries=0,patches_with_generated_artifacts=0,empty_ordinary_corrections=0,nonempty_regrades=0)
 # Include all live patches created while the archived scan was running.
 for phase in ('models','models-resume-v1','models-resume-v2'):
  for f in (root/phase).glob('*/g5-*-a*/model.patch'):
   key=phase+'/'+f.parent.name;d=auditdir/key;d.mkdir(parents=True,exist_ok=True);(d/'original.patch').write_bytes(f.read_bytes());audit['rows'].setdefault(key,dict(key=key,source=str(f)))
 for key,item in audit['rows'].items():
  raw=(auditdir/key/'original.patch').read_bytes();clean,p=project(raw);(auditdir/key/'cleaned.patch').write_bytes(clean);item.update(p,changed=raw!=clean,raw_sha256=sha(auditdir/key/'original.patch'),cleaned_sha256=sha(auditdir/key/'cleaned.patch'));counts['scanned_patches']+=1;counts['patches_with_pyc']+=bool(p['pyc_paths']);counts['patches_with_binary_files_entries']+=bool(p['binary_files_entries']);counts['patches_with_generated_artifacts']+=raw!=clean;a=bykey.get(key)
  if not a:continue
  if not clean.strip() and (raw!=clean or (not a.get('ended_on_5xx') and not a.get('harness_failure'))):
   d=root/'source-regrades-v1'/key;d.mkdir(parents=True,exist_ok=True);g=empty_result(a['task'],auditdir/key/'cleaned.patch');save(d/'grade-result.json',g);outcomes[key]=dict(result=g,grade_root=str(d),grade_sha256=sha(d/'grade-result.json'));counts['empty_ordinary_corrections']+=1
  elif raw!=clean:groups.setdefault(a['task'],[]).append(key)
 save(auditdir/'audit-final.json',dict(**counts,rows=audit['rows']));save(H/'patch-audit-summary.json',counts)
 if audit_only:print(counts,flush=True);return
 controls=json.loads((root/'controls-complete.json').read_text());template=json.loads((root/'grader-template.json').read_text());images=ModelImages(root,'source-regrade-image-leases');cost_before=sum(a['known_tokens_lower_bound'] for a in allrows.values())
 def issue(iid,keys):
  v=json.loads((root/controls['control_session']/iid/'final-control.json').read_text());lease=images.acquire_control_image(iid,v['image_lease']);plan=dict(template,images={iid:lease['image_id']},private_dataset=str(root/'dataset.json'),private_dataset_sha256=sha(root/'dataset.json'));planfile=root/'source-regrade-image-leases'/iid/'grader-plan.json';save(planfile,plan)
  def grade(key):
   d=root/'source-regrades-v1'/key;d.mkdir(parents=True,exist_ok=True);groot=d/'official';patch=auditdir/key/'cleaned.patch'
   with (d/'grader.log').open('xb') as log:p=subprocess.run(['/tmp/solpi-refinement-harbor-venv/bin/python',str(H/'grade_swe.py'),str(groot),iid,str(patch),str(planfile)],stdout=log,stderr=subprocess.STDOUT,timeout=950)
   f=groot/'grade-result.json'
   if p.returncode or not f.exists():raise RuntimeError('Deterministic regrade worker failed:'+key)
   g=json.loads(f.read_text());assert g['owned_containers_absent'];return key,dict(result=g,grade_root=str(groot),grade_sha256=sha(f))
  try:
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:return list(pool.map(grade,keys))
  finally:images.release(iid)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  fs=[pool.submit(issue,iid,keys) for iid,keys in groups.items()]
  for f in concurrent.futures.as_completed(fs):
   for key,value in f.result():outcomes[key]=value;counts['nonempty_regrades']+=1
   save(root/'source-regrades-v1/outcomes.json',outcomes);save(H/'patch-audit-summary.json',counts)
 for key,out in outcomes.items():
  a=bykey[key];g=out['result'];a['pre_source_regrade']={k:a.get(k) for k in ('solved','grade_valid','grader_sha256','patch_sha256')};a.update(solved=g['solved'],grade_valid=g['grade_valid'],graded_patch_sha256=g['patch_sha256'],grader_sha256=out['grade_sha256'],deterministic_regrade_root=out['grade_root'],source_regrade_model_calls=0,grader_owned_containers_absent=True)
 assert sum(a['known_tokens_lower_bound'] for a in allrows.values())==cost_before
 revised=[]
 for r in before:
  r=dict(r);r['attempt_rows']=[allrows[a['root']] for a in r['attempt_rows']];last=r['attempt_rows'][-1];r.update(solved=False if r.get('status')=='infra-exhausted' else last['solved'],grade_valid=last['grade_valid']);revised.append(r)
 done={r['cell_id'] for r in revised};prior={}
 for a in allrows.values():
  if a['cell_id'] not in done:prior.setdefault(a['cell_id'],[]).append(a)
 for rows in prior.values():rows.sort(key=lambda a:a['attempt'])
 save(root/'model-summary-before-source-regrade.json',before);save(root/'model-summary.json',revised);save(root/'source-regrades-v1/outcomes.json',outcomes);save(root/'source-regrade-recovery-v3.json',dict(retained_rows=revised,prior_attempt_rows=prior,last16_finished_attempts=[dict(cell_id=r['cell_id'],attempt=r['scored_attempt'],ended5xx=bool(r['attempt_rows'][-1].get('ended_on_5xx'))) for r in revised[-16:]],all_model_tokens_unchanged=True,no_model_calls=True,source_audit_sha256=sha(auditdir/'audit-final.json'),counts=counts));save(H/'patch-audit-summary.json',dict(**counts,retained_cells=len(revised),known_tokens_unchanged=True,model_calls=0));print('Source/empty regrades done',counts,flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--operation-commit');args=p.parse_args();main(args.audit_only,args.operation_commit)
