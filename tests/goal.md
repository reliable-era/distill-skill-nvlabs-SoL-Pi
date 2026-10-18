# Active contract (G6): Claude Opus 5.5 transfer check

**CURRENT:study paused after3/300 native cells (3 valid solves,1 complete pair),379,421 reported tokens.** Allowance671d86c;controller drained/exited. False-positive quota stop:stale76%/0% smoke counters were incorrectly used as learning anchors;earliest live79%/19%,latest80%/20%. This inflated rate forecasts and blocked Django13410's second arm before inference. All results/charges retained;297 cells unstarted,not failed. No code correction or automatic restart;await supervisor decision on first-live-baseline correction and frozen-order continuation. Report/audit: `framework/refinement/g6/study-report.md`,`study-pause-audit.json`.

**ACTIVE supervisor clarification after `16aab94`:START the fixed300 cells;the full-N preflight veto and5pp reservation are superseded.** Use observed utilization +(active/pending/candidate cells)*running rate,initial0.25pp and updated after actual1pp steps over completed study cells. Weekly cap0.90 before1792353600,0.70 afterward;no reset-clock zero imputation. Reserve whole frozen-order pairs;normal quota boundary stops new pairs and drains reserved pairs. Any429/rejection stops ALL admissions. Concurrency2 through20 clean cells,then4 only with no429/5xx/overloaded events. At every pause/completion or actual new-week60% crossing,report and await supervisor continuation decision. N150/prompt/plugin/model/grader/usage and all other guards remain fixed. No push.

**Historical preflight state (superseded):Study GO received after `9d95eb8`;admissions PAUSED by quota preflight at0/300.** N remains150. Before weekly reset1792353600 require projection<0.90;afterward<0.70,keeping all existing guards. Supervisor forecast0.25pp/run plus existing5pp in-flight reservation permits an optimistic36 current-window +260 new-window calls =296<300,so do not spend calls or reduce N. Concurrency2 for first20 cells,then4 only with no429/5xx/overloaded events;if ever admitted. Report at completion,any guard stop,or actual new-week weekly utilization crossing0.60. Current paused analysis is undefined,not zero-effect/failure data. Details/evidence: `framework/refinement/g6/study-report.md`.

User-approved, advisor-reviewed design. Initial v1 was fixed before treatment results;the explicit-v2 A/B/C amendment was approved AFTER two treatment outcomes were seen,and activation observations motivated the change. `framework/refinement/g6/protocol.md` and preregistration disclose it;do not pool natural and explicit activation.

- Compare **none vs ours only**, one round, Claude Code CLI **2.1.302**, requested
  model **claude-opus-5-5**, headless stream-json. Freeze the current committed
  efficient-coding plugin snapshot; record CLI version, plugin commit and actual
  provider-reported model IDs for every run. No model fallback or Qwen route.
- Population: the **444 G5 control-eligible issues**. Draw150 outcome-blind using
  proportional repository strata and recorded seed; draw2 seeded smoke issues
  from the remaining294. `framework/refinement/g6/preregistration.json` fixes
  exact IDs, Hamilton rounding, seeds, issue order and randomized arm orders.
  Never read G5 model outcomes to allocate. Smoke is excluded from scoring.
- Two issue workers initially: run each issue's randomized arms consecutively.
  **60 Claude turns /120 minutes**, not60 G5 requests; retain nested/subagent usage.
  Both use identical canonical G5 task bytes,without the Codex-specific suffix;
  treatment prepends `/distill-sol-pi:efficient-coding `,control does not. Both
  enable the same stock skills. Control has exactly the two verified CLI built-ins;
  treatment adds only the normally installed frozen distill-sol-pi plugin. Record
  IDs/versions and reject extras. Verify full skill body/task in native root
  conversation stream,not just advertisement. Claim explicitly invoking the skill.
  Before projected utilization reaches0.90,stop admissions using live all-reported
  quota scopes and in-flight reservations;resume only on actual headroom evidence.
  Keep N150 even if budget forces an incomplete study;all smoke remains excluded.
- Disposable HOME per attempt; no host CLAUDE.md, settings, memories, skills or
  hooks. Reuse frozen G5 issue images, official controls/grader, sanitized source,
  source-only projection and empty-patch rule. Actors never see gold/control
  records. Owned internal Docker network plus an API-only egress proxy; no host
  network, Docker socket, other backend operations or unrelated cleanup.
- Use only the dedicated setup-token file at `$HOME/.config/solpi-g6/claude-oauth-token`
  (mode600); never read/mount/copy host `.claude/.credentials.json`. Supply the
  token only at runtime via an owned tmpfs env file. Never persist its value in
  images, command lines, logs, archives or Git; redact before writing streams.
- Charge all attempts. Keep uncached input, cache-creation, cache-read and output
  per model from result/modelUsage, including subagents. Report token volume and
  the preregistered cache-adjusted token-volume proxy separately, not dollar cost.
  No usage imputation; incomplete coverage makes this a solve-rate study.
- Terminal API5xx/529 overload: max5 budget-counted clean attempts, G5 backoff and
  circuit rule, latest quality/all costs.429/subscription limit: pause admissions
  until explicit reset and rerun, outside that failure budget; unknown reset
  requires supervisor input. Ordinary caps/timeouts/empty/model outcomes do not
  earn retries. Harness or cleanup uncertainty stops admissions with costs saved.
- Primary: paired solve difference,95% task-bootstrap CI (20,000 draws, recorded
  seed), exact McNemar. Secondary: paired all-attempt tokens/solve ratio where
  usage permits; cache-adjusted estimate separately. Descriptive, no promotion
  gate; claim limited to this eligible cohort/Claude Code configuration and state
  contamination cannot be ruled out. Do not pool with G5.
- Verify runner with unit tests and **no-model Docker plumbing before any Opus
  call**. If dedicated token missing, STOP and report. When available, run only
  **2x2 smoke**, report per-run tokens, wall time, provider model ID, skill
  activation, grade and rate-limit events, then **WAIT for explicit go** before
  the300-run study. No study authorization is implied by smoke success.
- G6-only code/summaries plus this contract; private raw evidence in a new owned
  `/tmp/solpi-g6-*` root. Preserve all preexisting/unrelated Docker/Git objects;
  root free strictly above300GB,80GB reserve per active issue. Commit locally,
  no push; do not change shipped plugin, README, docs, G4/G5 records or backends.

Verification is the committed allocation/configuration, tests and actual isolated
Docker source/plugin/network/capture/grader/cleanup evidence; then the four smoke
summaries. Between steps recheck frozen hashes and admission gates. If credentials,
API access, reset timing or isolation cannot be verified, stop with retained
cost/evidence and the exact next input needed; do not relax scope or silently retry.

---

# Closed goal (G5): full SWE-bench Verified

Set 2026-10-14 at the user's request ("execute the full version of benchmark, SWE-bench").
Choices made by the user: **SWE-bench Verified, all 500 issues**; **4 arms, Codex, 1 round**.
G1-G4 results stand and are not pooled with G5. Runs under the same standing authorization
and Claude supervision. G5 is descriptive measurement: no gate, no early stop, nothing shipped.

- **Arms (4):** No skill; Karpathy (frozen `framework/refinement/g2/frozen/karpathy/`); ours
  (shipped `skills/efficient-coding/`, SKILL.md SHA `68ea78dc...`); Both (ours + Karpathy).
  Same skill mounting and prompt as G4 Part C.
- **Tasks:** all 500 SWE-bench Verified issues, from `tests/eval/swebench_verified.jsonl` (record
  its hash). Before any model call, run the official grader's gold and no-op checks on every
  issue; exclude only issues that fail them and record why. No other exclusion or substitution.
  The 6 README issues and the G4 Part C sample are included; report them as previously exposed.
- **Harness and caps:** Codex 0.160.0, 1 round, 60 requests / 120 min / 16K output, as in G4
  Part C. Codex client settings: `stream_idle_timeout_ms=1800000` (requests may queue at 8000
  for many minutes; G4 lost 21 runs to the 5-minute default). Record the full Codex config.
- **Model route:** `127.0.0.1:8000` only, called as a plain client. **Do not gate admission
  on `/get_load` or `/v1/models`, and never touch nginx, the tunnels or any backend** (user,
  2026-10-12: "you do the request on the service 8000, donot want to operate it"). Slow or
  queued requests are normal. Concurrency: **16 runs** at a time.
- **Fairness:** each issue's 4 arms are queued next to each other in a per-issue random order
  (recorded seed).
- **Infrastructure failures, amended by user instruction2026-10-16:** runs whose final
  native event is an HTTP5xx (including native `error`/`turn.failed` with “unexpected
  status502”) receive a clean-sandbox rerun, uniformly for every arm, up to **5 total
  attempts**, replacing the once-only limit for5xx. Keep `connection_infra_failure=True`.
  Between5xx attempts use exponential backoff starting60s, capped15min, with jitter.
  Log every observed5xx (time,status,cell,attempt,request index; unknown index explicit)
  in per-cell and global ledgers. If at least8 of the last16 finished attempts ended
  on5xx, pause new admissions10min and log the pause; still16 plain-client slots,
  never `/get_load` gating or backend operations. Charge every attempt, report retry
  overhead separately, score latest. After5 attempts still ending5xx, retain the cell
  as **infra-exhausted**, not solved or dropped. Apply retroactively to the64 identified
  final502 rows and16 harness-affected/socket/aborted/refused cells; retain all earlier
  costs and records. Ordinary model outcomes, unsolved results, caps, timeouts and
  empty patches without terminal5xx are never retried under this amendment. Other
  connection refused/reset, pre-answer disconnect, image/container pre-agent failures
  retain the original once-only rule. No push.
- **Capture-regression supervisor correction:** keep the short socket bind source
  alive through capture and grading,remove it only after actor removal. Persist
  docker-cp stderr. Any capture failure following native exit0 must trip the
  shared admission/provider-forwarding safety stop. The32 resume-v1 capture-failed
  attempts and cleanly supervisor-stopped in-flight attempts are harness failures:
  retain/charge their tokens,give a clean fresh attempt,and exclude these harness
  attempts from the5-attempt5xx budget. Ordinal attempt IDs remain unique and all
  evidence/costs remain retained. Commit and pass a resumed-path Docker capture
  lifecycle regression before resuming;no server changes or push.
- **Source-patch/empty-outcome supervisor correction:** exclude `__pycache__`,
  `.pyc` and other generated binary build products from source patches while
  preserving original captured bytes separately. Audit every retained patch,
  including private archives,and deterministically regrade affected attempts from
  cleaned derivatives with the same frozen grader and no new model calls. Empty
  patches are valid ordinary unsolved outcomes (`grade_valid=True,solved=False`),
  without official grader execution;apply retroactively. Preserve all tokens and
  raw/previous grades. Commit/tests before applying at a clean admission boundary;
  allow existing native work and graders to finish,no backend changes or push.
- **Docker images:** pull/build each issue's image when its arms are about to run and remove
  it after its 4 runs are graded, unless it existed before G5. Never remove images, containers
  or volumes G5 did not create. Keep free space on `/` above 300 GB.
- **Records:** every request's response model and usage, every run, failure, cap and cost.
  Raw traces and patches stay in `/tmp`; commit only summaries.
- **Analysis:** solves, total tokens, tokens per verified solve (failures included), timeouts;
  cost ratios ours/none, ours/K, Both/none, Both/K with paired task-cluster bootstrap 95%
  intervals (20,000 draws, recorded seed). Incomplete costs are lower bounds, never imputed.
- **Outcome:** commit a preregistration before the first model call, progress reports while
  running, and `framework/refinement/g5/report.md` at the end. Do not change the shipped
  skill, README or `docs/`, and do not push; Claude updates the docs and pushes after a privacy
  scan. Never write private IPs or hostnames into committed files; refer to the route as
  "127.0.0.1:8000".

---

# Closing goal (G4): fill the open TBD measurements (runs complete; Claude finishing docs)

Set 2026-10-12 at the user's request ("complete the jobs TBD"). G1-G3 are closed;
their results stand and are not pooled with G4. G4 runs under the same standing
authorization and Claude supervision (workspace `supervisor-policy.md`).

G4 is **descriptive measurement**, not a promotion test. The shipped skill
(`skills/efficient-coding/`, SKILL.md SHA `68ea78dc...`) is the "ours" arm everywhere;
no candidate is shipped from G4.

## Shared setup (all parts)

- **Model route (user decision, 2026-10-12):** the gpu02 load balancer
  `127.0.0.1:8000` only, **16 concurrent runs** in total across all G4 parts.
  8000 serves `Qwen3.8-27B-FP8` and full-precision `Qwen/Qwen3.8-27B`. **Amendment
  (user, 2026-10-12, before any G4 model call): treat the two as the same model.**
  No "mixed pool" label. Still record the response `model` field and usage of
  every request.
- **Admission:** rolling queue; start a run when one of the 16 slots frees and
  `8000/get_load` shows no waiting requests on any backend; otherwise wait.
- **Do not touch:** nginx or its config, the tunnel, any backend server, gpu01,
  or other workloads. If 8000 is down, pause and report.
- **Fairness:** a task's arms are queued next to each other in a per-task random
  order (recorded seed), so matched arms see the same load and pool mix.
- **Records:** keep every run, failure, cap hit and cost. Infrastructure failures
  (never reached the model, or connection refused/reset) are rerun once from
  scratch under the same rule for every arm, keeping both records.
- **Analysis per part:** solves, total tokens, tokens per verified solve
  (failures included), timeouts; cost ratios versus No skill and versus Karpathy
  with paired task-cluster bootstrap 95% intervals (20,000 draws, recorded seed).
  No pass/fail gate and no early stop.

## Part A: Pi-harness table including NVlabs SoL-Pi

Fills the README rows "NVlabs SoL-Pi" and "NVlabs SoL-Pi + Karpathy".

- **Harness:** Pi coding agent, one pinned version for all arms, recorded.
- **Arms (2), amended by the user before any G4 model call ("re-use"):** SoL-Pi
  extension; SoL-Pi extension + Karpathy (frozen
  `framework/refinement/g2/frozen/karpathy/`). The other four README rows re-use
  the existing Claude Code measurements; the report must state that the SoL-Pi
  rows used the Pi harness and the re-used rows used Claude Code 2.1.286.
- **SoL-Pi extension:** NVlabs/SoL-Pi at commit
  `1559b5cb12c72da4a485bc50fe326586b216fb19`, built from source with no edits.
  Enable all four mechanisms (Action Fusion, Online Context Compact,
  ObservationPack, Evidence-Preserving Reducer) as in the upstream full-stack
  configuration; record the exact config file and its hash. The reducer's helper
  model is the same 8000 route (no separate cheaper model is available); say so
  in the report. Do not modify upstream code; if it cannot run against this
  route, record the reason and report Part A as blocked rather than patching it.
- **Tasks:** the same tasks as the Claude Code table: the 10 synthetic
  diagnostics (5 development x 2 rounds + 5 held-out x 3 rounds = 25 attempts per
  arm) and the 6 SWE-bench Verified issues x 2 rounds (12 per arm). 74 runs.
  Use the original campaign caps for each benchmark (SWE-bench: 60 turns,
  1800 s); record them.
- Report the two SoL-Pi rows with their harness stated. Paired ratios versus the
  re-used rows are informational only, because the harness differs.
- Re-use the existing G3 runner, receipt broker and grader adapters where possible.

## Part B: Terminal-Bench 2.0

- **Harness:** Codex 0.160.0. **Arms (4):** No skill, Karpathy, ours, Both.
- **Tasks:** the 9 sealed Terminal-Bench tasks from G1 Step 2
  (`framework/refinement/g1/terminal-selection.json`), unsealed now. Recheck the
  gold/no-op grader controls first; exclude only tasks that fail and record them.
- **Rounds:** 3. 108 runs. Caps: 60 requests / 120 min / 16K output.

## Part C: larger SWE-bench Verified sample

- **Harness:** Codex 0.160.0. **Arms (4):** No skill, Karpathy, ours, Both.
- **Tasks:** a fresh random sample of 30 SWE-bench Verified issues, drawn with a
  new recorded seed before any model call. Exclude the 6 issues already in the
  README table and the 18 previously exposed issues. Run the official grader's
  gold/no-op checks first; replace nothing, exclude only failures and record them.
- **Rounds:** 1. 120 runs. Caps: 60 requests / 120 min / 16K output.

## Outcome

Commit a report per part. Do not change the shipped skill, the README or
`docs/`, and do not push; Claude updates the documentation and pushes after a
privacy scan. Order: preregister all three parts first, then run B and C while
preparing A, then A.

---

# Closed goal (G3): full-eligible Aider run of frozen candidate 2

Set 2026-10-11 at the user's request. G2 is closed negative (a697bde, 8692e5d);
its result stands, is not rewritten and is not pooled with G3. G3 runs under the
same standing authorization and Claude supervision (workspace `supervisor-policy.md`).

## Why G3 exists

G2 used 9 tasks. Candidate 2 was 62.5% cheaper per solve than No skill (CI
0.11-0.85) and at most 0.64x Karpathy, but the Karpathy interval (up to
0.31-1.13) crossed 1. With 9 task clusters, two or three tasks decided the
comparison. G3 asks the same question on every eligible Aider polyglot exercise.

## Fixed setup

- **Arms (4), frozen, no edits:** No skill; Karpathy
  (`framework/refinement/g2/frozen/karpathy/`); candidate 2, SHA
  `39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`
  (`framework/refinement/g2/frozen/candidate/`); Both (candidate 2 + Karpathy).
- **Tasks:** all 211 eligible exercises from `framework/refinement/g1/polyglot-selection.json`
  (pinned revision `7e0611e7`, 225 exercises minus its 14 development exclusions).
  The 9 G2 tasks are included; the candidate was frozen before G2 and never tuned
  on them. Before any model call, run the gold and no-op grader checks on all 211.
  Exclude a task only if those checks fail, and record it. No other exclusion or
  substitution.
- **Model and route:** `Qwen/Qwen3.8-27B` on the tunnel backend, direct
  `127.0.0.1:9012` only. Never use the nginx balancer on 8000 (it mixes this model
  with the FP8 model) and never fall back to 18001/18002. Preflight: `/v1/models`
  must report `Qwen/Qwen3.8-27B`; record it and recheck at each round start.
  Record the backend for every request. This is a different model variant from
  G1/G2 (FP8), so G3 results are a separate cohort.
- **Harness and caps:** Codex 0.160.0; 60 requests / 120 min / 16K output per run.
- **Scheduling:** rolling queue with **18 concurrent runs** (user-approved,
  2026-10-11). A new run starts when a slot frees and 9012 reports
  `num_waiting_reqs == 0`; otherwise wait. Task order is shuffled per round with
  a recorded seed. A task's four arms are queued next to each other in a
  per-task random arm order, so matched arms see similar load.
- **Rounds:** 3. Each round = 211 x 4 = 844 runs. Round 2 starts only after the
  round-1 futility check.
- **Do not touch:** nginx, the tunnel, the honey server or its configuration,
  18001/18002, gpu01, or other workloads. If 9012 is down, pause and report.

## Acceptance

Same rule as G2. All three must pass; tokens include failed runs:

1. Candidate vs No skill.
2. Both vs Karpathy.
3. Candidate vs Karpathy.

For each comparison, tokens per verified solve must be at least 5% lower, the
paired task-cluster bootstrap 95% interval of the cost ratio (20,000 replicates,
recorded seed) must lie below 1, and verified solves must be no fewer than the
comparator's. "Candidate vs Both" is informational only. If any run's cost is
incomplete, use the G2 conservative-bound treatment and say so.

## Stops

- **Futility only, after round 1:** stop G3 as negative if the candidate is not
  at least 5% cheaper per solve than No skill or than Karpathy, or has fewer
  solves than either. This check cannot declare a win.
- **Infrastructure failures:** a run that never reached the model, or whose
  connection to 9012 was refused or reset (not a model error or cap), is marked
  infra-failed and rerun once from scratch. Both records are kept. The rule is
  the same for every arm. Everything else, including every model failure and cap
  hit, is kept as-is.
- Terminal-Bench stays sealed and is not part of G3.

## Outcome

Report per round and in total: a score table for all four arms (solves, tokens,
tokens per solve, timeouts) and all ratios with 95% intervals. Do not change the
shipped skill or the README; Claude updates the README and asks the user before
shipping anything.

---

# Closed goal (G2): sealed confirmation of frozen candidate 2

Set 2026-10-09. The user asked Claude to decide, and Claude decided to continue
with one confirmation test. G1 is closed (f537bfa); its result stands and is not
rewritten. G2 is a new, separate contract. It runs under the same standing
authorization and Claude supervision (workspace `supervisor-policy.md`).

## Why G2 exists

In G1's screen, candidate 2 used 76% fewer tokens per solve than No skill and
45% fewer than Karpathy, with no fewer solves. G1 rejected it only because it
did not beat "Both". Both is candidate 2 plus Karpathy, so that rule requires
Karpathy to make the candidate worse. The rule is replaced here by the original
campaign's three comparisons. The screen used 3 exposed tasks and 1 round, and
the candidate was designed from those tasks, so its effect is unproven and
probably overestimated. G2 tests it once on sealed tasks.

## Fixed setup

- **Candidate:** G1 candidate 2, SHA `39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`,
  frozen. No edits, no new candidates.
- **Arms (4):** No skill, frozen Karpathy, candidate 2, Both (candidate 2 + frozen Karpathy).
- **Harness, model, route, budget:** unchanged from G1. Codex 0.160.0, local
  Qwen3.8-27B-FP8, direct 127.0.0.1:18001 only, admission when fewer than 8
  requests are running, 60 requests / 120 min / 16K output per run.
- **Tasks:** the 9 sealed Aider polyglot tasks from G1 Step 2
  (`framework/refinement/g1/polyglot-selection.json`). No substitution.
  The 9 sealed Terminal-Bench tasks stay sealed and are used only in stage 2.
- **Rounds:** 3 independently scheduled rounds; arm order randomized per task
  with a recorded seed. Stage 1 = 9 tasks × 4 arms × 3 rounds = 108 runs.

## Acceptance (per family)

All three comparisons must pass. Tokens include failed runs.

1. Candidate vs No skill.
2. Both vs Karpathy.
3. Candidate vs Karpathy.

For each comparison, tokens per verified solve must be at least 5% lower, and
the paired task-cluster bootstrap 95% interval of the cost ratio must lie below 1.
Total verified solves must be no fewer than the comparator's. "Candidate vs Both"
is reported for information only and is not a gate.

## Stops

- **Early stop (preregistered, futility only):** after round 1 (36 runs), stop G2
  as negative if the candidate is not at least 5% cheaper per solve than No skill,
  or if it has fewer solves than No skill. This check can end G2 early but cannot
  declare a win.
- **Stage 2:** run the same design on the 9 sealed Terminal-Bench tasks only if
  Aider passes all three comparisons. If Aider fails, G2 ends as negative.
- Keep every run, failure and cost. No retries except cells that never reached the
  model (infrastructure failures), recorded separately.

## Outcome

Report a score table per family (solves, tokens, tokens per solve, ratios with
95% intervals for all four arms). If accepted, recommend shipping candidate 2,
or Both if it is the cheapest configuration. Do not change the shipped skill
without the user's approval. If rejected, close the project with the negative result.

---

# Closed goal (G1, narrowed): economical skill refinement on Codex + local Qwen

Closed 2026-10-08 by a negative development stop (f537bfa). Kept as history.

Set 2026-10-05 by the user. This replaces the 2026-10-04 goal below, whose
≥3/5-harness and three-family criteria could not be met under the user's
scope override. Rationale and audit: workspace `review.md`. The goal is
not achieved. The user reopened G1 on 2026-10-08 with standing authorization
and Claude supervision (workspace supervisor-policy.md). The prior operational
stop and six zero-model startup failures remain preserved. That amendment
authorized scoped Step 3 recovery and later steps only after the gate passed;
it did not waive acceptance or the search stop rule.
See `STATUS.md` and `framework/refinement/g1/standing-authorization.md`.

Final development disposition (2026-10-08): two complete matched candidate
screens failed the all-comparator gate. Candidate 2 beat No skill and Karpathy
but cost 38.32% more tokens per solve than Both. The preregistered stop rule
ends this search; third slot unused, no winner freeze or confirmation calls,
canonical unchanged. G1 savings acceptance is NOT achieved. See
`framework/refinement/g1/report.md` and `prompt-to-artifact-audit.md` there.
No further inference is authorized by this exhausted search contract.

## Objective

Refine `skills/efficient-coding` so that Ours uses fewer tokens per verified
solve than No skill, Karpathy, and Both, without losing verified solves, in
one harness on two benchmark families.

## Fixed scope

- **Harness:** Codex 0.160.0 only. Pi is an optional later extension after a
  Codex result; it is not a requirement. Copilot, agy, Cursor are out of scope.
- **Model:** local `Qwen3.8-27B-FP8` only, shared server unchanged, no fallback.
- **Benchmark families (2):** Terminal-Bench 2.0 and Aider polyglot.
  SWE-bench is out of scope.
- **Arms (4):** No skill, frozen Karpathy, candidate, candidate + frozen Karpathy.
- **Budget per run:** identical across arms: 60 model requests, 120-minute
  wall safety and 16384 output tokens. Under the user's decision.md amendment
  committed before continuation calls, freeze independent of solve count if
  no new request/wall cap is hit. The nominal budget was frozen at the new
  window end, 2026-10-07 07:18:43 +08. This does not establish solvability.
  Step 5 requires at least three verified No-skill-solvable development tasks;
  this replaces the half-of-development / five-of-ten calibration solve gate.
  If fewer than three remain, attempt up to five frozen exposed, non-sealed
  Aider fixtures once in task-ID order within that window. If the resulting
  pool still has fewer than three after actual Aider/Go model tests, stop G1 as
  inconclusive. Standing authorization now permits candidate runs and later
  steps once the gate passes, without changing acceptance or candidate limits.
  The old 600 s / 16-request budget remains retired.

## Task pools

- **Development pool (open):** the nine previously selected Terminal-Bench
  tasks (`framework/refinement/pi-takeover/terminal-10pct-selection.json`)
  and the reused Go/polyglot fixtures. All are exposed and may be used for
  tuning. They must never be used for confirmation.
- **Confirmation pool (sealed):** a fresh metadata-only sample drawn with
  the existing selector and a new recorded seed: 9 Terminal-Bench 2.0 tasks
  from the 78 eligible unexposed tasks (quotas 1 easy / 5 medium / 3 hard)
  and 9 Aider polyglot tasks stratified by language. No agent reads their
  traces or outcomes before the candidate is frozen. No task replacement.

## Acceptance criteria

- In each family, Ours uses at least 5% fewer complete reported tokens per
  verified solve than each of No skill, Karpathy, and Both, with no observed
  reduction in solved count on the sealed confirmation panel. Costs include
  failures, timeouts, and retries. Incomplete costs block a savings claim.
- Three independently scheduled rounds per confirmation cell.
- The paired task-cluster bootstrap 95% interval for the cost ratio lies
  below 1 against all three comparators in each family. With 9 tasks this
  requires roughly a 25% or larger true reduction (see `review.md` B3).
  If that is not met, the result is reported as inconclusive, not a win.
  This freezes review.md decision rule B3(a): retain the interval-below-1
  requirement and screen for approximately 25% or greater token reduction
  against all three comparators, with no observed solve loss. Do not weaken
  the rule after seeing confirmation results.
- Report solve-rate uncertainty, round variability, and wall time per solve
  separately. Tokens are not dollars; no USD claim.

## Execution rules

- Order: commit and short `STATUS.md` → record shared-server admission rules →
  draw and validate sealed samples (grader controls only) → calibrate budget →
  derive ≤3 candidate mechanisms from existing trace token sinks → screen
  each on ≥3 control-solvable development tasks × 4 arms → freeze the best →
  confirmation → analysis → report. Details: workspace `review.md` Part C.
- At most 3 candidates. If two consecutive candidates show no improvement,
  or no candidate meets the target in screening, stop and report to the user.
- No harness onboarding or mock-infrastructure work. No candidate screens
  on a single task. No model calls until Step 2 is complete and committed and
  the Step 3 calibration contract is committed. The user's latest amendment
  authorized only the five unstarted primary tasks plus the conditional
  exposed-fixture fallback, never the five completed runs. Its commit dc768c3
  started a new four-hour window (03:18:43–07:18:43 +08 on 2026-10-07), latest
  start 05:18:43, with no extension or automatic task retries. All G1 model
  calls use direct 127.0.0.1:18001 without fallback. Admit only with valid
  metadata and 0 <= running requests < 8; waiting requests are allowed.
  Back off at most ten minutes, then pause and report. Record load at start,
  before every request and every 30 seconds. Flag any observation with running
  >= 6 or waiting > 0; retain all flagged runs without causal slowdown claims.
  Do not interfere with shared workloads or change shared servers.
  These historical windows stay closed. The user's 2026-10-08 standing
  authorization permits new bounded windows back to back, each committed
  before use, and the six proven zero-model startup cells with the permission
  fix. Saved-log-only classification permits one separate retry of SPARQL's
  infrastructure-interrupted run; regex's real output-limited attempt is not
  retried. Stop fallback at three verified solvable tasks. If the gate passes,
  commit/report Step 3 and proceed through Steps 4–9 without another approval
  stop. Ask only for a gate failing after actual Aider/Go tests, a needed goal
  rule change, shared-workload/server risks, or a final result. Claude may
  handle routine infrastructure fixes, windows and /goal resume on behalf of
  the user. See standing-authorization.md under framework/refinement/g1.
  No reservation or exclusive server use is assumed.
- Commit after each completed stage; keep `STATUS.md` to one page in plain
  readable text. Existing controls, frozen hashes, and the rules under
  "Controls and refinement loop" below still apply.

---

# Superseded goal (2026-10-04): economical skill refinement

Replaced by G1 above on 2026-10-05. Kept as history; its acceptance
criteria and launch instructions no longer apply.

Set 2026-10-04. Refine `skills/efficient-coding` so Ours beats No skill,
Karpathy, and Both in most harnesses across different benchmark families,
without sacrificing verified task completion.

## Pi takeover and user scope override

Codex session `nvlab-sol-pi-skills-eval` is paused and has handed coordination to Pi. Historical launch permissions are not replay authorization. Apply workspace `optmization.md`; use only local `Qwen3.8-27B-FP8` for evaluation, no more than3benchmark sources, and a small representative roughly10% subset. Do not restart/reconfigure the shared server or erase earlier attempts.

Current decision (2026-10-05): recovery-context terminal, 4 actors/63 POST/995896 complete provider tokens, all original grades0; no active worker or promotable candidate. Four recent separate coalesced descendants each have zero verified solves; no finite solve-economy ratios. `framework/refinement/pi-takeover/candidate-decision-review.md` and its hash-pinned JSON map the remaining requirements. Stop automatic resource-clause variants; next bounded work is original-versus-candidate cross-task instruction/adherence review of existing evidence. Canonical unchanged. Scope remains frozen9/89 and two benchmark sources (third deferred), local Qwen only; final acceptance below unchanged and unverified.

Historical takeover checkpoint (superseded by linked current decision, not replay authorization): one Codex harness. Scope-coverage passed the Go smoke (candidate1/1; other arms0/1; all costs complete) but failed Terminal (candidate0/1; controls1/1; two costs incomplete); both panels are independently audited. It is not promotion-ready. Patch-first completed4starts/57POST with all provider costs complete but failed quality versus No skill;rejected for promotion. The new incremental-coverage hypothesis changes one first-bullet prerequisite versus scope-coverage and adds frozen original Ours as a fifth historical control.56offline tests pass;5starts/80POST,600s actors,240s passive receipt grace,no retries/continuation. User-authorized8000 Nginx balances same-Qwen replicas18001/18002;both loads and per-request backend provenance are tracked. New quality/accounting remainpending;old direct-route controls are not pooled. This is two benchmark sources, not fresh confirmation. A nine-task metadata-stratified Terminal-Bench2.0 allocation is frozen from the89-task release; its environments/inference remain unstarted. Do not automatically launch older three-family or five-harness matrices.

Authoritative new state and evidence: [Pi takeover](framework/refinement/pi-takeover/README.md), [Go results](framework/refinement/pi-takeover/go-smoke-results.md), and [requirement audit](framework/refinement/pi-takeover/completion-requirements.md). The final performance criteria below are not established by a development smoke. No promotion, stable multi-harness win, billing savings, or goal completion is claimed.

## Acceptance criteria

- Primary harness panel: Pi, Codex, Copilot CLI, native Antigravity agy,
  and Cursor. Most means at least 3 of these 5, with the denominator frozen
  before confirmation; unavailable or unmeasured harnesses do not count as wins.
- In each winning harness, Ours must use at least 5% less complete reported
  tokens per verified solve than each of No skill, Karpathy, and Both, with
  no observed reduction in solved rate on the matched confirmation panel.
  Include failures, timeouts, retries, and any reducer calls in costs.
- Evaluate at least three benchmark families: repository repair (SWE-bench
  Verified), multilingual coding (Aider polyglot), and terminal workflows
  (Terminal-Bench 2). Official positive/negative grader controls and five-language polyglot
  adapters now pass. Integration for the sealed selected tasks remains
  unfinished; validate those environments before claiming confirmation results.
- Start with metadata-selected small samples, never select tasks by observed
  skill success. Keep development and sealed confirmation tasks separate;
  exclude the reused two-fixture pilot from confirmation. Freeze task IDs,
  revisions, difficulty strata, seeds, skill hashes, images and budgets.
- Run at least three independently scheduled rounds per confirmation cell;
  scheduling seeds are not model sampling seeds. Report paired task-cluster
  uncertainty and round variability. A small or inconclusive sample remains
  inconclusive; expand a frozen sample only under a predeclared rule.
- A demonstrated win requires the paired 95% interval for the cost ratio
  to lie below 1 against all three comparators in each winning harness.
  Report quality uncertainty as well; small samples do not prove equivalence.
- Report billing USD/solve and wall time/solve separately. Token-only wins
  are token-efficiency wins, not monetary savings. Unknowns remain TBD.
  Copilot/Cursor accounting must be resolved before claiming their cost wins.

## Controls and refinement loop

Freeze No skill and Karpathy. Freeze the existing Ours revision as an additional
historical control. For each candidate, Both means the same candidate plus frozen
Karpathy; it must not use an older, weaker Ours. Match backend/model/effort, task
prompt, limits, skill delivery, and image within a harness. Auto-routed models
must be stratified or treated as descriptive, not a controlled skill win.

Audit prior traces for needless reads, repeated validation, planning overhead,
and unnecessary code. Test a short conditional entrypoint, bounded evidence
retrieval, reuse of existing functionality, and stopping after sufficient
verification. Change one mechanism at a time; compare to the frozen original
on development tasks. Preserve required tests and exact evidence recall.

Keep portable skill instructions and optional harness extensions as separate
experimental arms. A prompt cannot implement native context replacement or
tool fusion. Count extension setup and auxiliary model costs. Do not install
new paid services or assume credentials exist; any missing route is TBD.

Promote only a frozen candidate that passes independent grading and the
confirmation criteria. Do not tune on confirmation results or announce a win
from cherry-picked tasks, model switches, reduced testing, or missing usage.
Record unsuccessful candidates and retain Docker workspaces and transcripts.

## References and hypotheses

- [NVlabs/SoL-Pi](https://github.com/NVlabs/SoL-Pi): investigate bounded,
  recoverable observations and evidence-preserving reduction. Native action
  fusion and compaction require separately measured harness integration.
- [Ponytail](https://github.com/dietrichgebert/ponytail): test reuse and platform
  primitives before custom code; retain validation and correctness. Its published
  results are external evidence, not performance of this skill.
- Jev exact intended project: TBD. A provisional relevant implementation is
  [lazniak/jevskill](https://github.com/lazniak/jevskill). Investigate selective,
  reversible reduction and routing only when measured savings exceed helper
  overhead. Its reported savings must be independently verified here.

## Starting evidence and next milestone

The completed native pilot contains 40 real attempts on two reused synthetic
fixtures. Ours did not beat No skill on reported tokens in Pi, Codex or agy;
Copilot/Cursor tokens and all actual billing remain TBD. See
[trial results](framework/trials/README.md).

First screen completed: ten public Go attempts in Pi/Codex, all graded passing.
The lean candidate fails the baseline token target in both. A Codex login-shell
PATH issue changes verification behavior; future images now pass six login-shell
probes. Five-language starter/reference sanity passes ten checks. The twelve-task
sealed allocation and predefined extension are frozen under framework/refinement.

Current milestone: complete the matched development screen of the frozen
independent-reads candidate on three reused families and four arms. Both local
Qwen Codex and Pi transports now pass a tiny independently graded repair with
reconciled provider usage. Codex's repaired development cohort stopped after
four Terminal attempts: all four arms failed; the next scheduler idle grace
expired, leaving eight Go/SWE cells unrun. Cleanup was independently verified.
The common failure review found incomplete repairs and cutoffs, with no
demonstrated delivery or grader defect. The unchanged Pi comparison stopped after
one actor at its budget cutoff, with incomplete usage and frozen ungraded quality;
eleven cells were unrun. Cleanup passed. Prospective successor protocols use the
same longer budget for every arm and grade saved work after expected cutoffs.
The Pi scope-coverage successor is running twelve fixed reused cells (seed 131,
600 seconds and sixteen provider requests per actor); Codex is queued behind it.
These use a separate prospective protocol; the earlier results remain unchanged.
Preserve the earlier partial cohort and zero-start Pi stage separately. These
development tasks cannot establish fresh wins, and the candidate has not qualified.
The scope-coverage candidate tests whether conditional coverage of exhaustive
requests prevents unsupported
exclusions while retaining focused reads for local changes.

The six development grading controls pass. All eight intended selected SWE
controls now pass across four tasks, with fourteen actual attempts retained.
Requests uses a documented isolated HTTP/HTTPS fixture and public CA adaptation;
this is not the public leaderboard protocol. Selected Terminal and polyglot
controls also pass. Fresh confirmation remains sealed and unexecuted.

References are pinned in `framework/refinement/references.json`; Jev's intended
identity remains TBD. Evaluate one mechanism at a time, preserving unfavorable
results. Candidate performance, most-harness superiority, and billing remain TBD.
Native Copilot documents a local-provider route without account authentication.
Original version preflight failed package extraction under128MiB scratch; later preserved version and native fake400 routing stages passed using separately scoped512MiB executable scratch. This does not change scored actor resources. One fake providerPOST with zero inference and empty native usage proves routing only, not Qwen stream/tool compatibility or complete accounting. No real Copilot model calls have run; completed startup/fake400 probes must not be repeated. A successful synthetic stream/tool/accounting gate remains unexecuted and requires separate authorization. See framework/refinement/pi-takeover/primary-harness-evidence-map.md for actual evidence and coverage limits.
Native agy and Cursor local-provider and full accounting support remain TBD.

The shipped skill is unchanged. Every execution stage has numeric start, request,
time and resource caps; fresh confirmation starts only after final candidate freeze.

---

The following records the previous goal and historical campaign context.

# Current evaluation status

The requested parallel native-harness pilot is complete: 40 model attempts across
Pi, Codex, Copilot, Antigravity agy, and Cursor Auto, comparing no skill, Karpathy,
ours, and both on two reused synthetic fixtures. Independent regrading found
39/40 passes. See `framework/trials/README.md` for separate quality, reported-token,
and latency tables, actual backends, and limitations. Ours did not beat no skill
on reported token efficiency in the three harnesses with usable token totals.
Billing, Cursor backend, and Copilot/Cursor comparable tokens remain TBD.

The broader goal remains an economical, stable skill with verified resolution
quality. Demonstrating that requires fresh public benchmark grader integration,
controlled model/effort comparisons and repeated trials. No superiority is claimed
and the shipped skill is unchanged. The earlier campaign specification follows
as historical context; its shared Qwen server constraints do not describe this
native-harness pilot.

# Goal

Measure whether the **nvlab-sol-pi-skills** bundle (`.claude/skills/efficient-coding`) lowers the
whole-task token cost of Claude Code **without lowering verified resolution quality**, alone and combined
with **andrej-karpathy-skills** (`karpathy-guidelines`), and write the results to `report.md` in this folder.

Claude Code runs inside Docker against a local model served on the host:
`Qwen3.8-27B-FP8 --host 127.0.0.1 --port 8000`.

**Success** = `report.md` exists with one row per benchmark and one column group per arm (4 arms),
giving verified resolution rate, total tokens, and tokens per verified solved task, averaged over
2–3 rounds with a fixed seed, plus paired differences and uncertainty. The bundle "wins" only if it cuts
cost per verified solved task while its resolution rate is not significantly lower than the arm without it.

## Arms

All four arms differ only in which skills are installed in the workspace.

| # | Arm | Skills in `<workspace>/.claude/skills/` | Purpose |
|---|---|---|---|
| 1 | `sol-pi` | `efficient-coding/` (unzipped from `.claude/skills/efficient-coding.zip`, frozen hash) | System under test |
| 2 | `baseline` | none | Reference for 1 |
| 3 | `karpathy` | `karpathy-guidelines/` (from the `andrej-karpathy-skills@karpathy-skills` plugin, frozen hash) | Competing skill |
| 4 | `karpathy+sol-pi` | both of the above | Is the bundle additive to karpathy? Reference: 3 |

Key comparisons: 1 vs 2 (does the bundle help?), 4 vs 3 (does it help on top of karpathy?),
1 vs 3 (bundle vs karpathy).

Held identical across arms: model, server flags, Claude Code version (`2.1.285`), `--max-turns`,
task prompt, repository snapshot, container image, time limit, and grading tests.

**Isolation:** each run uses a fresh container with a fresh `HOME`, so the host's
`~/.claude/CLAUDE.md`, plugins, and memory do not leak in (the host CLAUDE.md itself enforces
karpathy-guidelines and would contaminate arms A and B).

## Model server

The server is already running on the host (container `ykw-qwen38-dflash2-tp2`, sglang, host network)
and supports the Anthropic `/v1/messages` API that Claude Code needs:

```bash
curl -s http://127.0.0.1:8000/v1/models   # -> Qwen3.8-27B-FP8, max_model_len 262144
```

It runs with `--max-running-requests 1`, so agent runs are **sequential**. Do not restart or reconfigure
it; it is shared. Record its full launch args in the results for reproducibility.

## Agent container

One container per (task, arm, seed), using `--network host` so `127.0.0.1:8000` is reachable:

```bash
docker run --rm --network host \
  -e ANTHROPIC_BASE_URL=http://127.0.0.1:8000 \
  -e ANTHROPIC_API_KEY=dummy \
  -e ANTHROPIC_MODEL=Qwen3.8-27B-FP8 \
  -e ANTHROPIC_SMALL_FAST_MODEL=Qwen3.8-27B-FP8 \
  -e CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  -e HOME=/tmp/home \
  -v <workspace>:/testbed -w /testbed \
  <swebench-instance-image-with-claude-code> \
  claude -p "$(cat task_prompt.txt)" \
    --allow-dangerously-skip-permissions --dangerously-skip-permissions \
    --output-format stream-json --verbose --max-turns <N>
```

`-p` (non-interactive) and `stream-json` are added to the requested command so runs are batchable and
per-request token usage is logged. The agent never sees the grading tests.

## Benchmarks (rows of the report)

Scoped subsets per `docs/benchmark.md`; task lists are sampled once with **seed 42** and frozen in
`eval/tasks/`.

| Row | Subset | Grader |
|---|---|---|
| SWE-bench Verified | 1/10 target (50 of 500), stratified by difficulty; cut to what the pilot throughput allows and say so | Official `swebench` harness on the final `git diff` |
| Stress suite | 5 single-agent cases (below) | Hidden test script per case |
| Terminal-Bench 4.0 | optional, only if time remains | Its own harness |

Stress cases: small straightforward fix; large log with the decisive error in the middle; fabricated
quote / modified archive; successful edit followed by failing tests; interrupted task with a
continuation note. (Multi-agent handoff is out of scope: single agent only.)

**Rounds:** every (task, arm) runs **2–3 rounds** (r1–r3). The task sample and arm order are fixed by
seed 42; Claude Code exposes no sampling seed, so rounds measure run-to-run variance.

**Pilot decision (2026-10-01):** one SWE-bench run took ~14 min and ~1.07M tokens on the
single-request server, so 49 tasks × 4 arms × 3 rounds (~140 h) does not fit. Scored scope:
SWE-bench Verified **12 tasks** (seeded stratified: 5 `<15 min`, 6 `15 min–1 h`, 1 `1–4 h`; list in
`eval/tasks/swebench_verified_12.txt`) × **2 rounds**, stress suite 5 cases × **3 rounds**.

**Run settings found during smoke tests:** `--effort medium` (the server's chat template rejects Claude
Code's default `high`), `--max-turns 60`, 30 min wall limit. The 27B model did not call the Skill tool on
its own, so every arm's prompt ends with the same sentence asking it to load any skills installed in
`.claude/skills` (a no-op for the baseline); skill invocation is still logged per run.

## Metrics

Per run, from the stream-json log and the grader:

- **Verified resolved** (SWE-bench harness, run outside the agent container on the final `git diff`).
- Input tokens, output tokens, model requests, turns, wall time.
- **Tokens per verified solved task** = all tokens across all runs of an arm ÷ solved tasks
  (failed runs count in the numerator).
- False completion claims (agent says done, grader fails) and evidence-recovery failures (stress suite).
- Whether the skill was actually invoked (Skill tool call present in the log).

The local server reports only `input_tokens` / `output_tokens` (no cache fields), so cost is reported
in tokens. For `scripts/cost_audit.py`, normalize each request with cache fields = 0 and unit rates; any
dollar figure must state the reference price table it assumes.

## Protocol

1. Smoke test: 1 task × 4 arms × 1 round → verify: logs contain usage, skills load, grader runs, no host config leaks.
2. Pilot: measure minutes per run → verify: choose the SWE-bench subset size that fits, record the choice.
3. Main: all benchmark rows × 4 arms × 2–3 rounds, arm order shuffled per task with seed 42.
4. Analysis: paired per-task differences (1−2, 4−3, 1−3) with bootstrap 95% CIs over tasks×rounds.
5. Report: `report.md` in this folder — rows = benchmarks, columns = arms — with frozen hashes, server args, and limitations.

## Non-goals

- No change to the model, server, or skill contents during the scored runs.
- No claim of dollar savings from token counts alone, and no claim of the SoL-Pi paper's savings.
- Existing helper tests (`evidence.py`, `cost_audit.py`) prove utility correctness, not savings.

## Pruned follow-up campaign (2026-10-02)

The user authorized selecting a minimal representative subset, delegated execution,
repeated rounds, and evidence-supported skill improvement. See
`eval/pruned/plan.v1.json` and `eval/pruned/preregistration.txt`. Order seeds
42/73/101 randomize schedules; they do not control backend model sampling.
Development precedes candidate freeze and held-out evaluation. Report economy,
verified correctness, activation reliability, and variability separately. A skill
win is an experimental outcome to test, never a reason to exclude unfavorable tasks.

## Final status

Completed: all147 pruned attempts and independent final audit, with no provenance or grading infrastructure errors. Final results and limitations are in `report.md`; the requirement-by-requirement evidence is in `eval/pruned/audit/completion-requirements.md`.

The desired stable majority win was not established. Latest held-out diagnostics:14/15 versus baseline13/15, at18.87% higher tokens per solve. Repository scores: baseline6/8, latest7/8, Karpathy8/8, combined4/8. Eight incomplete repository usage records prevent supported savings claims; upstream repair retrieval limits unaided attribution. The development candidate was rejected and canonical latest retained. No further outcome-selected benchmark search was applied.

## Completed random-small follow-up (2026-10-03)

All16 frozen attempts completed and independent-final16.json passed with errors[]. Ours4/4 at1,063,019tokens/solve; both4/4 at1,476,167; baseline3/4 at≥2,009,397; Karpathy3/4 at≥1,795,306. Ours/both0timeouts; baseline/K1each with incomplete costs. Public repair/source/test retrieval qualifies attribution. Two conditionally sampled easy tasks limit generalization; previous147 results remain separate. Compact README table and detailed report/evidence published. Skill/backends unchanged, queue terminal/model lockfree.

## Newly observed confirmation gate

Native agy Go No skill fetched public official tests during development. Mount isolation alone is insufficient: before confirmation, enforce and audit uniform provider-only network access, preventing test/solution retrieval across all compared arms. Retain exposed development grades and costs with explicit caveats; do not use them as clean held-out evidence. This does not alter frozen acceptance thresholds or sealed task selection.
