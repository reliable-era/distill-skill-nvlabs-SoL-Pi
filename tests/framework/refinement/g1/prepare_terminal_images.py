"""Bounded selected image cache preparation only. No actor or grader calls."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parent

def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)

def main():
    launch = ROOT / 'terminal-images-launch.json'
    if launch.exists():
        raise RuntimeError('No automatic repeat of image preparation')
    private = pathlib.Path('/tmp/solpi-g1-image-prep-' + uuid.uuid4().hex[:12])
    private.mkdir(mode=0o700)
    docker_root = pathlib.Path(subprocess.check_output(['docker', 'info', '--format', '{{.DockerRootDir}}'], text=True, timeout=15).strip())
    disks = {p.stat().st_dev: p for p in [private, docker_root]}
    before = {device: shutil.disk_usage(path).free for device, path in disks.items()}
    plan = {'maximum_pulls': 9, 'concurrent_pulls': 1, 'per_pull_seconds': 300, 'global_seconds': 3000, 'minimum_free_bytes': 40 * 1024**3, 'maximum_growth_bytes': 32 * 1024**3, 'automatic_retries': 0, 'model_calls': 0, 'source': 'Frozen task.toml docker_image references'}
    with launch.open('x') as handle:
        json.dump({'pid': os.getpid(), 'private_root': str(private), 'plan': plan}, handle, indent=2)
    rows = []
    start = time.monotonic()
    for task in json.loads((ROOT / 'terminal-environment-inventory.json').read_text())['tasks']:
        current = {device: shutil.disk_usage(path).free for device, path in disks.items()}
        if min(current.values()) < plan['minimum_free_bytes'] or sum(max(0, before[d] - current[d]) for d in disks) > plan['maximum_growth_bytes']:
            save(ROOT / 'terminal-images-result.json', {'rows': rows, 'stop': 'Disk guard; no task substitution', 'model_calls': 0})
            return
        remaining = plan['global_seconds'] - (time.monotonic() - start)
        if remaining <= 0:
            break
        image = task['environment_metadata']['docker_image']
        row = {'task': task['task'], 'declared_image': image, 'status': 'pull_started'}
        rows.append(row)
        save(ROOT / 'terminal-images-progress.json', rows)
        log = private / (task['task'] + '.private.log')
        try:
            with log.open('xb') as handle:
                os.chmod(log, 0o600)
                result = subprocess.run(['docker', 'pull', image], stdout=handle, stderr=subprocess.STDOUT, timeout=min(300, remaining))
            row['pull_exit'] = result.returncode
            if result.returncode == 0:
                inspected = json.loads(subprocess.check_output(['docker', 'image', 'inspect', image], timeout=15))[0]
                row.update(status='cached', image_id=inspected['Id'], repo_digests=inspected['RepoDigests'], size_bytes=inspected['Size'])
            else:
                row['status'] = 'pull_failed; retain selected task'
        except subprocess.TimeoutExpired:
            row['status'] = 'pull_timeout; completion uncertain; no retry'
        finally:
            row['private_log_sha256'] = hashlib.sha256(log.read_bytes()).hexdigest()
            save(ROOT / 'terminal-images-progress.json', rows)
        if 'timeout' in row['status']:
            break
    save(ROOT / 'terminal-images-result.json', {'rows': rows, 'all_cached': len(rows) == 9 and all(r['status'] == 'cached' for r in rows), 'seconds': time.monotonic() - start, 'model_calls': 0, 'environment_controls_not_yet_run': True})

if __name__ == '__main__':
    main()
