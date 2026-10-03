#!/usr/bin/env python3
"""Sequential, isolated smoke comparison including original/revised combinations.

One round on the five existing stress cases is behavioral validation, not a
held-out efficiency benchmark. Never writes the original experiment's runs.
"""
import fcntl
import hashlib
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

from aggregate import parse_stream
from run_swe import ARMS

HERE = Path(__file__).resolve().parent
OUT = HERE / 'revision_eval'
CASES = ['s1_small_fix', 's2_large_log', 's3_fabricated_quote',
         's4_edit_then_fail', 's5_continuation']
CONDITIONS = {
    'baseline': ('baseline', False),
    'original': ('sol-pi', False),
    'revised': ('sol-pi', True),
    'karpathy': ('karpathy', False),
    'karpathy_original': ('karpathy+sol-pi', False),
    'karpathy_revised': ('karpathy+sol-pi', True),
}


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    OUT.mkdir(exist_ok=True)
    with (OUT / 'run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        revision = OUT / 'skills' / 'efficient-coding'
        source = HERE.parent / 'skills' / 'efficient-coding'
        if revision.exists():
            if hashes(revision) != hashes(source):
                raise RuntimeError('Revision snapshot differs; use a new experiment directory')
        else:
            shutil.copytree(source, revision)
        karpathy = OUT / 'skills' / 'karpathy-guidelines'
        karpathy_source = HERE / 'skills' / 'karpathy-guidelines'
        if karpathy.exists():
            if hashes(karpathy) != hashes(karpathy_source):
                raise RuntimeError('Karpathy snapshot differs; use a new experiment directory')
        else:
            shutil.copytree(karpathy_source, karpathy)
        original_hashes = hashes(HERE / 'skills' / 'efficient-coding')
        karpathy_hashes = hashes(karpathy_source)
        manifest = {'seed': 42, 'rounds': 1, 'cases': CASES,
                    'original_skill_files': original_hashes,
                    'revised_skill_files': hashes(revision),
                    'karpathy_skill_files': karpathy_hashes,
                    'conditions': CONDITIONS,
                    'execution_stages': [
                        {'conditions': ['original', 'revised', 'baseline'], 'seed': 42},
                        {'conditions': ['karpathy', 'karpathy_original', 'karpathy_revised'], 'seed': 42,
                         'note': 'Follow-up after initial three conditions; not interleaved with their completed runs'}],
                    'scope': 'In-sample smoke check, not proof of efficiency or noninferiority'}
        if (OUT / 'manifest.json').exists() and not (OUT / 'manifest.initial.json').exists():
            shutil.copy2(OUT / 'manifest.json', OUT / 'manifest.initial.json')
        (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        for stage in manifest['execution_stages']:
            rng = random.Random(stage['seed'])
            for case in CASES:
                for condition in rng.sample(stage['conditions'], len(stage['conditions'])):
                    arm, revised = CONDITIONS[condition]
                    skills = OUT / 'skills' if revised else HERE / 'skills'
                    subprocess.run([sys.executable, str(HERE / 'run_stress.py'), case, arm, '1',
                                    '--skills-root', str(skills), '--runs-root', str(OUT / condition / 'runs')],
                                   check=True)
        assert hashes(HERE / 'skills' / 'efficient-coding') == original_hashes
        assert hashes(karpathy_source) == karpathy_hashes
        rows = []
        for condition, (arm, revised) in CONDITIONS.items():
            for p in sorted((OUT / condition / 'runs' / 'stress').glob('*/*/r1/result.json')):
                r = json.loads(p.read_text())
                expected = {}
                for skill in ARMS[arm]:
                    files = karpathy_hashes if skill == 'karpathy-guidelines' else (
                        manifest['revised_skill_files'] if revised else original_hashes)
                    expected.update({skill + '/' + k: v for k, v in files.items()})
                assert r['skill_file_sha256'] == expected, str(p)
                assert r['arm'] == arm, str(p)
                r.update(parse_stream(p.parent / 'stream.jsonl'))
                r['condition'] = condition
                rows.append(r)
        summary = {}
        for condition in CONDITIONS:
            rs = [r for r in rows if r['condition'] == condition]
            assert sorted(r['case'] for r in rs) == sorted(CASES), condition
            solved = sum(r['resolved'] for r in rs)
            tokens = sum(r['total_tokens'] for r in rs)
            summary[condition] = {'runs': len(rs), 'solved': solved,
                                  'total_tokens': tokens, 'tokens_per_solved': tokens / solved if solved else None,
                                  'mean_requests': sum(r['requests'] for r in rs) / len(rs),
                                  'skill_invoked_runs': sum(bool(r['skills_invoked']) for r in rs),
                                  'max_turn_or_time_limit_runs': sum(r['end'] != 'success' or r['timed_out'] for r in rs)}
        (OUT / 'summary.json').write_text(json.dumps({'summary': summary, 'runs': rows}, indent=2))
        print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
