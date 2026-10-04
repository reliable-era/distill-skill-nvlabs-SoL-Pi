"""Conservative, failure-inclusive accounting; unknown billing stays unknown."""
from collections import defaultdict
from statistics import mean, pstdev

TOKEN_FIELDS = ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens')

def price_attempt(record, price):
    """Prices are USD/million tokens, input EXCLUDES cache; no inferred prices."""
    if not record.get('usage_complete') or record.get('token_semantics') != 'exclusive':
        return None
    values = [record.get(k) for k in TOKEN_FIELDS]
    if any(v is None or not isinstance(v, (int, float)) or v < 0 for v in values):
        return None
    if any(not isinstance(price.get(k), (int,float)) or isinstance(price.get(k),bool) or price[k]<0 for k in TOKEN_FIELDS):
        return None
    return sum(record[k] * price[k] / 1_000_000 for k in TOKEN_FIELDS)

def summarize(records):
    """Include failed/ungraded attempts in costs; unknown grades bound quality instead of inflating it."""
    records = list(records)
    solved = sum(r.get('solved') is True for r in records)
    graded = sum(isinstance(r.get('solved'), bool) for r in records)
    has_tokens = any(r.get(k) is not None for r in records for k in TOKEN_FIELDS)
    tokens = sum(sum(r.get(k) or 0 for k in TOKEN_FIELDS) for r in records) if has_tokens else None
    complete = all(r.get('usage_complete') and r.get('token_semantics') == 'exclusive'
                   and all(r.get(k) is not None for k in TOKEN_FIELDS) for r in records)
    known_costs = [r['cost_usd'] for r in records if r.get('cost_usd') is not None]
    dollars = sum(known_costs) if known_costs else None
    cost_complete = len(known_costs) == len(records) and bool(records)
    times = [r['elapsed_seconds'] for r in records if r.get('elapsed_seconds') is not None]
    rounds = defaultdict(list)
    for r in records:
        rounds[r.get('round', 0)].append(r.get('solved'))
    rates = [mean(v) for v in rounds.values()] if graded == len(records) else []
    return dict(attempts=len(records), graded=graded, solved=solved,
                solve_rate=solved / len(records) if records and graded == len(records) else None,
                graded_solve_rate=solved / graded if graded else None,
                solve_rate_lower_bound=solved / len(records) if records else None,
                solve_rate_upper_bound=(solved+len(records)-graded) / len(records) if records else None,
                ungraded=len(records)-graded,
                observed_tokens=tokens if records else None,
                tokens_complete=complete and bool(records),
                tokens_per_solve=tokens / solved if tokens is not None and solved else None,
                cost_usd=dollars, cost_complete=cost_complete,
                dollars_per_solve=dollars / solved if dollars is not None and solved else None,
                wall_seconds=sum(times) if times else None,
                wall_seconds_complete=len(times) == len(records) and bool(records),
                seconds_per_solve=sum(times) / solved if times and solved else None,
                timeouts=sum(r.get('status') == 'timeout' for r in records),
                round_solve_rate_stdev=pstdev(rates) if len(rates)>1 else None)

def terminal_usage(events, agent):
    """Decode documented terminal snapshots, never add streaming deltas.

    Completeness covers reported LLM tokens, not subscription billing or external
    tools. Interrupted runs and unsupported schemas retain unknown fields.
    """
    result = dict.fromkeys(TOKEN_FIELDS)
    result.update(usage_complete=False, token_semantics='unknown', usage_source='TBD')
    events = [e for e in events if isinstance(e, dict)]

    def valid(values):
        return all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and v >= 0 for v in values)

    if agent == 'codex':
        turns = [e for e in events if e.get('type') == 'turn.completed']
        # Exec emits cumulative token accounting at turn completion. Multiple
        # terminal records are ambiguous without version/session boundaries.
        if len(turns) != 1:
            return result
        u = turns[0].get('usage', {})
        if not isinstance(u, dict):
            return result
        inp, cached, out = (u.get(k) for k in
                            ('input_tokens', 'cached_input_tokens', 'output_tokens'))
        written = u.get('cache_write_input_tokens')
        if valid((inp, cached, out)) and inp >= cached:
            result.update(input_tokens=inp-cached, output_tokens=out,
                          cache_read_tokens=cached, cache_write_tokens=written,
                          usage_source='codex.turn.completed')
            # Older schemas omit cache-write usage; absence is not zero.
            # Nonzero writes need a verified inclusive-input contract.
            if written == 0 and valid((written,)):
                result.update(usage_complete=True, token_semantics='exclusive')
        return result

    if agent == 'pi':
        ends = [e for e in events if e.get('type') == 'agent_end']
        if len(ends) != 1 or not isinstance(ends[0].get('messages'), list):
            return result
        messages = [m for m in ends[0]['messages'] if isinstance(m, dict)
                    and m.get('role') == 'assistant']
        if not messages:
            return result
        totals = [0, 0, 0, 0]
        for message in messages:
            u = message.get('usage', {})
            if not isinstance(u, dict):
                return result
            values = [u.get(k) for k in ('input', 'output', 'cacheRead', 'cacheWrite')]
            # Pi initializes absent provider usage to all zeros. Require a
            # nonempty verified total, and reject aborted/error placeholders.
            if (not valid(values) or not valid((u.get('totalTokens'),))
                    or u['totalTokens'] <= 0 or sum(values) != u['totalTokens']
                    or message.get('stopReason') not in ('stop', 'toolUse', 'length')):
                return result
            totals = [a+b for a,b in zip(totals, values)]
        result.update(zip(TOKEN_FIELDS, totals))
        auxiliary_types = {'compaction_start', 'compaction_end', 'compaction',
                           'branch_summary', 'auto_compaction_start', 'auto_compaction_end'}
        auxiliary_seen = (any(e.get('type') in auxiliary_types for e in events)
                          or any(isinstance(m, dict) and m.get('role') != 'assistant'
                                 and m.get('usage') is not None for m in ends[0]['messages']))
        result.update(usage_complete=not auxiliary_seen, token_semantics='exclusive',
                      usage_source=('pi.agent_end.messages.usage; auxiliary scope unresolved'
                                    if auxiliary_seen else 'pi.agent_end.messages.usage'))
        return result

    if agent in ('claude', 'claude-code'):
        ends = [e for e in events if e.get('type') == 'result']
        if len(ends) != 1 or not isinstance(ends[0].get('modelUsage'), dict):
            return result
        usages = list(ends[0]['modelUsage'].values())
        if not usages:
            return result
        totals = [0, 0, 0, 0]
        for u in usages:
            if not isinstance(u, dict):
                return result
            values = [u.get(k) for k in ('inputTokens', 'outputTokens',
                                        'cacheReadInputTokens', 'cacheCreationInputTokens')]
            if not valid(values):
                return result
            totals = [a+b for a,b in zip(totals, values)]
        result.update(zip(TOKEN_FIELDS, totals))
        result.update(usage_complete=True, token_semantics='exclusive',
                      usage_source='claude.result.modelUsage')
    return result
