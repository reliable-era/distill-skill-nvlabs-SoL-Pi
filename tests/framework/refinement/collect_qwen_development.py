"""Summarize the frozen development screen without dropping failed attempts."""
import argparse
import json
from pathlib import Path


def summarize(plan, evidence):
    scheduled = {cell['id']: cell for cell in plan['schedule']}
    if len(scheduled) != len(plan['schedule']):
        raise ValueError('duplicate scheduled cell')
    seen = set()
    groups = {arm: [] for arm in ('none', 'K', 'candidate', 'Both')}
    for row in evidence['actors']:
        key = row['id']
        if key in seen or key not in scheduled:
            raise ValueError('duplicate or unexpected actor')
        seen.add(key)
        cell = scheduled[key]
        if row['family'] != cell['family'] or row['arm'] != cell['arm']:
            raise ValueError('actor metadata disagrees with schedule')
        value = row.get('observed_gross_tokens_lower_bound')
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError('invalid observed usage')
        if row.get('usage_complete') is True and (value is None or value == 0):
            raise ValueError('complete actor requires positive observed usage')
        groups[row['arm']].append(row)
    output = []
    for arm, rows in groups.items():
        expected = sum(cell['arm'] == arm for cell in scheduled.values())
        def valid_grade(row):
            grade = row.get('grade', {})
            return not grade.get('infrastructure_error') and type(grade.get('solved')) is bool
        solved = sum(valid_grade(row) and row['grade']['solved'] for row in rows)
        ungraded = sum(not valid_grade(row) for row in rows)
        complete = len(rows) == expected and all(row.get('usage_complete') is True for row in rows)
        lower_bound = sum(row.get('observed_gross_tokens_lower_bound') or 0 for row in rows)
        output.append(dict(arm=arm, expected_attempts=expected, recorded_attempts=len(rows),
                           missing_attempts=expected-len(rows), solved=solved, ungraded=ungraded,
                           usage_complete=complete, observed_gross_tokens_lower_bound=lower_bound,
                           complete_tokens_per_solve=lower_bound/solved if complete and solved else None,
                           cost_usd_per_solve=None))
    return {'scope': 'reused development fixtures; not fresh confirmation',
            'cohort': plan.get('cohort'), 'order_seed': plan.get('order_seed'),
            'prior_consumed_attempts': plan.get('prior_consumed_attempts'),
            'prior_attempts_included_in_arm_metrics': False,
            'backend': 'Qwen3.8-27B-FP8; separate from historical native routes',
            'errors': evidence.get('errors'), 'arms': output,
            'note': 'All recorded attempts contribute cost, including failures. Missing/incomplete costs remain TBD.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('plan', type=Path)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.plan.read_text()), json.loads(args.evidence.read_text())), indent=2))
