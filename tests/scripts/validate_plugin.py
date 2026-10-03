"""Validate the shipped plugin in a fresh, non-root container without model calls."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
assert market['plugins'][0]['name'] == plugin['name']
for relative in plugin['skills']:
    skill = ROOT / relative
    assert (skill / 'SKILL.md').is_file()
    for script in (skill / 'scripts').glob('*.py'):
        compile(script.read_text(), str(script), 'exec')
run('claude', '--version')
run('claude', 'plugin', 'validate', '.')
run('claude', 'plugin', 'validate', '.claude-plugin/plugin.json')
run('claude', 'plugin', 'marketplace', 'add', str(ROOT))
run('claude', 'plugin', 'install', f"{plugin['name']}@{market['name']}")
# Verify the actual installed skill bytes, not just a successful installer exit.
source = ROOT / 'skills/efficient-coding'
installed = list((Path.home() / '.claude/plugins/cache').rglob('skills/efficient-coding/SKILL.md'))
assert installed, 'Installed skill missing from plugin cache'
for original in source.rglob('*'):
    if original.is_file():
        copy = installed[0].parent / original.relative_to(source)
        assert copy.is_file() and copy.read_bytes() == original.read_bytes(), str(copy)
run('python3', str(source / 'scripts/evidence.py'), '--help')
run('python3', str(source / 'scripts/cost_audit.py'), '--help')
print(json.dumps({'status': 'passed', 'installed_skill_sha256': hashlib.sha256(installed[0].read_bytes()).hexdigest(), 'checks': ['manifest validation', 'marketplace registration', 'plugin installation', 'installed resource byte comparison', 'helper compilation and CLI entrypoints'], 'model_calls': 0}))
