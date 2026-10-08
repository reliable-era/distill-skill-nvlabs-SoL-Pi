"""Standing-authorized calibration recovery; no completed model-task reruns."""
import datetime, json, pathlib, subprocess, sys
import run_calibration_continuation as C
G=C.G
E=G/'calibration-recovery'
E.mkdir(exist_ok=True)
BASE_POOL=set(json.loads((G/'calibration-continuation/window-close-decision-audit.json').read_text())['screening_pool'])


def contract():
    physical=json.loads((G/'calibration-contract.json').read_text())
    by={t['id']:t for t in physical['development_pool']}
    # Food-chain is the primary zero-model cell. SPARQL is the separately
    # authorized single retry of an infrastructure-interrupted model attempt.
    physical['development_pool']=[by['go/exercises/practice/food-chain'],by['sparql-university']]+C.FALLBACK
    return physical


def window_end():
    value=subprocess.check_output(['git','log','-1','--format=%H|%cI','--','calibration-recovery-window.md'],cwd=G,text=True,timeout=20).strip()
    if not value:raise RuntimeError('Recovery window not committed')
    commit,stamp=value.split('|',1);start=datetime.datetime.fromisoformat(stamp);end=start+datetime.timedelta(hours=4)
    record={'window_commit':commit,'window_start':start.isoformat(),'window_end':end.isoformat(),'latest_start':(end-datetime.timedelta(hours=2)).isoformat()}
    path=E/'calibration-window.json'
    if path.exists() and json.loads(path.read_text())!=record:raise RuntimeError('Existing window cannot be renewed')
    path.write_text(json.dumps(record,indent=2)+'\n')
    return end.timestamp()


def controller():
    base=C.make_controller(primary_count=2,driver_path=__file__)
    base.E=E;base.load_contract=contract;base.window_end=window_end;base.PRIOR_SOLVED=BASE_POOL
    return base


def finalize(base):
    result=json.loads((E/'calibration-result.json').read_text())
    valid=[r for r in result['rows'] if r.get('provider_POST',0)>0]
    pool=sorted(BASE_POOL|{r['task'] for r in valid if r.get('solved') is True})
    hits=[r['task'] for r in valid if r['provider_POST']>=60 or r.get('actor_deadline_interrupted') or r.get('actor_seconds',0)>=7190]
    clean=not result['error'] and not result['cleanup_errors'] and result['owned_containers_absent']
    accounting=all(r.get('cost_complete') for r in valid)
    all_started_valid=all(r.get('provider_POST',0)>0 and 'grade_error' not in r for r in result['rows'] if 'native_exit' in r)
    base.save(E/'recovery-decision.json',{'screening_pool':pool,'gate_pass':len(pool)>=3 and clean and accounting and all_started_valid and not hits,'cap_hits':hits,'accounting_complete':accounting,'startup_or_grade_failures':[r['task'] for r in result['rows'] if 'native_exit' in r and (not r.get('provider_POST') or 'grade_error' in r)],'new_provider_requests':result['POST'],'new_complete_tokens':sum(r.get('provider_tokens_lower_bound',0) for r in valid),'error':result['error'],'scope':'Step 3 only; historical attempts preserved; no savings or promotion claim','next':'Audit and commit Step 3, then proceed through authorized Steps 4–9 if gate passes. Otherwise distinguish routine infrastructure repair/window boundary from an actually tested insufficient pool.'})

if __name__=='__main__':
    base=controller();base.main();finalize(base)
