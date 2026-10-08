"""Preregistered G1 matched screen; one committed bounded wave per invocation."""
import datetime, hashlib, json, pathlib, shutil, subprocess, sys
import run_calibration as R
import run_calibration_continuation as C
G=C.G
PLAN=G/'mechanisms/candidate-1-screen-plan.json'
wave=int(sys.argv[1]) if __name__=='__main__' else 1
E=G/('screen-candidate-1-wave-'+str(wave))
ARMS={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']}


def contract():
    plan=json.loads(PLAN.read_text());v=json.loads((G/'calibration-contract.json').read_text());by={t['id']:t for t in v['development_pool']}
    v['arms']=list(ARMS);v['phase']='G1 Step 5 matched development screen; no confirmation'
    if hashlib.sha256((G/'mechanisms/html-public-wheels.json').read_bytes()).hexdigest()!=plan['html_public_wheels_sha256']:raise RuntimeError('HTML wheel manifest changed')
    v['development_pool']=[{**by[cell['task']],'arm':cell['arm'],'cell_id':cell['cell_id']} for cell in plan['schedule'] if cell['wave']==wave]
    assert len(v['development_pool'])==6
    return v


def window_end():
    marker='candidate-1-wave-'+str(wave)+'-window.md'
    value=subprocess.check_output(['git','log','-1','--format=%H|%cI','--',marker],cwd=G,text=True,timeout=20).strip()
    if not value:raise RuntimeError('Screen window not committed')
    commit,stamp=value.split('|',1);start=datetime.datetime.fromisoformat(stamp);end=start+datetime.timedelta(hours=4)
    record={'window_commit':commit,'window_start':start.isoformat(),'window_end':end.isoformat(),'latest_start':(end-datetime.timedelta(hours=2)).isoformat(),'wave':wave}
    path=E/'screen-window.json'
    if path.exists() and json.loads(path.read_text())!=record:raise RuntimeError('No implicit window renewal')
    path.write_text(json.dumps(record,indent=2)+'\n');return end.timestamp()


def screen_prompt(instruction,spec,task,d):
    plan=json.loads(PLAN.read_text())
    if spec!=plan['task_resource_specs'][task['id']]:raise RuntimeError('Frozen task resources changed')
    for key in ARMS[task['arm']]:
        source=pathlib.Path(plan['skills'][key]['path'])
        if R.W.files(source)!=plan['skills'][key]['tree_hashes']:raise RuntimeError('Frozen skill tree changed')
        shutil.copytree(source,d/'skills'/key)
    text=instruction+'\n\n'+spec['guidance']+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
    for key in ARMS[task['arm']]:text+='\n'+(d/'skills'/key/'SKILL.md').read_text()
    if not ARMS[task['arm']]:text+='\nNo skill is supplied.\n'
    return text


def transform(code):
    def replace(old,new):
        nonlocal code
        if code.count(old)!=1:raise RuntimeError('Screen substitution not unique: '+old[:80])
        code=code.replace(old,new)
    replace("assert contract['arms'] == ['No skill']", "assert set(contract['arms']) == {'none','K','candidate','Both'}")
    replace("'arm':'No skill','family':task['family']", "'arm':task['arm'],'cell_id':task['cell_id'],'family':task['family']")
    replace("session.begin(ident,admission[0]['load'])", "session.begin(task['cell_id'],admission[0]['load'])")
    replace("requests=session.accounting_rows(ident)", "requests=session.accounting_rows(task['cell_id'])")
    old="            prompt=instruction+'\\n\\n'+spec['guidance']+'\\n\\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. No skill is supplied.\\n'"
    replace(old,"            prompt=screen_prompt(instruction,spec,task,d)")
    replace("    plan['launch_commit'] =", "    plan['screen_plan_sha256']=sha(SCREEN_PLAN)\n    plan['launch_commit'] =")
    replace("            if sources()!=live or W.files(task['source'])!=plan['task_source_hashes'][ident]:raise RuntimeError('Source identity changed')", "            if sha(SCREEN_PLAN)!=plan['screen_plan_sha256']:raise RuntimeError('Screen plan changed')\n            if sources()!=live or W.files(task['source'])!=plan['task_source_hashes'][ident]:raise RuntimeError('Source identity changed')")
    replace("'scope':'Step 3 calibration only; no savings or confirmation claim'", "'scope':'Step 5 matched development screen only; not confirmation or a savings acceptance claim'")
    return code


def controller():
    E.mkdir(exist_ok=True)
    base=C.make_controller(primary_count=999,driver_path=__file__,source_transform=transform)
    base.E=E;base.load_contract=contract;base.window_end=window_end;base.screen_prompt=screen_prompt;base.SCREEN_PLAN=PLAN
    base.driver_entries.append(G/'html_screen_grader_setup.py')
    original=base.grader_spec
    def grader_spec(task):
        if task=='break-filter-js-from-html':
            import html_screen_grader_setup as H
            return H,H.inputs(),'none'
        return original(task)
    base.grader_spec=grader_spec
    return base

if __name__=='__main__':
    base=controller();base.main()
