#!/usr/bin/env python3
"""Bounded single-task development screen. Never resumes/retries model attempts."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
TASK = Path('/tmp/solpi-polyglot-go-smoke-final')
IMAGE = 'sol-pi-eval-polyglot:2026-10-04'
SKILLS = {'karpathy': ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines',
          'shipped': ROOT/'skills/efficient-coding',
          'candidate': ROOT/'tests/framework/refinement/candidates/lean-tools/efficient-coding'}
ARMS = {'none': [], 'karpathy': ['karpathy'], 'shipped': ['shipped'], 'candidate': ['candidate'], 'both': ['karpathy', 'candidate']}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (OUT/'plan.json').exists():
        raise SystemExit('Plan exists; refuse automatic resume/retry')
    frozen = OUT/'frozen'; frozen.mkdir()
    for name, source in SKILLS.items():
        shutil.copytree(source, frozen/name)
    order = list(ARMS)
    random.Random(42).shuffle(order)
    image_id = subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()
    shutil.copy2(TASK/'manifest.json', OUT/'task-manifest.json')
    prompts = {}
    for arm, names in ARMS.items():
        prompt = (TASK/'prompt.txt').read_text()
        if names:
            prompt += '\n\nApply these supplied skill instructions:\n\n'
            prompt += '\n\n'.join((frozen/name/'SKILL.md').read_text() for name in names)
        prompts[arm] = prompt
        (OUT/(arm+'-prompt.txt')).write_text(prompt)
    plan = {'schema_version':1, 'purpose':'development only, not confirmation',
            'task':'go/exercises/practice/food-chain', 'rounds':1, 'maximum_attempts':5,
            'attempt_timeout_seconds':120, 'maximum_actor_wall_seconds':600,
            'order_seed':42, 'order':order, 'model_sampling_seed':'TBD: unavailable',
            'harness':'pi', 'provider':'openai', 'model':'gpt-6.1-sol', 'thinking':'low',
            'image':IMAGE, 'image_id':image_id, 'arms':ARMS,
            'skill_delivery':'uniform inline SKILL.md; readonly resources',
            'skill_sha256':{name:sha(frozen/name/'SKILL.md') for name in SKILLS},
            'prompt_sha256':{arm:hashlib.sha256(prompt.encode()).hexdigest() for arm,prompt in prompts.items()},
            'task_manifest_sha256':sha(OUT/'task-manifest.json'),
            'workspace_sha256':{str(p.relative_to(TASK/'workspace')):sha(p) for p in sorted((TASK/'workspace').rglob('*')) if p.is_file()},
            'stop_rule':'First auth/quota error stops remaining attempts; no automatic retries or provider substitutions',
            'billing_usd':'TBD'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('trial_collect',ROOT/'tests/framework/trials/collect.py')
    collect=importlib.util.module_from_spec(spec);spec.loader.exec_module(collect)
    auth=Path.home()/'.pi/agent/auth.json'
    blocked=not auth.is_file()
    results=[]
    for index,arm in enumerate(order):
        dest=OUT/arm;dest.mkdir()
        record={'harness':'pi','task':plan['task'],'arm':arm,'round':1,'configured_model':plan['model'],
                'billing_cost_usd':None,'skill_sha256':{k:plan['skill_sha256'][k] for k in ARMS[arm]}}
        if blocked:
            record.update(execution_status='not_attempted_auth_or_quota_unavailable',solved=None,reported_total_tokens=None)
        else:
            with tempfile.TemporaryDirectory(prefix='solpi-pi-go-') as directory:
                workspace=Path(directory)/'workspace';shutil.copytree(TASK/'workspace',workspace)
                resources=Path(directory)/'resources';resources.mkdir()
                for skill in ARMS[arm]:shutil.copytree(frozen/skill,resources/skill)
                name='solpi-dev-pi-go-'+arm
                command=['docker','run','--rm','--name',name,'--user','0:0','-e','HOME=/tmp/eval-home','-e','PI_TELEMETRY=0',
                         '--mount',f'type=bind,src={auth},dst=/auth/.pi/agent/auth.json,readonly',
                         '--mount',f'type=bind,src={workspace},dst=/workspace',
                         '--mount',f'type=bind,src={resources},dst=/skills,readonly','-w','/workspace',
                         image_id,'pi','--offline','--mode','json','--print','--no-session','--no-extensions',
                         '--no-context-files','--no-skills','--no-prompt-templates','--no-themes',
                         '--provider','openai','--model','gpt-6.1-sol','--thinking','low',prompts[arm]]
                start=time.monotonic();timed_out=False
                try:
                    run=subprocess.run(command,capture_output=True,timeout=120)
                    stdout,stderr,code=run.stdout,run.stderr,run.returncode
                except subprocess.TimeoutExpired as error:
                    stdout,stderr,code=error.stdout or b'',error.stderr or b'',None;timed_out=True
                    subprocess.run(['docker','rm','-f',name],capture_output=True)
                elapsed=time.monotonic()-start
                (dest/'stdout.jsonl').write_bytes(stdout);(dest/'stderr.txt').write_bytes(stderr)
                shutil.copytree(workspace,dest/'workspace')
                grade=subprocess.run(['docker','run','--rm','--network','none','--user','0:0',
                    '-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache',
                    '--mount',f'type=bind,src={workspace},dst=/workspace,readonly',
                    '--mount',f'type=bind,src={TASK}/grader,dst=/grader,readonly',image_id,'python3','/grader/grade.py'],
                    capture_output=True,timeout=240)
                (dest/'grade.txt').write_bytes(grade.stdout+grade.stderr)
                subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown',
                    '--mount',f'type=bind,src={workspace},dst=/workspace',image_id,'-R',f'{os.getuid()}:{os.getgid()}','/workspace'],capture_output=True,check=True)
                output=(stdout+stderr).decode(errors='replace').lower()
                blocked=any(s in output for s in ('out of extra usage','not authenticated','authentication failed','invalid api key','quota exceeded','usage limit','unauthorized','insufficient_quota','login required','rate_limit_exceeded'))
                events=collect.events(dest/'stdout.jsonl')
                total,basis=collect.token_total('pi',events)
                observed=sorted({message['model'] for event in events if event.get('type')=='agent_end'
                                 for message in event.get('messages',[]) if isinstance(message,dict) and isinstance(message.get('model'),str)})
                record.update(execution_status='blocked_auth_or_quota' if blocked else 'timeout' if timed_out else 'completed' if code==0 else 'agent_error',
                    timeout=timed_out,elapsed_seconds=elapsed,exit_code=code,grade_exit_code=grade.returncode,
                    solved=None if blocked or grade.returncode not in (0,1) else grade.returncode==0,
                    reported_total_tokens=total,token_basis=basis,observed_models=observed,
                    transcript_sha256=sha(dest/'stdout.jsonl'),grader_sha256=sha(dest/'grade.txt'))
        (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n');results.append(record)
        (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(record),flush=True)


if __name__=='__main__':
    main()
