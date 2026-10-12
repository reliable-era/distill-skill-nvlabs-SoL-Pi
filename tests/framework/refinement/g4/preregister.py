"""Build all-parts G4 freeze before ANY provider call. No inference here.
Blocked A remains explicit, no invented activation/compatibility/receipts.
B/C retain full queues and exclude only recorded control failures.
"""
import hashlib,json,pathlib,subprocess
H=pathlib.Path(__file__).resolve().parent
R=H.parents[3]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def tree(root):return {str(p.relative_to(root)):({'symlink':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(root.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}
def main():
 output=H/'preregistration.json'
 if output.exists():raise RuntimeError('Existing freeze; verify, never overwrite')
 protected=json.loads((H/'protected-baseline.json').read_text())
 for p,d in protected['protected'].items():assert sha(R/p)==d
 for p,d in protected['unrelated_nginx'].items():assert sha(R/'tests/framework/refinement/pi-takeover/qwen-load-balancer'/p)==d
 repaired=json.loads((H/'B-python-result.json').read_text());assert repaired['all5_valid'];smoke=json.loads((H/'actor-startup-smoke-uid0-result.json').read_text());assert smoke['passed'] and smoke['owned_container_absent'];g=json.loads((H/'C-grade-smoke-result.json').read_text());assert g['passed']
 b=json.loads((H/'B-eligibility.json').read_text());base={t['task']:t for t in json.loads((H/'B-images.json').read_text())['rows']};bt={t['task']:dict(base[t['task']],**{k:v for k,v in t.items() if k not in base[t['task']]},image_id=t['image_id']) for t in b['rows']}
 for t in repaired['rows']:
  assert t['valid_pair'] and t['prepare_container_absent'];bt[t['task']]['image_id']=t['image_id'];bt[t['task']]['gold_original_test_events']=next(c['test_events'] for c in t['pair']['controls'] if c['mode']=='gold')
 c=json.loads((H/'C-eligibility.json').read_text());eligibleC=[t['task'] for t in c['rows'] if t['eligible']];source=json.loads((H/'C-prepared-sources.json').read_text());assert source['all30_prepared'];cp=json.loads((H/'C-controls-offline-plan.json').read_text());s=json.loads((H/'selection.json').read_text());order=json.loads((H/'queue-order.json').read_text());assert [len(order['parts'][p]) for p in ('A','B','C')]==[74,108,120]
 skills={}
 for name,path in [('ours',R/'skills/efficient-coding'),('K',R/'tests/framework/refinement/g2/frozen/karpathy')]:skills[name]=dict(path=str(path),SKILL_sha256=sha(path/'SKILL.md'),tree=tree(path))
 assert skills['ours']['SKILL_sha256']==s['ours_sha256'];assert skills['K']['SKILL_sha256']=='6e22cc54cb02a5e98ae42d06d9d7292db0c1b43894831b32879beb0166b2aea7'
 images={r['task']:r['image_id'] for r in c['rows']}
 for image in set(images.values())|{t['image_id'] for t in bt.values()}:assert json.loads(subprocess.check_output(['docker','image','inspect',image],timeout=20))[0]['Id']==image
 a=json.loads((H/'A-config-provenance.json').read_text());assert a['upstream_source_unmodified'] and a['model_calls']==0 and not a['config_loaded'];assert not subprocess.check_output(['git','-C','/tmp/solpi-g4-upstream','status','--short'],text=True).strip()
 a_inputs=dict(diagnostics_tree=tree(pathlib.Path(s['part_A']['synthetic_fixture_root'])),upstream_package_sha256=sha(pathlib.Path('/tmp/solpi-g4-upstream/package.json')),upstream_lock_sha256=sha(pathlib.Path('/tmp/solpi-g4-upstream/package-lock.json')),validation_sha256=sha(H/'upstream-validation-result.json'),original_SWE_dataset_sha256=sha(R/'tests/eval/swebench_verified.jsonl'),tasks=s['part_A'],primary_helper_capture_runtime='Not implemented because mandatory source security prerequisite failed; no A call authorized',caps={'turns':60,'seconds':1800})
 plan=dict(contract='5b8e715',full_preregistration=True,route='127.0.0.1:8000',shared_slots=16,model_policy=s['model_policy'],runtime_hashes={str(p):sha(p) for p in H.glob('*.py')},input_hashes={str(H/f):sha(H/f) for f in ('selection.json','queue-order.json','protected-baseline.json','B-eligibility.json','B-python-result.json','C-eligibility.json','C-controls-offline-plan.json','C-prepared-sources.json','historical-A.json','sol-pi.full-stack.json','A-config-provenance.json')},skills=skills,arm_skills={'none':[],'K':['K'],'ours':['ours'],'Both':['K','ours']},eligible_tasks={'B':list(bt),'C':eligibleC,'A':[]},images=images,terminal_tasks=bt,terminal_source='/tmp/solpi-refinement-terminal-bench-2',prepared_tasks={r['task']:r['private_root'] for r in source['rows']},wheelhouse=cp['wheelhouse'],wheel_sha256=cp['wheel_sha256'],grader_plan=str(H/'C-controls-offline-plan.json'),grader_python='/tmp/solpi-refinement-harbor-venv/bin/python',caps=s['BC_caps'],queue_order_sha256=sha(H/'queue-order.json'),all_planned_cells=302,eligible_B_cells=108,eligible_C_cells=4*len(eligibleC),A=dict(planned_cells=74,frozen_inputs=a_inputs,source_config=a,status='PREPARATION_BLOCKED_REQUIRED_SECURITY_AUDIT_NOT_ROUTE_TESTED',inference_authorized=False,historical_reuse=True,unknown_new_scores_costs=True),descriptive_analysis=dict(source_sha256=sha(H/'analyze.py'),seeds=s['bootstrap_seeds'],draws=20000,no_gate=True,no_early_stop=True,undefined_draws_retained=True,unknown_costs_no_imputation=True),model_calls_before_freeze=0,source_protection=protected)
 output.write_text(json.dumps(plan,indent=2)+'\n');print('All-parts freeze written; commit before any inference or model compatibility probe')
if __name__=='__main__':main()
