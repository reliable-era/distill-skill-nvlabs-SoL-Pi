#!/usr/bin/env python3
"""Eight-start native public polyglot development screen, with independent restored tests."""
import concurrent.futures, fcntl, hashlib, importlib.util, json, os, random, shutil, subprocess, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; OUT=Path(__file__).resolve().parent
TASK=Path('/tmp/solpi-polyglot-go-smoke-v2')
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
SOURCES={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','candidate':ROOT/'tests/framework/refinement/candidates/locate-first/efficient-coding'}
ARMS={'none':[],'karpathy':['karpathy'],'candidate':['candidate'],'both':['karpathy','candidate']}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
patcher=None
collect=None
def grade(workspace,dest):
    result=subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','python3',
        '-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','-e','GOPROXY=off','-e','GOSUMDB=off','-e','GOTOOLCHAIN=local',
        '--mount',f'type=bind,src={workspace},dst=/workspace,readonly',
        '--mount',f'type=bind,src={OUT}/frozen/grader,dst=/grade,readonly',IMAGE,'/grade/grade.py'],capture_output=True,timeout=240)
    dest.write_bytes(result.stdout+result.stderr)
    return result.returncode

def _attempt(harness,arm,prompt):
    if len(list(OUT.glob('*/*/actor-start.json')))>=8: raise RuntimeError('Eight-start budget exhausted; no actor launch')
    dest=OUT/harness/arm; dest.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='solpi-swe-actor-') as tmp:
        tmp=Path(tmp); workspace=tmp/'workspace'; shutil.copytree(TASK/'workspace',workspace)
        home=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()/harness
        credential=home/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json')
        if not credential.is_file(): raise RuntimeError('Private persistent auth unavailable; no actor launch')
        resources=tmp/'skills'; resources.mkdir()
        for key in ARMS[arm]: shutil.copytree(OUT/'frozen'/key,resources/key)
        name=f'solpi-go-locate-first-{harness}-{arm}'
        command=['docker','run','--rm','--name',name,'--user','0:0','--entrypoint','/bin/bash','-e','HOME=/eval-home','-e','PI_TELEMETRY=0', '--mount',f'type=bind,src={home},dst=/eval-home','--mount',f'type=bind,src={workspace},dst=/workspace','--mount',f'type=bind,src={resources},dst=/skills,readonly','-w','/workspace',IMAGE,'-c','exec "$@"','actor']
        if harness=='pi': command+=['pi','--offline','--mode','json','--print','--no-session','--no-extensions','--no-context-files','--no-skills','--no-prompt-templates','--no-themes','--provider','openai','--model','gpt-6.1-sol','--thinking','low',prompt]
        else: command+=['codex','exec','--json','--ignore-user-config','--skip-git-repo-check','--ephemeral','--dangerously-bypass-approvals-and-sandbox','--model','gpt-6.1-sol',prompt]
        with (dest/'actor-start.json').open('x') as f:json.dump({'harness':harness,'arm':arm,'configured_model':'gpt-6.1-sol','timeout_seconds':180,'counts_against_eight_start_total':True},f,indent=2);f.write('\n')
        start=time.monotonic(); timeout=False
        try:
            run=subprocess.run(command,capture_output=True,timeout=180); stdout,stderr,code=run.stdout,run.stderr,run.returncode
        except subprocess.TimeoutExpired as e:
            stdout,stderr,code=e.stdout or b'',e.stderr or b'',None; timeout=True
            subprocess.run(['docker','rm','-f',name],capture_output=True)
        elapsed=time.monotonic()-start
        (dest/'stdout.jsonl').write_bytes(stdout); (dest/'stderr.txt').write_bytes(stderr)
        # Extract before cleanup using trusted original, never trusting actor refs/index.
        patch=patcher.snapshot_patch(TASK/'workspace',workspace); (dest/'model.patch').write_text(patch)
        shutil.copytree(workspace,dest/'workspace',ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
        events=collect.events(dest/'stdout.jsonl'); total,basis=collect.token_total(harness,events)
        blocked=any(s in (stdout+stderr).decode(errors='replace').lower() for s in ['quota exceeded','insufficient_quota','out of extra usage','authentication failed','invalid_grant','failed to refresh oauth','unauthorized','usage limit','login required'])
        record={'harness':harness,'arm':arm,'task':'go/exercises/practice/food-chain','round':1,'model':'gpt-6.1-sol','execution_status':'blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if code==0 else 'agent_error','elapsed_seconds':elapsed,'exit_code':code,'timeout':timeout,'reported_total_tokens':total,'token_basis':basis,'billing_cost_usd':None,'solved':None,'transcript_sha256':sha(dest/'stdout.jsonl'),'patch_sha256':sha(dest/'model.patch')}
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','--mount',f'type=bind,src={tmp},dst=/cleanup',IMAGE,'-R',f'{os.getuid()}:{os.getgid()}','/cleanup'],capture_output=True,check=True)
        subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','--mount',f'type=bind,src={home},dst=/private-auth',IMAGE,'-R',f'{os.getuid()}:{os.getgid()}','/private-auth'],capture_output=True,check=True)
    print(json.dumps(record),flush=True)
    if blocked: raise RuntimeError('Auth or quota stop')
    return record

def attempt(harness,arm,prompt):
    cache=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()
    if OUT in cache.parents or cache==OUT: raise RuntimeError('Private auth cache must be outside repository')
    with (cache/(harness+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _attempt(harness,arm,prompt)

def source_files(directory):
    return {str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and '.git' not in p.parts}

def prepare():
    if (OUT/'plan.json').exists():raise SystemExit('Plan exists; no overwrite')
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    frozen=OUT/'frozen';frozen.mkdir()
    for key,source in SOURCES.items():shutil.copytree(source,frozen/key)
    runtime=frozen/'runtime';runtime.mkdir()
    shutil.copy2(ROOT/'tests/framework/benchmarks/swe_patch.py',runtime/'swe_patch.py')
    shutil.copy2(ROOT/'tests/framework/trials/collect.py',runtime/'collect.py')
    shutil.copy2(ROOT/'tests/framework/accounting.py',frozen/'accounting.py')
    shutil.copytree(TASK/'grader',frozen/'grader')
    order=list(ARMS);random.Random(107).shuffle(order)
    prompts={}
    for arm,keys in ARMS.items():
        prompts[arm]=(TASK/'prompt.txt').read_text()+('\n\nApply these supplied skill instructions:\n\n'+'\n\n'.join((frozen/key/'SKILL.md').read_text() for key in keys) if keys else '')
        (OUT/(arm+'-prompt.txt')).write_text(prompts[arm])
    shutil.copy2(TASK/'manifest.json',OUT/'task-manifest.json')
    plan={'purpose':'Previously exposed public Aider polyglot adapted Go development task; no clean held-out claim','maximum_attempts':8,'maximum_actor_wall_seconds':1440,'attempt_timeout_seconds':180,'rounds':1,'order_seed':107,'model_sampling_seed':'TBD','arms':ARMS,'order':order,'harnesses':['pi','codex'],'model':'gpt-6.1-sol','pi_thinking':'low','codex_effort':'native default','image_id':IMAGE,'task_manifest':json.loads((TASK/'manifest.json').read_text()),'skill_delivery':'uniform inline SKILL.md plus complete readonly resources /skills','skill_sha256':{k:sha(frozen/k/'SKILL.md') for k in SOURCES},'skill_trees_sha256':{k:source_files(frozen/k) for k in SOURCES},'prompt_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in prompts.items()},'original_source_files_sha256':source_files(TASK/'workspace'),'grader_files_sha256':source_files(frozen/'grader'),'runtime_source_sha256':{'run_screen.py':sha(Path(__file__)),**{str(p.relative_to(OUT)):sha(p) for p in frozen.rglob('*.py')}},'protocol':'native harness, fixed single attempt, no post-grade repair; restore original official tests independently, count executed accepted tests, network none, no credentials in grader','credential_policy':'externally seeded-once persistent private per-harness HOME, shared cache/codex.lock or pi.lock across concurrent campaigns, preserve refreshed auth, host seeds never written','stop_rule':'all starts count; auth/quota failures stop affected harness, no retries','exposure':'task previously exposed to development harnesses; external test fetch audit mandatory; no clean held-out claims','billing_usd':'TBD'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    budget={'purpose':'Root-authorized development allocation; no automatic launch','max_actor_attempts':8,'per_harness_maximum':4,'actor_timeout_seconds':180,'automatic_retries':0,'order_seed':107,'harnesses':['pi','codex'],'arms':list(ARMS),'task':'go/exercises/practice/food-chain','local_plan_sha256':sha(OUT/'plan.json'),'launch_policy':'Codex four initially; Pi requires fresh human auth and separate root authorization'}
    (OUT/'budget.json').write_text(json.dumps(budget,indent=2)+'\n');print('Prepared eight-start budget, no actors launched')

def launch(harness):
    global patcher,collect
    plan=json.loads((OUT/'plan.json').read_text());budget=json.loads((OUT/'budget.json').read_text())
    assert budget['local_plan_sha256']==sha(OUT/'plan.json') and budget['max_actor_attempts']==8 and budget['per_harness_maximum']==4 and budget['actor_timeout_seconds']==180 and budget['automatic_retries']==0
    for relative,digest in plan['runtime_source_sha256'].items():assert sha(OUT/relative)==digest,relative
    for key,files in plan['skill_trees_sha256'].items():assert source_files(OUT/'frozen'/key)==files
    assert source_files(TASK/'workspace')==plan['original_source_files_sha256'] and source_files(OUT/'frozen/grader')==plan['grader_files_sha256']
    for arm,digest in plan['prompt_sha256'].items():assert sha(OUT/(arm+'-prompt.txt'))==digest
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    cache=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()
    if ROOT==cache or ROOT in cache.parents:raise RuntimeError('Auth cache must be outside Git')
    if not (cache/harness/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json')).is_file():raise RuntimeError('Private auth unavailable; no launch')
    if (OUT/harness).exists():raise RuntimeError('Harness directory exists; no automatic replay')
    with (OUT/('launch-'+harness+'.json')).open('x') as f:json.dump({'harness':harness,'plan_sha256':sha(OUT/'plan.json'),'budget_sha256':sha(OUT/'budget.json'),'maximum_this_harness':4,'maximum_total':8,'credential_policy':'persistent private cache, same per-harness fcntl lock across stages'},f,indent=2);f.write('\n')
    patcher=load('frozen_bridge_launch',OUT/'frozen/runtime/swe_patch.py');collect=load('frozen_collect_launch',OUT/'frozen/runtime/collect.py')
    assert patcher.snapshot_patch(TASK/'workspace',TASK/'workspace')==''
    control_log=OUT/('baseline-grade-'+harness+'.txt');baseline=grade(TASK/'workspace',control_log)
    (OUT/('grader-sanity-'+harness+'.json')).write_text(json.dumps({'baseline_grade_exit_code':baseline,'baseline_grade_sha256':sha(control_log),'network':'none','credentials_mounted':False,'reference_sanity':'Prior original/reference controls retained under ../../development/pi-go-v2 and ../../grader-sanity; no inference from sanity'},indent=2)+'\n')
    if baseline!=1:raise RuntimeError('Baseline must reject via trusted grader before actor calls')
    records=[]
    for arm in plan['order']:
        try:records.append(attempt(harness,arm,(OUT/(arm+'-prompt.txt')).read_text()))
        except RuntimeError:
            path=OUT/harness/arm/'result.json'
            if path.exists():records.append(json.loads(path.read_text()))
            break
        (OUT/(harness+'-results.json')).write_text(json.dumps(records,indent=2)+'\n')
    for record in records:
        if record['execution_status']=='blocked_auth_or_quota':continue
        dest=OUT/harness/record['arm'];code=grade(dest/'workspace',dest/'grade.txt')
        record.update(grade_exit_code=code,solved=code==0 if code in (0,1) else None,grade_sha256=sha(dest/'grade.txt'))
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
        (OUT/(harness+'-results.json')).write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--prepare',action='store_true');mode.add_argument('--launch',action='store_true');parser.add_argument('--harness',choices=['pi','codex']);args=parser.parse_args()
    if args.prepare:prepare()
    elif not args.harness:parser.error('--launch requires --harness')
    else:launch(args.harness)
