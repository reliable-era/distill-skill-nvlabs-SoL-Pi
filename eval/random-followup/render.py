"""Small descriptive tables from independently collected follow-up cells."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('collection', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
d = json.loads(args.collection.read_text())
assert not d['source_errors'], d['source_errors']
s = d['stages']['real_swe']
arms = ['baseline', 'latest', 'karpathy', 'karpathy_latest']
labels = ['No skill', 'SoL-Pi (ours)', 'Karpathy', 'Both skills']
rows = [c for c in d['cells'] if c['status'] == 'graded']
cases = sorted({c['case'] for c in d['cells']})
lines = ['# Random small follow-up', '', 'Qwen3.8-27B-FP8; Claude Code 2.1.286. Two randomly selected new easy issues, four configurations, two scheduling rounds. Scheduling seeds do not control model RNG.', '', f"Graded: {s['graded']}/{s['expected']}. " + ('Complete.' if s['complete'] else 'Provisional; incomplete cells are not zeros.'), '', '## Correctness', '', '| Task | ' + ' | '.join(labels) + ' |', '|---|' + '---:|' * 4]
for case in cases:
    values = []
    for arm in arms:
        rs = [r for r in rows if r['case'] == case and r['arm'] == arm]
        values.append(f"{sum(r['resolved'] for r in rs)}/{len(rs)}" if rs else 'pending')
    lines.append('| ' + case + ' | ' + ' | '.join(values) + ' |')
lines += ['', '## Token traffic across all attempts', '', '| Task | ' + ' | '.join(labels) + ' |', '|---|' + '---:|' * 4]
for case in cases:
    values = []
    for arm in arms:
        rs = [r for r in rows if r['case'] == case and r['arm'] == arm]
        values.append(('' if all(r['usage_complete'] for r in rs) else '≥') + f"{sum(r['total_tokens'] for r in rs):,}" if rs else 'pending')
    lines.append('| ' + case + ' | ' + ' | '.join(values) + ' |')
lines += ['', '## Aggregate efficiency and stability', '', '| Configuration | Solves | Tokens / solve | Model timeouts | Incomplete usage runs |', '|---|---:|---:|---:|---:|']
for arm, label in zip(arms, labels):
    m = s['arms'][arm]
    cost = 'pending' if not m['n'] else 'undefined (zero solves)' if m['tokens_per_solve'] is None else ('' if m['usage_complete'] else '≥') + f"{m['tokens_per_solve']:,.0f}"
    lines.append(f"| {label} | {m['solved']}/{m['n']} | {cost} | {m['timeouts']} | {m['incomplete_usage_runs']} |")
lines += ['', 'Costs include failed attempts. ≥ indicates incomplete recorded lower bounds and cannot establish savings. Aggregate tables use only complete matched task-rounds. Two task clusters cannot establish broad superiority. Public repair retrieval and official grades must be assessed separately in the independent audit.']
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text('\n'.join(lines) + '\n')
