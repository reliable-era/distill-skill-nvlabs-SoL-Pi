"""Fresh G1 samples using existing selectors, metadata only; never overwrite."""
import collections
import hashlib
import importlib.util
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
REFINEMENT = ROOT.parent
SEED = 20261006
POLYGLOT_REVISION = '7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def freeze(name, value):
    with (ROOT / name).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write('\n')

def draw():
    terminal = load('g1_terminal_selector', REFINEMENT / 'pi-takeover/select_subset.py')
    previous = json.loads((REFINEMENT / 'pi-takeover/terminal-10pct-selection.json').read_text())
    terminal.EXPOSED = terminal.EXPOSED | {r['id'] for r in previous['selected_tasks']}
    terminal.SEED = SEED
    tb = terminal.select(pathlib.Path('/tmp/solpi-refinement-terminal-bench-2'))
    assert tb['eligible_population'] == 78
    assert tb['selected_size'] == 9
    assert tb['stratum_quotas'] == {'easy': 1, 'medium': 5, 'hard': 3}
    tb['harness'] = 'Codex 0.160.0 only'
    tb['status'] = 'Sealed G1 allocation; gold/no-op controls pending; no model attempts'
    freeze('terminal-selection.json', tb)

    source = pathlib.Path('/tmp/solpi-polyglot-grader-source')
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == POLYGLOT_REVISION
    # Git tree names only: do not read prompts, solutions, tests or .meta contents.
    paths = subprocess.check_output(['git', '-C', str(source), 'ls-tree', '-r', '--name-only', revision], text=True).splitlines()
    rows = []
    for path in paths:
        parts = path.split('/')
        if len(parts) == 6 and parts[1:3] == ['exercises', 'practice'] and parts[-2:] == ['.meta', 'config.json']:
            task = '/'.join(parts[:4])
            rows.append({'id': task, 'canonical_id': 'aider:' + task, 'benchmark': 'aider-polyglot', 'language': parts[0], 'repo': 'Aider-AI/polyglot-benchmark'})
    excluded = {'aider:go/exercises/practice/food-chain', 'aider:javascript/exercises/practice/bowling', 'aider:python/exercises/practice/proverb', 'aider:cpp/exercises/practice/sublist', 'aider:rust/exercises/practice/acronym', 'aider:java/exercises/practice/series'}
    for name in ['confirmation-selection.json', 'confirmation-extension.json']:
        prior = json.loads((REFINEMENT / name).read_text())
        excluded.update(r['canonical_id'] for r in prior['selected_tasks'] if r['benchmark'] == 'aider-polyglot')
    selector_path = REFINEMENT.parent / 'benchmarks/select.py'
    selector = load('g1_language_selector', selector_path)
    poly = selector.select(rows, 9, SEED, strata=('language',), exclude=excluded)
    assert poly['selected_size'] == 9 and poly['all_strata_covered']
    assert {r['language'] for r in poly['selected_tasks']} == {r['language'] for r in rows}
    poly['provenance'] = {'source': str(source), 'revision': revision, 'metadata_read_surface': 'pinned Git tree path names only', 'selector_sha256': hashlib.sha256(selector_path.read_bytes()).hexdigest()}
    poly['language_counts'] = dict(collections.Counter(r['language'] for r in poly['selected_tasks']))
    poly['exclusion_rule'] = 'Previously used pilot/smoke fixtures and previously prepared confirmation allocations; conservative metadata-only exclusion, independent of scores'
    poly['status'] = 'Sealed G1 allocation; gold/no-op controls pending; no model attempts'
    freeze('polyglot-selection.json', poly)
    freeze('selection-audit.json', {'seed': SEED, 'terminal_eligible': 78, 'terminal_quotas': tb['stratum_quotas'], 'polyglot_languages': poly['language_counts'], 'selection_hashes': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['terminal-selection.json', 'polyglot-selection.json']}, 'selection_only_not_environment_validation': True, 'no_model_calls': True, 'no_model_traces_read': True})
    print('Frozen 9 Terminal-Bench tasks and 9 language-stratified Aider tasks. Controls pending.')

if __name__ == '__main__':
    draw()
