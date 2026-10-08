"""Preregistered G2 paired task-cluster analysis (stdlib, no model calls)."""
import argparse, collections, json, math, pathlib, random
ARMS = ('none', 'K', 'candidate', 'Both')
GATES = (('candidate', 'none'), ('Both', 'K'), ('candidate', 'K'))

def ratio(a_tokens, a_solves, b_tokens, b_solves):
    if not a_solves or not b_solves or not b_tokens:
        return None
    return (a_tokens / a_solves) / (b_tokens / b_solves)

def percentile(values, p):
    # Nearest-rank percentile; conservative +inf for any undefined replicate.
    ordered = sorted(values)
    value = ordered[max(0, math.ceil(len(ordered) * p) - 1)]
    return value if math.isfinite(value) else None

def analyze(rows, tasks, rounds, seed, repetitions=20000):
    expected = {(t, r, a) for t in tasks for r in rounds for a in ARMS}
    identities = [(v['task'], v['round'], v['arm']) for v in rows]
    if len(identities) != len(set(identities)):
        raise ValueError('Duplicate model cell; never choose among retries')
    if set(identities) != expected:
        raise ValueError('Analysis requires exactly the planned complete round roster')
    evidence_complete = all(v['grade_valid'] and v['cost_complete'] and v.get('provider_eof_valid', True) for v in rows)
    aggregates = {}
    for arm in ARMS:
        selected = [v for v in rows if v['arm'] == arm]
        solves = sum(v['solved'] is True for v in selected)
        tokens = sum(v['tokens_lower_bound'] for v in selected)
        known = all(v['cost_complete'] for v in selected)
        wall = sum(v['native_wall_seconds'] for v in selected)
        # Wilson descriptive quality interval; does not assert population equivalence.
        n = len(selected); p = solves / n; z = 1.959963984540054
        denom = 1 + z*z/n; center = (p + z*z/(2*n))/denom
        half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/denom
        aggregates[arm] = dict(cells=n, solves=solves, tokens_lower_bound=tokens,
            costs_complete=known, unknown_grades=sum(not v['grade_valid'] for v in selected),
            tokens_per_solve=tokens/solves if known and solves else None,
            native_wall_seconds=wall, native_wall_per_solve=wall/solves if solves else None,
            solve_fraction=p, descriptive_wilson_95=[center-half, center+half],
            rounds={str(r): dict(solves=sum(v['solved'] is True for v in selected if v['round']==r),
                tokens=sum(v['tokens_lower_bound'] for v in selected if v['round']==r)) for r in rounds})
    pairs = tuple(dict.fromkeys(GATES + (('candidate', 'Both'), ('K', 'none'), ('Both', 'none'))))
    totals = {t: {a: (sum(v['tokens_lower_bound'] for v in rows if v['task']==t and v['arm']==a),
                     sum(v['solved'] is True for v in rows if v['task']==t and v['arm']==a))
                  for a in ARMS} for t in tasks}
    draws = {pair: [] for pair in pairs}; rng = random.Random(seed)
    if evidence_complete:
        for _ in range(repetitions):
            picked = rng.choices(tasks, k=len(tasks))
            values = {a: (sum(totals[t][a][0] for t in picked), sum(totals[t][a][1] for t in picked)) for a in ARMS}
            for a,b in pairs:
                value = ratio(*values[a], *values[b])
                draws[a,b].append(value if value is not None else math.inf)
    comparisons = {}
    for a,b in pairs:
        aa=aggregates[a]; bb=aggregates[b]
        point = ratio(aa['tokens_lower_bound'],aa['solves'],bb['tokens_lower_bound'],bb['solves']) if evidence_complete else None
        sample = draws[a,b]
        interval = [percentile(sample,.025), percentile(sample,.975)] if sample else [None,None]
        # Null upper endpoint means +inf / undefined, never a passing interval.
        quality = aa['solves'] >= bb['solves'] if evidence_complete else None
        point_met = point is not None and aa['tokens_lower_bound']*bb['solves']*100 <= bb['tokens_lower_bound']*aa['solves']*95
        comparisons[a+'/'+b] = dict(ratio=point, bootstrap_95=interval,
            undefined_replicates=sum(not math.isfinite(v) for v in sample),
            no_fewer_solves=quality, point_5_percent_met=point_met,
            interval_below_1=interval[1] is not None and interval[1]<1,
            gate=(a,b) in GATES, passes=evidence_complete and point_met and quality and interval[1] is not None and interval[1]<1)
    early=comparisons['candidate/none']
    futility = not early['point_5_percent_met'] or not early['no_fewer_solves']
    return dict(evidence_complete=evidence_complete, tasks=tasks, rounds=rounds,
        aggregates=aggregates, comparisons=comparisons,
        round_1_negative_stop=evidence_complete and rounds==[1] and futility,
        round_1_gate_unverifiable=not evidence_complete and rounds==[1],
        family_accepted=evidence_complete and rounds==[1,2,3] and all(comparisons[a+'/'+b]['passes'] for a,b in GATES),
        bootstrap=dict(seed=seed, repetitions=repetitions, unit='task; retain all rounds and matched arms',
            percentile_method='nearest rank 2.5/97.5%; undefined replicates are +inf, null interval endpoint means not finite'),
        quality_interval_note='Wilson descriptive only; repeated task attempts are not independent population draws')

def main():
    p=argparse.ArgumentParser();p.add_argument('audit',type=pathlib.Path);p.add_argument('--rounds',type=int,default=1);p.add_argument('--output',required=True,type=pathlib.Path);args=p.parse_args()
    plan=json.loads((pathlib.Path(__file__).parent/'plan.json').read_text());audit=json.loads(args.audit.read_text());family=audit['family'];rounds=list(range(1,args.rounds+1))
    result=analyze([v for v in audit['rows'] if v['round'] in rounds],plan['families'][family]['tasks'],rounds,plan['analysis']['bootstrap_seeds'][family],plan['analysis']['bootstrap_repetitions'])
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('evidence_complete','round_1_negative_stop','family_accepted','comparisons')},indent=2))
if __name__=='__main__':main()
