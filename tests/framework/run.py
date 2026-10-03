#!/usr/bin/env python3
"""Freeze and execute an explicit, isolated evaluation matrix (stdlib only)."""
import argparse
import fcntl
import functools
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import time
import tempfile
import uuid
from accounting import summarize, terminal_usage, price_attempt

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def tree_digest(path):
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f'Task input directory does not exist: {path}')
    files = []
    for p in sorted(path.rglob('*')):
        if '.git' in p.relative_to(path).parts:
            continue
        if p.is_symlink():
            raise ValueError(f'Symlink not permitted in frozen task snapshot: {p}')
        if p.is_file() and '.git' not in p.relative_to(path).parts:
            files.append([str(p.relative_to(path)), hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o111])
    return digest(files)

def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as f:
            temporary = f.name
            json.dump(value, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.link(temporary, path)  # atomic publication, refuses an existing target
    finally:
        if temporary:
            os.unlink(temporary)

def freeze(args):
    source = json.loads(args.spec.read_text())
    registry = json.loads((HERE / 'agents.json').read_text())
    agents = registry.get('agents', registry)
    if isinstance(agents, list):
        agents = {a['id']: a for a in agents}
    if source['mode'] not in ('same-model', 'native'):
        raise ValueError('mode must be same-model or native')
    if source['mode'] == 'same-model' and (not source.get('backend_id') or 'TBD' in source['backend_id']):
        raise ValueError('same-model mode requires backend_id, with compatible per-agent model names')
    if len(set(source['rounds'])) != len(source['rounds']):
        raise ValueError('duplicate rounds')
    if len({t['id'] for t in source['tasks']}) != len(source['tasks']):
        raise ValueError('duplicate task ids')
    for task in source['tasks']:
        task['workspace'] = str((args.spec.parent / task['workspace']).resolve())
        task['workspace_sha256'] = tree_digest(task['workspace'])
        if task.get('grader_dir'):
            task['grader_dir'] = str((args.spec.parent / task['grader_dir']).resolve())
            task['grader_sha256'] = tree_digest(task['grader_dir'])
        if task.get('grader_image'):
            info = subprocess.run(['docker','image','inspect',task['grader_image']],capture_output=True,text=True,check=True)
            task['grader_image_id'] = json.loads(info.stdout)[0]['Id']
        if not isinstance(task['grader_argv'], list) or not task['grader_argv']:
            raise ValueError('explicit independent grader_argv required')
    for config in source['configurations']:
        agent = config['agent']
        if 'TBD' in str(config.get('model','')):
            raise ValueError('Replace TBD model before freezing a campaign')
        if agent == 'mock':
            config['command_template'] = ['python3', '-c', "from pathlib import Path; p=Path('calc.py'); p.write_text(p.read_text().replace('return a - b','return a + b'))"]
        else:
            config['command_template'] = agents[agent]['command_template']
            if not config['command_template']:
                raise ValueError(f'Agent {agent} integration is TBD')
            if source['mode'] == 'same-model' and not config.get('model'):
                raise ValueError(f'{agent}: same-model requires explicit model')
        skill = config.get('skill')
        if skill:
            skill_path = (args.spec.parent / skill).resolve()
            config['skill_text'] = skill_path.read_text()
            config['skill_sha256'] = hashlib.sha256(skill_path.read_bytes()).hexdigest()
            config['skill_dir'] = str(skill_path.parent)
            config['skill_tree_sha256'] = tree_digest(skill_path.parent)
        else:
            config['skill_text'] = ''
            config['skill_sha256'] = None
            config['skill_dir'] = None
        config['skill_loading'] = 'explicit prompt text; native skill discovery not assumed'
        image = config.get('image', agents.get(agent, {}).get('image', source.get('image')))
        if not image:
            raise ValueError(f'{agent}: image is required')
        info = subprocess.run(['docker','image','inspect', image], capture_output=True,text=True,check=True)
        config['image'] = image
        config['image_id'] = json.loads(info.stdout)[0]['Id']
    if len({c['id'] for c in source['configurations']}) != len(source['configurations']):
        raise ValueError('duplicate configuration ids')
    jobs = [dict(task=t['id'], config=c['id'], round=r) for t in source['tasks']
            for c in source['configurations'] for r in source['rounds']]
    budget=source.get('budget',{})
    if any(c['agent']!='mock' for c in source['configurations']):
        if not budget.get('max_attempts') or not budget.get('max_wall_seconds'):
            raise ValueError('Real-agent campaigns require explicit max_attempts and max_wall_seconds budget')
    if budget.get('max_attempts') and len(jobs)>budget['max_attempts']:
        raise ValueError('Matrix exceeds frozen attempt budget')
    random.Random(source['schedule_seed']).shuffle(jobs)
    source.update(schema_version=1, jobs=jobs, retries=0,
                  seed_semantics='selection/scheduling only; model random seeds are not controlled',
                  registry_sha256=digest(registry))
    source['plan_sha256'] = digest(source)
    write_new(args.output, source)
    print(f'Frozen {len(jobs)} attempts: {args.output}')

def redact(text):
    text = re.sub(r'(?i)(authorization\s*[:=]\s*)(?:bearer\s+)?[^\s,}]+',r'\1[REDACTED]',text)
    text = re.sub(r'(?i)("?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|authorization)"?\s*[:=]\s*)[^\s,}]+',r'\1[REDACTED]',text)
    return re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,})\b','[REDACTED]',text)

def container(argv, name, timeout, logfile):
    start = time.monotonic()
    proc = None
    status, code = 'failed', None
    try:
        fd = os.open(logfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            create = list(argv)
            if create[:2] != ['docker','run']:
                raise ValueError('container expects docker run arguments')
            create[1] = 'create'
            proc = subprocess.Popen(create, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = proc.wait(timeout=timeout)
                if code == 0:
                    # Name is fully registered before any agent process starts.
                    proc = subprocess.Popen(['docker','start','--attach',name],stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
                    code = proc.wait(timeout=max(.001,timeout-(time.monotonic()-start)))
                status = 'completed' if code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                code, status = None, 'timeout'
    finally:
        # Covers timeout, Ctrl-C and unexpected errors as well as normal exit.
        subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        if logfile.exists():
            logfile.chmod(0o600)
            logfile.write_text(redact(logfile.read_text(errors='replace')))
    return code, status, time.monotonic()-start

def copy_workspace(source, target):
    # A code snapshot never supplies historical solutions or host Git configuration.
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('.git'))
    for p in [target, *target.rglob('*')]:
        original_exec = p.stat().st_mode & 0o111
        p.chmod(0o777 if p.is_dir() else (0o666 | original_exec))


def output_lock(function):
    @functools.wraps(function)
    def wrapped(args):
        path = args.output if hasattr(args, 'output') else args
        path.mkdir(parents=True, exist_ok=True)
        with (path / 'runner.lock').open('a') as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Another runner/recovery is already using this output directory')
            return function(args)
    return wrapped

@output_lock
def execute(args):
    plan = json.loads(args.plan.read_text())
    claimed = plan.pop('plan_sha256')
    if digest(plan) != claimed:
        raise ValueError('Plan changed after freeze')
    args.output.mkdir(parents=True, exist_ok=True)
    marker = args.output / 'plan-sha256.txt'
    if marker.exists() and marker.read_text().strip() != claimed:
        raise ValueError('Output directory belongs to another plan')
    marker.write_text(claimed+'\n')
    metadata=args.output/'campaign.json'
    if not metadata.exists():
        write_new(metadata,dict(plan_sha256=claimed,planned_attempts=len(plan['jobs']),mode=plan['mode'],backend_id=plan.get('backend_id','TBD')))
    tasks = {t['id']:t for t in plan['tasks']}
    configs = {c['id']:c for c in plan['configurations']}
    agent_env = {}
    for entry in args.agent_env:
        agent, separator, value = entry.partition('=')
        if not separator or agent in agent_env or agent not in {c['agent'] for c in configs.values()}:
            raise ValueError('agent-env requires one known AGENT=/absolute/private/file per agent')
        agent_env[agent] = Path(value).resolve()
    if args.env_file and len({c['agent'] for c in configs.values()}) > 1:
        raise ValueError('Use per-agent --agent-env files for a multi-agent plan')
    for task in tasks.values():
        if tree_digest(task['workspace']) != task['workspace_sha256']:
            raise ValueError('Task workspace changed after freeze')
        if task.get('grader_dir') and tree_digest(task['grader_dir']) != task['grader_sha256']:
            raise ValueError('Independent grader changed after freeze')
    for c in configs.values():
        if c.get('skill_dir') and tree_digest(c['skill_dir']) != c['skill_tree_sha256']:
            raise ValueError('Skill bundle changed after freeze')
    budget=plan.get('budget',{})
    for i, job in enumerate(plan['jobs']):
        out = args.output / f'{i:05d}-{digest(job)[:12]}'
        result_path = out / 'result.json'
        if result_path.exists():
            existing=json.loads(result_path.read_text())
            if existing.get('plan_sha256') != claimed or any(existing.get(k)!=v for k,v in job.items()):
                raise ValueError('Existing result belongs to another attempt or plan')
            continue
        # An interrupted attempt is not rerun silently. Preserve and mark it first.
        if out.exists():
            raise ValueError(f'Interrupted attempt exists at {out}; classify it explicitly before continuing')
        past=[json.loads(p.read_text()) for p in args.output.glob('*/result.json')]
        elapsed=sum((r.get('elapsed_seconds') or 0)+(r.get('grader_seconds') or 0) for r in past)
        spent=sum(r.get('cost_usd') or 0 for r in past)
        if budget.get('max_wall_seconds') and elapsed>=budget['max_wall_seconds']:
            print('Frozen cumulative run-time budget reached; campaign stopped.'); break
        if budget.get('max_known_cost_usd') is not None and spent>=budget['max_known_cost_usd']:
            print('Known-cost budget reached; campaign stopped.'); break
        if budget.get('require_priced_usage') and any(r.get('cost_usd') is None for r in past):
            print('Pricing or telemetry unknown; campaign stopped by frozen budget policy.'); break
        out.mkdir()
        t, c = tasks[job['task']], configs[job['config']]
        name = 'solpi-eval-'+uuid.uuid4().hex[:14]
        write_new(out/'attempt.json',dict(**job,benchmark=t.get('benchmark','TBD'),agent=c['agent'],model=c.get('model','TBD'),container_name=name,plan_sha256=claimed))
        work = out / 'workspace'
        copy_workspace(t['workspace'], work)
        prompt = t['prompt']
        if c['skill_text']:
            prompt = 'Apply these coding instructions. Supporting resources are in /opt/eval-skill/:\n'+c['skill_text']+'\n\nTask:\n'+prompt
        template = list(c['command_template'])
        if not c.get('model'):
            for flag in ('--model', '-m'):
                if flag in template and template[template.index(flag)+1] == '{model}':
                    index = template.index(flag)
                    del template[index:index+2]
        command = [part.replace('{prompt}',prompt).replace('{model}',c.get('model','')) for part in template]
        docker = ['docker','run','--init','--rm','--name',name,'--network',plan.get('agent_network','bridge'),
                  '--cpus',str(plan.get('cpus',2)), '--memory',str(plan.get('memory','4g')),
                  '--mount',f'type=bind,src={work.resolve()},dst=/workspace', '--workdir','/workspace']
        if c.get('skill_dir'):
            docker += ['--mount',f'type=bind,src={c["skill_dir"]},dst=/opt/eval-skill,readonly']
        if c.get('credential_volume'):
            docker += ['--mount',f'type=volume,src={c["credential_volume"]},dst=/auth,readonly']
        # Docker env-file is supplied at run time, never written into frozen plan or results.
        env_file = agent_env.get(c['agent'], args.env_file)
        if env_file:
            docker += ['--env-file',str(env_file.resolve())]
        docker += [c['image_id'], *command]
        agent_code,status,seconds=container(docker,name,min(plan['timeout_seconds'],max(1,budget.get('max_wall_seconds',float('inf'))-elapsed)),out/'agent.log')
        grade_name=name+'-grade'
        grade=['docker','run','--init','--rm','--name',grade_name,'--network','none','--cpus','2','--memory','2g',
               '--mount',f'type=bind,src={work.resolve()},dst=/workspace,readonly','--workdir','/workspace']
        if t.get('grader_dir'):
            grade += ['--mount',f'type=bind,src={t["grader_dir"]},dst=/grade,readonly']
        grade += [t.get('grader_image_id', c['image_id']),*t['grader_argv']]
        remaining = budget.get('max_wall_seconds',float('inf'))-elapsed-seconds
        if remaining <= 0:
            grade_code,grade_status,grade_seconds = None,'budget_exhausted',0
        else:
            grade_code,grade_status,grade_seconds=container(grade,grade_name,min(plan.get('grade_timeout_seconds',60),remaining),out/'grader.log')
        # Exit 1 means a valid completed rejection; other exits are grader errors (not quality failures).
        solved = grade_code == 0 if grade_code in (0,1) else None
        events=[]
        for line in (out/'agent.log').read_text().splitlines():
            try:
                e=json.loads(line)
                if isinstance(e,dict): events.append(e)
            except ValueError: pass
        usage=terminal_usage(events,c['agent'])
        record=dict(**job,benchmark=t.get('benchmark','TBD'),agent=c['agent'],model=c.get('model','TBD'),backend_id=plan.get('backend_id','TBD'),
                    plan_sha256=claimed,image_id=c['image_id'],skill_sha256=c['skill_sha256'],
                    skill_loading=c['skill_loading'],status=status,agent_exit_code=agent_code,
                    solved=solved,grader_status=grade_status,grader_exit_code=grade_code,
                    elapsed_seconds=seconds,grader_seconds=grade_seconds,**usage)
        prices=plan.get('prices',{})
        if c['agent']=='claude':
            terminal=[e for e in events if e.get('type')=='result']
            models=terminal[0].get('modelUsage',{}) if len(terminal)==1 else {}
            components=[]
            for model,value in models.items():
                component=dict(input_tokens=value.get('inputTokens'), output_tokens=value.get('outputTokens'),
                               cache_read_tokens=value.get('cacheReadInputTokens'),cache_write_tokens=value.get('cacheCreationInputTokens'),
                               usage_complete=usage['usage_complete'],token_semantics=usage['token_semantics'])
                components.append(price_attempt(component,prices.get(model,{})))
            record['observed_usage_models']=list(models)
            record['cost_usd']=sum(components) if components and all(v is not None for v in components) else None
        elif c['agent']=='pi':
            components=[]
            for event in events:
                if event.get('type')!='agent_end': continue
                for message in event.get('messages',[]):
                    if not isinstance(message,dict) or message.get('role')!='assistant': continue
                    u=message.get('usage',{})
                    model=message.get('model')
                    provider=message.get('provider')
                    component=dict(input_tokens=u.get('input'),output_tokens=u.get('output'),
                                   cache_read_tokens=u.get('cacheRead'),cache_write_tokens=u.get('cacheWrite'),
                                   usage_complete=usage['usage_complete'],token_semantics=usage['token_semantics'])
                    price=prices.get(f'{provider}/{model}',prices.get(model,{})) if model else {}
                    components.append(price_attempt(component,price))
            record['cost_usd']=sum(components) if components and all(v is not None for v in components) else None
        else:
            record['cost_usd']=price_attempt(record,prices.get(c.get('model'),{}))
        record['configured_model']=c.get('model')
        record['observed_models']=record.get('observed_usage_models',[])
        if c['agent']=='pi':
            record['observed_models']=sorted({m['model'] for e in events if e.get('type')=='agent_end' for m in e.get('messages',[]) if isinstance(m,dict) and m.get('role')=='assistant' and isinstance(m.get('model'),str)})
        record['cost_source']='explicit frozen USD/million manifest' if record['cost_usd'] is not None else 'TBD'
        write_new(result_path,record)
        print(f'{i+1}/{len(plan["jobs"])} {job}: {status}, solved={solved}',flush=True)
    report(args.output)

def report(path):
    records=[json.loads(p.read_text()) for p in sorted(path.glob('*/result.json'))]
    groups={}
    for r in records:
        groups.setdefault((r.get('benchmark','TBD'),r['config']),[]).append(r)
    summary={' / '.join(key):summarize(value) for key,value in groups.items()}
    (path/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    metadata=json.loads((path/'campaign.json').read_text()) if (path/'campaign.json').exists() else {}
    progress=[f'Campaign progress: {len(records)}/{metadata["planned_attempts"]} recorded attempts; {metadata["planned_attempts"]-len(records)} pending or unclassified.', ''] if metadata else []
    lines=progress+['| Configuration | Agent | Configured model | Observed model(s) | Backend ID |',
           '|---|---|---|---|---|']
    for config in sorted({r['config'] for r in records}):
        items=[r for r in records if r['config']==config]
        models=sorted({m for r in items for m in r.get('observed_models',[])})
        lines.append(f'| {config} | {items[0].get("agent","TBD")} | {items[0].get("configured_model") or items[0].get("model","TBD")} | {", ".join(models) or "TBD"} | {items[0].get("backend_id","TBD")} |')
    lines += ['', '| Benchmark | Configuration | Solved / attempts | Ungraded | Tokens / solve | LLM USD / solve | Agent seconds / solve | Timeouts |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    for key,s in summary.items():
        def show(value,complete):
            return 'TBD' if value is None else ('' if complete else '≥')+f'{value:.3f}'
        # Zero observed usage with incomplete telemetry gives no usable token estimate.
        tokens=show(s['tokens_per_solve'],s['tokens_complete']) if s['tokens_complete'] or s['observed_tokens'] else 'TBD'
        benchmark, _, config = key.partition(' / ')
        lines.append(f'| {benchmark} | {config} | {s["solved"]}/{s["attempts"]} | {s["ungraded"]} | {tokens} | {show(s["dollars_per_solve"],s["cost_complete"])} | {show(s["seconds_per_solve"],s["wall_seconds_complete"])} | {s["timeouts"]} |')
    lines += ['', 'Costs include every attempt. Ungraded attempts have unknown quality; they are not excluded from the displayed denominator. ≥ indicates incomplete telemetry; TBD means unknown. Scheduling seeds do not set model sampling seeds.', '']
    (path/'summary.md').write_text('\n'.join(lines))
    print('\n'.join(lines))

@output_lock
def recover(path):
    for attempt in sorted(path.glob('*/attempt.json')):
        out=attempt.parent
        if (out/'result.json').exists():
            continue
        record=json.loads(attempt.read_text())
        for name in (record['container_name'],record['container_name']+'-grade'):
            subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for log in out.glob('*.log'):
            log.chmod(0o600)
            log.write_text(redact(log.read_text(errors='replace')))
        record.update(status='interrupted',solved=None,elapsed_seconds=None,cost_usd=None,
                      usage_complete=False,token_semantics='unknown',usage_source='TBD')
        write_new(out/'result.json',record)
    report(path)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    f=sub.add_parser('freeze'); f.add_argument('spec',type=Path); f.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('run'); r.add_argument('plan',type=Path); r.add_argument('--output',type=Path,required=True); r.add_argument('--env-file',type=Path); r.add_argument('--agent-env',action='append',default=[],help='AGENT=/private/file.env; repeat for multi-agent plans')
    s=sub.add_parser('report'); s.add_argument('output',type=Path)
    k=sub.add_parser('recover'); k.add_argument('output',type=Path)
    a=p.parse_args()
    if a.cmd=='freeze': freeze(a)
    elif a.cmd=='run': execute(a)
    elif a.cmd=='recover': recover(a.output)
    else: report(a.output)

if __name__=='__main__': main()
