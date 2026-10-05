"""Selected gold/starter controls only; opaque logs, no agents or model calls."""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
ADAPTER = ROOT.parents[1] / 'benchmarks/polyglot.py'
SOURCE = pathlib.Path('/tmp/solpi-polyglot-grader-source')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)

def main():
    selection = ROOT / 'polyglot-selection.json'
    launch = ROOT / 'polyglot-controls-launch.json'
    if launch.exists():
        raise RuntimeError('Already launched; no automatic rerun')
    spec = importlib.util.spec_from_file_location('g1_polyglot', ADAPTER)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    private = pathlib.Path('/tmp/solpi-g1-polyglot-controls-' + uuid.uuid4().hex[:12])
    private.mkdir(mode=0o700)
    plan = {'selection_sha256': sha(selection), 'adapter_sha256': sha(ADAPTER), 'grader_sha256': sha(ADAPTER.with_name('polyglot_grade.py')), 'source_revision': adapter.REVISION, 'maximum_controls': 18, 'per_control_seconds': 300, 'global_seconds': 5400, 'cpus': 1, 'memory_bytes': 2147483648, 'scratch_bytes': 1073741824, 'network': 'none', 'model_calls': 0, 'automatic_retries': 0}
    with launch.open('x') as handle:
        json.dump({'private_root': str(private), 'pid': os.getpid(), 'plan': plan}, handle, indent=2)
    rows = []
    started = time.monotonic()
    try:
        for task in json.loads(selection.read_text())['selected_tasks']:
            language = task['language']
            row = {'task': task['id'], 'controls': [], 'model_calls': 0}
            rows.append(row)
            if language not in adapter.COMMANDS:
                row['status'] = 'Unsupported language in existing official-test adapter; task retained, not substituted'
                save(ROOT / 'polyglot-controls-progress.json', rows)
                continue
            image_tag = 'sol-pi-eval-polyglot-java-login:2026-10-04' if language == 'java' else 'sol-pi-eval-polyglot-login:2026-10-04' if language in ('go', 'python') else 'sol-pi-eval-polyglot-multilingual-login:2026-10-04'
            image = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', image_tag], text=True, timeout=15).strip()
            output = private / (language + '-' + task['id'].split('/')[-1])
            manifest = adapter.prepare(SOURCE, task['id'], output)
            row.update(image_id=image, manifest_sha256=sha(output / 'manifest.json'), private_preparation=str(output))
            for mode in ('workspace', 'reference'):
                remaining = plan['global_seconds'] - (time.monotonic() - started)
                if remaining <= 0:
                    row['status'] = 'Global control budget expired'
                    return
                name = 'solpi-g1-grade-' + uuid.uuid4().hex[:12]
                log = output / (mode + '.private.log')
                command = ['docker', 'run', '--rm', '--name', name, '--network', 'none', '--cpus', '1', '--memory', '2g', '--pids-limit', '512', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--read-only', '--tmpfs', '/tmp:rw,exec,size=1g', '-e', 'HOME=/tmp', '-e', 'GOCACHE=/tmp/go-cache', '--entrypoint', 'python3', '-v', str(output / mode) + ':/workspace:ro', '-v', str(output / 'grader') + ':/grader:ro', image, '/grader/grade.py']
                if mode == 'reference':
                    command.append('--reference-control')
                result = {'mode': mode, 'container_name': name, 'expected_exit': 0 if mode == 'reference' else 1}
                row['controls'].append(result)
                save(ROOT / 'polyglot-controls-progress.json', rows)
                start = time.monotonic()
                try:
                    with log.open('xb') as handle:
                        os.chmod(log, 0o600)
                        process = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, timeout=min(300, remaining))
                    result['exit_code'] = process.returncode
                except subprocess.TimeoutExpired:
                    result['timeout'] = True
                    result['exit_code'] = None
                finally:
                    subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30)
                    gone = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, timeout=10)
                    result.update(seconds=time.monotonic() - start, private_log_sha256=sha(log), owned_container_absent=gone.returncode != 0 and 'No such' in gone.stderr)
                    save(ROOT / 'polyglot-controls-progress.json', rows)
                if not result['owned_container_absent']:
                    raise RuntimeError('Owned grader cleanup uncertain')
            row['valid_pair'] = all(c['exit_code'] == c['expected_exit'] and c['owned_container_absent'] for c in row['controls'])
            save(ROOT / 'polyglot-controls-progress.json', rows)
    finally:
        save(ROOT / 'polyglot-controls-result.json', {'rows': rows, 'all_nine_pairs_valid': len(rows) == 9 and all(r.get('valid_pair') for r in rows), 'model_calls': 0, 'model_traces_read': False, 'raw_grader_logs_private': True, 'seconds': time.monotonic() - started})
    print('Polyglot controls finished; inspect structured grades only, not private logs.')

if __name__ == '__main__':
    main()
