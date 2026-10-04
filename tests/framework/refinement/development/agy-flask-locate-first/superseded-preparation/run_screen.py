#!/usr/bin/env python3
"""Four bounded native agy development actors, followed by official SWE grading."""
import concurrent.futures, fcntl, hashlib, importlib.util, json, os, random, shutil, subprocess, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; OUT=Path(__file__).resolve().parent
TASK=Path('/tmp/solpi-refinement-flask-native-task-v2'); DATA=Path('/tmp/solpi-refinement-swe-data.json')
IMAGE='sha256:10a67635ce037886b760a72f6eef8459beb6a0c6e070c0748a037839135acc45'
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
SOURCES={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','candidate':ROOT/'tests/framework/refinement/candidates/locate-first/efficient-coding'}
ARMS={'none':[],'karpathy':['karpathy'],'candidate':['candidate'],'both':['karpathy','candidate']}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
patcher=None
collect=None
NATIVE=Path('/home/wangjian/.local/bin/agy')
MODEL='gemini-3.8-flash-low'
CACHE=Path('/tmp/solpi-refinement-auth-cache')
GLOBAL=ROOT/'tests/framework/refinement/development-budget-agy-flask-locate-first.json'
def official(predictions,runid):
    work=OUT/'official'/runid; work.mkdir(parents=True)
    p=work/'predictions.jsonl'; p.write_text('\n'.join(json.dumps(x) for x in predictions)+'\n')
    with (work/'harness.txt').open('wb') as log:
        result=subprocess.run([PYTHON,'-m','swebench.harness.run_evaluation','-d',str(DATA),'-p',str(p),'-id',runid,'--max_workers','1','-t','180','--report_dir',str(work)],cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    reports=list(work.glob('logs/run_evaluation/**/report.json'))
    return result.returncode,reports

def files(directory):return {str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and '.git' not in p.parts}
def prepare():
    if (OUT/'plan.json').exists():raise SystemExit('Plan exists; refuse overwrite')
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    frozen=OUT/'frozen';frozen.mkdir()
    for key,source in SOURCES.items():shutil.copytree(source,frozen/key)
    runtime=frozen/'runtime';runtime.mkdir();shutil.copy2(ROOT/'tests/framework/benchmarks/swe_patch.py',runtime/'swe_patch.py');shutil.copy2(ROOT/'tests/framework/trials/collect.py',runtime/'collect.py');shutil.copy2(ROOT/'tests/framework/accounting.py',frozen/'accounting.py')
    order=list(ARMS);random.Random(108).shuffle(order)
    prompts={}
    for arm,keys in ARMS.items():
        prompts[arm]=(TASK/'prompt.txt').read_text()+('\n\nApply these supplied skill instructions:\n\n'+'\n\n'.join((frozen/key/'SKILL.md').read_text() for key in keys) if keys else '')
        (OUT/(arm+'-prompt.txt')).write_text(prompts[arm])
    probe=subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','/opt/native-agy','--mount',f'type=bind,src={NATIVE},dst=/opt/native-agy,readonly',IMAGE,'--version'],capture_output=True,text=True,check=True)
    (OUT/'native-version-probe.txt').write_text(probe.stdout+probe.stderr)
    plan={'purpose':'Native agy four-arm exposed SWE development screen; not confirmation','maximum_attempts':4,'maximum_actor_wall_seconds':720,'attempt_timeout_seconds':180,'native_print_timeout_seconds':170,'rounds':1,'order_seed':108,'model_sampling_seed':'TBD','harness':'agy','requested_model':MODEL,'observed_actual_backend':'TBD','native_version':probe.stdout.strip(),'native_binary':str(NATIVE),'native_binary_sha256':sha(NATIVE),'image_id':IMAGE,'arms':ARMS,'order':order,'task_manifest':json.loads((TASK/'manifest.json').read_text()),'dataset_revision':'78f471bf655a3137b2e8a75af1501690ec009ec3','original_source_files_sha256':files(TASK/'workspace'),'runtime_source_sha256':{'run_screen.py':sha(Path(__file__)),**{str(p.relative_to(OUT)):sha(p) for p in frozen.rglob('*.py')}},'skill_trees_sha256':{k:files(frozen/k) for k in SOURCES},'skill_sha256':{k:sha(frozen/k/'SKILL.md') for k in SOURCES},'prompt_sha256':{a:hashlib.sha256(p.encode()).hexdigest() for a,p in prompts.items()},'skill_delivery':'Uniform inline SKILL.md + full readonly resources /skills','credentials':'Seed private agy HOME once outside Git from host OAuth; persist refresh, serialize CACHE/agy.lock; never host write','stop_rule':'No retries; auth/quota failure stops remaining arms; SDK ERROR despite exit0 is failure, total usage TBD unless complete successful terminal accounting','quality':'Grade stopped partial patches independently; keep availability outcomes distinct from patch quality','grading':'Official swebench5.0.2 private original dataset, before-actor harmless marker baseline control; no gold/tests/credentials mounted across actor/grader boundary','external_access':'Mandatory saved web/tool/fetch audit; native cloud search gate TBD; no claim of clean held-out isolation regardless no local fetch markers','known_unrelated_failures':'Three baseline cookie-domain failures in test_basic persist even with gold','billing_usd':'TBD','global_budget_path':str(GLOBAL),'launch_status':'prepared only; root must review and approve concrete frozen four-start stage'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    budget={'purpose':'Separate prepared native agy development stage; not extension of broad12stage','max_actor_attempts':4,'actor_timeout_seconds':180,'native_print_timeout_seconds':170,'automatic_retries':0,'order_seed':108,'task':'pallets__flask-5014','harness':'agy','arms':list(ARMS),'candidate_sha256':plan['skill_sha256']['candidate'],'local_plan_sha256':sha(OUT/'plan.json'),'launch_status':'not_started; awaiting root review','billing_usd':'TBD'}
    if GLOBAL.exists():raise RuntimeError('Global budget exists; refuse overwrite')
    GLOBAL.write_text(json.dumps(budget,indent=2)+'\n');print('Prepared four-start agy stage; no model calls')

def seed_auth():
    home=CACHE/'agy';token=home/'.gemini/antigravity-cli/antigravity-oauth-token'
    if token.exists():return 'Existing cache retained without overwrite'
    original=Path.home()/'.gemini/antigravity-cli/antigravity-oauth-token'
    if not original.is_file():raise RuntimeError('Host agy OAuth seed absent; no auto login')
    token.parent.mkdir(parents=True,exist_ok=True);home.chmod(0o700);shutil.copy2(original,token);token.chmod(0o600)
    return 'Seeded once outside Git; host untouched; authentication validity unproven'

def actor(arm,prompt):
    with (CACHE/'agy.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert sha(NATIVE)==json.loads((OUT/'plan.json').read_text())['native_binary_sha256']
        dest=OUT/'agy'/arm;dest.mkdir(parents=True)
        if len(list(OUT.glob('agy/*/actor-start.json')))>=4:raise RuntimeError('Four-start cap exhausted')
        home=CACHE/'agy';token=home/'.gemini/antigravity-cli/antigravity-oauth-token'
        if not token.is_file():raise RuntimeError('Private auth unavailable')
        with tempfile.TemporaryDirectory(prefix='solpi-agy-flask-') as directory:
            workspace=Path(directory)/'workspace';shutil.copytree(TASK/'workspace',workspace)
            resources=Path(directory)/'resources';resources.mkdir()
            for key in ARMS[arm]:shutil.copytree(OUT/'frozen'/key,resources/key)
            name='solpi-agy-flask-locate-'+arm
            command=['docker','run','--rm','--name',name,'--user','0:0','--entrypoint','/opt/native-agy','-e','HOME=/eval-home','--mount',f'type=bind,src={NATIVE},dst=/opt/native-agy,readonly','--mount',f'type=bind,src={home},dst=/eval-home','--mount',f'type=bind,src={workspace},dst=/workspace','--mount',f'type=bind,src={resources},dst=/skills,readonly','-w','/workspace',IMAGE,'--print',prompt,'--model',MODEL,'--output-format','stream-json','--dangerously-skip-permissions','--print-timeout','170s']
            with (dest/'actor-start.json').open('x') as f:json.dump({'harness':'agy','arm':arm,'requested_model':MODEL,'timeout_seconds':180,'native_print_timeout_seconds':170,'counts_against_four_start_cap':True},f,indent=2);f.write('\n')
            start=time.monotonic();timeout=False
            try:
                run=subprocess.run(command,capture_output=True,timeout=180);stdout,stderr,code=run.stdout,run.stderr,run.returncode
            except subprocess.TimeoutExpired as e:
                stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True;subprocess.run(['docker','rm','-f',name],capture_output=True)
            elapsed=time.monotonic()-start;(dest/'stdout.jsonl').write_bytes(stdout);(dest/'stderr.txt').write_bytes(stderr)
            (dest/'model.patch').write_text(patcher.snapshot_patch(TASK/'workspace',workspace));shutil.copytree(workspace,dest/'workspace',ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
            events=collect.events(dest/'stdout.jsonl');terminal=[e.get('result',{}) for e in events if e.get('event')=='result'];sdk_success=len(terminal)==1 and terminal[0].get('status')=='SUCCESS'
            text=(stdout+stderr).decode(errors='replace').lower();blocked=any(s in text for s in ('invalid_grant','resource_exhausted','rate_limit_exceeded','quota exceeded','authentication failed','unauthorized','sign in to','login required','invalid api key'))
            total,basis=collect.token_total('agy',events) if sdk_success and not timeout and code==0 else (None,'TBD: error/timeout or missing successful complete native terminal accounting')
            status='blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if code==0 and sdk_success else 'native_sdk_error' if code==0 else 'agent_error'
            record={'harness':'agy','arm':arm,'task':'pallets__flask-5014','round':1,'requested_model':MODEL,'observed_actual_backend':'TBD','execution_status':status,'sdk_terminal_statuses':[x.get('status') for x in terminal],'terminal_result_count':len(terminal),'elapsed_seconds':elapsed,'exit_code':code,'timeout':timeout,'reported_total_tokens':total,'token_basis':basis,'billing_cost_usd':None,'solved':None,'official_patch_resolved':None,'transcript_sha256':sha(dest/'stdout.jsonl'),'patch_sha256':sha(dest/'model.patch')}
            (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
            for source,target in ((Path(directory),'/cleanup'),(home,'/private-auth')):
                subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','--mount',f'type=bind,src={source},dst={target}',IMAGE,'-R',f'{os.getuid()}:{os.getgid()}',target],capture_output=True,check=True)
        print(json.dumps(record),flush=True);return record,blocked

def launch():
    global patcher,collect
    plan=json.loads((OUT/'plan.json').read_text());budget=json.loads(GLOBAL.read_text())
    assert budget['local_plan_sha256']==sha(OUT/'plan.json') and budget['max_actor_attempts']==4 and budget['automatic_retries']==0 and budget['order_seed']==108
    assert budget['harness']=='agy' and set(budget['arms'])==set(ARMS) and budget['actor_timeout_seconds']==180 and budget['native_print_timeout_seconds']==170
    for relative,digest in plan['runtime_source_sha256'].items():assert sha(OUT/relative)==digest
    for key,source in plan['skill_trees_sha256'].items():assert files(OUT/'frozen'/key)==source
    for arm,digest in plan['prompt_sha256'].items():assert sha(OUT/(arm+'-prompt.txt'))==digest
    assert files(TASK/'workspace')==plan['original_source_files_sha256'] and sha(DATA)==plan['task_manifest']['private_dataset_sha256'] and sha(NATIVE)==plan['native_binary_sha256']
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    assert subprocess.check_output([PYTHON,'-c','import importlib.metadata;print(importlib.metadata.version("swebench"))'],text=True).strip()=='5.0.2'
    if (OUT/'agy').exists():raise RuntimeError('Actor directory exists; refuse replay')
    if not (CACHE/'agy/.gemini/antigravity-cli/antigravity-oauth-token').is_file():raise RuntimeError('Private seed unavailable; no launch')
    with (OUT/'launch.json').open('x') as f:json.dump({'local_plan_sha256':sha(OUT/'plan.json'),'global_budget_sha256':sha(GLOBAL),'maximum_starts':4,'root_execution_approval':'Required before explicit launch invocation'},f,indent=2);f.write('\n')
    patcher=load('frozen_agy_bridge',OUT/'frozen/runtime/swe_patch.py');collect=load('frozen_agy_collect',OUT/'frozen/runtime/collect.py')
    assert patcher.snapshot_patch(TASK/'workspace',TASK/'workspace')==''
    control={'instance_id':'pallets__flask-5014','model_name_or_path':'agy-locate-first-noop-control','model_patch':'diff --git a/.solpi_noop_marker b/.solpi_noop_marker\nnew file mode 100644\n--- /dev/null\n+++ b/.solpi_noop_marker\n@@ -0,0 +1 @@\n+Grader sanity only.\n'}
    code,reports=official([control],'solpi-agy-flask-noop-108');assert code==0 and reports
    report=json.loads(reports[0].read_text())['pallets__flask-5014'];assert not report['resolved'] and not report['infra_failure']
    (OUT/'baseline-control.json').write_text(json.dumps({'official_report':str(reports[0].relative_to(OUT)),'official_report_sha256':sha(reports[0]),'resolved':False},indent=2)+'\n')
    records=[]
    for arm in plan['order']:
        record,blocked=actor(arm,(OUT/(arm+'-prompt.txt')).read_text());records.append(record);(OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
        if blocked:break
    for record in records:
        dest=OUT/'agy'/record['arm'];code,reports=official([{'instance_id':'pallets__flask-5014','model_name_or_path':'agy-'+record['arm'],'model_patch':(dest/'model.patch').read_text()}],'solpi-agy-flask-'+record['arm']+'-108')
        if reports:
            report=json.loads(reports[0].read_text())['pallets__flask-5014'];record['official_patch_resolved']=report['resolved'];record['official_report']=str(reports[0].relative_to(OUT));record['official_report_sha256']=sha(reports[0])
        elif not (dest/'model.patch').read_text():record['official_patch_resolved']=False;record['official_empty_patch_rejection']=True
        record['solved']=None if record['execution_status']=='blocked_auth_or_quota' else record['official_patch_resolved'];record['official_harness_exit_code']=code
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n');(OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--prepare',action='store_true');mode.add_argument('--seed-auth',action='store_true');mode.add_argument('--launch',action='store_true');args=parser.parse_args()
    if args.prepare:prepare()
    elif args.seed_auth:print(seed_auth())
    else:launch()
