#!/usr/bin/env python3
"""Read completed traces without changing the running experiment's aggregates.

Request counts deduplicate assistant message IDs; tool calls deduplicate call IDs.
Text sizes are characters/bytes, never claimed as provider token counts.
"""
import json
import random
from collections import Counter
from pathlib import Path
from statistics import mean
import aggregate

HERE = Path(__file__).resolve().parent


def clustered_pairs(rows):
    """Resample whole tasks, retaining every round and the paired arms."""
    output = {}
    for bench in sorted({r['benchmark'] for r in rows}):
        cells = {(r['task'], r['round'], r['arm']): r for r in rows if r['benchmark'] == bench}
        keys = sorted({(t, rnd) for t, rnd, _ in cells
                       if all((t, rnd, a) in cells for a in aggregate.ARMS)})
        tasks = sorted({t for t, _ in keys})
        output[bench] = {}
        for left, right in aggregate.PAIRS:
            by_task = {t: [(cells[t, rnd, left], cells[t, rnd, right])
                           for tt, rnd in keys if tt == t] for t in tasks}

            def metrics(pairs):
                lt = sum(a['total_tokens'] for a, _ in pairs)
                rt = sum(b['total_tokens'] for _, b in pairs)
                ls = sum(a['resolved'] for a, _ in pairs)
                rs = sum(b['resolved'] for _, b in pairs)
                return ((lt - rt) / len(pairs), (ls - rs) / len(pairs),
                        lt / ls - rt / rs if ls and rs else None)

            all_pairs = [pair for t in tasks for pair in by_task[t]]
            rng = random.Random(42)
            samples = [metrics([pair for t in rng.choices(tasks, k=len(tasks))
                                for pair in by_task[t]]) for _ in range(5000)]
            ci = []
            for index in range(3):
                values = sorted(s[index] for s in samples if s[index] is not None)
                ci.append([values[int(.025 * len(values))], values[int(.975 * len(values))]] if values else None)
            differences = [(a['total_tokens'] - b['total_tokens'], a['task'], a['round']) for a, b in all_pairs]
            output[bench][f'{left} - {right}'] = {
                'task_clusters': len(tasks), 'matched_runs': len(all_pairs),
                'd_tokens_per_run': metrics(all_pairs)[0], 'd_tokens_cluster_ci95': ci[0],
                'd_resolve': metrics(all_pairs)[1], 'd_resolve_cluster_ci95': ci[1],
                'd_tokens_per_solved': metrics(all_pairs)[2], 'd_tokens_per_solved_cluster_ci95': ci[2],
                'note': 'Empirical paired bootstrap cannot establish equivalence when paired outcomes never differ.',
                'positive_negative_zero_cells': [sum(d > 0 for d, _, _ in differences),
                                                  sum(d < 0 for d, _, _ in differences),
                                                  sum(d == 0 for d, _, _ in differences)],
                'largest_cost_increases': sorted(differences, reverse=True)[:3],
                'leave_one_task_out_d_tokens_per_run': {
                    t: metrics([p for tt in tasks if tt != t for p in by_task[tt]])[0] for t in tasks},
            }
    return output


def inspect(run):
    run = Path(run).resolve()
    messages, calls, texts, events, results = {}, {}, [], [], []
    for line in (run / 'stream.jsonl').open():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(event)
        message = event.get('message', {})
        if event.get('type') == 'assistant':
            mid = message.get('id')
            if mid not in messages:
                messages[mid] = {'usage': {}, 'content': []}
            messages[mid]['usage'] = message.get('usage') or {}
            for block in message.get('content', []):
                if block not in messages[mid]['content']:
                    messages[mid]['content'].append(block)
                if block.get('type') == 'tool_use':
                    calls[block['id']] = block
        if event.get('type') == 'user':
            for block in message.get('content', []):
                if isinstance(block, dict) and block.get('type') == 'tool_result':
                    results.append(block)
    ordered = list(messages.values())
    skill_indices = [i for i, m in enumerate(ordered) if any(
        b.get('type') == 'tool_use' and b.get('name') == 'Skill'
        for b in m['content'])]
    successful_skill_ids = {r.get('tool_use_id') for r in results
                            if 'Launching skill: efficient-coding' in str(r.get('content', ''))}
    successful_skill_indices = [i for i, m in enumerate(ordered) if any(
        b.get('type') == 'tool_use' and b.get('id') in successful_skill_ids for b in m['content'])]
    reference_calls, skill_file_calls, helper_calls = [], [], []
    for call in calls.values():
        inp = json.dumps(call.get('input', {}))
        if 'efficient-coding' in inp and any(s in inp for s in ('references/', 'assets/')):
            reference_calls.append(call)
        if 'efficient-coding' in inp and 'SKILL.md' in inp:
            skill_file_calls.append(call)
        if 'evidence.py' in inp or 'cost_audit.py' in inp:
            helper_calls.append(call)
    tool_counts = Counter(c.get('name') for c in calls.values())
    separate_edit_bash = 0
    for first, second in zip(ordered, ordered[1:]):
        names1 = [b.get('name') for b in first['content'] if b.get('type') == 'tool_use']
        names2 = [b.get('name') for b in second['content'] if b.get('type') == 'tool_use']
        if any(n in ('Edit', 'Write') for n in names1) and 'Bash' in names2:
            separate_edit_bash += 1
    for m in ordered:
        texts.extend(b.get('text', '') for b in m['content'] if b.get('type') == 'text')
    input_by_request = [m['usage'].get('input_tokens', 0) for m in ordered]
    result_sizes = [len(json.dumps(r.get('content', ''), ensure_ascii=False).encode()) for r in results]
    return {
        'run': str(run.relative_to(HERE)),
        'requests': len(ordered), 'input_by_request': input_by_request,
        'tool_counts': dict(tool_counts), 'reference_calls': reference_calls,
        'skill_file_calls': skill_file_calls,
        'helper_calls': helper_calls, 'skill_request_indices_zero_based': skill_indices,
        'first_successful_efficient_coding_request_index': min(successful_skill_indices, default=None),
        'tool_validation_errors': sum('<tool_use_error>' in str(r.get('content', '')) for r in results),
        'skill_validation_errors': sum('<tool_use_error>' in str(r.get('content', '')) and
            calls.get(r.get('tool_use_id'), {}).get('name') == 'Skill' for r in results),
        'api_error_results': sum('API Error:' in str(r.get('content', '')) for r in results),
        'skill_request_input_tokens': sum(input_by_request[i] for i in skill_indices),
        'separate_edit_then_bash_requests': separate_edit_bash,
        'assistant_text_chars': sum(map(len, texts)),
        'large_tool_result_count_over_10KiB_serialized': sum(s > 10240 for s in result_sizes),
        'max_tool_result_serialized_bytes': max(result_sizes, default=0),
        'compact_events': sum(e.get('type') == 'system' and 'compact' in e.get('subtype', '') for e in events),
        'fusion_claim_texts': [t for t in texts if 'fus' in t.lower()],
    }


def main():
    rows = aggregate.collect()
    summary = aggregate.summarize(rows)
    traces = {str(Path(r['benchmark']) / r['task'] / r['arm'] / f"r{r['round']}"): inspect(
        HERE / 'runs' / r['benchmark'] / r['task'] / r['arm'] / f"r{r['round']}") for r in rows}
    for r in rows:
        trace = traces[f"{r['benchmark']}/{r['task']}/{r['arm']}/r{r['round']}"]
        assert trace['requests'] == r['requests'], trace['run']
        assert sum(trace['input_by_request']) == r['input_tokens'], trace['run']
    groups = {}
    for bench, s in summary.items():
        cells = {(r['task'], r['round'], r['arm']): r for r in rows if r['benchmark'] == bench}
        keys = sorted({(t, rnd) for t, rnd, _ in cells if all((t, rnd, a) in cells for a in aggregate.ARMS)})
        groups[bench] = {}
        for arm in aggregate.ARMS:
            ts = [traces[f'{bench}/{t}/{arm}/r{rnd}'] for t, rnd in keys]
            groups[bench][arm] = {
                'matched_runs': len(ts),
                'mean_assistant_text_chars': mean(t['assistant_text_chars'] for t in ts),
                'mean_skill_request_input_tokens': mean(t['skill_request_input_tokens'] for t in ts),
                'reference_read_runs': sum(bool(t['reference_calls']) for t in ts),
                'skill_file_read_runs': sum(bool(t['skill_file_calls']) for t in ts),
                'tool_validation_errors': sum(t['tool_validation_errors'] for t in ts),
                'skill_validation_errors': sum(t['skill_validation_errors'] for t in ts),
                'api_error_results': sum(t['api_error_results'] for t in ts),
                'helper_execution_or_read_runs': sum(bool(t['helper_calls']) for t in ts),
                'separate_edit_then_bash_requests': sum(t['separate_edit_then_bash_requests'] for t in ts),
                'compact_events': sum(t['compact_events'] for t in ts),
                'large_tool_results_over_10KiB_serialized': sum(t['large_tool_result_count_over_10KiB_serialized'] for t in ts),
                'tool_counts': dict(sum((Counter(t['tool_counts']) for t in ts), Counter())),
            }
    out = HERE / 'diagnostics'
    out.mkdir(exist_ok=True)
    data = {'note': 'Snapshot of completed, graded runs. Skill request input is charged traffic on those requests, not a causal overhead estimate. Serialized result size is a proxy, not upstream eligibility or token count.',
            'summary': summary, 'clustered_pairs': clustered_pairs(rows),
            'verified_usage_runs': len(rows), 'trace_groups': groups, 'traces': traces}
    (out / 'skill-diagnosis.json').write_text(json.dumps(data, indent=2))
    print(json.dumps({'summary': summary, 'trace_groups': groups}, indent=2))


if __name__ == '__main__':
    main()
