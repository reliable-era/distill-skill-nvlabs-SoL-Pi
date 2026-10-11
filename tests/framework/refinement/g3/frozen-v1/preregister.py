"""Generate G3 full committed schedule/analysis/runtime/controls freeze; no POST."""
import hashlib,json,pathlib,random,subprocess
from run_cell import H,tree,sha,BINARY,BINARY_SHA

def main():
 assert not (H/'plan.json').exists();audit=json.loads((H/'controls-audit.json').read_text());tasks=audit['control_valid_tasks'];assert len(tasks)==196
 rows={r['task']:r for r in json.loads((H/'controls-result.json').read_text())['rows']};rows.update({r['task']:r for r in json.loads((H/'controls-repair-result.json').read_text())['rows']});assert all(rows[t]['valid_pair'] for t in tasks)
 skills={key:dict(path=str(H.parent/'g2/frozen'/key),tree=tree(H.parent/'g2/frozen'/key)) for key in ('candidate','karpathy')};assert skills['candidate']['tree']['SKILL.md']=='39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25'
 seeds={str(n):2026101100+n*100 for n in (1,2,3)};schedule=[]
 for n in (1,2,3):
  rng=random.Random(seeds[str(n)]);ordered=list(tasks);rng.shuffle(ordered)
  for task in ordered:
   arms=['none','K','candidate','Both'];rng.shuffle(arms)
   for arm in arms:schedule.append(dict(cell_id=f'g3-r{n}-t{tasks.index(task)}-{arm}',task=task,round=n,arm=arm))
 repo=pathlib.Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=H,text=True).strip());protected={}
 tracked=subprocess.check_output(['git','ls-files','tests/framework/refinement/g1','tests/framework/refinement/g2','skills/efficient-coding','README.md','tests/framework/benchmarks'],cwd=repo,text=True).splitlines()
 for name in tracked:
  p=repo/name
  if p.is_file():protected[str(p)]=sha(p)
 names=['analyze.py','test_analyze.py','transport.py','test_transport.py','relay.py','run_cell.py','scheduler.py','test_scheduler.py','audit.py','preregister.py']
 plan=dict(contract_commit='68cff75',tasks=tasks,eligible_before_controls=211,controls_exclusions=audit['excluded_tasks'],controls_audit_sha256=sha(H/'controls-audit.json'),arms=['none','K','candidate','Both'],arm_skills={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']},skills=skills,round_seeds=seeds,bootstrap_seed=2026101111,bootstrap_repetitions=20000,schedule=schedule,primary_runs_per_round=784,primary_runs_maximum=2352,images=json.loads((H/'controls-plan.json').read_text())['images'],prepared_tasks={t:rows[t]['private_preparation'] for t in tasks},grader_trees={t:tree(pathlib.Path(rows[t]['private_preparation'])/'grader') for t in tasks},starter_trees={t:tree(pathlib.Path(rows[t]['private_preparation'])/'workspace') for t in tasks},prompt_sha256={t:sha(pathlib.Path(rows[t]['private_preparation'])/'prompt.txt') for t in tasks},source_revision='7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f',binary_sha256=BINARY_SHA,model='Qwen/Qwen3.8-27B',route='127.0.0.1:9012',max_slots=18,caps={'requests':60,'wall_seconds':7200,'output_tokens':16384},window={'duration_hours':4,'latest_start_hours':2},retry_rule='one rerun from scratch only never-model or9012 refused/reset; not caps/model errors; both attempt records and all costs included; terminal solve determined by last eligible attempt',scheduling='primary dispatch in frozen adjacent-arm order; admission serialized in dispatch order, all9012 waiting ranks zero,18 allocated run slots; uniform retries retain same slot and may admit between primary admissions; no rounds interleave',unknown_cost_rule='no imputation; finite conservative upper surrogate only if numerator arm costs complete, unknown denominator lower bound authorized; exact/surrogate intervals labeled; unknown numerator blocks cost acceptance',futility='after complete round1 negative if candidate/none or candidate/K point not≤.95 or fewer solves than either; no early success; unverifiable evidence inconclusive',acceptance='all3 required candidate/none,Both/K,candidate/K point≤.95,paired95% upper<1,no fewer solves; candidate/Both informational only',protected_files=protected,implementation_sha256={n:sha(H/n) for n in names},no_shipping=True,no_README_change=True,no_push=True,model_calls_at_freeze=0)
 assert sha(BINARY)==BINARY_SHA and len(schedule)==2352
 (H/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print('Full G3 plan generated:2352 primary cells;3 independent adjacent-arm queues; frozen control/private fixtures and runtime hashes')
if __name__=='__main__':main()
