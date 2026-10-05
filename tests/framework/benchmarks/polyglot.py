#!/usr/bin/env python3
"""Prepare isolated Aider-polyglot exercises from a verified pinned checkout.

Native-agent adaptation: fixed single attempt, tests withheld from actor, official
exercise test runner after restoring tests. This is not the original Aider two-try
leaderboard protocol. Supports Python, Go, Rust, C++, Java; Java requires cached Gradle dependencies.
JavaScript support is limited to selected alphametics with the official cached npm runner.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

REVISION = '7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f'
HARNESS_REVISION = '5dc9490bb35f9729ef2c95d00a19ccd30c26339c'
COMMANDS = {'python': ['python3', '-m', 'pytest', '-q'], 'go': ['go', 'test', '-json', './...'],
            'rust': ['cargo', 'test', '--offline', '--', '--include-ignored'],
            'cpp': ['bash', '/grader/cpp-test.sh'], 'java': ['bash', './gradlew', '--offline', 'test'],
            'javascript': ['bash', '/grader/npm-test.sh']}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source, task, output):
    source = Path(source).resolve()
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        raise ValueError('Dataset revision differs from frozen source')
    parts = Path(task).parts
    if len(parts) != 4 or parts[1:3] != ('exercises', 'practice') or parts[0] not in COMMANDS:
        raise ValueError('Unsupported canonical practice path')
    if subprocess.run(['git', '-C', str(source), 'diff', '--quiet', 'HEAD', '--', task]).returncode:
        raise ValueError('Exercise differs from pinned Git content')
    if parts[0] == 'javascript' and task != 'javascript/exercises/practice/alphametics':
        raise ValueError('JavaScript support is scoped to the selected alphametics task')
    exercise = source.joinpath(*parts)
    config = json.loads((exercise / '.meta/config.json').read_text())
    files = dict(config['files'])
    protected = [name for name in files['solution'] if name in ('Cargo.toml',)]
    files['solution'] = [name for name in files['solution'] if name not in protected]
    output = Path(output)
    if output.exists():
        raise ValueError('Refuse to overwrite prepared task')
    output.mkdir(parents=True)
    actor = output / 'workspace'; actor.mkdir()
    grader = output / 'grader'; grader.mkdir()
    reference = output / 'reference'; reference.mkdir()
    # Preserve support/build files; withhold metadata examples and all original tests.
    test_files = set(files['test'])
    for path in exercise.rglob('*'):
        rel = path.relative_to(exercise)
        if not path.is_file() or rel.parts[0] in ('.meta', '.docs') or str(rel) in test_files:
            continue
        dest = actor / rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, dest)
    for name in files['test']:
        dest = grader / 'tests' / name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(exercise / name, dest)
    shutil.copytree(actor, reference, dirs_exist_ok=True)
    shutil.copytree(actor, grader / 'support', dirs_exist_ok=True)
    examples = files.get('example', [])
    # Examples may include private auxiliary source; cardinality is not a contract.
    mapping = {}
    remaining = list(examples)
    for solution in files['solution']:
        matches = [example for example in remaining if Path(example).name == Path(solution).name]
        if len(matches) > 1:
            raise ValueError('Ambiguous reference filename match')
        if len(matches) == 1:
            mapping[solution] = matches[0]; remaining.remove(matches[0])
    # Selected meetup's official reference is header-only. Keep its original
    # starter .cpp unchanged; never fabricate a second reference solution.
    if task == 'cpp/exercises/practice/meetup':
        if files['solution'] != ['meetup.cpp', 'meetup.h'] or examples != ['.meta/example.h']:
            raise ValueError('Selected meetup reference metadata changed')
        mapping = {'meetup.h': '.meta/example.h'}
        remaining = []
    else:
        unmapped = [name for name in files['solution'] if name not in mapping]
        if unmapped:
            if len(unmapped) != len(remaining):
                raise ValueError('Ambiguous reference-to-solution mapping')
            mapping.update(zip(unmapped, remaining)); remaining = []
    for solution, example in mapping.items():
        dest = reference / solution; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(exercise / example, dest)
    auxiliary = []
    for example in remaining:
        # A helper must share a reference source directory with a mapped example.
        parents = {str(Path(solution).parent) for solution, mapped in mapping.items()
                   if Path(mapped).parent == Path(example).parent}
        if len(parents) != 1:
            raise ValueError('Ambiguous reference auxiliary source directory')
        name = str(Path(parents.pop()) / Path(example).name)
        if name in mapping or (reference / name).exists():
            raise ValueError('Reference auxiliary destination collision')
        shutil.copy2(exercise / example, reference / name); auxiliary.append(name)
    docs = exercise / '.docs'
    prompt = '\n\n'.join((docs / name).read_text() for name in ('introduction.md', 'instructions.md', 'instructions.append.md') if (docs / name).exists())
    prompt += '\n\nModify only these solution files: ' + ', '.join(files['solution'])
    prompt += '. Preserve existing public names. Use only standard libraries.\n'
    (output / 'prompt.txt').write_text(prompt)
    manifest = {'schema_version': 1, 'benchmark': 'aider-polyglot', 'task_id': task,
                'dataset_revision': REVISION, 'harness_revision': HARNESS_REVISION,
                'source': 'https://github.com/Aider-AI/polyglot-benchmark',
                'official_runner_source': 'https://github.com/Aider-AI/aider/blob/' + HARNESS_REVISION + '/benchmark/benchmark.py',
                'test_command': COMMANDS[parts[0]], 'solution_files': files['solution'], 'test_files': files['test'],
                'test_timeout_seconds': 180, 'reference_mapping': mapping, 'reference_auxiliary_files': auxiliary,
                'protocol_deviations': ['Native harness, not Aider', 'One fixed-budget attempt; no post-grade repair turn',
                                        'Tests absent from actor filesystem; official tests restored independently',
                                        'Offline dependency flags; Go JSON events for executed-test accounting'] +
                                       (['Cargo.toml is immutable trusted support to prevent suppressing tests'] if protected else []) +
                                       (['Private reference control overlays auxiliary examples; default candidate grader accepts only declared solution files'] if auxiliary else []),
                'source_files_sha256': {str(p.relative_to(exercise)): digest(p) for p in sorted(exercise.rglob('*')) if p.is_file()}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    shutil.copy2(output / 'manifest.json', grader / 'manifest.json')
    shutil.copy2(Path(__file__).with_name('polyglot_grade.py'), grader / 'grade.py')
    if parts[0] == 'cpp':
        shutil.copy2(Path(__file__).with_name('polyglot_cpp_test.sh'), grader / 'cpp-test.sh')
    if parts[0] == 'javascript':
        runner = Path('/tmp/solpi-aider-harness-source')
        if subprocess.check_output(['git', '-C', str(runner), 'rev-parse', 'HEAD'], text=True).strip() != HARNESS_REVISION:
            raise ValueError('Official JavaScript runner revision mismatch')
        raw = subprocess.check_output(['git', '-C', str(runner), 'show', HARNESS_REVISION + ':benchmark/npm-test.sh'])
        (grader / 'npm-test.sh').write_bytes(raw)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--task', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    manifest = prepare(args.source, args.task, args.output)
    print(json.dumps({'task_id': manifest['task_id'], 'output': str(args.output)}))


if __name__ == '__main__':
    main()
