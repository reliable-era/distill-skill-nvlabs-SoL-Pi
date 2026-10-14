#!/usr/bin/env python3
"""G4 Part A: run the 74 preregistered cells (Pi 0.85.1 + unmodified NVlabs SoL-Pi, all four
mechanisms) on the original 10 diagnostics and 6 SWE-bench issues, through 127.0.0.1:8000.

Task setup, prompts, caps (60 turns, 1800 s) and graders follow the original Claude Code
runners (tests/eval/run_stress.py, run_swe.py, pruned/run_campaign.py). Raw runs go to
RUNS; only the per-cell summary is kept in the repository.
Usage: run_A.py [--slots 8] [--only CELL ...]
"""
import argparse, concurrent.futures, hashlib, json, pathlib, shutil, subprocess, sys, threading, time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import proxy

G4 = REPO / 'tests/framework/refinement/g4'
EVAL = REPO / 'tests/eval'
RUNS = pathlib.Path('/tmp/solpi-g4A-runs')
TEMPLATE = RUNS / 'pi-template'
UPSTREAM = pathlib.Path('/tmp/solpi-g4-upstream')
NODE = pathlib.Path('/home/wangjian/.hermes/node/bin/node')
KARPATHY = REPO / 'tests/framework/refinement/g2/frozen/karpathy'
GRADER_PY = '/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/eval/.venv/bin/python'
# Full SWE-bench Verified file: the frozen four-issue subset lacks django-11964 and sympy-12481 (records identical otherwise).
GRADE_DATASET = str(REPO / 'tests/eval/swebench_verified.jsonl')
MODEL, PROVIDER, TIMEOUT = 'Qwen/Qwen3.8-27B', 'g4-route8000', 1800
PI = 'node /solpi/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'
SWE_PROMPT = """<issue>
{problem}
</issue>

The repository at /testbed is checked out at the commit where this issue exists.
Resolve the issue by editing the non-test source files in /testbed. The Python environment is already set up.
Do not modify existing tests. When you are done, stop."""
# Pi counterpart of the original runners' SKILL_HINT; identical in both arms, a no-op without skills.
GRADE_LOCKS = {}  # the SWE harness names containers by instance, so grade one copy of an instance at a time
SKILL_HINT = "\n\nBefore you start, read every skill listed in your available skills (if any) and follow it."


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def run_cell(cell, swe_tasks):
    out = RUNS / cell['cell_id']
    if (out / 'result.json').exists():
        return json.loads((out / 'result.json').read_text())
    if out.exists():
        shutil.rmtree(out)
    (out / 'relay').mkdir(parents=True)
    kind, rest = cell['task'].split('/', 1)
    if kind == 'swe':
        task = swe_tasks[rest]
        image = f"swebench/sweb.eval.x86_64.{rest.replace('__', '_1776_')}:latest"
        workdir, prompt = '/testbed', SWE_PROMPT.format(problem=task['problem_statement'])
    else:
        src = EVAL / 'pruned/diagnostics' / rest
        image, workdir, prompt = 'stress-base:1', '/work', (src / 'prompt.txt').read_text().rstrip()
    (out / 'prompt.txt').write_text(prompt + SKILL_HINT)
    shutil.copytree(TEMPLATE, out / 'home', symlinks=True)
    relay = proxy.Relay(out / 'relay')
    threading.Thread(target=relay.serve_forever, daemon=True).start()
    models = {'providers': {PROVIDER: {
        'baseUrl': f'http://127.0.0.1:{relay.server_address[1]}/v1', 'api': 'openai-completions', 'apiKey': 'dummy',
        'compat': {'supportsDeveloperRole': False},
        'models': [{'id': MODEL, 'reasoning': True, 'contextWindow': 262144, 'maxTokens': 32000}]}}}
    (out / 'home/.pi/agent/models.json').write_text(json.dumps(models))
    name = 'solpi-g4A-' + cell['cell_id'].lower()
    sh(['docker', 'rm', '-f', name])
    mounts = ['-v', f'{out}/home:/pihome', '-v', f'{UPSTREAM}:/solpi:ro', '-v', f'{NODE}:/opt/node/node:ro',
              '-v', f'{KARPATHY}:/skills/karpathy:ro']
    subprocess.run(['docker', 'run', '-d', '--name', name, '--network', 'host', '-e', 'HOME=/pihome', *mounts,
                    image, 'sleep', 'infinity'], check=True, capture_output=True)
    try:
        if kind == 'swe':
            sh(['docker', 'exec', name, 'git', '-C', '/testbed', 'reset', '--hard', task['base_commit']], check=True)
            sh(['docker', 'exec', name, 'git', '-C', '/testbed', 'clean', '-fd'], check=True)
            head = sh(['docker', 'exec', name, 'git', '-C', '/testbed', 'rev-parse', 'HEAD'], check=True).stdout.strip()
            assert head == task['base_commit'], head
            activate = 'source /opt/miniconda3/bin/activate testbed && '
        else:
            sh(['docker', 'cp', str(src / 'repo'), f'{name}:/work'], check=True)
            sh(['docker', 'exec', name, 'bash', '-c',
                'chown -R root:root /work && cd /work && git init -q && git add -A && '
                "git -c user.email=e@e -c user.name=e commit -qm init && printf '__pycache__/\\n' >> .git/info/exclude"],
               check=True)
            activate = ''
        sh(['docker', 'cp', str(out / 'prompt.txt'), f'{name}:/tmp/prompt.txt'], check=True)
        skills = '--no-skills' + (' --skill /skills/karpathy' if cell['arm'] == 'solpi_K' else '')
        cmd = (f'{activate}export PATH=/opt/node:$PATH && cd {workdir} && {PI} --mode json --provider {PROVIDER} '
               f'--model {MODEL} --thinking medium {skills} "$(cat /tmp/prompt.txt)"')
        t0, timed_out = time.time(), False
        with open(out / 'pi.jsonl', 'w') as f, open(out / 'stderr.txt', 'w') as e:
            try:
                rc = subprocess.run(['docker', 'exec', name, 'bash', '-c', cmd], stdout=f, stderr=e, timeout=TIMEOUT).returncode
            except subprocess.TimeoutExpired:
                timed_out, rc = True, None
        wall = time.time() - t0
        sh(['docker', 'exec', name, 'pkill', '-f', 'cli.js'])
        relay.shutdown()
        if kind == 'swe':
            diff = sh(['docker', 'exec', name, 'bash', '-c', 'cd /testbed && git config core.fileMode false && '
                       f"git add -A && git diff --cached {task['base_commit']}"]).stdout
        else:
            diff = sh(['docker', 'exec', name, 'bash', '-c',
                       'cd /work && git config core.fileMode false && git add -A && git diff --cached']).stdout
        (out / 'patch.diff').write_text(diff)
        grade = {}
        if kind == 'diagnostic':
            sh(['docker', 'cp', str(src / 'hidden/test_hidden.py'), f'{name}:/work/test_hidden.py'], check=True)
            try:
                g = sh(['docker', 'exec', name, 'bash', '-c', 'cd /work && python -m pytest -q -p no:cacheprovider test_hidden.py'],
                       timeout=120)
                grade = dict(resolved=g.returncode == 0, grade_exit_code=g.returncode, grade_timed_out=False)
                (out / 'grade.txt').write_text(g.stdout + g.stderr)
            except subprocess.TimeoutExpired:
                grade = dict(resolved=False, grade_exit_code=124, grade_timed_out=True)
    finally:
        sh(['docker', 'exec', name, 'chown', '-R', '1003:1003', '/pihome'])
        sh(['docker', 'rm', '-f', name])
    if kind == 'swe':
        # Original official grader (swebench 4.1.0, run_campaign.grade) on its own run-shaped folder.
        gr = out / 'grade-run'
        gr.mkdir()
        (gr / 'result.json').write_text(json.dumps({'instance_id': rest}))
        shutil.copy(out / 'patch.diff', gr / 'patch.diff')
        code = 'import sys,pathlib;sys.path.insert(0,sys.argv[1]);from run_campaign import grade;grade(pathlib.Path(sys.argv[2]),pathlib.Path(sys.argv[3]),1800,sys.argv[4])'
        with GRADE_LOCKS.setdefault(rest, threading.Lock()):
            sh([GRADER_PY, '-c', code, str(EVAL / 'pruned'), str(gr), str(out / 'grading'), GRADE_DATASET])
        grade = json.loads((gr / 'graded.json').read_text()) if (gr / 'graded.json').exists() else dict(resolved=None, grade_status='grader_crashed')
    recs = relay.records
    model_recs = [r for r in recs if r.get('role') in ('primary', 'helper') and not r.get('cap_refusal')]
    unknown = [r['n'] for r in model_recs if r['usage'] is None]
    result = dict(
        cell_id=cell['cell_id'], task=cell['task'], arm=cell['arm'], round=cell['round'], exit_code=rc,
        timed_out=timed_out, wall_s=round(wall, 1), patch_bytes=len(diff), resolved=grade.get('resolved'), grade=grade,
        primary_requests=sum(r['role'] == 'primary' for r in model_recs),
        helper_requests=sum(r['role'] == 'helper' for r in model_recs),
        turn_cap_hit=any(r.get('cap_refusal') for r in recs),
        total_tokens=sum(r['usage'].get('total_tokens', 0) for r in model_recs if r['usage']),
        helper_tokens=sum(r['usage'].get('total_tokens', 0) for r in model_recs if r['usage'] and r['role'] == 'helper'),
        unknown_cost_requests=unknown, non200=[(r['n'], r['status'], r['upstream']) for r in model_recs if r['status'] != 200],
        response_models=sorted({r['model'] for r in model_recs if r['model']}),
        upstreams=sorted({r['upstream'] for r in model_recs if r['upstream']}),
        first_request_tools=next((r.get('tools') for r in recs if r.get('n') == 1), None),
        image=image, prompt_sha256=sha(out / 'prompt.txt'), skill_sha256=sha(KARPATHY / 'SKILL.md') if cell['arm'] == 'solpi_K' else None,
        reached_model=bool(model_recs))
    (out / 'result.json').write_text(json.dumps(result, indent=1))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slots', type=int, default=8)
    ap.add_argument('--only', nargs='*')
    a = ap.parse_args()
    cells = json.loads((G4 / 'queue-order.json').read_text())['parts']['A']
    assert len(cells) == 74
    if a.only:
        cells = [c for c in cells if c['cell_id'] in a.only]
    swe_tasks = {t['instance_id']: t for t in map(json.loads, open(EVAL / 'swebench_verified.jsonl'))}

    def job(cell):
        try:
            res = run_cell(cell, swe_tasks)
        except Exception as e:
            print(json.dumps({'cell_id': cell['cell_id'], 'runner_error': repr(e)}), flush=True)
            return {'cell_id': cell['cell_id'], 'resolved': None, 'runner_error': repr(e)}
        if not res['reached_model'] and not res.get('infra_rerun'):
            # Never reached the model: infrastructure failure, rerun once from scratch.
            shutil.move(str(RUNS / cell['cell_id']), str(RUNS / (cell['cell_id'] + '.infra-attempt1')))
            res = run_cell(cell, swe_tasks)
            res['infra_rerun'] = True
            (RUNS / cell['cell_id'] / 'result.json').write_text(json.dumps(res, indent=1))
        print(json.dumps({k: res[k] for k in ('cell_id', 'task', 'arm', 'resolved', 'total_tokens', 'primary_requests',
                                               'helper_requests', 'wall_s', 'timed_out', 'non200')}), flush=True)
        return res

    with concurrent.futures.ThreadPoolExecutor(a.slots) as ex:
        results = list(ex.map(job, cells))
    print('DONE', len(results), 'cells', sum(bool(r['resolved']) for r in results), 'resolved', flush=True)


if __name__ == '__main__':
    main()
