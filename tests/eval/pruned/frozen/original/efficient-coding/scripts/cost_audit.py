#!/usr/bin/env python3
"""Audit normalized per-request token usage and cost; does not collect telemetry."""
import argparse
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
import sys

FIELDS = ("input_uncached_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens")


def audit(path, attempted, solved):
    if not 0 <= solved <= attempted:
        raise ValueError("Require 0 <= solved <= attempted")
    totals = dict.fromkeys(FIELDS, 0)
    components = defaultdict(lambda: {"requests": 0, "cost": Decimal(0)})
    requests = 0
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line, parse_float=Decimal)
        if not isinstance(item, dict):
            raise ValueError(f"Line {line_number}: expected an object")
        component = item.get("component")
        rates = item.get("rates_per_million")
        if not isinstance(component, str) or not component.strip() or not isinstance(rates, dict):
            raise ValueError(f"Line {line_number}: missing component or rates")
        cost = Decimal(0)
        for field in FIELDS:
            count = item.get(field)
            rate = rates.get(field)
            if type(count) is not int or count < 0:
                raise ValueError(f"Line {line_number}: invalid or missing {field}")
            if isinstance(rate, bool) or not isinstance(rate, (int, Decimal)):
                raise ValueError(f"Line {line_number}: invalid or missing rate for {field}")
            price = Decimal(rate)
            if not price.is_finite() or price < 0:
                raise ValueError(f"Line {line_number}: rate must be nonnegative and finite")
            totals[field] += count
            cost += Decimal(count) * price / Decimal(1_000_000)
        components[component]["requests"] += 1
        components[component]["cost"] += cost
        requests += 1
    if not requests:
        raise ValueError("Usage file has no requests")
    total = sum((entry["cost"] for entry in components.values()), Decimal(0))

    def number(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("Cost exceeds numeric reporting range")
        return result

    return {"requests": requests, "attempted_tasks": attempted, "verified_solved_tasks": solved,
            "completion_rate": solved / attempted if attempted else None,
            "tokens": totals, "total_token_traffic": sum(totals.values()),
            "total_cost_usd": number(total),
            "cost_per_verified_solved_task_usd": number(total / solved) if solved else None,
            "components": {name: {"requests": entry["requests"], "cost_usd": number(entry["cost"])}
                           for name, entry in sorted(components.items())},
            "accounting": "Caller-normalized exclusive token categories and supplied per-request rates"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("usage_jsonl")
    parser.add_argument("--attempted", type=int, required=True)
    parser.add_argument("--solved", type=int, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.usage_jsonl, args.attempted, args.solved)
    except (OSError, ValueError, TypeError, InvalidOperation, OverflowError) as error:
        print(json.dumps({"ok": False, "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
