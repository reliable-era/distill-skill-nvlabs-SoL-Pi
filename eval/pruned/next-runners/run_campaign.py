#!/usr/bin/env python3
"""Frozen plan -> serial, resumable model jobs and official isolated grades.
Seeds shuffle task/arm order only; backend RNG is not controlled.
"""
import argparse, fcntl, hashlib, importlib.metadata, json, random, subprocess, sys, time
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def grade(run, work, timeout, dataset_name="princeton-nlp/SWE-bench_Verified"):
    if (run / 'graded.json').exists():
        return
    if importlib.metadata.version('swebench') != '4.1.0':
        raise RuntimeError('Official SWE grader must be swebench 4.1.0')
    result = json.loads((run / 'result.json').read_text())
    iid = result['instance_id']
    tag = 'pruned'
    work.mkdir(parents=True, exist_ok=True)
    pred = work / 'prediction.jsonl'
    pred.write_text(json.dumps({'instance_id': iid, 'model_name_or_path': tag,
                               'model_patch': (run / 'patch.diff').read_text()}) + '\n')
    cmd = [sys.executable, '-m', 'swebench.harness.run_evaluation',
           '--dataset_name', str(dataset_name), '--predictions_path', str(pred),
           '--run_id', 'grade', '--instance_ids', iid, '--max_workers', '1',
           '--namespace', 'swebench', '--cache_level', 'instance', '--timeout', str(timeout)]
    started = time.time()
    with (work / 'stdout.txt').open('w') as out, (work / 'stderr.txt').open('w') as err:
        try:
            rc = subprocess.run(cmd, cwd=work, stdout=out, stderr=err, timeout=timeout + 600).returncode
        except subprocess.TimeoutExpired:
            rc = None
    rep = work / 'logs/run_evaluation/grade' / tag / iid / 'report.json'
    audit = {'harness_version': '4.1.0', 'exit_code': rc, 'wall_s': time.time()-started,
             'prediction_sha256': digest(pred), 'report_path': str(rep), 'dataset_name': str(dataset_name)}
    dataset_path = Path(dataset_name)
    if dataset_path.is_file():
        audit['dataset_sha256'] = digest(dataset_path)
    if rep.exists():
        audit.update(resolved=json.loads(rep.read_text())[iid]['resolved'], grade_status='official_report')
    elif not (run / 'patch.diff').read_text().strip():
        audit.update(resolved=False, grade_status='empty_patch')
    else:
        audit.update(resolved=None, grade_status='infrastructure_error')
    (run / 'graded.json').write_text(json.dumps(audit, indent=2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path)
    ap.add_argument('--stage', action='append')
    ap.add_argument('--arm', action='append')
    ap.add_argument('--case', action='append')
    ap.add_argument('--seed', action='append', type=int)
    ap.add_argument('--max-jobs', type=int)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    plan = json.loads(a.plan.read_text())
    root = Path(plan['campaign_root']).resolve()
    binary = Path(plan['claude_bin']).resolve()
    if digest(binary) != plan['claude_sha256']:
        raise RuntimeError('Pinned Claude executable changed')
    for path, expected in plan['file_sha256'].items():
        if digest(Path(path)) != expected:
            raise RuntimeError(f'Frozen source changed: {path}')
    jobs = []
    for stage in plan['stages']:
        if a.stage and stage['name'] not in a.stage: continue
        for seed in stage['seeds']:
            if a.seed and seed not in a.seed: continue
            rng = random.Random(seed)
            for case in rng.sample(stage['cases'], len(stage['cases'])):
                if a.case and case not in a.case: continue
                for label in rng.sample(stage['arms'], len(stage['arms'])):
                    if a.arm and label not in a.arm: continue
                    jobs.append((stage, seed, case, label))
    if a.max_jobs: jobs = jobs[:a.max_jobs]
    if a.dry_run:
        print(json.dumps([(s['name'], seed, case, label) for s, seed, case, label in jobs], indent=2)); return
    root.mkdir(parents=True, exist_ok=True)
    # One queue owns all model requests. No background child survives runner teardown.
    with (EVAL / 'pruned/model.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for stage, seed, case, label in jobs:
            arm = plan['arms'][label]
            runs = root / stage['name'] / label / 'runs'
            cmd = [sys.executable, str(EVAL / ('run_stress.py' if stage['kind']=='stress' else 'run_swe.py')),
                   case, arm['runner_arm'], str(seed), '--skills-root', arm['skills_root'],
                   '--runs-root', str(runs), '--claude-bin', str(binary), '--timeout', str(plan['timeout']),
                   '--max-turns', str(plan['max_turns'])]
            if stage['kind']=='stress': cmd += ['--cases-root', stage['cases_root']]
            print('START', stage['name'], seed, case, label, flush=True)
            rc = subprocess.run(cmd).returncode
            run = runs / ('stress' if stage['kind']=='stress' else 'swebench') / case / arm['runner_arm'] / f'r{seed}'
            if rc == 0 and stage['kind']=='swe': grade(run, root/'grading'/stage['name']/label/f'{case}-{seed}', plan.get('grade_timeout',1800), plan.get('grade_dataset', 'princeton-nlp/SWE-bench_Verified'))
            record = {'stage':stage['name'], 'seed':seed, 'case':case, 'arm':label,
                      'runner_exit':rc, 'run':str(run), 'completed_at':time.time()}
            with (root/'progress.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
            print('DONE', json.dumps(record), flush=True)
            if rc: raise RuntimeError(f'Runner failed with {rc}; stop and audit before resuming')

if __name__ == '__main__': main()
