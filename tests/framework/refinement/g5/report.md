# G5 final report — 444 control-eligible SWE-bench Verified issues

**Scope:** G5 contract `fed9674`, one round, four frozen arms. This result concerns **the 444 control-eligible issues**, not all 500 SWE-bench Verified issues. It is descriptive, separate from G1–G4, and does not establish a skill promotion or actual token savings.

## 1. Population, configuration and scoring

All 500 issues went through the official gold/no-op control process. Eligibility was **official gold `resolved=True` and official no-op `resolved=False`**, without coverage, log-text or `tests_status` vetoes. The final report-only audit reproduces444 eligible and56 excluded issues:53 gold-false,2 no-op-true, and1 without the required reports. No excluded issue was replaced. All44 Sphinx issues were excluded; repository coverage is therefore materially different from the full benchmark.

The completed eligible panel has **1,776 cells**, 444 per arm, with **1,998 charged attempts** and 21,926 recorded provider requests. Every latest grade is a known Boolean; no cell is infra-exhausted. Quality uses only the latest permitted attempt, while costs retain every earlier attempt, including harness failures. There is no grade or usage imputation.

- Arms: none; frozen K; frozen ours; Both mounting **K before ours**.
- Model: `Qwen/Qwen3.8-27B`; Codex 0.160.0.
- Per-attempt caps:60 requests,7,200 seconds,16,384 output tokens;30-minute stream-idle timeout; no hidden client retries.
- 16 rolling occupied slots, plain local client, no metadata gating or backend intervention.
- Frozen issue-adjacent queue seed 2026101401; original task/test definitions, skill snapshots and resource configuration retained.
- Bootstrap seed 2026101402, 20,000 paired task-cluster draws, as preregistered.

## 2. Per-arm outcomes and all-attempt charges

| Arm | Cells | Latest solves | Solve rate | Infra-exhausted | Total charged tokens | Tokens per solve |
|---|---:|---:|---:|---:|---:|---:|
| none |444|146|32.88%|0|≥80,773,184|≥553,240|
| K |444|161|36.26%|0|≥87,163,412|≥541,387|
| ours |444|181|40.77%|0|≥100,450,014|≥554,972|
| Both |444|161|36.26%|0|≥97,614,439|≥606,300|

Tokens per solve are all-attempt token totals divided by latest solves; the displayed lower bounds are rounded **down** to whole tokens. Exact recorded fractions and completeness flags are in `results.json`.

**Usage limitation:**172 historical attempts across91 cells have incomplete usage, distributed23/23/22/23 cells across none/K/ours/Both. All1,776 latest attempts have complete usage, but this does **not** make all-attempt costs complete. Total recorded charges are **≥366,001,049 tokens**. Unknown historical usage is neither set to zero nor inferred from missing receipts or infrastructure status.

### Retry and harness overhead — disjoint accounting

The following partitions all charges into latest-scored attempts and superseded work. “Retry overhead” here means superseded **nonharness** attempts; harness overhead is separate. Neither category is removed from the preceding totals.

| Arm | Latest-scored tokens, exact | Superseded retry attempts | Retry tokens | Superseded harness attempts | Harness tokens |
|---|---:|---:|---:|---:|---:|
| none |77,619,827|42|≥1,330,692|15|≥1,822,665|
| K |83,379,799|41|≥1,989,209|15|≥1,794,404|
| ours |97,354,494|38|≥1,690,546|16|≥1,404,974|
| Both |93,333,243|40|≥2,337,786|15|≥1,943,410|
| **Total** |**351,687,363**|**161**|**≥7,348,233**|**61**|**≥6,965,453**|

Thus1,776 latest attempts +161 superseded retries +61 superseded harness attempts =1,998 attempts. Their known charges sum exactly to366,001,049 tokens. All161 superseded nonharness retry attempts and11 harness attempts have incomplete usage.

Earlier progress summaries used a different convention: **expenditure after ordinal attempt1**, including successful final retry runs. That expenditure is ≥4,593,052/≥6,356,696/≥8,489,128/≥6,949,159 tokens for none/K/ours/Both, respectively (≥26,388,035 total). It overlaps the disjoint partition above and must **not** be added again. Both views are retained explicitly in `results.json`.

## 3. Paired task-cluster analysis

Each draw samples444 issues with replacement from sorted eligible IDs, using Python `Random(2026101402).randrange(444)`. The same issue multiplicities apply to all four arms and all comparisons, retaining each issue's full attempt costs and latest quality. Intervals are linear2.5th/97.5th percentiles over20,000 draws, not independent arm bootstraps. The bootstrap describes variation in this eligible task mix, not repeated model trajectories or the56 excluded issues.

### Solve-rate differences

Differences are first arm minus second arm, in percentage points (pp). All20,000 draws are defined for each pair.

| Pair | Difference | Paired95% bootstrap interval | First-only / second-only solves | Exact McNemar p |
|---|---:|---:|---:|---:|
| ours vs none |+7.88pp|[+2.93,+12.84]pp|80 /45|0.002226|
| ours vs K |+4.50pp|[−0.45,+9.46]pp|73 /53|0.090123|
| Both vs none |+3.38pp|[−1.13,+7.88]pp|62 /47|0.179671|
| Both vs K |0.00pp|[−4.73,+4.73]pp|59 /59|1.000000|

**Descriptive McNemar note:** two-sided exact binomial test on discordant pairs under probability0.5; no continuity correction and no multiplicity adjustment. These p-values are supplemental descriptive notes, not confirmatory promotion criteria. Equal K/Both solve totals do not mean identical solved sets:59 issues favor each arm.

### Tokens-per-solve ratios: actual costs versus a recorded-token proxy

The requested actual ratio is `(all charged tokens / latest solves)first / (all charged tokens / latest solves)second`; values below1 would favor the first arm. **Its point estimate and95% interval are unavailable for every pair**, because every arm has incomplete historical usage. All20,000 actual-cost ratio draws are undefined for every pair under the preregistered no-imputation policy; these nulls are retained privately, not silently dropped or replaced.

For transparency, the same paired draws also give the following **supplemental quotient of recorded-token lower bounds per solve**:

| Pair | Recorded-token TPS quotient | Paired95% proxy interval |
|---|---:|---:|
| ours vs none |1.0031|[0.8498,1.1831]|
| ours vs K |1.0251|[0.8799,1.1867]|
| Both vs none |1.0959|[0.9377,1.2798]|
| Both vs K |1.1199|[0.9720,1.2905]|

All20,000 **proxy** draws are defined. These quotients and intervals quantify only the recorded-token calculation: **a quotient of two lower bounds is not a lower bound on the true ratio**. They do not account for unknown usage and do not demonstrate actual savings. `results.json` keeps the unavailable true-cost ratios and these supplemental proxies in separate fields.

## 4. Per-repository latest solves

Each eligible issue has one cell per arm. Counts below are solves, not rates; the eligible column is the denominator for every arm in that row. The Sphinx zeros mean **no eligible cells were run**, not44 model failures per arm.

| Repository | Dataset issues | Eligible issues | none | K | ours | Both |
|---|---:|---:|---:|---:|---:|---:|
| astropy/astropy |22|21|4|8|7|5|
| django/django |231|229|74|80|96|85|
| matplotlib/matplotlib |34|33|8|8|14|9|
| mwaskom/seaborn |2|2|0|0|0|0|
| pallets/flask |1|1|1|0|1|0|
| psf/requests |8|2|1|1|1|1|
| pydata/xarray |22|22|5|2|8|5|
| pylint-dev/pylint |10|9|2|2|3|1|
| pytest-dev/pytest |19|19|6|12|11|11|
| scikit-learn/scikit-learn |32|31|19|19|13|18|
| sphinx-doc/sphinx |44|0|0|0|0|0|
| sympy/sympy |75|75|26|29|27|26|
| **Total** |**500**|**444**|**146**|**161**|**181**|**161**|

Django accounts for229/444 eligible issues (51.6%). Effects vary by repository; for example, ours exceeds K on Django and matplotlib but has fewer solves on scikit-learn. Small repository counts are not independently powered comparisons. Known prior task exposure was preregistered; this is not a pristine holdout.

## 5. Deviations, repairs and retained provenance

All changes below remain G5-only. Original attempts, patches, grades and usage evidence are retained privately, including failures; there are no replacement issues or deleted cost rows.

1. **Controls and eligibility.** The initial dataset-schema failure produced34 pre-grader refusals with no model calls; official cached metadata compatibility was repaired without changing frozen original test definitions. Earlier extra coverage/log/infra eligibility heuristics were withdrawn in favor of official `resolved` booleans only. All500 final decisions were re-audited;71 explicitly authorized infrastructure control-pair reruns remain in the record. The final population is444 eligible/56 excluded.
2. **Terminal HTTP5xx amendment.** The supervisor's amendment replaced the once-only5xx rule with up to **five budget-counted attempts**, clean sandboxes,60-second exponential backoff with0–20% positive jitter capped at900 seconds, and a600-second admission pause when at least8 of the last16 finished attempts end in5xx. Latest quality is scored; all costs remain charged. Model errors, ordinary empty patches, caps and timeouts are not5xx retry entitlements. Harness failures remain charged but are outside that five-attempt budget; ordinal attempt IDs are preserved. No cell ultimately exhausted the budget. The ledger contains169 HTTP-response observations and338 repeated native diagnostic observations (507 combined), with 165 attempts classified as terminal5xx, not 507 extra requests. It records93 backoffs and9 circuit-pause events; pause events can overlap/extend one pause. Unavailable historic times/request indices remain explicitly unknown.
3. **Socket repair.** Overlong Unix-domain socket paths were replaced by owned short bind sources. The original socket/stop-cascade recovery accounts for24 retained harness attempts:16 before native start and8 with native activity. Their charges were not erased or treated as ordinary scored failures.
4. **Capture lifecycle repair.** Short bind sources initially disappeared before stopped-container workspace copying. The repaired lifetime is capture → grading → actor removal → broker cleanup, with retained copy stderr and a shared admission/forwarding safety stop on native-success capture failure.32 capture-failed and4 supervisor-interrupted native attempts are retained and charged as harness failures. Three interrupted request completions remain unknown; usage was not invented. Together with the24 original recovery attempts and1 pre-native deployment-drain attempt, these make61 harness attempts. Safe deployments subsequently drained in-flight work rather than killing native calls or graders.
5. **Generated artifacts and empty patches.** Source-only projection excludes generated bytecode, caches and native build products while retaining legitimate binary assets and original captured bytes. A Git binary patch is not itself an artifact. The historical scan covered233 patches;50 contained generated artifacts,30 cleaned patches remained nonempty and20 became empty. **30 official cleaned-source regrades** and **60 historical empty-outcome corrections** used **zero model calls**, the same frozen controls/images/tests/resources, and unchanged known token charges. Ordinary empty source patches are valid unsolved outcomes without official grader execution. The path parser also received the neutral-working-directory/space-path correction. Original bytes and grades are retained, not silently rewritten.
6. **Missing `tests_status`.** The grader now adjudicates the official Boolean `resolved` before optional status/coverage/log diagnostics. The four archived reports for `g5-037-K`, `g5-112-K`, `g5-112-Both`, `g5-171-K` all have `resolved=False`, `infra_failure=False` and missing `tests_status`; an old diagnostic KeyError had incorrectly made them unknown. Retained-report-only adjudication made all four valid unsolved, with **no model calls, grader executions or test reruns** and unchanged tokens/solve count. `patch_successfully_applied=False` did not override the official outcome.
7. **Six retained pre-fix cells.** Genuine completed model outcomes from the original controller were retained rather than rerun selectively. They used the earlier lifecycle, but received the applicable deterministic source/empty re-adjudication without new model calls. These six cells remain in the final paired panel:

   | Cell | Arm | Latest solved | Retained model attempts |
   |---|---|---:|---:|
   | g5-012-K |K|False|2|
   | g5-016-Both |Both|True|2|
   | g5-018-Both |Both|True|1|
   | g5-016-ours |ours|True|2|
   | g5-018-ours |ours|True|2|
   | g5-022-ours |ours|True|1|

   This mixed lifecycle provenance is a limitation, not a reason to discard their costs or rerun only successful/unsuccessful cells.

## 6. Completion, ownership, storage and integrity audit

- The controller is no longer running. Its normal completion marker records1,776 cells/1,998 attempts after the executor and storage watcher closed; the final controller log has no traceback. A numeric OS exit status was not independently captured, so none is invented.
- A final Docker namespace inspection found **zero G5-owned containers**.499 distinct lease image IDs were reconciled.418 IDs have explicit G5-creation records; none remains. Two dangling G5-created images were removed at the final audit only after checking creation records, preexisting protection, tags and absence of referencing containers. Removal used **no force and no parent pruning**. The81 preexisting leased images were preserved. No new volumes remain; unrelated/preexisting objects were not targeted.
- At the2026-10-16 15:12:43 UTC cleanup snapshot, root free space was **1,835,648,925,696 bytes** (1,835.65GB, about 1.670TiB), above the300GB floor. Privately retained evidence occupied235,621,802,746 bytes (235.62GB). Free-space changes on the shared filesystem are not attributed to image removal.
- All1,776 latest native-stream, patch, capture-proof and grade hash bindings were reconciled to retained files/archive manifests or explicit no-model correction files. All **465 archives,215,670,497,995 bytes**, were rehashed and match their creation hashes; their original byte/mode/link verification remains intact. This audit exported no raw contents.
- All500 official control decisions were read and independently re-derived from retained reports. The full four-arm panel, sequential attempt identities, budget exclusions, latest quality, all-attempt token sums, cost completeness and repository totals were checked.
- **73 tests passed** using unittest discovery from the G5 directory, including4 real-Docker lifecycle fixtures with zero model calls and the new paired-statistics, missing-usage, overhead and exact-McNemar tests. Actual pair p-values were additionally checked using an independent exact rational-binomial recurrence; SciPy is not required.
- Frozen preregistration/amendment hashes were verified. Analysis and integrity checking made **zero model calls and zero grader reruns**. Only compact summaries, code and hashes enter Git; raw traces, patches, grades and bootstrap draws remain private. No G4 files, README, docs or skills were changed; no push.

## 7. Interpretation and reproducibility

On the444 control-eligible issues, ours has the highest observed solve count:181 versus146 for none and161 for K. The paired ours–none solve-rate interval is positive; the ours–K interval crosses zero. Both matches K's aggregate solve count. The recorded-token TPS quotient for ours versus none is near1, but neither the proxy intervals nor the incomplete all-attempt usage establish actual cost savings. These findings do not generalize automatically to all500 issues, other model rounds, or G1–G4.

`results.json` is the full-precision machine-readable summary. `final_analysis.py` reproduces the paired draws, disjoint cost partition, repository counts and exact McNemar calculations from retained inputs; `final_integrity.py` verifies the retained archive/manifest chain. `final-integrity-summary.json` is the compact integrity evidence.

Key input/draw SHA256 anchors (the remaining hashes are in `results.json`):

- Final model summary: `94169f4cd69e22f5f30198377535a1fc563a5ff703a5a7e1521879c4cda79e1d`.
- Frozen queue: `83810ee920c0e8246179e9e6ad28e51c44d738287b1faa4fb70a9ebf44322b36`.
- Private paired multiplicity matrix: `5c96cac9bf191dd1cdbe7a1133b4df56ab3cf22342e99db9b0de0a5f05dbc3e3`.
- Private paired statistics including undefined draws: `e7d13fccbb743e853aab9d58173471fd518c5ca9ebb853b03c59591bbbc59f3e`.
