#!/usr/bin/env python3
"""Offline Docker starter/reference checks; no inference, no scored results."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, action='append', required=True)
    parser.add_argument('--image', required=True)
    parser.add_argument('--grader-mount', choices=['/grader', '/grade'], default='/grader')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image_id = subprocess.check_output(['docker', 'image', 'inspect', args.image, '--format', '{{.Id}}'], text=True).strip()
    rows = []
    for task in args.prepared:
        task = task.resolve()
        manifest = json.loads((task / 'manifest.json').read_text())
        for kind in ('workspace', 'reference'):
            command = ['docker', 'run', '--rm', '--network', 'none', '--user', '0', '--read-only',
                       '--tmpfs', '/tmp:rw,exec,size=512m', '-e', 'HOME=/tmp', '-e', 'GOCACHE=/tmp/go-cache',
                       '--mount', 'type=bind,src=' + str(task / kind) + ',dst=/workspace,readonly',
                       '--mount', 'type=bind,src=' + str(task / 'grader') + ',dst=' + args.grader_mount + ',readonly',
                       image_id, 'python3', args.grader_mount + '/grade.py']
            start = time.monotonic()
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=240)
            rows.append({'task_id': manifest['task_id'], 'kind': kind, 'exit_code': result.returncode,
                         'expected_exit_code': 1 if kind == 'workspace' else 0,
                         'wall_seconds': round(time.monotonic() - start, 3), 'stdout': result.stdout,
                         'manifest_sha256': hashlib.sha256((task / 'manifest.json').read_bytes()).hexdigest()})
    record = {'schema_version': 1, 'kind': 'grader sanity only, no model inference', 'image_id': image_id,
              'dataset_revision': manifest['dataset_revision'], 'checks': rows,
              'passed': all(row['exit_code'] == row['expected_exit_code'] for row in rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'passed': record['passed'], 'checks': len(rows)}))
    if not record['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
