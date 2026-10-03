#!/usr/bin/env python3
"""Render independently collected matched results with explicit scope/version."""
import argparse, csv, json
from pathlib import Path

LABELS = {
    'baseline': ('No skill', 'baseline'),
    'original': ('SoL-Pi', 'original frozen'),
    'latest': ('SoL-Pi', 'latest frozen'),
    'karpathy': ('Karpathy', 'frozen Karpathy'),
    'karpathy_latest': ('Karpathy + SoL-Pi', 'latest frozen SoL-Pi'),
    'candidate': ('SoL-Pi candidate', 'rejected development candidate'),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.collection.read_text())
    if data['source_errors']:
        raise SystemExit('Provenance errors: refuse rendering comparison')
    rows = []
    for stage, result in data['stages'].items():
        expected_per_arm = result['expected'] // len(result['arms'])
        for arm, metrics in result['arms'].items():
            name, version = LABELS[arm]
            rows.append(dict(stage=stage, configuration=name, version=version,
                             complete=result['complete'], usage_complete=metrics.get('usage_complete',False), incomplete_usage_runs=metrics.get('incomplete_usage_runs',0), matched_attempts=metrics['n'],
                             planned_attempts=expected_per_arm, solved=metrics['solved'],
                             total_tokens=metrics['total_tokens'],
                             tokens_per_verified_solve=metrics['tokens_per_solve'],
                             token_p90=metrics['tokens_p90'], token_max=metrics['tokens_max'],
                             timeouts=metrics['timeouts'],
                             grade_timeouts=metrics.get('grade_timeouts', 0)))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir/'comparison.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    text = ['Provider-reported tokens include all matched failed attempts. Round labels randomize scheduling, not model sampling RNG.',
            'Fallback usage without a terminal summary is a recorded lower bound; affected costs carry ≥ and cannot establish savings.',
            'Partial stages show complete matched cells only; pending is not a measured zero. Development results are not validation.',
            '', '| Stage | Configuration | Version | Status | Verified / matched | Total tokens | Tokens / solve |',
            '|---|---|---|---|---:|---:|---:|']
    for row in rows:
        pending = row['matched_attempts'] == 0
        status = 'complete' if row['complete'] else 'pending' if pending else 'provisional'
        quality = 'pending' if pending else f"{row['solved']}/{row['matched_attempts']}"
        total = 'pending' if pending else f"{row['total_tokens']:,}"
        tps = row['tokens_per_verified_solve']
        cost = 'pending' if pending else 'undefined (zero solves)' if tps is None else f'{tps:,.2f}'
        if not pending and not row['usage_complete']:
            total = '≥ ' + total
            if tps is not None: cost = '≥ ' + cost
            status += '; incomplete usage'
        text.append(f"| {row['stage']} | {row['configuration']} | {row['version']} | {status} | {quality} | {total} | {cost} |")
    (args.output_dir/'comparison.txt').write_text('\n'.join(text)+'\n')
    print(args.output_dir/'comparison.csv')

if __name__ == '__main__':
    main()
