#!/usr/bin/env python3
"""Twelve frozen bounded development actors, followed by official SWE grading."""
import concurrent.futures, hashlib, importlib.util, json, os, random, shutil, subprocess, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; OUT=Path(__file__).resolve().parent
TASK=Path('/tmp/solpi-refinement-flask-native-task-v2'); DATA=Path('/tmp/solpi-refinement-swe-data.json')
IMAGE='sha256:10a67635ce037886b760a72f6eef8459beb6a0c6e070c0748a037839135acc45'
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
SOURCES={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','shipped':ROOT/'skills/efficient-coding','leanparent':ROOT/'tests/framework/refinement/candidates/lean-tools/efficient-coding','candidate':ROOT/'tests/framework/refinement/candidates/lean-tools-no-reread/efficient-coding'}
ARMS={'none':[],'karpathy':['karpathy'],'shipped':['shipped'],'leanparent':['leanparent'],'candidate':['candidate'],'both':['karpathy','candidate']}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
patcher=load('swe_patch',ROOT/'tests/framework/benchmarks/swe_patch.py')
collect=load('collect',ROOT/'tests/framework/trials/collect.py')
def official(predictions,runid):
    work=OUT/'official'/runid; work.mkdir(parents=True)
    p=work/'predictions.jsonl'; p.write_text('\n'.join(json.dumps(x) for x in predictions)+'\n')
    with (work/'harness.txt').open('wb') as log:
        result=subprocess.run([PYTHON,'-m','swebench.harness.run_evaluation','-d',str(DATA),'-p',str(p),'-id',runid,'--max_workers','1','-t','180','--report_dir',str(work)],cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    reports=list(work.glob('logs/run_evaluation/**/report.json'))
    return result.returncode,reports

def attempt(harness,arm,prompt):
    dest=OUT/harness/arm; dest.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='solpi-swe-actor-') as tmp:
        tmp=Path(tmp); workspace=tmp/'workspace'; shutil.copytree(TASK/'workspace',workspace)
        home=tmp/'home'; home.mkdir(); credential=Path.home()/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json')
        target=home/('.pi/agent/auth.json' if harness=='pi' else '.codex/auth.json'); target.parent.mkdir(parents=True); shutil.copy2(credential,target)
        resources=tmp/'skills'; resources.mkdir()
        for key in ARMS[arm]: shutil.copytree(OUT/'frozen'/key,resources/key)
        name=f'solpi-swe-dev-{harness}-{arm}'
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
        blocked=any(s in (stdout+stderr).decode(errors='replace').lower() for s in ['quota exceeded','insufficient_quota','out of extra usage','authentication failed','unauthorized','usage limit','login required'])
        record={'harness':harness,'arm':arm,'task':'pallets__flask-5014','round':1,'model':'gpt-6.1-sol','execution_status':'blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if code==0 else 'agent_error','elapsed_seconds':elapsed,'exit_code':code,'timeout':timeout,'reported_total_tokens':total,'token_basis':basis,'billing_cost_usd':None,'solved':None,'transcript_sha256':sha(dest/'stdout.jsonl'),'patch_sha256':sha(dest/'model.patch')}
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','--mount',f'type=bind,src={tmp},dst=/cleanup',IMAGE,'-R',f'{os.getuid()}:{os.getgid()}','/cleanup'],capture_output=True,check=True)
    print(json.dumps(record),flush=True)
    if blocked: raise RuntimeError('Auth or quota stop')
    return record

def main():
    if (OUT/'plan.json').exists(): raise SystemExit('Frozen plan exists; refuse actor retries')
    assert subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()==IMAGE
    frozen=OUT/'frozen'; frozen.mkdir()
    for key,source in SOURCES.items(): shutil.copytree(source,frozen/key)
    prompts={}
    for arm,keys in ARMS.items():
        prompts[arm]=(TASK/'prompt.txt').read_text()+ ('\n\nApply these supplied skill instructions:\n\n'+'\n\n'.join((frozen/key/'SKILL.md').read_text() for key in keys) if keys else '')
        (OUT/(arm+'-prompt.txt')).write_text(prompts[arm])
    order=list(ARMS); random.Random(105).shuffle(order)
    plan={'purpose':'development only; one public SWE fixture; no held-out confirmation','maximum_attempts':12,'maximum_actor_wall_seconds':2160,'attempt_timeout_seconds':180,'rounds':1,'order_seed':105,'model_sampling_seed':'TBD: unavailable','arms':ARMS,'order':order,'harnesses':['pi','codex'],'model':'gpt-6.1-sol','pi_thinking':'low','codex_effort':'native default','image_id':IMAGE,'task_manifest':json.loads((TASK/'manifest.json').read_text()),'dataset_revision':'78f471bf655a3137b2e8a75af1501690ec009ec3','skill_delivery':'uniform inline text and readonly resources /skills','skill_sha256':{k:sha(frozen/k/'SKILL.md') for k in SOURCES},'prompt_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in prompts.items()},'grading':'official swebench5.0.2 run_evaluation; private gold outside actors','stop_rule':'auth/quota rejection stops remaining actors for that harness; no automatic retries','known_unrelated_failures':'Three cookie-domain test_basic tests fail on original dependencies even with gold; official selected blueprint tests unaffected','billing_usd':'TBD'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    # Validate bridge produces empty baseline and official baseline rejects before any actor.
    assert patcher.snapshot_patch(TASK/'workspace',TASK/'workspace')==''
    code,reports=official([{'instance_id':'pallets__flask-5014','model_name_or_path':'swe-native-bridge-noop','model_patch':''}],'solpi-swe-native-bridge-noop-105')
    report=json.loads(reports[0].read_text()) if reports else {}
    (OUT/'bridge-sanity.json').write_text(json.dumps({'exit_code':code,'reports':[str(p.relative_to(OUT)) for p in reports],'report':report,'empty_patch':True},indent=2)+'\n')
    if code!=0 or not reports: raise RuntimeError('Official bridge sanity did not produce report')
    def campaign(harness):
        records=[]
        for arm in order:
            try: records.append(attempt(harness,arm,prompts[arm]))
            except RuntimeError: break
        return records
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records=sum([f.result() for f in [pool.submit(campaign,h) for h in ('pi','codex')]],[])
    for record in records:
        h,a=record['harness'],record['arm']; dest=OUT/h/a
        code,reports=official([{'instance_id':'pallets__flask-5014','model_name_or_path':f'{h}-{a}','model_patch':(dest/'model.patch').read_text()}],f'solpi-swe-native-{h}-{a}-105')
        if reports:
            report=json.loads(reports[0].read_text()); leaf=report.get('pallets__flask-5014',report)
            record['solved']=leaf.get('resolved'); record['official_report']=str(reports[0].relative_to(OUT)); record['official_report_sha256']=sha(reports[0])
        record['official_harness_exit_code']=code
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        (OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__': main()
