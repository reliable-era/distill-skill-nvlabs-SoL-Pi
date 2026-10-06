"""Finite window-close audit; never launches an actor or contacts a server."""
import datetime, hashlib, json, pathlib, time
G=pathlib.Path(__file__).resolve().parent
E=G/'calibration-continuation'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    window=json.loads((E/'calibration-window.json').read_text());result=json.loads((E/'calibration-result.json').read_text());root=pathlib.Path(result['root'])
    inputs={p:sha(E/p) for p in ['calibration-window.json','calibration-result.json','aider-startup-failure-audit.json']}
    deadline=datetime.datetime.fromisoformat(window['window_end']).timestamp()
    wait={'status':'WAIT_UNTIL_AUTHORIZED_WINDOW_END','until':window['window_end'],'model_POST':0,'server_polling':False,'locked_inputs':inputs}
    (E/'window-close-wait.json').write_text(json.dumps(wait,indent=2)+'\n')
    time.sleep(max(0,deadline-time.time()))
    assert all(sha(E/p)==value for p,value in inputs.items()), 'Input changed; do not freeze'
    raw=json.loads((root/'transport/ledger.json').read_text());derived=json.loads((root/'transport/prospective-ledger.json').read_text())['records']
    assert raw['provider_POST']==len(raw['records'])==len(derived)==71
    assert all(r['provider_backend']=='127.0.0.1:18001' and r['stream_eof'] and r['provider_status']==200 and r['error'] is None for r in raw['records'])
    assert all(r['accounting_view']['derived_cost']['provider_cost_complete'] for r in derived)
    assert not result['cleanup_errors'] and result['owned_containers_absent'] and result['error'] is None
    hits=[task for task,count in raw['per_actor'].items() if count>=60]
    hits+=[r['task'] for r in result['rows'] if r.get('actor_deadline_interrupted') or r.get('actor_seconds',0)>=7190]
    hits+=[r['actor'] for r in raw['local_budget_denials'] if r['reason'] in ('per_actor_POST_cap','actor_deadline_reserve')]
    startup=json.loads((E/'aider-startup-failure-audit.json').read_text())
    assert all(raw['per_actor'][r['task']]==0 for r in startup['failed_launches'])
    prior=json.loads((G/'calibration-attempt-2/calibration-summary-audit.json').read_text())
    valid=[r for r in result['rows'] if r.get('provider_POST',0)>0]
    pool=sorted({r['task'] for r in prior['rows'] if r['solved'] is True}|{r['task'] for r in valid if r['solved'] is True})
    report={'status':'INCONCLUSIVE_SCREENING_POOL_INSUFFICIENT_WITH_STARTUP_FAILURES','closed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'window_end':window['window_end'],'cap_hits':sorted(set(hits)),'budget_frozen':not hits,'frozen_budget':{'requests':60,'wall_seconds':7200,'output_tokens':16384} if not hits else None,'freeze_basis':'User-authorized nominal budget rule at window end; cap checks and complete provider accounting. Not proof that this budget prevents model or harness failures.','model_runs_new':len(valid),'failed_startup_attempts':len(startup['failed_launches']),'failed_startup_tasks':[r['task'] for r in startup['failed_launches']],'provider_requests_new':71,'provider_tokens_new':sum(r['accounting_view']['derived_cost']['gross_tokens'] for r in derived),'zero_request_startup_cost_known_zero':True,'unknown_provider_costs':0,'screening_pool':pool,'step_3_complete':False,'g1_complete':False,'quality_caveat':'Six tasks never reached Codex. Their starter grades are not model-quality observations; failure to reach a three-task pool cannot establish model inability to separate skills.','no_task_retry_or_server_change':True,'no_step_4':True,'confirmation_rule_unchanged':True,'sealed_samples_untouched':True,'inputs_sha256':inputs}
    (E/'window-close-decision-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
