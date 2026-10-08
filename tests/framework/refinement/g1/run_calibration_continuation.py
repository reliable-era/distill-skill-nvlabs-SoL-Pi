"""Authorized pending-task continuation; existing runs and sealed tasks untouched."""
# Load standard-library dependencies before adding the archive helper path.
import datetime, hashlib, http.client, json, pathlib, shutil, ssl, subprocess, sys, tarfile, time, types
G = pathlib.Path(__file__).resolve().parent
E = G / 'calibration-continuation'
E.mkdir(exist_ok=True)
PRIOR = json.loads((G/'calibration-attempt-2/calibration-summary-audit.json').read_text())
FALLBACK = json.loads((G/'calibration-fallback-fixtures.json').read_text())['fixtures']
PRIOR_SOLVED = {r['task'] for r in PRIOR['rows'] if r['solved'] is True}


def window_end():
    # The committing timestamp, not preparation time, starts the new window.
    value = subprocess.check_output(['git','log','-1','--format=%H|%cI','--','calibration-decision-amendment.md'],cwd=G,text=True,timeout=20).strip()
    if not value: raise RuntimeError('Decision amendment not committed; no model calls')
    commit, stamp = value.split('|',1)
    start = datetime.datetime.fromisoformat(stamp)
    end = start + datetime.timedelta(hours=4)
    record = {'amendment_commit':commit,'window_start':start.isoformat(),'window_end':end.isoformat(),'latest_start':(end-datetime.timedelta(hours=2)).isoformat()}
    path=E/'calibration-window.json'
    if path.exists() and json.loads(path.read_text()) != record: raise RuntimeError('Window metadata changed; no renewal')
    path.write_text(json.dumps(record,indent=2)+'\n')
    return end.timestamp()


def load_contract():
    physical=json.loads((G/'calibration-contract.json').read_text())
    pending=physical['pending_primary_ids']
    assert set(pending)==set(PRIOR['rows'][i]['task'] for i in range(len(PRIOR['rows'])) if not PRIOR['rows'][i]['started'])
    assert not set(pending).intersection(r['task'] for r in PRIOR['rows'] if r['started'])
    by={t['id']:t for t in physical['development_pool']}
    physical['development_pool']=[by[ident] for ident in pending]+FALLBACK
    return physical


def fixture_spec(ident, base):
    extra=next((r for r in FALLBACK if r['id']==ident),None)
    image=extra['image_id'] if extra else base.S.IMAGE
    return {'actor_image_id':image,'grader_image_id':image,'cpus':1,'memory_mb':2048,'mounts':[],'environment':{},'guidance':''}


def grade_fixture(base, ident, work, prepared, d, prefix, owned, spec, row):
    grade=prefix+'-polyglot-grade';owned.append(grade)
    args=['create','--pull=never','--name',grade,'--network','none','--cpus','1','--memory','2g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,exec,size=1g','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','-e','GOPROXY=off','-e','GOSUMDB=off','-e','GOTOOLCHAIN=local','-v',str(work)+':/workspace:ro','-v',str(prepared/'grader')+':/grader:ro']
    if ident.startswith('javascript/'):
        args+=['-v','/tmp/solpi-g1-js-deps:/npm-install:ro']
    base.docker(*args,'--entrypoint','python3',spec['grader_image_id'],'/grader/grade.py')
    with (d/'verifier.log').open('wb') as out:
        result=subprocess.run(['docker','start','-a',grade],stdout=out,stderr=subprocess.STDOUT,timeout=240)
    base.docker('rm',grade);owned.remove(grade)
    if not base.absent(grade):raise RuntimeError('Owned fixture grader cleanup uncertain')
    row.update(verifier_exit=result.returncode,solved=result.returncode==0 if result.returncode in (0,1) else None)
    if result.returncode not in (0,1):raise RuntimeError('Original fixture grader unavailable')


def make_controller(primary_count=5, driver_path=None):
    source=G/'run_calibration.py';code=source.read_text()
    def replace(old,new):
        nonlocal code
        if code.count(old)!=1:raise RuntimeError('Continuation replacement is not unique: '+old[:80])
        code=code.replace(old,new)
    replace("E = G / 'calibration-attempt-2'", "E = G / 'calibration-continuation'")
    replace("contract = json.loads((G/'calibration-contract.json').read_text())", "contract = load_contract()")
    replace("end = datetime.datetime.fromisoformat(contract['window_end']).timestamp()", "end = window_end()")
    replace("            if time.monotonic()+7200>deadline:break\n            ident=task['id'];", f"            if time.monotonic()+7200>deadline:break\n            if index>={primary_count} and len(PRIOR_SOLVED)+sum(r.get('solved') is True for r in rows)>=3:break\n            ident=task['id'];")
    replace("manifest=polyglot.prepare('/tmp/solpi-polyglot-grader-source',ident,prepared)", "manifest=fallback_prepare('/tmp/solpi-polyglot-grader-source',ident,prepared)")
    replace("spec={'actor_image_id':S.IMAGE,'grader_image_id':S.IMAGE,'cpus':1,'memory_mb':2048,'mounts':[],'environment':{},'guidance':''}", "spec=fixture_spec(ident,controller)")
    # Prepared workspaces and CODEX_HOME are root-owned. Aider images default
    # to a non-root login user; preserve isolation/caps but select the intended
    # container-only root identity, as used by the Terminal task images.
    replace("            args+=docker_options(spec);argv=A.argv('codex',8000,d)", "            if task['family']=='aider-polyglot':args[1:1]=['--user','0:0']\n            args+=docker_options(spec);argv=A.argv('codex',8000,d)")
    old_start="                    grade=prefix+'-go-grade';owned.append(grade)"
    start=code.index(old_start)
    end=code.index("            except Exception as e:row['grade_error']",start)
    code=code[:start]+"                    grade_fixture(controller,ident,work,prepared,d,prefix,owned,spec,row)\n"+code[end:]
    replace("'budget_pass':sum(r.get('solved') is True for r in rows)>=5 and not cleanup_errors", "'budget_pass':False,'budget_policy':'Decision amendment; evaluated independently after accounting and cap audit'")
    replace("            if sources()!=live or W.files(task['source'])!=plan['task_source_hashes'][ident]:raise RuntimeError('Source identity changed')", "            if any(sha(G/name)!=value for name,value in plan['continuation_sources'].items()):raise RuntimeError('Continuation source changed')\n            if sources()!=live or W.files(task['source'])!=plan['task_source_hashes'][ident]:raise RuntimeError('Source identity changed')")
    driver_entries=[G/'run_calibration_continuation.py',G/'calibration_fallback_adapter.py']+([pathlib.Path(driver_path)] if driver_path else [])
    replace("    plan['launch_commit'] =", "    plan['prior_summary_sha256']=sha(G/'calibration-attempt-2/calibration-summary-audit.json')\n    plan['fallback_manifest_sha256']=sha(G/'calibration-fallback-fixtures.json')\n    plan['continuation_sources']={p.name:sha(p) for p in driver_entries}\n    plan['launch_commit'] =")
    module=types.ModuleType('g1_pending_calibration')
    module.__file__=str(source)
    module.__dict__.update(load_contract=load_contract,window_end=window_end,fixture_spec=fixture_spec,grade_fixture=grade_fixture,PRIOR_SOLVED=PRIOR_SOLVED,driver_entries=driver_entries)
    exec(compile(code,'<G1 committed continuation>','exec'),module.__dict__)
    from calibration_fallback_adapter import prepare
    module.fallback_prepare=prepare;module.controller=module
    return module


def finalize(base):
    path=E/'calibration-result.json'
    if not path.exists():raise RuntimeError('Continuation lacks a terminal report')
    result=json.loads(path.read_text());root=pathlib.Path(result['root']);raw=json.loads((root/'transport/ledger.json').read_text())
    hits=[]
    for row in result['rows']:
        if row.get('provider_POST',0)>=60 or row.get('actor_deadline_interrupted') or row.get('actor_seconds',0)>=7190:
            hits.append(row['task'])
    hits.extend(task for task,count in raw['per_actor'].items() if count>=60)
    for denial in raw['local_budget_denials']:
        if denial['reason'] in ('per_actor_POST_cap','actor_deadline_reserve'):hits.append(denial['actor'])
    pool=sorted(PRIOR_SOLVED|{r['task'] for r in result['rows'] if r.get('solved') is True})
    pending=set(json.loads((G/'calibration-contract.json').read_text())['pending_primary_ids'])
    completed={r['task'] for r in result['rows'] if 'native_exit' in r}
    # If primary tasks remain at the clean latest-start boundary, only freeze at
    # the explicitly authorized window end. This timer makes no server calls.
    if pending-completed and not result['error'] and not hits:
        remaining=window_end()-time.time()
        if remaining>0:
            base.save(E/'window-boundary-wait.json',{'until':datetime.datetime.fromtimestamp(window_end(),datetime.timezone.utc).isoformat(),'reason':'Primary tasks remain; no full 120-minute run fits; no polling or model calls'})
            time.sleep(remaining)
    costs_known=all(r.get('cost_complete') for r in result['rows'] if 'native_exit' in r)
    clean=not result['cleanup_errors'] and result['owned_containers_absent'] and not result['error']
    frozen=not hits and costs_known and clean
    summary={'cap_hits':sorted(set(hits)),'budget_frozen':frozen,'frozen_budget':{'requests':60,'wall_seconds':7200,'output_tokens':16384} if frozen else None,'screening_pool':pool,'step_3_complete':frozen and len(pool)>=3,'disposition':'Report G1 inconclusive if fewer than three solvable development tasks; never savings achievement','prior_cohort':str(G/'calibration-attempt-2/calibration-summary-audit.json'),'new_native_starts':result['starts'],'new_provider_requests':result['POST'],'new_tokens_lower_bound':sum(r.get('provider_tokens_lower_bound',0) for r in result['rows']),'new_costs_complete':costs_known,'remaining_primary':sorted(pending-completed),'fallback_executed':[r['task'] for r in result['rows'] if r['task'] in {f['id'] for f in FALLBACK} and 'native_exit' in r],'error':result['error'],'window_extended':False,'no_candidate_calls':True,'confirmation_floor_risk':'Terminal-Bench confirmation may be inconclusive under unchanged B3(a); Aider cannot replace its separate acceptance gate'}
    base.save(E/'decision-summary.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    controller=make_controller()
    controller.main()
    finalize(controller)
