#!/usr/bin/env python3
"""Render eval/results/summary.json into the tables used by ../report.md (printed to stdout)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "results" / "summary.json").read_text())
ARMS = ["sol-pi", "baseline", "karpathy", "karpathy+sol-pi"]
LABEL = {"sol-pi": "1 sol-pi", "baseline": "2 baseline", "karpathy": "3 karpathy",
         "karpathy+sol-pi": "4 karpathy+sol-pi"}
NAME = {"swebench": "SWE-bench Verified (12 tasks)", "stress": "Stress suite (5 cases)"}


def k(x):
    return "–" if x is None else f"{x / 1000:,.0f}k"


def main():
    print("### Resolution rate (solved / runs)\n")
    print("| Benchmark | " + " | ".join(LABEL[a] for a in ARMS) + " |")
    print("|---|" + "---|" * len(ARMS))
    for b, s in S.items():
        cells = []
        for a in ARMS:
            x = s["arms"].get(a)
            cells.append("–" if not x else
                         f"{x['resolve_rate']:.0%} ({x['solved']}/{x['runs']}); by round "
                         + "/".join(f"{r:.0%}" for r in x["resolve_rate_by_round"]))
        print(f"| {NAME.get(b, b)} | " + " | ".join(cells) + " |")

    print("\n### Tokens (input + output, all runs incl. failures)\n")
    print("| Benchmark | Metric | " + " | ".join(LABEL[a] for a in ARMS) + " |")
    print("|---|---|" + "---|" * len(ARMS))
    for b, s in S.items():
        for m, f in [("mean tokens / run", "mean_tokens_per_run"), ("mean output tokens / run", "mean_output_tokens"),
                     ("**tokens / verified solve**", "tokens_per_solved")]:
            print(f"| {NAME.get(b, b)} | {m} | " + " | ".join(k(s["arms"].get(a, {}).get(f)) for a in ARMS) + " |")
        for m, f, fmt in [("mean requests / run", "mean_requests", "{:.1f}"), ("mean wall min / run", "mean_wall_s", "{:.1f}")]:
            print(f"| {NAME.get(b, b)} | {m} | " + " | ".join(
                fmt.format(s["arms"][a][f] / (60 if f == "mean_wall_s" else 1)) if a in s["arms"] else "–" for a in ARMS) + " |")

    print("\n### Behaviour\n")
    print("| Benchmark | Metric | " + " | ".join(LABEL[a] for a in ARMS) + " |")
    print("|---|---|" + "---|" * len(ARMS))
    for b, s in S.items():
        for m, f in [("false completion claims", "false_completions"), ("hit turn/time limit", "timeouts_or_killed"),
                     ("runs that invoked a skill", "skill_invoked_runs")]:
            print(f"| {NAME.get(b, b)} | {m} | " + " | ".join(
                str(s["arms"][a][f]) if a in s["arms"] else "–" for a in ARMS) + " |")

    print("\n### Paired differences (matched task × round; bootstrap 95% CI)\n")
    print("| Benchmark | Comparison | n | Δ resolve rate [CI] | wins/losses | Δ tokens / run [CI] |")
    print("|---|---|---|---|---|---|")
    for b, s in S.items():
        for c, p in s["pairs"].items():
            lo, hi = p["d_resolve_ci95"]; tlo, thi = p["d_tokens_ci95"]
            print(f"| {NAME.get(b, b)} | {c} | {p['n']} | {p['d_resolve']:+.0%} [{lo:+.0%}, {hi:+.0%}] | "
                  f"{p['wins_losses'][0]}/{p['wins_losses'][1]} | {k(p['d_tokens_per_run'])} [{k(tlo)}, {k(thi)}] |")


def per_task(bench):
    import csv
    rows = [r for r in csv.DictReader(open(HERE / "results" / "runs.csv")) if r["benchmark"] == bench]
    tasks = sorted({r["task"] for r in rows})
    print(f"\n### Per task: {NAME.get(bench, bench)} (solved/runs, mean tokens)\n")
    print("| Task | " + " | ".join(LABEL[a] for a in ARMS) + " |")
    print("|---|" + "---|" * len(ARMS))
    for t in tasks:
        cells = []
        for a in ARMS:
            rs = [r for r in rows if r["task"] == t and r["arm"] == a]
            if not rs:
                cells.append("–"); continue
            sol = sum(r["resolved"] == "True" for r in rs)
            cells.append(f"{sol}/{len(rs)}, {k(sum(int(r['total_tokens']) for r in rs) / len(rs))}")
        print(f"| {t} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
    for b in S:
        per_task(b)
