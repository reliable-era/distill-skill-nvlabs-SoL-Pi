#!/usr/bin/env python3
"""Render the six-condition smoke comparison after all measurements finish."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'revision_eval'
LABELS = {
    'baseline': 'Baseline (no skills)',
    'original': 'Original sol-pi',
    'revised': 'Latest sol-pi',
    'karpathy': 'Karpathy only',
    'karpathy_original': 'Karpathy + original sol-pi',
    'karpathy_revised': 'Karpathy + latest sol-pi',
}


def main():
    data = json.loads((OUT / 'summary.json').read_text())
    summary = data['summary']
    assert set(summary) == set(LABELS), 'Six conditions must be complete before rendering'
    for condition in LABELS:
        assert summary[condition]['runs'] == 5, condition
        rs = [r for r in data['runs'] if r['condition'] == condition]
        assert len(rs) == 5 and len({r['case'] for r in rs}) == 5, condition
        assert sum(r['total_tokens'] for r in rs) == summary[condition]['total_tokens'], condition
        assert sum(r['resolved'] for r in rs) == summary[condition]['solved'], condition
    baseline = summary['baseline']['tokens_per_solved']
    values = [
        ['Verified solves'] + [f"{summary[c]['solved']}/{summary[c]['runs']}" for c in LABELS],
        ['Tokens per verified solve'] + [f"{summary[c]['tokens_per_solved']:,.0f}"
                                        if summary[c]['tokens_per_solved'] is not None else 'Undefined' for c in LABELS],
        ['Change versus baseline'] + [f"{100 * (summary[c]['tokens_per_solved'] / baseline - 1):+.1f}%"
                                     if summary[c]['tokens_per_solved'] is not None else 'Undefined' for c in LABELS],
        ['Mean model requests/case'] + [f"{summary[c]['mean_requests']:.1f}" for c in LABELS],
    ]
    with (OUT / 'comparison.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', *LABELS.values()])
        writer.writerows(values)
    table = '| ' + ' | '.join(['Metric', *LABELS.values()]) + ' |\n'
    table += '|---|' + '---:|' * len(LABELS) + '\n'
    table += ''.join('| ' + ' | '.join(row) + ' |\n' for row in values)
    (OUT / 'comparison.txt').write_text(table)
    report = HERE.parent / 'report.md'
    text = report.read_text().split('\n### Revision smoke observations\n')[0]
    text += '\n### Revision smoke observations\n\n'
    text += ('The consolidated smoke comparison covers the same five stress cases, one round per condition. '
             'Original and latest refer to the two efficient-coding versions, not the upstream Pi runtime extension. '
             'Baseline/original/latest were run in the initial stage; Karpathy-only and both combinations were measured '
             'in a subsequent stage with the same prompts, model, limits, and graders. '
             '[Measurement data](eval/revision_eval/summary.json), [manifest](eval/revision_eval/manifest.json), '
             'and [CSV](eval/revision_eval/comparison.csv) are separate from the original multi-round matrix.\n\n')
    manifest = json.loads((OUT / 'manifest.json').read_text())
    if manifest.get('observed_agent_versions') and manifest.get('observed_models'):
        text += ('Observed agent version: ' + ', '.join(manifest['observed_agent_versions']) +
                 '; model: ' + ', '.join(manifest['observed_models']) + '.\n\n')
    text += table
    text += ('\nThis one-round, in-sample comparison does not establish savings, transfer, or noninferiority. '
             'The largest revised standalone regression reads a full log before the skill loads; '
             'shortening instructions cannot retroactively replace that history.\n')
    report.write_text(text)
    print(table)


if __name__ == '__main__':
    main()
