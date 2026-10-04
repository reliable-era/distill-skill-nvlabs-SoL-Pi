# Measure efficiency without rewarding incomplete work

## Measure the task

Fix behavior and acceptance checks before comparisons. Track completion, correctness, total API cost, wall time, model requests, retries, recalls, and integration failures. Count failed tasks and every component.

- Verified completion rate: verified solved tasks / attempted tasks.
- Cost per solved task: all costs / verified solved tasks.
- Cost per aggregate score: total cost / sum of scores. Do not silently use average score.
- Coordinator/integration cost share and duplicate investigations.
- Recall frequency, receipt rejections, and recovery from omitted evidence.

Zero solved tasks make cost per solved task undefined. Count summary/reducer calls even when rejected. Separate cached/uncached prices. API cost excludes machine time, storage, and human effort unless separately counted.

## Normalize observed telemetry

`scripts/cost_audit.py usage.jsonl --attempted 5 --solved 4` reads one object per request. Normalize provider counters into **mutually exclusive** categories. Do not label an inclusive prompt count as uncached input:

```json
{
  "component": "main",
  "input_uncached_tokens": 1000,
  "cache_read_tokens": 10000,
  "cache_write_tokens": 0,
  "output_tokens": 300,
  "rates_per_million": {
    "input_uncached_tokens": 2,
    "cache_read_tokens": 0.2,
    "cache_write_tokens": 2.5,
    "output_tokens": 8
  }
}
```

These synthetic example prices are not current rates. Use actual billed rates per request, including model changes. Component labels can be `main`, `coordinator`, `worker:<id>`, `reducer`, `compaction`, or `retry`. Label a request once; do not duplicate retries as worker records.

Report request counts, token categories/traffic, total/component costs, and cost per verified solved task. Reject negative/missing/nonfinite values and impossible completion counts. The script does not collect telemetry, interpret provider caches, or verify the supplied solved count. Prefer bills over inconsistent estimates.

## Roll out one change at a time

Compare baseline and one mechanism on matched tasks, models, budgets, acceptance checks, and prices. Add combinations after components pass the quality constraint. Repeat noisy runs and report variation; never infer universal savings from one run or lower-quality results.

Include small-fix, large-log, handoff, and long-context cases. Set permissible quality loss explicitly; zero-loss work must reject cheaper policies that miss required behavior. Do not weaken tests or stop early to lower measured cost.

For a small request without telemetry, report the actual change and checks. Avoid administrative cost reports or guessed percentages.
