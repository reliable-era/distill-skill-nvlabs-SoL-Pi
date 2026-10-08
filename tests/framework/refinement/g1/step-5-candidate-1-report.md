# Step 5 — candidate 1 matched screen complete: not qualified

All twelve predeclared cells completed under two windows committed before use.
Each of HTML, food-chain and TeX received four fresh matched arms. All failures,
including three request-cap hits, remain included; no completed cell was retried
or replaced. Both workers are terminal and all owned resources are independently
confirmed absent. Original grades and complete provider costs are valid in every
cell. Canonical skill and sealed selections remain unchanged.

| Arm | Solves / 3 | Complete tokens, all attempts | Tokens / verified solve | Native wall, all attempts |
|---|---:|---:|---:|---:|
| No skill | 2 | 4,485,890 | 2,242,945 | 48.99 min |
| Frozen Karpathy | 1 | 5,897,596 | 5,897,596 | 52.56 min |
| Candidate 1 | 1 | 3,244,909 | 3,244,909 | 25.00 min |
| Same candidate + Karpathy | 0 | 6,094,590 | Undefined (zero solves) | 32.09 min |

Candidate / No-skill tokens-per-solve ratio: **1.4467** (44.67% higher),
with observed quality loss: one solve versus two. Food-chain accounts for the
family loss: No skill solved it; candidate did not. Both had one Terminal-Bench
solve. Candidate / Karpathy ratio: **0.5502** (44.98% lower), without observed
solve-count loss in this screen. Candidate / Both ratio is **undefined** because
Both solved nothing; it is not counted as a comparator win.

**Decision: candidate 1 does not qualify.** It misses the approximately 25%
all-comparator development target and loses a solve against No skill. This is
the first non-improving candidate; the stop-after-two-consecutive-non-improving
rule has not fired. One of at most three candidate slots has been used. Any next
candidate must be supported by measured exposed-development evidence and frozen
before a new fresh four-arm screen; no acceptance criteria will be weakened.

Total screen inventory: **12 starts / 405 requests / 19,722,985 complete tokens;
4 verified solves / 8 failures; zero unknown-cost or unknown-grade cells**.
Wave 2 contributed 127 requests / 3,875,062 tokens, three solves / three failures.
The two halves belong to one preregistered matched screen; calibration and
historical cohorts are not pooled into its performance estimate.

Quality and variability: this is one development round with only two exposed
Terminal-Bench tasks and one Aider task. Solve counts and task-level outcomes
are observed, not estimates of stable population quality. Task and arm variation
is visible in the twelve rows; there are no independent repeated development
rounds from which to claim round-to-round stability. No confirmation confidence
interval or acceptance claim is made. Native wall is reported separately and
includes failed attempts. Retained load flags do not justify adjustment,
exclusion, reruns or causal slowdown claims. No USD claim.

Evidence: `mechanisms/candidate-1-screen-plan.json`,
`mechanisms/candidate-1-screen-audit.json`, both `screen-candidate-1-wave-*`
`calibration-result.json` and `wave-completion-audit.json`, and private native,
prompt, provider-receipt and original-verifier artifacts at the recorded roots.
The independent audit checks cell uniqueness/completeness, exact skill/prompt
contents, resource equality, direct18001, caps, admission timestamps, provider
accounting and original test evidence. No winner freeze, sealed model call,
confirmation, final G1 acceptance or promotion occurred.
