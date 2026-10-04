#!/usr/bin/env python3
"""Eight frozen bounded development actors, followed by official SWE grading."""
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
def official(predictions,runid):
    work=OUT/'official'/runid; work.mkdir(parents=True)
    p=work/'predictions.jsonl'; p.write_text('\n'.join(json.dumps(x) for x in predictions)+'\n')
    with (work/'harness.txt').open('wb') as log:
        result=subprocess.run([PYTHON,'-m','swebench.harness.run_evaluation','-d',str(DATA),'-p',str(p),'-id',runid,'--max_workers','1','-t','180','--report_dir',str(work)],cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    reports=list(work.glob('logs/run_evaluation/**/report.json'))
    return result.returncode,reports

def _attempt(harness,arm,prompt):
    dest=OUT/harness/arm; dest.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='solpi-swe-actor-') as tmp:
        tmp=Path(tmp); workspace=tmp/'workspace'; shutil.copytree(TASK/'workspace',workspace)
        home=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()/harness
        credential=home/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json')
        if not credential.is_file(): raise RuntimeError('Private persistent auth unavailable; no actor launch')
        resources=tmp/'skills'; resources.mkdir()
        for key in ARMS[arm]: shutil.copytree(OUT/'frozen'/key,resources/key)
        name=f'solpi-swe-locate-first-{harness}-{arm}'
        command=['docker','run','--rm','--name',name,'--user','0:0','--entrypoint','/bin/bash','-e','HOME=/eval-home','-e','PI_TELEMETRY=0', '--mount',f'type=bind,src={home},dst=/eval-home','--mount',f'type=bind,src={workspace},dst=/workspace','--mount',f'type=bind,src={resources},dst=/skills,readonly','-w','/workspace',IMAGE,'-c','exec "$@"','actor']
        if harness=='pi': command+=['pi','--offline','--mode','json','--print','--no-session','--no-extensions','--no-context-files','--no-skills','--no-prompt-templates','--no-themes','--provider','openai','--model','gpt-6.1-sol','--thinking','low',prompt]
        else: command+=['codex','exec','--json','--ignore-user-config','--ephemeral','--dangerously-bypass-approvals-and-sandbox','--model','gpt-6.1-sol',prompt]
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
        record={'harness':harness,'arm':arm,'task':'pallets__flask-5014','round':1,'model':'gpt-6.1-sol','execution_status':'blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if code==0 else 'agent_error','elapsed_seconds':elapsed,'exit_code':code,'timeout':timeout,'reported_total_tokens':total,'token_basis':basis,'billing_cost_usd':None,'solved':None,'transcript_sha256':sha(dest/'stdout.jsonl'),'patch_sha256':sha(dest/'model.patch')}
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
    if (OUT/'plan.json').exists(): raise SystemExit('Frozen plan exists; refuse overwrite')
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    frozen=OUT/'frozen'; frozen.mkdir()
    for key,source in SOURCES.items(): shutil.copytree(source,frozen/key)
    runtime=frozen/'runtime'; runtime.mkdir()
    shutil.copy2(ROOT/'tests/framework/benchmarks/swe_patch.py',runtime/'swe_patch.py')
    shutil.copy2(ROOT/'tests/framework/trials/collect.py',runtime/'collect.py')
    shutil.copy2(ROOT/'tests/framework/accounting.py',frozen/'accounting.py')
    order=list(ARMS);random.Random(106).shuffle(order)
    prompts={}
    for arm,keys in ARMS.items():
        prompts[arm]=(TASK/'prompt.txt').read_text()+('\n\nApply these supplied skill instructions:\n\n'+'\n\n'.join((frozen/key/'SKILL.md').read_text() for key in keys) if keys else '')
        (OUT/(arm+'-prompt.txt')).write_text(prompts[arm])
    shutil.copy2(TASK/'manifest.json',OUT/'task-manifest.json')
    source=source_files(TASK/'workspace')
    importlib_bridge=load('frozen_bridge_prepare',runtime/'swe_patch.py');assert importlib_bridge.snapshot_patch(TASK/'workspace',TASK/'workspace')==''
    plan={'purpose':'development only; locate-first single-delta candidate; previously exposed SWE fixture, not confirmation','status_at_freeze':'prepared only; zero actors launched','maximum_attempts':8,'maximum_actor_wall_seconds':1440,'attempt_timeout_seconds':180,'rounds':1,'order_seed':106,'model_sampling_seed':'TBD: unavailable','arms':ARMS,'order':order,'harnesses':['pi','codex'],'model':'gpt-6.1-sol','pi_thinking':'low','codex_effort':'native default','image_id':IMAGE,'task_manifest':json.loads((TASK/'manifest.json').read_text()),'dataset_revision':'78f471bf655a3137b2e8a75af1501690ec009ec3','skill_delivery':'uniform inline text plus readonly /skills resources; same delivery as prior screen','skill_sha256':{k:sha(frozen/k/'SKILL.md') for k in SOURCES},'skill_trees_sha256':{k:source_files(frozen/k) for k in SOURCES},'prompt_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in prompts.items()},'original_source_files_sha256':source,'original_source_sha256':hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest(),'runtime_source_sha256':{'run_screen.py':sha(Path(__file__)),**{str(p.relative_to(OUT)):sha(p) for p in frozen.rglob('*.py')}},'grading':'official swebench5.0.2, private gold/dataset never mounted actors, harmless marker baseline sanity before inference','stop_rule':'auth/quota rejection stops remaining harness attempts; any started actor counts against eight; no retries','known_unrelated_failures':'Three test_basic cookie-domain failures in original dependencies even after gold; no claim of full-suite cleanliness','billing_usd':'TBD','credential_strategy':'persistent private per-harness HOME outside Git, serialized fcntl lock, externally seeded once, never copy stale host seed per actor','availability_gate':'Root must verify credentials or obtain fresh login after terminal invalid_grant; no new phase launch until verified','launch_requirement':'Explicit --launch with --global-stage frozen16-start file, after current terminal stage complete. Launch manifest records global-stage digest before any model calls.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print('Prepared eight-attempt plan. No actors launched.')

def launch(global_stage):
    global patcher,collect
    plan=json.loads((OUT/'plan.json').read_text())
    for relative,digest in plan['runtime_source_sha256'].items():assert sha(OUT/relative)==digest,relative
    assert source_files(TASK/'workspace')==plan['original_source_files_sha256']
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    for arm,digest in plan['prompt_sha256'].items():assert sha(OUT/(arm+'-prompt.txt'))==digest
    for key,files in plan['skill_trees_sha256'].items():assert source_files(OUT/'frozen'/key)==files
    stage=Path(global_stage).resolve();json.loads(stage.read_text())
    cache=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()
    if ROOT==cache or ROOT in cache.parents: raise RuntimeError('Private auth cache must be outside repository')
    for harness in ('pi','codex'):
        if not (cache/harness/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json')).is_file(): raise RuntimeError('Private auth availability gate not satisfied; no model starts')
    # Exclusive launch guard means even a failed grader control cannot silently replay actors.
    guard=OUT/'launch-manifest.json'
    with guard.open('x') as f:json.dump({'global_stage':str(stage),'global_stage_sha256':sha(stage),'plan_sha256':sha(OUT/'plan.json'),'launched_after_terminal_complete':'Root must verify live state before explicitly invoking this command','maximum_actor_starts':8,'credential_strategy':'persistent private per-harness HOME outside Git, serialized fcntl lock, seed only once externally, preserve refresh updates; host auth never written'},f,indent=2);f.write('\n')
    patcher=load('frozen_bridge_launch',OUT/'frozen/runtime/swe_patch.py');collect=load('frozen_collect_launch',OUT/'frozen/runtime/collect.py')
    control={'instance_id':'pallets__flask-5014','model_name_or_path':'locate-first-noop-control','model_patch':'diff --git a/.solpi_noop_marker b/.solpi_noop_marker\nnew file mode 100644\n--- /dev/null\n+++ b/.solpi_noop_marker\n@@ -0,0 +1 @@\n+Grader sanity only.\n'}
    code,reports=official([control],'solpi-swe-locate-first-noop-106')
    if code!=0 or not reports:raise RuntimeError('Official control failed infrastructure; no actor replay')
    report=json.loads(reports[0].read_text());leaf=report.get('pallets__flask-5014',report)
    assert leaf.get('resolved') is False and not leaf.get('infra_failure'),report
    (OUT/'bridge-sanity.json').write_text(json.dumps({'exit_code':code,'report':report,'official_report_sha256':sha(reports[0]),'empty_baseline_snapshot_patch':True},indent=2)+'\n')
    def campaign(harness):
        records=[]
        for arm in plan['order']:
            try:records.append(attempt(harness,arm,(OUT/(arm+'-prompt.txt')).read_text()))
            except RuntimeError:
                failed=OUT/harness/arm/'result.json'
                if failed.exists():records.append(json.loads(failed.read_text()))
                break
        return records
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records=sum([f.result() for f in [pool.submit(campaign,h) for h in ('pi','codex')]],[])
    (OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
    for record in records:
        h,a=record['harness'],record['arm'];dest=OUT/h/a
        code,reports=official([{'instance_id':'pallets__flask-5014','model_name_or_path':f'{h}-{a}','model_patch':(dest/'model.patch').read_text()}],f'solpi-swe-locate-first-{h}-{a}-106')
        if reports:
            report=json.loads(reports[0].read_text());leaf=report.get('pallets__flask-5014',report)
            record['solved']=leaf.get('resolved');record['official_report']=str(reports[0].relative_to(OUT));record['official_report_sha256']=sha(reports[0])
        elif not (dest/'model.patch').read_text():record['solved']=False;record['official_empty_patch_rejection']=True
        record['official_harness_exit_code']=code
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n');(OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--prepare',action='store_true');mode.add_argument('--launch',action='store_true');parser.add_argument('--global-stage');args=parser.parse_args()
    if args.prepare:prepare()
    elif not args.global_stage:parser.error('--launch requires --global-stage')
    else:launch(args.global_stage)
