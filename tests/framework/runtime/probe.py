"""Offline installation probes; never invokes a model or reads credentials."""
import concurrent.futures
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent

def probe(agent):
    results = []
    for command in (agent['version_command'], [agent['executable'], '--help']):
        process = subprocess.run(['docker', 'run', '--init', '--rm', '--network', 'none', agent['image'], *command], text=True, capture_output=True, timeout=90)
        results.append({'command': command, 'exit_code': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr})
    return {'id': agent['id'], 'image': agent['image'], 'probes': results}

if __name__ == '__main__':
    agents = json.loads((ROOT / 'agents.json').read_text())['agents']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(probe, agents))
    data = {'network': 'none', 'model_requests': 0, 'agents': results}
    (ROOT / 'runtime' / 'installation-check.json').write_text(json.dumps(data, indent=2) + '\n')
    for agent in results:
        print(agent['id'], 'PASS' if all(x['exit_code'] == 0 for x in agent['probes']) else 'FAIL')
    raise SystemExit(any(x['exit_code'] != 0 for agent in results for x in agent['probes']))
