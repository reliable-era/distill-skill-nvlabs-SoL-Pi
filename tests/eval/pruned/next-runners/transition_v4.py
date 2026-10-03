#!/usr/bin/env python3
"""Prepare only by default. Root authorization is required for --execute-authorized."""
import argparse
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
PREP = Path(__file__).resolve().parent
V3 = ROOT / 'eval/pruned/plan.v3-heldout.json'
V4 = ROOT / 'eval/pruned/plan.v4-real-swe.json'
PYTHON = ROOT / 'eval/.venv/bin/python'
HELDOUT_PID = 1027961

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic(path, data):
    tmp = path.with_name(path.name + '.transition-tmp')
    tmp.write_bytes(data)
    os.replace(tmp, path)

def pid_live(pid):
    try:
        stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0]
        return stat != 'Z'
    except FileNotFoundError:
        return False

def verify_hashes(pins):
    for path, expected in pins.items():
        if sha(path) != expected:
            raise RuntimeError(f'Hash mismatch: {path}')

def verify_complete(plan):
    if pid_live(HELDOUT_PID):
        raise RuntimeError(f'Heldout PID {HELDOUT_PID} is still live')
    stage = next(s for s in plan['stages'] if s['name'] == 'heldout')
    checked = []
    for seed in stage['seeds']:
        for case in stage['cases']:
            for label in stage['arms']:
                arm = plan['arms'][label]['runner_arm']
                run = Path(plan['campaign_root']) / 'heldout' / label / 'runs/stress' / case / arm / f'r{seed}'
                result = json.loads((run / 'result.json').read_text())
                if (result.get('case'), result.get('arm'), result.get('round')) != (case, arm, seed):
                    raise RuntimeError(f'Wrong cell identity: {run}')
                if type(result.get('resolved')) is not bool or result.get('grade_timed_out') is not False:
                    raise RuntimeError(f'Invalid grade: {run}')
                if result.get('grade_exit_code') != (0 if result['resolved'] else 1):
                    raise RuntimeError(f'Inconsistent grade: {run}')
                if not (run / 'grade.txt').is_file():
                    raise RuntimeError(f'Missing grade output: {run}')
                checked.append(str(run))
    if len(checked) != 60:
        raise RuntimeError(f'Expected 60 cells, got {len(checked)}')
    return checked

def candidate_plan(plan, manifest, archive):
    new = copy.deepcopy(plan)
    for source, entry in manifest.items():
        new['file_sha256'][source] = entry['new_sha256']
        new['file_sha256'][str(archive / Path(source).name)] = entry['old_sha256']
    new['execution_authorization'] = 'Root authorized real_swe only after all 60 heldout grades completed and guarded pristine-runner transition verified. Execute 32 fixed cells serially under model.lock; no other stages or model jobs.'
    new['real_swe_protocol'] = 'Restore /testbed with git reset --hard task base_commit and git clean -fd; verify exact HEAD and clean porcelain before Claude; retain activated testbed environment. Grade with swebench 4.1.0 using pinned local grade_dataset JSONL; record dataset SHA. Frozen tasks, arms, seeds, skills and limits are unchanged.'
    assert new['stages'] == plan['stages'] and new['arms'] == plan['arms']
    for key, value in plan.items():
        if key not in ('file_sha256', 'execution_authorization'):
            assert new[key] == value
    return new

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-authorized', action='store_true', help='Use only after explicit root review and authorization; installs and launches model queue')
    args = parser.parse_args()
    plan = json.loads(V3.read_text())
    manifest = json.loads((PREP / 'manifest.json').read_text())
    if len(plan['file_sha256']) != 141 or len(manifest) != 2:
        raise RuntimeError('Unexpected pin or runner count')
    verify_hashes(plan['file_sha256'])
    if sha(plan['claude_bin']) != plan['claude_sha256']:
        raise RuntimeError('Claude binary changed')
    for source, entry in manifest.items():
        if plan['file_sha256'][source] != entry['old_sha256'] or sha(entry['copy']) != entry['new_sha256']:
            raise RuntimeError(f'Runner provenance mismatch: {source}')
        py_compile.compile(entry['copy'], doraise=True)
    archive = ROOT / 'eval/pruned/runner-archive/pre-v4'
    new = candidate_plan(plan, manifest, archive)
    preview = PREP / 'plan.v4-preview.json'
    atomic(preview, (json.dumps(new, indent=2) + '\n').encode())
    if not args.execute_authorized:
        print(json.dumps({'mode': 'prepare_only', 'v3_pins_verified': 141, 'prepared_runners_verified': 2, 'preview': str(preview), 'heldout_live': pid_live(HELDOUT_PID), 'no_install_or_model_calls': True}, indent=2))
        return
    # Hold the same queue lock while checking completion, installing, and validating.
    with (ROOT / 'eval/pruned/model.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cells = verify_complete(plan)
        # Orphan runners can outlive the lock owner: reject them independently.
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit() or int(proc.name) == os.getpid():
                continue
            try:
                argv = (proc / 'cmdline').read_bytes().split(b'\0')
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            active_drivers = {str(ROOT / 'eval/run_stress.py').encode(), str(ROOT / 'eval/run_swe.py').encode(), str(ROOT / 'eval/pruned/run_campaign.py').encode()}
            if active_drivers.intersection(argv) and pid_live(int(proc.name)):
                raise RuntimeError(f'Active benchmark driver PID {proc.name}; audit before transition')
        verify_hashes(plan['file_sha256'])
        if V4.exists():
            raise RuntimeError('v4 already exists; audit before resuming, never duplicate launch')
        archive.mkdir(parents=True, exist_ok=True)
        originals = {Path(source): Path(source).read_bytes() for source in manifest}
        for source, data in originals.items():
            target = archive / source.name
            if target.exists() and target.read_bytes() != data:
                raise RuntimeError(f'Conflicting archive: {target}')
            atomic(target, data)
        atomic(archive / 'manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
        launched = False
        try:
            for source, entry in manifest.items():
                atomic(Path(source), Path(entry['copy']).read_bytes())
                py_compile.compile(source, doraise=True)
            atomic(V4, (json.dumps(new, indent=2) + '\n').encode())
            verify_hashes(new['file_sha256'])
            cmd = [str(PYTHON), str(ROOT / 'eval/pruned/run_campaign.py'), str(V4), '--stage', 'real_swe']
            dry = subprocess.run(cmd + ['--dry-run'], capture_output=True, text=True, check=True)
            jobs = json.loads(dry.stdout)
            if len(jobs) != 32 or any(j[0] != 'real_swe' for j in jobs):
                raise RuntimeError('Unexpected real_swe schedule')
            atomic(PREP / 'v4-dry-run.json', dry.stdout.encode())
            metadata = ROOT / 'eval/pruned/real-swe-v4-process.json'
            if metadata.exists():
                raise RuntimeError('Existing SWE launch metadata; audit before resuming')
            log = ROOT / 'eval/pruned/real-swe-v4.log'
            # Child starts but waits for this parent to release model.lock.
            with log.open('ab', buffering=0) as output:
                process = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            launched = True
            print(f'LAUNCHED PID {process.pid}; log {log}', flush=True)
            record = {'pid': process.pid, 'command': cmd, 'cwd': str(ROOT), 'log': str(log), 'launched_at': time.time(), 'planned_cells': 32, 'stage': 'real_swe', 'v4_sha256': sha(V4), 'completed_heldout_cells': len(cells)}
            atomic(metadata, (json.dumps(record, indent=2) + '\n').encode())
            os.kill(process.pid, 0)
            print(json.dumps(record, indent=2))
        except BaseException:
            if not launched:
                for source, data in originals.items():
                    atomic(source, data)
                V4.unlink(missing_ok=True)
                verify_hashes(plan['file_sha256'])
            else:
                # Never rollback sources beneath a launched queue or automatically relaunch.
                print('Queue launched: audit actual PID/log before any further action', file=sys.stderr)
            raise

if __name__ == '__main__':
    main()
