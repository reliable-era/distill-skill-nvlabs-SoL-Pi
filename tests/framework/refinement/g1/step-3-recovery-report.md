# Step 3 recovery complete: four verified control-solvable tasks

Standing authorization and local startup/completion fixes were committed in
7d1eca5; bounded window committed before inference in 4c155b8. Window:
2026-10-08 12:44:15–16:44:15 +08, latest start 14:44:15. Direct18001 only;
valid admission running < 8, waiting allowed; 60 requests / 120 min / 16K.

| Task | Result | Requests | Complete tokens | Native wall | Original tests |
|---|---|---:|---:|---:|---:|
| go/food-chain | Solved | 18 | 274,604 | 4.93 min | 11 |
| sparql-university | Solved, separate authorized retry | 13 | 448,941 | 9.31 min | 3 |

Totals: two starts, two verified solves, 31 requests, 723,545 complete tokens,
zero unknown-cost requests, no request/wall cap hits. All 31 receipts have
provider status 200, EOF and source-normalized complete accounting on direct
127.0.0.1:18001. Both runs have descriptive heavy-load flags; retain them and
report wall time without causal load adjustments. Per-request and 30-second
load records are preserved.

The eligible pool now contains break-filter-js-from-html, overfull-hbox,
go/exercises/practice/food-chain and sparql-university. The first two retain
their original prior-calibration grades; SPARQL's original failed/interrupted
attempt and its costs remain separate from this successful retry. The five
fallback fixtures did not run because the gate reached three after food-chain;
none has been substituted or relabeled solved. Their zero-model startup failures
from the previous cohort remain preserved.

Saved-log audit: regex reached the model and spent its output allowance on
reasoning, ending turn.completed without an executed artifact write. It is a
real failure and was not retried. SPARQL executed two successful file reads,
then ended turn.failed with fatal SDK 429. Both forwarded provider requests
were status 200/EOF, not provider-rate-limit failures. The owned frontend's
nonblocking completion lock is the supported race diagnosis (not a directly
recorded lock observation). Local bounded serialization fixes the race without
provider resends, changing shared servers, or increasing model caps. The
one retry was explicitly authorized and is separately recorded.

Nominal caps remain frozen. The three-solvable-task gate passes; Step 3 is now
complete, not a savings result. Proceed to Step 4 under standing authorization.
B3(a), candidate limit, original graders and sealed allocations stay unchanged.

Advance floor-risk disclosure remains: the exposed Terminal-Bench results may
leave few sealed solves, noisy tokens-per-solve and inconclusive paired 95%
ratio intervals. Aider cannot replace Terminal-Bench's separate acceptance
requirement. No sealed model calls, candidates, comparative savings or
promotion yet; canonical skill unchanged.

Evidence: calibration-recovery/{saved-log-classification.json,
step-3-recovery-audit.json,request-accounting-audit.json,
per-run-load-records.json,calibration-result.json,recovery-decision.json}.
Private native/model traces and exact artifacts: /tmp/solpi-g1-cal-b20f02279a06.
Worker 892212 terminal; owned containers/network absent, cleanup errors empty.
Previous cohorts and immutable archive files are unchanged.
