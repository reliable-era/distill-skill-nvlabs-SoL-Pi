"""Original selected Terminal-Bench gold/no-op controls, no model agent."""
import hashlib
import json
import os
import pathlib
import subprocess
import time
import tomllib
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = pathlib.Path('/tmp/solpi-refinement-terminal-bench-2')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)

def execute(name, command, log, seconds):
    with log.open('xb') as stream:
        os.chmod(log, 0o600)
        try:
            result = subprocess.run(['docker', 'exec', name, *command], stdout=stream, stderr=subprocess.STDOUT, timeout=seconds)
            return {'exit_code': result.returncode, 'log_sha256': sha(log)}
        except subprocess.TimeoutExpired:
            return {'exit_code': None, 'timeout': True, 'log_sha256': sha(log)}

def main():
    launch = ROOT / 'terminal-controls-launch.json'
    if launch.exists():
        raise RuntimeError('No automatic control restart')
    cache = json.loads((ROOT / 'terminal-images-result.json').read_text())
    assert cache['all_cached']
    private = pathlib.Path('/tmp/solpi-g1-terminal-controls-' + uuid.uuid4().hex[:12])
    private.mkdir(mode=0o700)
    plan = {'maximum_controls': 18, 'global_seconds': 21600, 'automatic_retries': 0, 'model_agent_calls': 0, 'resources': 'Original task.toml CPU, memory and verifier time limits; no GPU', 'gold_seconds': 'Original task agent timeout, maximum 3600', 'network': 'Default Docker bridge for original public dependency acquisition; no model credentials or host config mounted', 'logs': 'Private, hashes and structured reward only exported'}
    with launch.open('x') as handle:
        json.dump({'pid': os.getpid(), 'private_root': str(private), 'runner_sha256': sha(pathlib.Path(__file__)), 'plan': plan}, handle, indent=2)
    rows = []
    started = time.monotonic()
    try:
        for task in cache['rows']:
            source = SOURCE / task['task']
            metadata = tomllib.loads((source / 'task.toml').read_text())
            environment = metadata['environment']
            hashes = {str(p.relative_to(source)): sha(p) for area in ['tests', 'solution'] for p in (source / area).rglob('*') if p.is_file()}
            row = {'task': task['task'], 'image_id': task['image_id'], 'source_hashes': hashes, 'controls': [], 'model_agent_calls': 0}
            rows.append(row)
            for mode in ['nop', 'gold']:
                if time.monotonic() - started >= 21600:
                    return
                directory = private / task['task'] / mode
                logs = directory / 'logs'
                (logs / 'verifier').mkdir(parents=True)
                # Only this empty writable grader-output endpoint is accessible
                # to the container. No private gold logs are exposed to actors.
                logs.chmod(0o777)
                (logs / 'verifier').chmod(0o777)
                name = 'solpi-g1-tb-control-' + uuid.uuid4().hex[:12]
                control = {'mode': mode, 'container_name': name, 'expected_reward': '1' if mode == 'gold' else '0'}
                row['controls'].append(control)
                save(ROOT / 'terminal-controls-progress.json', rows)
                created = False
                try:
                    command = ['docker', 'create', '--pull=never', '--name', name, '--cpus', str(environment['cpus']), '--memory', str(environment['memory_mb']) + 'm', '--pids-limit', '512', '--security-opt', 'no-new-privileges', '-v', str(source / 'tests') + ':/tests:ro', '-v', str(source / 'solution') + ':/solution:ro', '-v', str(logs) + ':/logs', '--entrypoint', '/bin/sh', task['image_id'], '-c', 'sleep infinity']
                    subprocess.run(command, capture_output=True, check=True, timeout=15)
                    created = True
                    subprocess.run(['docker', 'start', name], capture_output=True, check=True, timeout=15)
                    if mode == 'gold':
                        control['oracle'] = execute(name, ['bash', '/solution/solve.sh'], directory / 'oracle.private.log', min(3600, metadata.get('agent', {}).get('timeout_sec', 3600)))
                        if control['oracle']['exit_code'] != 0:
                            control['classification'] = 'Original gold execution failed; retained'
                        if control['oracle'].get('timeout'):
                            raise RuntimeError('Gold timeout; stop owned container before any verifier')
                    control['verifier'] = execute(name, ['bash', '/tests/test.sh'], directory / 'verifier.private.log', metadata['verifier']['timeout_sec'])
                    reward = logs / 'verifier/reward.txt'
                    control['reward'] = reward.read_text().strip() if reward.exists() else None
                    control['valid_expected_reward'] = control['reward'] == control['expected_reward'] and control['verifier'].get('timeout') is not True and (mode == 'nop' or control['oracle']['exit_code'] == 0)
                    ctrf = logs / 'verifier/ctrf.json'
                    if ctrf.exists():
                        events = json.loads(ctrf.read_text()).get('results', {}).get('tests', [])
                        control['test_events'] = len(events)
                except Exception as error:
                    control.update(error_type=type(error).__name__, classification='Control infrastructure failure; retained')
                finally:
                    if created:
                        subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30)
                    gone = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, timeout=10)
                    control['owned_container_absent'] = gone.returncode != 0 and 'No such' in gone.stderr
                    save(ROOT / 'terminal-controls-progress.json', rows)
                if not control['owned_container_absent']:
                    raise RuntimeError('Owned control cleanup uncertain')
            row['valid_pair'] = all(c.get('valid_expected_reward') and c['owned_container_absent'] for c in row['controls'])
            assert hashes == {str(p.relative_to(source)): sha(p) for area in ['tests', 'solution'] for p in (source / area).rglob('*') if p.is_file()}
            save(ROOT / 'terminal-controls-progress.json', rows)
    finally:
        save(ROOT / 'terminal-controls-result.json', {'rows': rows, 'all_nine_pairs_valid': len(rows) == 9 and all(r.get('valid_pair') for r in rows), 'model_agent_calls': 0, 'model_traces_read': False, 'private_root': str(private), 'seconds': time.monotonic() - started})

if __name__ == '__main__':
    main()
