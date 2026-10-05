# Completed Go development smoke — exploratory, not confirmation

Plan `f597ed4236f1df62e1bb6d981879e93767ce82c00080090ad7ff5f4ee83e527d` completed4starts/50providerPOSTs. Independent `smoke-audit.json` passed with errors[]. All four provider costs are complete, native reconciliation agrees, output budgets are valid, and owned cleanup was independently verified.

One previously exposed `food-chain` fixture, one scheduling round, Codex0.160.0, local Qwen3.8-27B-FP8 only. Same frozen scope-coverage candidate in Candidate/Both. Historical cohorts excluded.

| Arm | Solved attempts | Provider-reported tokens | Native actor seconds | Requests |
|---|---:|---:|---:|---:|
| No skill | 0/1 |153,345|262.4|13|
| Karpathy |0/1|232,823|491.4|13|
| Candidate |1/1|137,752|497.5|12|
| Candidate + Karpathy |0/1|163,078|205.2|12|

The candidate uses10.2%less traffic than No skill,40.8%less than Karpathy,15.5%less than Both on these attempts. It is slower than each comparator in actor wall time; this is not a latency win. All failures retain their costs. Tokens-per-solve is undefined for the three zero-solve arms; do not report finite ratios against them.

The trusted Go grader accepted11original test events for the candidate and rejected11for each other arm. These are tests within one task, not11independent solved tasks. No infrastructure error or timeout was observed in the panel. A single stochastic reused task cannot establish causal prompt superiority, stability, quality equivalence, confidence intervals, billing savings, or a majority-harness win.

Decision: retain the candidate unchanged for one bounded second-family development probe on existing `sanitize-git-repo`. Reuse its exact certified grader/cached image. Do not promote the candidate, alter the nine-task fresh allocation, or prepare all nine new environments based on this one result.
