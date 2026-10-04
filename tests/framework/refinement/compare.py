#!/usr/bin/env python3
"""Paired task-cluster comparison for frozen confirmation records.

Schema: harness, benchmark, task, round, arm, solved (bool), tokens (complete
reported total), usage_complete (bool). No inference, missing-data imputation,
or post-outcome task selection. Scheduling rounds are not sampling seeds.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random

COMPARATORS = ('none', 'karpathy', 'both')


def ratio(records, tasks, comparator):
    costs = {'ours': 0, comparator: 0}
    solves = {'ours': 0, comparator: 0}
    for task in tasks:
        for r in records[task]:
            if r['arm'] in costs:
                costs[r['arm']] += r['tokens']
                solves[r['arm']] += int(r['solved'])
    if not all(solves.values()) or costs[comparator] == 0:
        return None
    return (costs['ours'] / solves['ours']) / (costs[comparator] / solves[comparator])


def compare(rows, *, bootstrap=10000, seed=42):
    groups = defaultdict(list)
    for r in rows:
        groups[r['harness']].append(r)
    result = {}
    for harness, records in sorted(groups.items()):
        keys = [(r['benchmark'], r['task'], r['round'], r['arm']) for r in records]
        if len(set(keys)) != len(keys):
            raise ValueError('Duplicate confirmation cell')
        by_task = defaultdict(list)
        missing = []
        for r in records:
            if (r.get('usage_complete') is not True or type(r.get('solved')) is not bool
                    or type(r.get('tokens')) not in (int, float)
                    or not math.isfinite(r['tokens']) or r['tokens'] <= 0):
                missing.append((r['task'], r['arm']))
            by_task[(r['benchmark'], r['task'])].append(r)
        required = {'ours', *COMPARATORS}
        cells = defaultdict(set)
        for r in records:
            cells[(r['benchmark'], r['task'], r['round'])].add(r['arm'])
        balanced = all(v == required for v in cells.values())
        rounds = defaultdict(set)
        for b, task, rnd in cells:
            rounds[(b, task)].add(rnd)
        enough = len(by_task) >= 2 and all(len(v) >= 3 for v in rounds.values())
        families = {r['benchmark'] for r in records}
        status = {'balanced': balanced, 'missing_telemetry_or_grades': missing,
                  'families': sorted(families), 'tasks': len(by_task),
                  'at_least_three_rounds': enough, 'comparisons': {}, 'win': False}
        if missing or not balanced:
            status['reason'] = 'TBD: incomplete telemetry/grades or unmatched panel'
            result[harness] = status
            continue
        tasks = sorted(by_task)
        rng = random.Random(seed)
        samples = [rng.choices(tasks, k=len(tasks)) for _ in range(bootstrap)]
        for comp in COMPARATORS:
            observed = ratio(by_task, tasks, comp)
            simulated = [ratio(by_task, s, comp) for s in samples]
            # Undefined draws (zero solves) make evidence inconclusive; dropping
            # them would condition intervals on successful bootstrap samples.
            interval = None
            if simulated and all(v is not None for v in simulated):
                simulated.sort()
                interval = [simulated[int(.025 * (len(simulated)-1))],
                            simulated[int(.975 * (len(simulated)-1))]]
            quality_ok = sum(r['solved'] for r in records if r['arm'] == 'ours') >= sum(
                r['solved'] for r in records if r['arm'] == comp)
            quality_draws = []
            for sample in samples:
                sampled = [r for task in sample for r in by_task[task]]
                a = [r['solved'] for r in sampled if r['arm'] == 'ours']
                b = [r['solved'] for r in sampled if r['arm'] == comp]
                quality_draws.append(sum(a) / len(a) - sum(b) / len(b))
            quality_draws.sort()
            quality_interval = ([quality_draws[int(.025 * (len(quality_draws)-1))],
                                 quality_draws[int(.975 * (len(quality_draws)-1))]]
                                if quality_draws else None)
            passed = (observed is not None and observed <= .95 and interval is not None
                      and interval[1] < 1 and quality_ok)
            status['comparisons'][comp] = {'cost_ratio': observed,
                'paired_task_cluster_95_interval': interval,
                'no_observed_quality_loss': quality_ok,
                'paired_quality_difference_95_interval': quality_interval,
                'quality_equivalence_proven': False, 'gate_passed': passed}
        status['win'] = (enough and len(families) >= 3 and
                         all(c['gate_passed'] for c in status['comparisons'].values()))
        status['reason'] = 'Confirmation allocation/provenance must be audited independently'
        result[harness] = status
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('records', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    rows = json.loads(a.records.read_text())
    a.output.write_text(json.dumps(compare(rows), indent=2) + '\n')


if __name__ == '__main__':
    main()
