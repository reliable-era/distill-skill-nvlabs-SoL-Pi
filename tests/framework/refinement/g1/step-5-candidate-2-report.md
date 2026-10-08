# Candidate 2 complete — fails the all-comparator gate; stop search

All twelve fresh predeclared cells completed under windows committed before
use. No cell was retried, replaced or borrowed. Original grades and full provider
costs are valid in all cells. Both workers and owned resources are absent.

| Arm | Solves / 3 | Complete tokens, all attempts | Tokens / solve | Native wall, all attempts | Native wall / solve |
|---|---:|---:|---:|---:|---:|
| No skill | 1 | 6,740,629 | 6,740,629 | 33.74 min | 33.74 min |
| Frozen Karpathy | 2 | 5,797,995 | 2,898,997.5 | 41.10 min | 20.55 min |
| Candidate 2 | 2 | 3,208,285 | 1,604,142.5 | 29.25 min | 14.63 min |
| Same candidate + Karpathy | 2 | 2,319,543 | 1,159,771.5 | 17.19 min | 8.59 min |

Candidate tokens-per-verified-solve ratios:
- Against No skill: **0.23798** (76.20% lower).
- Against Karpathy: **0.55334** (44.67% lower).
- Against Both: **1.38315** (38.32% higher).

There is no observed solved-count loss overall or in either represented family.
Candidate solved HTML and food-chain; the other skilled arms solved food-chain
and TeX. These are different task outcomes even when solved counts match.

**Decision: not qualified.** Candidate 2 beats two comparators, but not Both.
The goal requires all three. Under the improvement definition frozen before
candidate-2 calls, this is the second consecutive non-improvement against the
all-comparator goal gate. Enforce the stop-after-two rule: **no third candidate,
new inference window, winner freeze, sealed confirmation or promotion**. Do not
relabel Both as the candidate or otherwise change the comparison after results.

Screen inventory: **12 starts / 393 requests / 18,066,452 complete tokens;
7 solves / 5 failures; zero unknown costs or grades**. Wave 2 contributed
178 requests / 8,391,926 tokens, four solves / two failures. Wave 1's HTML /
Karpathy request-cap hit is included. Budgets remain 60 / 7200 / 16384 across
all arms; model/backend, original graders, images, source pins and isolation
remain matched. Candidate-1 costs are not pooled into these ratios.

Uncertainty and variability: one development round, two exposed Terminal-Bench
tasks and one exposed Aider task cannot establish stable population quality or
round-to-round behavior. Both screens show substantial task/arm variation; they
are separate tuning cohorts, not repetitions of one fixed skill. Observed
quality is reported without an equivalence claim. Wall includes failures and is
separate from token efficiency. Load flags are retained without exclusions,
adjustments, retries or causal slowdown claims. No USD claim.

Evidence: `mechanisms/candidate-2-screen-plan.json`,
`mechanisms/candidate-2-screen-audit.json`, both second-candidate wave results
and completion audits, and private prompt/native/provider/original-verifier
artifacts at their recorded roots. The independent audit reports
`COMPLETE_SCREEN`, `qualifies_for_winner_consideration: false`,
`improving_against_all_comparators: false`, and
`stop_after_two_non_improving: true`.

G1's savings objective is **not achieved**. This is a negative development stop,
not a failed or passed confirmation trial. Canonical skill is unchanged; the
18 sealed tasks remain unused by models. Per-family 5% savings, three independent
confirmation rounds and paired task-cluster 95% intervals below 1 remain
unverified, so no acceptance or promotion claim is permitted.
