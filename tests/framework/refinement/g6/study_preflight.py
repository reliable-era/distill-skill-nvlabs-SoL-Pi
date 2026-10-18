"""Non-secret study-budget evidence and zero-admission paused analysis.
This branch deliberately refuses to overwrite/report zero if study work exists.
"""
import datetime,json,time
from common import H,private_root,prereg,save,sha,check_frozen
from study_policy import forecast,RESET

def current_budget():
    if list((private_root()/'study').rglob('native.jsonl')):raise RuntimeError('Study data exists;replay actual study observations/remaining-N before continuation,not the old smoke snapshot')
    summary=json.loads((H/'smoke-explicit-v2-summary.json').read_text());observations={}
    for row in summary['runs']:
        for scope,value in (row.get('quota_after') or {}).items():
            if 'seven_day' in scope and value.get('utilization') is not None:
                item=(value['observed_epoch'],value['utilization'],scope)
                if scope not in observations or item[0]>observations[scope][0]:observations[scope]=item
    if not observations:raise RuntimeError('No actual weekly utilization evidence;do not probe with inference')
    observed,u,scope=max(observations.values(),key=lambda x:x[1]);result=forecast(u,300)
    result.update(evaluated_epoch=time.time(),actual_observation_epoch=observed,actual_observation_age_seconds=time.time()-observed,actual_scope=scope,smoke_summary_sha256=sha(H/'smoke-explicit-v2-summary.json'))
    return result

def main():
    p=check_frozen();root=private_root();assert not list((root/'study').rglob('attempt-progress.json'));assert not list((root/'study').rglob('native.jsonl'));assert not (root/'study-launch.json').exists()
    budget=current_budget();assert not budget['admissions_allowed'],'This report generator only handles the blocked zero-admission branch'
    evidence=dict(status='PAUSED before controller/credential/Docker/model work',supervisor_go_received=True,budget=budget,study_issues_fixed=150,study_cells_fixed=300,study_calls=0,study_attempts=0,completed_pairs=0,unstarted_cells=300,study_tokens=0,credential_access=False,remote_model_or_quota_probe_calls=0,sample_binding_sha256=p['amendment_explicit_v2']['sample_binding_sha256'],prior_smoke_costs_separate=True,prior_smoke_reported_tokens=812369)
    save(root/'study-budget-preflight.json',evidence);save(root/'STUDY-ADMISSIONS-PAUSED.json',dict(reason='Remaining-N forecast cannot fit current plus next weekly window with all existing guards',study_calls=0,N_unchanged=True,preflight_sha256=sha(root/'study-budget-preflight.json')))
    save(H/'study-budget-summary.json',evidence)
    undefined=dict(value=None,reason='No admitted study cells or complete study pairs;not zero effect/zero solve rate')
    analysis=dict(status='incomplete;quota preflight pause',target_issues=150,target_cells=300,admitted_cells=0,complete_pairs=0,unstarted_cells=300,unstarted_are_not_model_failures=True,arms={arm:dict(target=150,admitted=0,known_grades=0,solved=None,solve_rate=None,tokens=0,tokens_per_solve=None) for arm in ('none','ours')},paired_solve_difference=undefined,paired_bootstrap_95_ci=undefined,bootstrap_seed=p['analysis']['bootstrap_seed'],bootstrap_draws_planned=20000,bootstrap_draws_executed=0,exact_mcnemar_p=undefined,discordant_counts=None,paired_token_per_solve_ratio=undefined,paired_cache_adjusted_proxy_ratio=undefined,no_missing_usage_or_quality_imputation=True,no_smoke_quality_pooling=True,no_new_study_costs=True,prior_smoke_volume_separate=812369,contamination_not_ruled_out=True)
    save(H/'study-results.json',analysis);print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
