#!/usr/bin/env python3
"""Bounded native agy development; mounted credential never enters workspace."""
from pathlib import Path
import hashlib,importlib.util,json,os,random,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
TASK=Path('/tmp/solpi-polyglot-go-smoke-v2')
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
MODEL='gemini-3.8-flash-low'
SKILLS={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','shipped':ROOT/'skills/efficient-coding','parent':ROOT/'tests/framework/refinement/candidates/lean-tools/efficient-coding','candidate':ROOT/'tests/framework/refinement/candidates/lean-tools-no-reread/efficient-coding'}
ARMS={'none':[],'karpathy':['karpathy'],'shipped':['shipped'],'parent':['parent'],'candidate':['candidate'],'both':['karpathy','candidate']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if (OUT/'plan.json').exists():raise RuntimeError('Frozen plan exists; no automatic replay')
    binary=Path.home()/'.local/bin/agy'; auth=Path.home()/'.gemini/antigravity-cli/antigravity-oauth-token'
    if not binary.is_file() or not auth.is_file():raise RuntimeError('Native binary/auth unavailable; do not substitute provider')
    order=list(ARMS);random.Random(105).shuffle(order)
    manifests={str(p.relative_to(TASK)):sha(p) for p in TASK.rglob('*') if p.is_file()}
    plan={'purpose':'Development only, not confirmation','task':'aider:go/exercises/practice/food-chain','image_id':IMAGE,'model':MODEL,'arms':ARMS,'order':order,'ordering_seed':105,'model_sampling_seed':'TBD','max_attempts':6,'actor_timeout_seconds':180,'rounds':1,'retries':0,'task_files':manifests,'binary_sha256':sha(binary),'skills':{k:sha(v/'SKILL.md') for k,v in SKILLS.items()},'actual_billing_usd':'TBD','credential_policy':'Readonly mount into disposable HOME; no credentials to grader'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('trial_collect',ROOT/'tests/framework/trials/collect.py');collect=importlib.util.module_from_spec(spec);spec.loader.exec_module(collect)
    results=[];blocked=False
    for arm in order:
        dest=OUT/arm;dest.mkdir();workspace=dest/'workspace';shutil.copytree(TASK/'workspace',workspace)
        resources=dest/'resources';resources.mkdir()
        prompt=(TASK/'prompt.txt').read_text()
        for k in ARMS[arm]:
            shutil.copytree(SKILLS[k],resources/k)
            prompt+='\n\n'+(SKILLS[k]/'SKILL.md').read_text()
        (dest/'prompt.txt').write_text(prompt)
        if blocked:
            r={'arm':arm,'execution_status':'not_attempted_after_provider_error','solved':None,'reported_total_tokens':None};(dest/'result.json').write_text(json.dumps(r));results.append(r);continue
        name='solpi-agy-go-'+arm;start=time.monotonic();timeout=False
        cmd=['docker','run','--rm','--name',name,'--user','0:0','-e','HOME=/tmp/eval-home','-w','/workspace','-v',f'{workspace}:/workspace','-v',f'{resources}:/skills:ro','-v',f'{binary}:/opt/native-agy:ro','-v',f'{auth}:/auth/agy-token:ro',IMAGE,'bash','-c','mkdir -p "$HOME/.gemini/antigravity-cli"; cp /auth/agy-token "$HOME/.gemini/antigravity-cli/antigravity-oauth-token"; chmod 600 "$HOME/.gemini/antigravity-cli/antigravity-oauth-token"; exec /opt/native-agy --print "$1" --model "$2" --output-format stream-json --dangerously-skip-permissions --print-timeout 170s','native-agy',prompt,MODEL]
        try:
            p=subprocess.run(cmd,capture_output=True,timeout=180);stdout,stderr,code=p.stdout,p.stderr,p.returncode
        except subprocess.TimeoutExpired as e:
            stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True
        finally:subprocess.run(['docker','rm','-f',name],capture_output=True)
        elapsed=time.monotonic()-start;(dest/'stdout.jsonl').write_bytes(stdout);(dest/'stderr.txt').write_bytes(stderr)
        grade=subprocess.run(['docker','run','--rm','--network','none','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','-v',f'{workspace}:/workspace:ro','-v',f'{TASK}/grader:/grade:ro',IMAGE,'python3','/grade/grade.py'],capture_output=True,timeout=240)
        (dest/'grade.txt').write_bytes(grade.stdout+grade.stderr)
        subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','-v',f'{workspace}:/workspace',IMAGE,'-R',f'{os.getuid()}:{os.getgid()}','/workspace'],capture_output=True,check=True)
        output=(stdout+stderr).decode(errors='replace').lower();blocked=any(s in output for s in ['quota exceeded','resource_exhausted','authentication failed','unauthorized','login required','rate_limit_exceeded'])
        events=collect.events(dest/'stdout.jsonl');total,basis=collect.token_total('agy',events)
        terminal=[e.get('result',{}) for e in events if e.get('event')=='result']
        calls={e['step_update']['step_index'] for e in events if e.get('event')=='step_update' and e.get('step_update',{}).get('step_type')=='tool' and e['step_update'].get('state')=='DONE'}
        r={'harness':'agy','task':plan['task'],'arm':arm,'round':1,'configured_model':MODEL,'observed_model':'TBD unless native init identifies route','solved':grade.returncode==0 if grade.returncode in (0,1) else None,'execution_status':'blocked_provider' if blocked else 'timeout' if timeout else 'completed' if code==0 else 'agent_error','terminal_results':terminal,'elapsed_seconds':elapsed,'timeout':timeout,'exit_code':code,'grade_exit_code':grade.returncode,'reported_total_tokens':total,'token_basis':basis,'tool_calls':len(calls),'transcript_sha256':sha(dest/'stdout.jsonl'),'actual_billing_usd':'TBD'}
        (dest/'result.json').write_text(json.dumps(r,indent=2)+'\n');results.append(r);(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:r[k] for k in ('arm','solved','execution_status','reported_total_tokens')}),flush=True)
    # Exact mounted credential-value scan prints only counts, never matching text.
    raw=auth.read_bytes();secrets=[raw]
    try:
        def visit(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if isinstance(x,str) and ('token' in k.lower() or 'secret' in k.lower()) and len(x)>12:secrets.append(x.encode())
                    visit(x)
            elif isinstance(v,list):
                for x in v:visit(x)
        visit(json.loads(raw))
    except ValueError:pass
    hits=[str(f.relative_to(OUT)) for f in OUT.rglob('*') if f.is_file() and any(s and s in f.read_bytes() for s in secrets)]
    (OUT/'security-check.json').write_text(json.dumps({'exact_mounted_credential_hits':hits,'actor_attempts_repeated':0},indent=2)+'\n');assert not hits

if __name__=='__main__':main()
