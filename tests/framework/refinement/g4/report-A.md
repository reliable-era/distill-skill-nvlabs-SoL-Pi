# G4 Part A — blocked preparation and reused historical measurements

**Status: PREPARATION_BLOCKED_REQUIRED_SECURITY_AUDIT; ROUTE NOT TESTED.**
This is a descriptive evidence report, not a gate or shipment decision. Parts
B/C continue separately. G1–G3 results are closed, unchanged and not pooled here.

## New upstream SoL-Pi rows: unavailable, not zero

| Fresh arm | Planned cells | Attempted | Verified solves | Provider tokens / tokens per solve | Helper requests/costs |
|---|---:|---:|---|---|---|
| Unmodified upstream SoL-Pi (`solpi`) |37|0|Unavailable|Unavailable|No calls; activation/transport not verified|
| Same upstream + frozen Karpathy (`solpi_K`) |37|0|Unavailable|Unavailable|No calls; activation/transport not verified|

The74 cells are the original10 diagnostics (5 development×2 rounds,
5 heldout×3) plus6 original SWE Verified issues×2, for each of the two arms.
They remain in the frozen queue; they are **unattempted blocked cells**, not
failed-control exclusions, failures, savings, or evidence of inferiority.
Original caps remain60 turns/1800s. No four redundant fresh Claude arms were run.

## Why startup stopped

Pinned unmodified NVlabs SoL-Pi commit
`1559b5cb12c72da4a485bc50fe326586b216fb19` requires Pi0.85.1. The initial npm12
validation has156 passing tests/two package-output failures. An isolated npm11.6.2
validation passes all158 tests, typechecking and package checks, then the
upstream-required `npm audit --audit-level=high` fails (three high-severity locked
dependency advisories). Upstream installation instructions require stopping.
Both original validation attempts/log hashes are preserved in
`upstream-validation-result.json`; no upstream/lockfile patch or audit-fix occurred.

The planned `sol-pi.full-stack.json` sets actionFusion, observationPack,
evidencePreservingReducer and onlineContextCompact true, with the unchanged
cacheWriteReadRatio12.5. `A-config-provenance.json` records its exact hash and
explicitly marks config-loaded, provider-registration, effective mechanisms and
Pi primary/helper capture transport **not verified**. The planned reducer is the
same logical Qwen model on8000, not a cheaper helper. No Part A model/probe/helper
call occurred, so helper cost is not a measured zero-token invocation.

**This prerequisite failure does not establish8000 incompatibility.** No API
compatibility/startup inference was attempted. Bypassing the required stop would
need explicit approval; none is presumed. A's report must not say that the
unmodified extension was proved unable to use8000.

## Original four Claude Code2.1.286 rows, reused without repricing

Source: `historical-A.json`, which freezes148 original cells (132 pruned plus16
random-followup), verifies12 original stage CSV totals and records source hashes.
The shipped ours skill is SHA68ea78dc, not a rejected candidate or old bundle.
Original reported model identity and campaign identities are retained in that
artifact. The two user-declared Qwen variants are one logical model; no variant
shares or mixed-pool label are used.

The following amounts are **original CLI query-pipeline reported token estimates
or lower bounds**, NOT newly collected exact provider receipts, dollars, or
reconstructed pricing. The frozen completeness flag concerns original usage
records; it does not convert CLI estimates into exact provider metering.

| Historical arm | Campaign | Attempts | Solves | Original reported tokens / lower bound | Original amount per solve / lower bound | Usage records complete | Model timeouts |
|---|---|---:|---:|---:|---:|---|---:|
| none | Diagnostics |25|21|4,919,635|234,268.33|Yes|0|
| ours | Diagnostics |25|23|5,817,212|252,922.26|Yes|0|
| K | Diagnostics |25|19|5,623,830|295,991.05|Yes|0|
| Both | Diagnostics |25|22|6,335,331|287,969.59|Yes|0|
| none | SWE |12|9|≥14,545,393|≥1,616,154.78|No;3 incomplete records|3|
| ours | SWE |12|11|≥15,651,630|≥1,422,875.45|No;2 incomplete records|2|
| K | SWE |12|11|≥15,928,429|≥1,448,039.00|No;2 incomplete records|2|
| Both | SWE |12|8|≥15,488,838|≥1,936,104.75|No;3 incomplete records|3|

Original grader-timeout counts are0 in all eight campaign rows. Incomplete
record identities remain in the provenance artifact; costs are not imputed or
rewritten. Table values are display rounding of frozen original amounts, not
cost re-estimation.

## Comparisons and limits

Fresh upstream numerator costs/solves are unavailable: all `solpi`/`solpi_K`
ratios versus reused none/K are undefined, and all20,000 prospective paired
cluster draws for those cross-harness comparisons are undefined. No interval
can be manufactured from zero attempts. Bootstrap seed remains2026101211; the
final analysis must retain null draws, not replace them with zero. `analysis-A-historical.json` actually records all20,000 paired task-cluster draws
on148 original cells/16 clusters, using unchanged original CLI amounts. Historical
full-panel ratio points are unavailable because original usage is incomplete.
Only775/20,000 draws define historical ratios;19,225 are retained null. The
conditional-on-defined-draw intervals below are **not** full-panel95% intervals
and do not establish a savings claim:

| Historical comparison | Full-panel point | Conditional interval (775 defined draws) | Undefined draws |
|---|---|---|---:|
| none/K |Unavailable|[0.775966,1.208888]|19,225|
| K/none |Unavailable|[0.827207,1.288717]|19,225|
| ours/none |Unavailable|[0.785356,1.291653]|19,225|
| ours/K |Unavailable|[0.772002,1.264476]|19,225|
| Both/none |Unavailable|[0.998455,1.283646]|19,225|
| Both/K |Unavailable|[0.876589,1.329386]|19,225|

Fresh upstream comparisons have0 defined/20,000 null draws and no interval. This
analysis keeps historical CLI instrumentation separate from B/C provider costs;
no source-validation test is presented as performance evidence.

Even if fresh rows become available with approved prerequisites, paired ratios
against Claude Code2.1.286 would be **informational cross-harness comparisons**:
Pi0.85.1/upstream mechanisms versus Claude Code, differing instrumentation and
historical CLI estimates versus fresh provider receipts. No pooled A/B/C causal
claim, gate, pass/fail threshold, promotion, shipment or push follows.

## Evidence and remaining audit boundary

- Selection/order/resources/config/source provenance: `selection.json`,
  `queue-order.json`, `preregistration.json` (commit03e4bc5 before first G4 POST).
- Reused original measurements: `historical-A.json`, original source hashes and
  stage-total checks; no historical actor/grader rerun.
- Required upstream stop: `upstream-validation-result.json`,
  `A-preparation-status.md`, `A-config-provenance.json`.
- No live A-owned actor/helper processes were started. Original local validation
  jobs finished; source clean. This is not a claim that B/C cleanup is complete.
- Full goal completion remains pending B/C execution/reports, actual-data20k
  analysis, all-attempt reconciliation and the final requirement/integrity audit.
