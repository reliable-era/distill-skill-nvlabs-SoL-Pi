#!/usr/bin/env python3
"""Authorized one-shot transition watcher; never retries a terminal transition."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[2]
PID = 1027961
STATUS = PREP / 'watch-transition-status.json'

def alive(pid):
    try:
        return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0] != 'Z'
    except FileNotFoundError:
        return False

def record(state, **details):
    data = {'watcher_pid': os.getpid(), 'heldout_pid': PID, 'state': state, 'updated_at': time.time(), **details}
    tmp = STATUS.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(tmp, STATUS)
    print(json.dumps(data), flush=True)

def main():
    # The attempt marker is written before invocation; even a crash cannot trigger a retry.
    attempted = PREP / 'watch-transition-attempt.json'
    if attempted.exists():
        record('terminal_error', error='Attempt marker exists; audit manually, no automatic retry')
        return 1
    record('waiting', poll_seconds=30)
    while alive(PID):
        time.sleep(30)
        record('waiting', poll_seconds=30)
    record('heldout_terminal')
    cmd = [str(ROOT / 'eval/.venv/bin/python'), str(PREP / 'transition_v4.py'), '--execute-authorized']
    with attempted.open('x') as output:
        json.dump({'attempted_at': time.time(), 'command': cmd, 'authorization': 'Root reviewed transition_v4.py and explicitly authorized exactly one guarded transition after all60 valid heldout grades, PID terminal, and lock free.'}, output, indent=2)
    try:
        result = subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL)
        if result.returncode:
            record('terminal_error', error='Guarded transition failed; no retry or model restart', transition_exit_code=result.returncode)
            return 1
        metadata = ROOT / 'eval/pruned/real-swe-v4-process.json'
        launched = json.loads(metadata.read_text())
        record('transition_complete', real_swe=launched)
        return 0
    except BaseException as error:
        record('terminal_error', error=repr(error), retry=False)
        return 1

if __name__ == '__main__':
    sys.exit(main())
