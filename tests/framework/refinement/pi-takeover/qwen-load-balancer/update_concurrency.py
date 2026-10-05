"""Drain and update the two owned gpu02 replicas, preserving Docker settings."""
import datetime
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'nginx.conf'
PREFIX = '/tmp/solpi-qwen-load-balancer-18080/'
STAMP = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
PRIVATE = Path('/tmp/solpi-qwen-concurrency-' + STAMP)
PRIVATE.mkdir(mode=0o700)


def docker(*args):
    return subprocess.check_output(['docker', *args], timeout=300).decode().strip()


def get(port, path):
    c = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    try:
        c.request('GET', path)
        r = c.getresponse()
        assert r.status == 200, (port, path, r.status)
        return json.loads(r.read())
    finally:
        c.close()


def reload_nginx():
    cmd = ['/usr/sbin/nginx', '-p', PREFIX, '-c', str(CONFIG)]
    subprocess.run(cmd + ['-t'], check=True)
    subprocess.run(cmd + ['-s', 'reload'], check=True)


class DockerHTTP(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(120)
        self.sock.connect('/var/run/docker.sock')


results = []
for name, port in [('jev-pi-qwen38-replica-20261004-nccl-only', 18001),
                   ('ykw-qwen38-dflash2-tp2', 18002)]:
    old = json.loads(docker('inspect', name))[0]
    args = old['Config']['Cmd']
    assert args[args.index('--port') + 1] == str(port)
    assert args[args.index('--served-model-name') + 1] == 'Qwen3.8-27B-FP8'
    if (args[args.index('--max-running-requests') + 1] == '8'
            and args[args.index('--max-mamba-cache-size') + 1] == '48'):
        print(f'Already configured: {port}', flush=True)
        continue
    original = CONFIG.read_text()
    assert 'server 10.193.104.97:18001 ' in original
    assert 'server 10.193.104.97:18002 ' in original
    pid = int(Path(PREFIX, 'nginx.pid').read_text())
    assert PREFIX.rstrip('/').encode() in Path(f'/proc/{pid}/cmdline').read_bytes()
    saved = PRIVATE / f'{name}.json'
    saved.write_text(json.dumps(old))
    saved.chmod(0o600)
    original_line = f'server 127.0.0.1:{port} max_fails=1 fail_timeout=5s;'
    assert original.count(original_line) == 1
    draining = original.replace(original_line, f'server 127.0.0.1:{port} down;')
    backup = name + '-concurrency1-' + STAMP
    created = None
    renamed = False
    try:
        CONFIG.write_text(draining)
        reload_nginx()
        print(f'Draining {name} on {port}', flush=True)
        deadline = time.monotonic() + 1800
        idle_samples = 0
        while time.monotonic() < deadline:
            rows = get(port, '/get_load')
            idle = bool(rows) and all(r.get('num_reqs') == 0 and r.get('num_waiting_reqs') == 0 for r in rows)
            idle_samples = idle_samples + 1 if idle else 0
            if idle_samples >= 3:
                break
            print(f'Load {port}: {rows}', flush=True)
            time.sleep(3)
        else:
            raise RuntimeError(f'Drain timeout for {port}')
        # Idle and removed from nginx: preserve its writable layer before replacing it.
        docker('stop', '-t', '30', name)
        image = docker('commit', name)
        docker('rename', name, backup)
        renamed = True
        docker('update', '--restart', 'no', backup)
        config = dict(old['Config'])
        config['Image'] = image
        config['Cmd'] = list(args)
        config['Cmd'][config['Cmd'].index('--max-running-requests') + 1] = '8'
        config['Cmd'][config['Cmd'].index('--max-mamba-cache-size') + 1] = '48'
        config['Env'] = [e for e in config['Env'] if not e.startswith('PYTHONDONTWRITEBYTECODE=')]
        config['Env'].append('PYTHONDONTWRITEBYTECODE=1')
        config.pop('Hostname', None)
        config['HostConfig'] = dict(old['HostConfig'])
        config['HostConfig']['RestartPolicy'] = {'Name': 'unless-stopped', 'MaximumRetryCount': 0}
        c = DockerHTTP('docker')
        c.request('POST', '/v1.41/containers/create?name=' + name, json.dumps(config), {'Content-Type': 'application/json'})
        response = c.getresponse()
        body = json.loads(response.read())
        c.close()
        assert response.status == 201, (response.status, body)
        created = body['Id']
        docker('start', created)
        print(f'Starting {port} with max-running-requests=8, max-mamba-cache-size=48', flush=True)
        deadline = time.monotonic() + 1200
        while time.monotonic() < deadline:
            try:
                info = get(port, '/get_server_info')
                assert info['max_running_requests'] == 8
                assert info['max_mamba_cache_size'] == 48
                state = info['internal_states'][0]
                assert state['effective_max_running_requests_per_dp'] == 8
                models = get(port, '/v1/models')
                assert any(m['id'] == 'Qwen3.8-27B-FP8' for m in models['data'])
                health = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
                try:
                    health.request('GET', '/health')
                    health_response = health.getresponse()
                    health_response.read()
                    assert health_response.status == 200
                finally:
                    health.close()
                break
            except (OSError, ValueError, KeyError, AssertionError, http.client.HTTPException):
                pass
            container = json.loads(docker('inspect', created))[0]
            if not container['State']['Running']:
                raise RuntimeError(f'Updated {port} stopped unexpectedly')
            time.sleep(5)
        else:
            raise RuntimeError(f'Readiness timeout for {port}')
        CONFIG.write_text(original)
        reload_nginx()
        results.append({'container': name, 'port': port, 'backup': backup,
                        'id': created, 'snapshot_image': image,
                        'max_running_requests': 8, 'max_mamba_cache_size': 48,
                        'memory_usage': state['memory_usage']})
        (ROOT / 'gpu02-concurrency-update.json').write_text(json.dumps({'private_backup': str(PRIVATE), 'replicas': results}, indent=2) + '\n')
        print(f'Healthy and restored to nginx: {port}', flush=True)
    except Exception:
        if created:
            docker('rm', '-f', created)
        if renamed:
            docker('rename', backup, name)
            policy = old['HostConfig']['RestartPolicy']['Name'] or 'no'
            docker('update', '--restart', policy, name)
        docker('start', old['Id'])
        CONFIG.write_text(original)
        reload_nginx()
        raise
