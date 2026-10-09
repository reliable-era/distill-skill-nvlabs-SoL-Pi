# G2 final result — negative confirmation, no shipping

## Decision and evidence boundary

**G2 ends NEGATIVE under the explicitly authorized conservative K-denominator
analysis.** All108 planned Aider cells completed; no further tuning, retries,
Terminal calls or shipping. Candidate/No skill passes, but Both/Karpathy and
candidate/Karpathy do not pass the required final gates. No comparator was
substituted, and candidate/Both remains informational.

This is a **test disposition**, not proof that the candidate has no effect or
that its true K-comparator ratios exceed the thresholds. The original
preregistered complete-cost analysis remains **evidence-incomplete/inconclusive**:
round1 JS/K request97 has no terminal provider usage/EOF receipt. Its cost was
never estimated, excluded or rerun. The supervisor's separately recorded ruling
allows only conservative K-denominator bounds; those bounds did not establish
all gates. Larger unknown K cost could improve the true K ratios, so failure of
the surrogate is not evidence that the true K comparisons necessarily fail.
The candidate's exact No-skill comparison alone is insufficient for G2 acceptance.

G1 remains closed negative at `f537bfa`; the separate G2 contract is `1401e9a`.
No historical development/calibration costs or solves were pooled into G2.
Canonical remains `68ea78dcb9ee8a565f99c8a1b8bfec13f4c6d65c5695ce847eb5577b0449b1ef`.
No candidate recommendation or canonical change is made.

## Aider all-arm score table

Nine sealed tasks × four matched arms × three independent rounds =108 cells;
27 per arm. **2,544 provider requests, ≥82,334,104 tokens,41 verified solves,
67 failures**. All grades valid;107 cells have complete costs/EOF, one K cell
has the retained named accounting gap. Two No-skill60-request cap failures
are included at full cost. Tokens include every failed run.

| Arm | Solves / attempts | Failures | Provider tokens | Tokens / verified solve | Descriptive solve Wilson95% |
|---|---:|---:|---:|---:|---:|
| No skill | 7 /27 |20|23,658,140|3,379,734.29|13.17–44.68%|
| Karpathy |10 /27|17|≥19,813,433|≥1,981,343.30|21.53–55.77%|
| Candidate2 |13 /27|14|16,465,773|1,266,597.92|30.74–66.01%|
| Both |11 /27|16|22,396,758|2,036,068.91|24.51–59.27%|

K entries are **lower bounds**, not complete totals. Exact K tokens/solve is
unavailable. Quality intervals are descriptive: repeated attempts of the same
nine tasks are not independent population draws. All required observed
no-fewer-solves comparisons pass, but population quality equivalence is not proven.

## Ratios and paired task-cluster95% intervals

20,000 paired task-cluster replicates, seed2026100911; each sampled task retains
all matched arms and all three rounds. Nearest-rank2.5th/97.5th percentiles.
Undefined replicates are+∞, never discarded. A null upper endpoint would block
acceptance; all final surrogate endpoints below are finite.

| Comparison | Point ratio / bound | Paired95% interval | Undefined replicates | ≥5% cheaper | No fewer solves | Upper<1 | Required disposition |
|---|---:|---:|---:|---|---|---|---|
| Candidate / No skill |0.374763|[0.114493,0.854773]|79|yes|13≥7|yes|PASS|
| Both / K |≤1.027620|surrogate[0.352441,2.946979]|31|not established|11≥10|no|FAIL TO ESTABLISH|
| Candidate / K |≤0.639262|surrogate[0.309018,1.129367]|12|yes conservatively|13≥10|no|FAIL TO ESTABLISH|
| Candidate / Both |0.622080|[0.296785,1.199350]|21|yes|13≥11|no|informational only|
| K / No skill |≥0.586242|lower-bound surrogate[0.235331,1.151644]|79|not established for true K|10≥7|no|informational only|
| Both / No skill |0.602435|[0.198498,1.573309]|98|yes|11≥7|no|informational only|

No-skill reference ratio to itself is1. K-denominator intervals are intervals
for an **upper-bound surrogate**, not exact equal-tailed intervals for the
unknown true ratio. The true point and each replicate ratio are≤surrogate;
therefore its97.5th percentile is a conservative upper bound, but a failed bound
cannot prove the true gate fails. K/No-skill has the reverse≥relation and no
upper-bound acceptance interpretation. No missing-cost imputation was made.
The exact candidate/No-skill estimate is62.52% lower tokens/solve on this panel,
with the stated paired interval; this does not satisfy the all-comparator G2
contract or establish generalized savings.

Original outputs: `analysis/aider-final-original.json` preserves unavailable
ratios and `evidence_complete:false`. Authorized output:
`analysis/aider-final.json` records `raw_evidence_complete:false`,
`analysis_eligible_under_supervisor_ruling:true`, and `family_accepted:false`.
The computational `evidence_complete` field in that output describes only the
surrogate projection, never raw complete accounting.

## Round variability and futility

Each table entry is solves / total tokens, nine attempts per arm per round.

| Round | No skill | K | Candidate | Both | All-arm solves / tokens |
|---|---:|---:|---:|---:|---:|
|1|2 /6,782,379|3 /≥7,225,667|5 /4,405,945|5 /6,775,810|15 /≥25,189,801|
|2|3 /7,038,351|3 /5,657,715|4 /7,440,601|3 /6,833,144|13 /26,969,811|
|3|2 /9,837,410|4 /6,930,051|4 /4,619,227|3 /8,787,804|13 /30,174,492|

Complete round1 futility was survived: exact candidate/No-skill0.259846582,
5 vs2 solves. Integer check `881189000 ≤3221630025` establishes the5% threshold.
This boundary did not declare early success. Independent36-,72-,108-cell
boundaries precede later rounds/final analysis. No additional partial-round
stopping rule or outcome-based schedule change was used.

## Wall and load — separate from token acceptance

| Arm | Summed native actor seconds | Native seconds / solve |
|---|---:|---:|
| No skill |13,266.91|1,895.27|
| K |11,111.07|1,111.11|
| Candidate |8,948.73|688.36|
| Both |10,554.56|959.51|

These are recorded native wall sums, not throughput, campaign elapsed time or
causal slowdown estimates. They exclude some setup, grading, queue observation
and between-wave pauses. Provider observation outages interrupted the agent,
not the running experiments; workers were reconciled rather than duplicated.
Ten cells retain heavy-load flags without exclusion, adjustment or causal claim.
All1,520 start/periodic load records and per-request observations are retained;
nominal cadence30s, maximum observed recorded gap30.607051s. Start admission
requires running<8; waiting requests are allowed. Backoff maximum600s.
Longest recorded native run1,947.852264s. Caps remain60 requests/7200s/16384
output tokens; two capped failures (`g2-aider-r2-t3-none`,
`g2-aider-r3-t7-none`) are retained. No USD or wall-to-cost conversion.

## Provenance, repair and cleanup

- Pre-inference freeze `75ab79c`: full216 conditional schedule, source/skill/
  resource hashes and original analysis; offline verification `0ed59c8`.
- Aider round seeds2026101001/2026101101/2026101201. Terminal conditional seeds
  2026101002/2026101102/2026101202. Complete schedules independently reproduced
  from these seeds. Sealed Aider selection SHA:
  `8a33bef7e3b7cf613c1d7cd56703c6821fa3d3b0ec4bb9ef264ee7256546a74d`.
- Frozen candidate SHA:
  `39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`;
  Karpathy SHA:
  `6e22cc54cb02a5e98ae42d06d9d7292db0c1b43894831b32879beb0166b2aea7`.
  Full trees and actual delivered prompts verified for every cell, including Both.
- Codex0.160.0 SHA:
  `12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad`.
  Local Qwen3.8-27B-FP8, direct127.0.0.1:18001 only. All wave launch runtime,
  provider/container/image/source fingerprints unchanged; request/response hashes
  verified. Full actor/grader image IDs and resource recipes in `plan.json`.
- Source pins: Aider grader tree `7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f`;
  official runner `5dc9490bb35f9729ef2c95d00a19ccd30c26339c`;
  Terminal sealed checkout `2fd12b88aafdd04a52c298e3940bcb189f9766d6`.
  Original grader/source/test manifests remain unchanged. JS read-only grader
  cache21,487 entries/tree digest checked before final JS calls. Failures of
  original syntax/compile/solution tests were not infrastructure-rescued.
- JS/K exact captured-artifact replay passed9 original tests with no inference.
  Raw failure/null grade/transport evidence remains untouched; sidecar hashes
  and `audit_repairs.py` distinguish repaired grade from unknown cost/EOF.
  `analysis-notes.md` contains the explicit prospective bounded ruling; original
  mathematical implementation/seed/20,000 draws unchanged. Eleven tests passed.
- Every bounded window committed before inference, prior unused allowances
  retired; latest start commit+2h, window end commit+4h. Specific workers checked
  before bounded waits. All workers and prefix-owned containers/networks are now
  independently absent. No model retry, substitution, fallback, shared-server,
  nginx, gpu01 or unknown-workload intervention.
- `audits/aider.json`, `audits/final-execution.json`,
  `analysis/final-boundary-check.json`, raw wave results and completion audits
  cover the actual108-cell experiment. Private receipts/native traces/prompts/
  captures/verifiers remain at indexed launch roots, not copied into this report.
  Supplemental execution audit was added after inference began and is explicitly
  not a replacement preregistration or statistical acceptance test.

## Conditional Terminal and project boundary

**Terminal-Bench was not attempted (0 cells/0 requests); no score or savings
claim exists for it.** Aider did not pass all three gates, so the conditional
Terminal adapter/resource work and108 calls were not eligible. Its frozen design
is retained, not substituted or pooled. This confirmation is closed negative;
no new candidate, retest or resumed G1 search is authorized by it.

`requirements.md` is the final prompt-to-artifact audit. `tests/STATUS.md` gives
the short disposition. End-of-G2 archival/README/public-push actions mentioned in
workspace policy occur only after reporting and are outside this contract's
G2-only/G1-preservation scope; none were performed as part of G2.
