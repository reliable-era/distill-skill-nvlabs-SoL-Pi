#!/usr/bin/env python3
"""Aggregate graded runs into per-run rows (runs.csv) and per-benchmark x arm summaries (summary.json)."""
import csv, json, random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ["sol-pi", "baseline", "karpathy", "karpathy+sol-pi"]
PAIRS = [("sol-pi", "baseline"), ("karpathy+sol-pi", "karpathy"), ("sol-pi", "karpathy")]


def parse_stream(path):
    usage_by_msg, skills, result = {}, [], None
    for line in path.read_text().splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "assistant":
            m = d["message"]
            usage_by_msg[m.get("id")] = m.get("usage") or {}
            for c in m.get("content", []):
                if c.get("type") == "tool_use" and c.get("name") == "Skill":
                    skills.append(c["input"].get("skill") or c["input"].get("command"))
        elif d.get("type") == "result":
            result = d
    if result and result.get("usage"):
        u = result["usage"]
        inp = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
        out, requests = u.get("output_tokens", 0), len(usage_by_msg)
    else:  # killed before a result event: fall back to the last usage of each streamed message
        inp = sum(u.get("input_tokens", 0) for u in usage_by_msg.values())
        out = sum(u.get("output_tokens", 0) for u in usage_by_msg.values())
        requests = len(usage_by_msg)
    return {"input_tokens": inp, "output_tokens": out, "total_tokens": inp + out, "requests": requests,
            "turns": (result or {}).get("num_turns"), "end": (result or {}).get("subtype", "killed"),
            "skills_invoked": ";".join(s for s in skills if s)}


def collect():
    rows = []
    for bench in ("swebench", "stress"):
        for res in sorted((HERE / "runs" / bench).glob("*/*/r*/result.json")):
            run = res.parent
            r = json.loads(res.read_text())
            if r["round"] == 0:  # r0 = smoke tests, not scored
                continue
            if bench == "swebench":
                if not (run / "graded.json").exists():
                    continue
                r["resolved"] = json.loads((run / "graded.json").read_text())["resolved"]
            r.update(parse_stream(run / "stream.jsonl"))
            r["task"] = r.pop("instance_id", None) or r.pop("case")
            r["benchmark"] = bench
            # claimed done = ended normally (not max-turns / timeout / error) but grader failed
            r["false_completion"] = (not r["resolved"]) and r["end"] == "success" and not r["timed_out"]
            rows.append(r)
    return rows


def boot_ci(diffs, n=2000, seed=42):
    if not diffs:
        return None, None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def summarize(rows):
    out = {}
    for bench in sorted({r["benchmark"] for r in rows}):
        b = [r for r in rows if r["benchmark"] == bench]
        tasks = sorted({r["task"] for r in b})
        rounds = sorted({r["round"] for r in b})
        cell = {(r["task"], r["arm"], r["round"]): r for r in b}
        # only tasks x rounds that every arm finished, so the comparison is matched
        keys = [(t, k) for t in tasks for k in rounds if all((t, a, k) in cell for a in ARMS)]
        arms = {}
        for a in ARMS:
            rs = [cell[(t, a, k)] for t, k in keys]
            if not rs:
                continue
            solved = sum(r["resolved"] for r in rs)
            tok = sum(r["total_tokens"] for r in rs)
            per_round = [sum(cell[(t, a, k)]["resolved"] for t, kk in keys if kk == k) /
                         max(1, sum(1 for _, kk in keys if kk == k)) for k in rounds]
            arms[a] = {
                "runs": len(rs), "solved": solved, "resolve_rate": solved / len(rs),
                "resolve_rate_by_round": per_round,
                "total_tokens": tok, "mean_tokens_per_run": tok / len(rs),
                "mean_input_tokens": sum(r["input_tokens"] for r in rs) / len(rs),
                "mean_output_tokens": sum(r["output_tokens"] for r in rs) / len(rs),
                "tokens_per_solved": tok / solved if solved else None,
                "mean_requests": sum(r["requests"] for r in rs) / len(rs),
                "mean_wall_s": sum(r["wall_s"] for r in rs) / len(rs),
                "false_completions": sum(r["false_completion"] for r in rs),
                "timeouts_or_killed": sum(r["end"] != "success" or r["timed_out"] for r in rs),
                "skill_invoked_runs": sum(bool(r["skills_invoked"]) for r in rs),
            }
        pairs = {}
        for x, y in PAIRS:
            dr = [cell[(t, x, k)]["resolved"] - cell[(t, y, k)]["resolved"] for t, k in keys]
            dt = [cell[(t, x, k)]["total_tokens"] - cell[(t, y, k)]["total_tokens"] for t, k in keys]
            if dr:
                pairs[f"{x} - {y}"] = {
                    "n": len(dr), "d_resolve": sum(dr) / len(dr), "d_resolve_ci95": boot_ci(dr),
                    "d_tokens_per_run": sum(dt) / len(dt), "d_tokens_ci95": boot_ci(dt),
                    "wins_losses": [sum(d > 0 for d in dr), sum(d < 0 for d in dr)]}
        out[bench] = {"tasks": len(tasks), "rounds": rounds, "matched_runs_per_arm": len(keys),
                      "arms": arms, "pairs": pairs}
    return out


if __name__ == "__main__":
    rows = collect()
    cols = ["benchmark", "task", "arm", "round", "resolved", "total_tokens", "input_tokens",
            "output_tokens", "requests", "turns", "wall_s", "end", "timed_out", "false_completion",
            "patch_bytes", "skills_invoked"]
    with open(HERE / "results" / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    s = summarize(rows)
    (HERE / "results" / "summary.json").write_text(json.dumps(s, indent=2))
    print(json.dumps(s, indent=1)[:4000])
