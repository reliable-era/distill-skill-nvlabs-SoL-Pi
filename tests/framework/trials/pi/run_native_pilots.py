"""Frozen native-provider Pi, Cursor, and Antigravity pilots, independent Docker grade."""
import concurrent.futures, hashlib, json, os, pathlib, shutil, subprocess, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = ROOT/'tests/framework/trials'
IMAGE = 'sol-pi-eval-trial:2026-10-04'
TASKS = ['heldout/d2_interfaces', 'heldout/d5_small_control']
ARMS = {'none': [], 'karpathy': ['karpathy'], 'ours': ['ours'], 'both': ['karpathy', 'ours']}
SKILLS = {'karpathy': ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines', 'ours': ROOT/'skills/efficient-coding'}
MODELS = {'pi_openai': ('openai','gpt-6.1-sol'), 'cursor': ('cursor','gpt-5.3-codex-low'), 'agy': ('google-antigravity','gemini-3.8-flash-low'), 'cursor_auto': ('cursor','auto (resolved backend TBD)')}

def run(harness):
    provider, model = MODELS[harness]
    out = BASE/harness
    out.mkdir(exist_ok=True)
    plan={'tasks':TASKS, 'arms':ARMS, 'image':IMAGE, 'provider':provider, 'model':model,
          'rounds':1, 'attempt_timeout_seconds':120, 'maximum_attempts':8,
          'selection_note':'Preselected two synthetic diagnostic fixtures; no selection by observed outcome.',
          'stop_rule':'Stop first authentication/quota error; preserve attempted error, remaining arms TBD.',
          'comparison':'Native provider system comparison; different model backends are not a causal harness comparison.',
          'skill_sha256':{k:hashlib.sha256((v/'SKILL.md').read_bytes()).hexdigest() for k,v in SKILLS.items()}}
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    results=json.loads((out/'results.json').read_text()) if (out/'results.json').exists() else []
    blocked=any(r.get('execution_status','').startswith('blocked_') for r in results)
    for task in TASKS:
        fixture=ROOT/'tests/eval/pruned/diagnostics'/task
        for arm, selected in ARMS.items():
            if any(r['task']==task and r['arm']==arm for r in results):continue
            runid=task.rsplit('/',1)[-1]+'-'+arm
            dest=out/runid
            dest.mkdir(exist_ok=True)
            if blocked:
                result={'harness':harness,'provider':provider,'model':model,'task':task,'arm':arm,
                        'execution_status':'not_attempted_after_provider_error','solved':None,'billing_cost_usd':'TBD'}
                results.append(result)
                (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
                (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
                continue
            with tempfile.TemporaryDirectory(prefix='solpi-native-') as temp:
                temp=pathlib.Path(temp)
                workspace=temp/'workspace'
                shutil.copytree(fixture/'repo',workspace)
                skills=temp/'skills';skills.mkdir()
                for skill in selected: shutil.copytree(SKILLS[skill],skills/skill)
                prompt=(fixture/'prompt.txt').read_text()
                if selected: prompt+='\nRead and follow each supplied skill at '+', '.join('/skills/'+s+'/SKILL.md' for s in selected)+'.'
                name='solpi-'+harness+'-'+runid
                command=['docker','run','--rm','--name',name,'--user','0:0','-e','HOME=/tmp/eval-home',
                         '--mount',f'type=bind,src={workspace},dst=/workspace',
                         '--mount',f'type=bind,src={skills},dst=/skills,readonly','-w','/workspace']
                if harness=='pi_openai':
                    command+=['--mount',f'type=bind,src={pathlib.Path.home()}/.pi/agent/auth.json,dst=/auth/.pi/agent/auth.json,readonly',
                              '-e','PI_TELEMETRY=0',IMAGE,'pi','--offline','--mode','json','--print','--no-session',
                              '--no-extensions','--no-context-files','--no-skills','--no-prompt-templates','--no-themes',
                              '--provider',provider,'--model',model,'--thinking','low',prompt]
                elif harness.startswith('cursor'):
                    command+=['--mount',f'type=bind,src={pathlib.Path.home()}/.config/cursor/auth.json,dst=/auth/.config/cursor/auth.json,readonly',
                              IMAGE,'cursor-agent','--print','--force','--trust','--output-format','stream-json']
                    if harness=='cursor':command+=['--model',model]
                    command+=[prompt]
                else:
                    command+=['--mount',f'type=bind,src={pathlib.Path.home()}/.local/bin/agy,dst=/opt/native-agy,readonly',
                              '--mount',f'type=bind,src={pathlib.Path.home()}/.gemini/antigravity-cli/antigravity-oauth-token,dst=/auth/agy-token,readonly',
                              IMAGE,'bash','-c',
                              'mkdir -p "$HOME/.gemini/antigravity-cli"; cp /auth/agy-token "$HOME/.gemini/antigravity-cli/antigravity-oauth-token"; chmod 600 "$HOME/.gemini/antigravity-cli/antigravity-oauth-token"; exec /opt/native-agy --print "$1" --model "$2" --output-format stream-json --dangerously-skip-permissions --print-timeout 115s',
                              'native-agy',prompt,model]
                start=time.time();timeout=False
                try:
                    p=subprocess.run(command,capture_output=True,timeout=120)
                    stdout,stderr,exitcode=p.stdout,p.stderr,p.returncode
                except subprocess.TimeoutExpired as exc:
                    stdout,stderr,exitcode=exc.stdout or b'',exc.stderr or b'',None;timeout=True
                    subprocess.run(['docker','rm','-f',name],capture_output=True)
                elapsed=time.time()-start
                (dest/'stdout.jsonl').write_bytes(stdout);(dest/'stderr.txt').write_bytes(stderr)
                shutil.copytree(workspace,dest/'workspace',dirs_exist_ok=True)
                grade=subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','python3',
                    '--mount',f'type=bind,src={workspace},dst=/workspace,readonly',
                    '--mount',f'type=bind,src={fixture}/hidden,dst=/grader,readonly','-w','/workspace','-e','PYTHONPATH=/workspace',
                    IMAGE,'-m','pytest','-q','-p','no:cacheprovider','/grader/test_hidden.py'],capture_output=True,timeout=30)
                (dest/'grade.txt').write_bytes(grade.stdout+grade.stderr)
                # Actor processes run as container root for narrow 0600 credential imports;
                # return generated directories to the host owner before temporary cleanup.
                subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown',
                    '--mount',f'type=bind,src={workspace},dst=/workspace',IMAGE,'-R',
                    f'{os.getuid()}:{os.getgid()}','/workspace'],capture_output=True,check=True)
                text=(stdout+stderr).decode(errors='replace')
                error=False
                for line in stdout.decode(errors='replace').splitlines():
                    try: event=json.loads(line)
                    except ValueError: continue
                    if event.get('type')=='message_end' and event.get('message',{}).get('errorMessage'):error=True
                    if event.get('type') in ('error','agent_error') or event.get('is_error'):error=True
                auth_error=any(x in text.lower() for x in ["out of extra usage",'not authenticated','authentication failed',
                    'invalid api key','quota exceeded','usage limit','unauthorized','insufficient_quota','sign in to','login required',
                    'premium request','authentication required','not logged in','actionrequirederror','named models unavailable',
                    'free plans can only use auto','resource_exhausted','rate_limit_exceeded'])
                if auth_error:blocked=True
                status='blocked_provider_auth_or_quota' if auth_error else 'agent_error' if error or exitcode not in (0,None) else 'timeout' if timeout else 'completed'
                result={'harness':harness,'provider':provider,'model':model,'task':task,'arm':arm,
                    'execution_status':status,'elapsed_seconds':elapsed,'exit_code':exitcode,'timeout':timeout,
                    'grade_exit_code':grade.returncode,'solved':None if auth_error else grade.returncode==0,
                    'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'billing_cost_usd':'TBD',
                    'token_usage':'TBD pending transcript normalization','grade_environment':IMAGE,
                    'skill_sha256':{s:plan['skill_sha256'][s] for s in selected},
                    'credential_policy':'Read-only credential-only mount, copied into disposable isolated HOME.'}
                results.append(result)
                (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
                (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
                print(json.dumps(result),flush=True)
    return harness

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for result in executor.map(run,MODELS):print('finished',result,flush=True)
