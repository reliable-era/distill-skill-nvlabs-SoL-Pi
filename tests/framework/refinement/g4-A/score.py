#!/usr/bin/env python3
"""Score G4: Part A from the run_A.py cells, Parts B/C from Pi's canonical windows 01-07 plus the
nginx-502 reruns (attempt 2, preregistered) and the idle-timeout reruns (attempts 3-4, deviation).

Quality is the latest attempt; every attempt's known tokens are charged. A cost is a lower bound
("≥") when any charged attempt lacks complete usage. Ratios use a paired task-cluster bootstrap
(20,000 draws, preregistered seeds); draws with no solves in either arm are undefined and dropped.
Writes results.json next to this file. Usage: score.py
"""
import json, pathlib, random

HERE = pathlib.Path(__file__).resolve().parent
G4 = HERE.parent / 'g4'
A_RUNS = pathlib.Path('/tmp/solpi-g4A-runs')
RETRY = pathlib.Path('/tmp/solpi-g4-BC-retry-8b389db7b117')
SEEDS = {'A': 2026101211, 'B': 2026101212, 'C': 2026101213}
DRAWS = 20000


def a_cells():
    out = []
    for c in json.loads((G4 / 'queue-order.json').read_text())['parts']['A']:
        r = json.loads((A_RUNS / c['cell_id'] / 'result.json').read_text())
        out.append(dict(cell_id=c['cell_id'], task=c['task'], arm=c['arm'], solved=bool(r['resolved']),
                        tokens=r['total_tokens'], complete=not r['unknown_cost_requests'], timeout=r['timed_out'],
                        helper_tokens=r['helper_tokens'], requests=r['primary_requests'], attempts=1 + bool(r.get('infra_rerun'))))
    return out


def bc_cells(part, last_attempt):
    canon = json.loads((G4 / 'windows-01-07-canonical.json').read_text())['cells']
    out = []
    for c in canon:
        if c['part'] != part or not c['attempts']:
            continue
        solved = c['verified_solved']
        tokens = sum(a['known_tokens_lower_bound'] for a in c['attempts'])
        complete = all(a['exact_provider_tokens'] is not None for a in c['attempts'])
        timeout = any(a['native_timeout'] for a in c['attempts'])
        n = len(c['attempts'])
        for k, suffix in ((2, ''), (3, '-a3'), (4, '-a4')):
            f = RETRY / f"{c['cell_id']}-attempts{suffix}.json"
            if k > last_attempt or not f.exists():
                continue
            r = json.loads(f.read_text())[0]
            solved, n = r['solved'], n + 1
            tokens += r['known_tokens_lower_bound']
            complete = complete and r['cost_complete']
            timeout = timeout or r['timeout']
        out.append(dict(cell_id=c['cell_id'], task=c['task'], arm=c['arm'], solved=solved is True,
                        grade_unknown=solved is None, tokens=tokens, complete=complete, timeout=timeout, attempts=n))
    return out


def per_arm(cells):
    arms = {}
    for c in cells:
        a = arms.setdefault(c['arm'], dict(cells=0, solved=0, grade_unknown=0, tokens=0, complete=True, timeouts=0, attempts=0))
        a['cells'] += 1
        a['solved'] += c['solved']
        a['grade_unknown'] += c.get('grade_unknown', False)
        a['tokens'] += c['tokens']
        a['complete'] &= c['complete']
        a['timeouts'] += c['timeout']
        a['attempts'] += c['attempts']
    for a in arms.values():
        a['tokens_per_solve'] = round(a['tokens'] / a['solved']) if a['solved'] else None
    return arms


def ratio(cells, arm, base, seed):
    tasks = sorted({c['task'] for c in cells})
    by = {(t, x): [0, 0] for t in tasks for x in (arm, base)}
    for c in cells:
        if c['arm'] in (arm, base):
            by[c['task'], c['arm']][0] += c['tokens']
            by[c['task'], c['arm']][1] += c['solved']

    def tps(sample, x):
        tok, sol = sum(by[t, x][0] for t in sample), sum(by[t, x][1] for t in sample)
        return tok / sol if sol else None

    point = (lambda a, b: a / b if a and b else None)(tps(tasks, arm), tps(tasks, base))
    rng, draws = random.Random(seed), []
    for _ in range(DRAWS):
        s = [rng.choice(tasks) for _ in tasks]
        a, b = tps(s, arm), tps(s, base)
        if a and b:
            draws.append(a / b)
    draws.sort()
    ci = [round(draws[int(0.025 * len(draws))], 3), round(draws[int(0.975 * len(draws)) - 1], 3)] if draws else None
    return dict(point=round(point, 3) if point else None, ci95=ci, defined_draws=len(draws), undefined_draws=DRAWS - len(draws))


def main():
    res = {}
    a = a_cells()
    for bench in ('diagnostic', 'swe'):
        res[f'A/{bench}'] = dict(arms=per_arm([c for c in a if c['task'].startswith(bench)]))
    for part in ('B', 'C'):
        for last, label in ((2, 'preregistered_attempt2'), (4, 'with_attempts3_4')):
            cells = bc_cells(part, last)
            res[f'{part}/{label}'] = dict(
                arms=per_arm(cells),
                ratios={f'{x}/{y}': ratio(cells, x, y, SEEDS[part]) for x, y in
                        (('ours', 'none'), ('ours', 'K'), ('Both', 'none'), ('Both', 'K'))})
    (HERE / 'results.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
