#!/usr/bin/env python3
"""Prepare original SWE source and public issue prompt; gold never enters actor.

Input is a private pinned dataset JSON, not vendored here. Official image may
have a setup commit after base_commit: explicitly restore original revision.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import re
import uuid


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--instance', required=True)
    p.add_argument('--image', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('Refuse to overwrite prepared source')
    rows = json.loads(a.dataset.read_text())
    selected = [r for r in rows if r['instance_id'] == a.instance]
    if len(selected) != 1:
        p.error('Expected one exact dataset instance')
    r = selected[0]
    if not re.fullmatch(r'[0-9a-f]{40}', r['base_commit']):
        p.error('Dataset base_commit must be a full Git SHA')
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', a.image]))[0]
    a.output.mkdir(parents=True)
    name = 'solpi-swe-prepare-' + uuid.uuid4().hex[:12]
    try:
        subprocess.run(['docker', 'create', '--name', name, '--network', 'none',
                        a.image, 'git', '-C', '/testbed', 'checkout', '--detach',
                        r['base_commit']], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['docker', 'start', '-a', name], check=True)
        state = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]['State']
        if state['ExitCode'] != 0:
            raise RuntimeError('Original revision restoration failed')
        subprocess.run(['docker', 'cp', name + ':/testbed/.', str(a.output / 'workspace')], check=True)
    finally:
        subprocess.run(['docker', 'rm', '-f', name], stdout=subprocess.DEVNULL, check=False)
    workspace = a.output / 'workspace'
    commit = subprocess.check_output(['git', '-C', str(workspace), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != r['base_commit']:
        raise RuntimeError('Prepared actor source does not match pinned dataset')
    # Original clone history can contain future fixes. Expose a fresh single
    # snapshot commit, not upstream refs/objects, while keeping git diff usable.
    shutil.rmtree(workspace / '.git')
    subprocess.run(['git', '-C', str(workspace), 'init', '--quiet'], check=True)
    subprocess.run(['git', '-C', str(workspace), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(workspace), '-c', 'user.name=Evaluation',
                    '-c', 'user.email=evaluation@example.invalid', 'commit',
                    '--quiet', '-m', 'Original task snapshot'], check=True)
    prompt = r['problem_statement'] + '\n\nImplement the requested repository repair.\n'
    prompt += 'Python environment: python3 uses the preinstalled testbed environment.\n'
    (a.output / 'prompt.txt').write_text(prompt)
    manifest = {'benchmark': 'swe-bench-verified', 'instance_id': a.instance,
                'base_commit': commit, 'image_id': image['Id'],
                'private_dataset_sha256': hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
                'actor_prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                'gold_in_actor': False, 'upstream_git_history_in_actor': False,
                'actor_snapshot_commit': subprocess.check_output(['git', '-C', str(workspace), 'rev-parse', 'HEAD'], text=True).strip(), 'grading': 'Official swebench harness, separate Docker',
                'dataset_revision': 'TBD: supply external frozen provenance alongside this manifest'}
    (a.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Original source and public issue prepared; gold remains private.')


if __name__ == '__main__':
    main()
