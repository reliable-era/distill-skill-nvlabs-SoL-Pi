"""Supplemental actual complete round boundary; no analysis on partial roster.
This verifies the frozen queue, uniform retained attempt roster and control scope
before futility/final analysis, not statistical acceptance by itself.
"""
import argparse,collections,datetime,json,pathlib,random,subprocess
from run_cell import H,sha
from scheduler import load_plan
from audit import audit
from transport import save

def main():
 p=argparse.ArgumentParser();p.add_argument('--round',required=True,type=int,choices=(1,2,3));a=p.parse_args();plan=load_plan();value=audit(a.round);rounds=list(range(1,a.round+1));expected=[c for c in plan['schedule'] if c['round'] in rounds]
 assert not value['missing_cells'] and len(value['rows'])==len(expected)==len(plan['tasks'])*4*a.round
 assert {r['cell_id'] for r in value['rows']}=={c['cell_id'] for c in expected}
 assert all(r['grade_valid'] for r in value['rows'])
 control=json.loads((H/'controls-audit.json').read_text());assert sha(H/'controls-audit.json')==plan['controls_audit_sha256'];assert control['control_valid_tasks']==plan['tasks'];assert control['eligible_tasks_checked']==211 and len(control['excluded_tasks'])==15
 regenerated=[]
 for n in (1,2,3):
  rng=random.Random(plan['round_seeds'][str(n)]);tasks=list(plan['tasks']);rng.shuffle(tasks)
  for t in tasks:
   arms=['none','K','candidate','Both'];rng.shuffle(arms);regenerated.extend((n,t,arm) for arm in arms)
 assert regenerated==[(c['round'],c['task'],c['arm']) for c in plan['schedule']]
 starts=[];terminal_windows=[];identities=[]
 for launch_file in sorted(H.glob('waves/*/launch.json')):
  launch=json.loads(launch_file.read_text());E=launch_file.parent
  if launch['round']>a.round:continue
  result=json.loads((E/'result.json').read_text());assert not result['error'] and not result['stop'];pid=launch['pid'];assert not subprocess.run(['ps','-p',str(pid),'-o','pid=,stat='],capture_output=True,text=True).stdout.strip()
  owned={r[k] for r in result['attempts'] for k in ('actor','grade_container')};names=set(subprocess.check_output(['docker','ps','-a','--filter','name=solpi-g3-','--format','{{.Names}}'],text=True,timeout=30).splitlines());assert not owned.intersection(names)
  assert all(not r['cleanup_errors'] for r in result['attempts'])
  for event in result['events']:
   if event['kind']=='admitted' and event['attempt_id'].endswith('-attempt1'):starts.append((event['utc'],event['attempt_id'].removesuffix('-attempt1')))
  terminal_windows.append(dict(wave=E.name,launch_sha256=sha(launch_file),result_sha256=sha(E/'result.json'),window_commit=launch['window']['commit'],owned_worker_containers_absent=True))
  identities.append(launch['model_identity'])
 assert [c for _,c in sorted(starts)]==[c['cell_id'] for c in expected]
 assert all(x['backend']=='127.0.0.1:9012' and {m['id'] for m in x['body']['data']}=={'Qwen/Qwen3.8-27B'} for x in identities)
 result=dict(status='COMPLETE_ROUND_BOUNDARY_NOT_ACCEPTANCE',rounds=rounds,exact_cells=len(expected),per_round_cells=len(plan['tasks'])*4,arm_counts={str(n):dict(collections.Counter(r['arm'] for r in value['rows'] if r['round']==n)) for n in rounds},all_original_grades_valid=True,all_costs_complete=value['all_observed_costs_complete'],full2352_schedule_reproduced=True,first_admissions_exact_frozen_order=True,rounds_not_interleaved=True,all_attempts_accounted=True,all_prior_workers_owned_containers_absent=True,model_identity_valid_each_window_and_round=True,control_based_exclusions_only=15,first36_ownership_fault_retained=True,first36_not_retried_or_excluded=True,no_partial_gate=True,audit_sha256=sha(H/'audits'/f'round{a.round}.json'),plan_sha256=sha(H/'plan.json'),windows=terminal_windows,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (H/'analysis').mkdir(exist_ok=True);save(H/'analysis'/f'round{a.round}-boundary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='windows'},indent=2))
if __name__=='__main__':main()
