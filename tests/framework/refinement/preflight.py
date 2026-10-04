#!/usr/bin/env python3
"""Run official grader sanity checks only; never launch inference.

Use a dedicated venv with integration-requirements.txt. Gold datasets and oracle
solutions must remain private grader inputs, outside all actor workspaces.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def check_terminal(report, expected):
    stats = report['stats']
    if (report['n_total_trials'] != 1 or stats['n_completed_trials'] != 1
            or stats['n_errored_trials'] != 0 or stats['n_retries'] != 0):
        raise ValueError('Terminal sanity incomplete or infrastructure errors present')
    evals = list(stats['evals'].values())
    if len(evals) != 1 or evals[0]['n_errors'] != 0:
        raise ValueError('Terminal sanity evaluator error')
    rewards = evals[0]['reward_stats']['reward']
    if set(rewards) != {str(float(expected))} or len(next(iter(rewards.values()))) != 1:
        raise ValueError('Unexpected terminal verifier reward')


def check_swe(report, expected):
    if (report['completed_instances'] != 1 or report['resolved_instances'] != expected
            or any(report[k] != 0 for k in ('infra_failure_instances',
                       'ambiguous_failure_instances', 'empty_patch_instances', 'error_instances'))):
        raise ValueError('Unexpected SWE sanity outcome or infrastructure failure')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    sub = p.add_subparsers(dest='family', required=True)
    tb = sub.add_parser('terminal')
    tb.add_argument('--task', type=Path, required=True)
    swe = sub.add_parser('swe')
    swe.add_argument('--dataset', type=Path, required=True)
    swe.add_argument('--instance', required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('Refuse to overwrite grader evidence; use a fresh output directory')
    a.output.mkdir(parents=True)
    a.output = a.output.resolve()
    if a.family == 'terminal':
        for agent in ('oracle', 'nop'):
            subprocess.run([str(Path(sys.executable).with_name('harbor')), 'run',
                            '--path', str(a.task.resolve()), '--agent', agent,
                            '--n-attempts', '1', '--n-concurrent', '1',
                            '--max-retries', '0', '--jobs-dir', str(a.output),
                            '--job-name', agent], check=True)
            check_terminal(json.loads((a.output / agent / 'result.json').read_text()),
                           1 if agent == 'oracle' else 0)
    else:
        # Nonempty no-op patch makes the harness execute regression tests;
        # an empty prediction would merely be skipped, not exercise the grader.
        patch = ('diff --git a/.solpi_noop_marker b/.solpi_noop_marker\n'
                 'new file mode 100644\n--- /dev/null\n+++ b/.solpi_noop_marker\n'
                 '@@ -0,0 +1 @@\n+Grader sanity only.\n')
        pred = a.output / 'noop.jsonl'
        pred.write_text(json.dumps({'instance_id': a.instance,
                                   'model_name_or_path': 'noop-sanity',
                                   'model_patch': patch}) + '\n')
        for label, prediction in [('reference', 'gold'), ('noop', str(pred))]:
            subprocess.run([sys.executable, '-m', 'swebench.harness.run_evaluation',
                            '--dataset_name', str(a.dataset.resolve()),
                            '--predictions_path', prediction, '--instance_ids', a.instance,
                            '--run_id', label, '--max_workers', '1', '--timeout', '600',
                            '--report_dir', str(a.output / 'reports')],
                           cwd=a.output, check=True)
            model = 'gold' if label == 'reference' else 'noop-sanity'
            report = a.output / 'reports' / f'{model}.{label}.json'
            check_swe(json.loads(report.read_text()), 1 if label == 'reference' else 0)
    print('Official positive/negative grader sanity passed; these are not model scores.')


if __name__ == '__main__':
    main()
