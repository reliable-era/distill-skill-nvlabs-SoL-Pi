# G3 final result — negative at the mandatory round1 futility boundary

Contract: `68cff75`, Active G3 in `tests/goal.md`. **No savings acceptance,
no candidate promotion, no shipment or push.** G1/G2 remain closed, unchanged
and unpooled. This is the separate `Qwen/Qwen3.8-27B` direct9012 cohort.

## Disposition

All **784 round1 cells** completed:196 control-valid tasks × four frozen arms.
Candidate solved **52**, fewer than No skill **56** and Karpathy **57**.
Candidate/No-skill tokens per verified solve = **1.154659615**, not≤0.95.
Candidate/Karpathy =0.927076032 meets the point-cost threshold, but fails the
observed solve-count condition. The preregistered round1 futility rule therefore
requires a **negative stop**. Round2 was never started; rounds2–3 are
**unattempted/ineligible**, not omitted results or missing cells. The remaining
1,568 preregistered primary cells must not run. No early success is claimed.

`analysis/round1-boundary.json` verifies the complete actual roster, original
seeded admission order and cleanup. Original frozen `analyze.py` and the separate
Counter-weighted `independent_analysis.py` agree on all six point ratios,
integer5% tests and20,000 paired task-cluster bootstrap intervals.
This is a negative stopped experiment, **not a completed three-round confirmation
or proof that a skill is universally inferior**.

## Round1 and total scores (identical because of the mandatory stop)

Costs include every attempted provider request, including failed solutions and
output-cap responses. All totals are exact reported standard provider input+
output tokens; no costs are imputed and no conservative unknown-cost surrogate
is needed. This measures gross tokens, not dollar cost, GPU work or cached-token
pricing. Solves come from original accepted tests on captured final artifacts.

| Arm | Solves /196 | Failures | Requests | Provider tokens | Tokens / verified solve | Native7200s timeouts | Verified180s test deadlines |
|---|---:|---:|---:|---:|---:|---:|---:|
| No skill |56|140|1,605|25,521,055|455,733.13|0|0|
| Karpathy |57|139|1,765|32,353,709|567,608.93|0|1|
| Candidate2 |52|144|1,652|27,363,265|526,216.63|0|0|
| Both |55|141|1,638|28,663,548|521,155.42|0|1|
| **Total** |**220 /784**|**564**|**6,660**|**113,901,577**|—|**0**|**2**|

No60-request run cap was reached; no infrastructure or completed-model run was
retried. Of6,660 responses,6,546 terminate as `response.completed` and114 as
`response.incomplete` for `max_output_tokens`: none33, K24, candidate27, Both30.
All114 have exact captured standard usage and remain charged to their original
native attempts. The16384 output-token cap was forwarded on every request;
there are no omitted paid retries or output-cap costs.

## Ratios and paired95% intervals

Lower is cheaper. Round1 and total intervals coincide. Seed **2026101111**;
**20,000** task-cluster draws retain all matched arms (and all observed rounds)
for each sampled task; nearest-rank .025/.975 endpoints. Undefined draws would
remain+∞; there were **zero** in each of the six comparisons.

| Comparison | Exact cost/solve ratio | Paired95% interval | Point≤.95 | No fewer observed solves | Interval upper<1 |
|---|---:|---|---|---|---|
| Candidate / No skill |1.154660|[0.894915,1.487688]|No|No:52<56|No|
| Both / Karpathy |0.918159|[0.718953,1.165522]|Yes|No:55<57|No|
| Candidate / Karpathy |0.927076|[0.726491,1.189651]|Yes|No:52<57|No|
| Candidate / Both (informational) |1.009712|[0.784786,1.303668]|No|No:52<55|No|
| Karpathy / No skill (informational) |1.245485|[0.976169,1.579067]|No|Yes:57≥56|No|
| Both / No skill (informational) |1.143554|[0.892983,1.456436]|No|No:55<56|No|

The three required final-comparison rows are shown for the observed round;
**all-three-round acceptance is not attempted or established**. Candidate's
observed cost/solve is15.47% higher than none and7.29% lower than K. Neither a
point saving against K nor a negative experiment disposition is a proven savings
claim. Every listed interval includes1. Candidate/Both is informational only.

## Quality, runtime and uncertainty

Descriptive Wilson95% solve-rate intervals: none28.57% [22.71%,35.26%],
K29.08% [23.17%,35.79%], candidate26.53% [20.84%,33.12%],
Both28.06% [22.24%,34.73%]. These are not a population-quality equivalence or
non-inferiority test. The contract uses no-fewer **observed** solves. No round
variability can be estimated: rounds2–3 were correctly forbidden by futility.
Task resampling does not quantify missing rounds, deployment shifts or all
shared-service temporal correlation; this is one fixed eligible benchmark pool.

**Startup-regime confound retained:** the first36 cells had a local file-owner
fault that hindered edits. All36 original grades/costs remain:4 solves,
32 failures,322 requests,6,634,448 tokens. No model-reached cell was rescued,
rerun or excluded. A prospective byte-identical starter tar set UID/GID0; four
immutable-image offline probes verified existing-file edits and directory creation
without extra capabilities. The remaining748 cells used that repaired regime.
The combined preregistered result is a heterogeneous-runtime result; do not claim
a homogeneous-runtime or pure causal skill effect, or acceptance on a selected
repaired-only subset.

Original12 wave01 incomplete-cost flags remain in the raw results. The old parser
missed terminal `response.incomplete` usage that was physically captured. Named
exact-byte projections recover real totals, not estimated or fabricated usage.
Original parser/source bytes and its audit are preserved in `frozen-v1/` and the
wave01 records; `execution-repair.json` binds the committed repair hashes.

Two sum-of-multiples K/Both raw grades remain exit2/null after original180s
`TimeoutExpired`. Exact captured solutions again time out with unchanged tests,
image/resources and deadline; the original gold passes in1.82s. Captured loops
advance by a zero factor on an original test enabled by the official npm runner.
The explicitly marked derived outcomes are failed original tests, **not solves,
infrastructure model retries or a budget raise**. Replay adds zero model calls;
all original records, artifacts/log hashes and failure costs remain. Futility is
also decisive from candidate/none, whose original grades are complete without
these two projections.

Recorded native wall sums (not calendar times or a speedup claim): none57,381.10s,
K61,815.59s, candidate54,531.64s, Both59,347.82s. They cover admitted native
runtime before final grading. First provider POST15:40:23.953894UTC, last provider
end20:21:00.787042UTC on2026-10-11. Overlapping18-slot runs, preparations,
waiting-zero admission, grading and bounded-window gaps prevent interpreting
summed native times as elapsed experiment time.8,154 start/periodic load records,
plus per-request observations, are retained; no workload/server intervention
was made to equalize load.

## Eligibility, freeze and execution provenance

- Actual pinned source `7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f` enumerates225
  exercises. Exactly14 original development exclusions leave211. Gold/no-op
  original grader checks on all211 precede every model call. Three preparation
  mapping failures and three Jest count-parser failures were repaired before
  inference, preserving previous failed records and original test semantics.
  There are428 immutable control logs plus three original preparation failures.
-196 tasks pass controls;15 failed-control exclusions only: go counter(no executed
  tests), go ledger/markdown, java ledger/tree-building and JS ledger(no-op
  passes); java hangman/rest-api and rust gigasecond/grep(missing offline
  dependencies); rust alphametics/decimal/pig-latin/poker/robot-name(official gold
  does not compile against pinned support). Full reasons/log hashes are in
  `controls-audit.json`; no model outcome changed eligibility.
- `47ccf73` controls plan; `b587ceb` control setup/count repairs; `65e7e82` final
  controls audit; `93e58b7` isolated runtime; `5d9ca19` original preregistration;
  `7257c9d` fixed-prefix bounded-fragment clarification, all before inference.
  Seeds: round1 **2026101200**, round2 **2026101300**, round3 **2026101400**.
  Full2,352-cell queue remains immutable; independently reproduced, four arms
  adjacent per task with randomized order, no outcome-selected scheduling.
- Five bounded rolling18-slot windows: `88afe49`(36), `2461722`(72),
  `d5c6ea3`(288), `e983287`(288), `a21fb66`(100). Each committed before calls,
  four-hour end and two-hour latest start, prior unused allowance retired.
  Every actual admission and provider request fits its recorded window.
- No skill resources for none; frozen K for K, frozen candidate for candidate,
  both same trees for Both. Candidate SKILL SHA
  `39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`;
  K SHA `6e22cc54cb02a5e98ae42d06d9d7292db0c1b43894831b32879beb0166b2aea7`.
  Full trees, prompts, starters, graders and actual resources are reconstructed
  and hash-checked for every attempt, not inferred from an arm label.
- Codex-cli0.160.0, binary SHA
  `12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad`.
  Actor: network none,1CPU/2GB/pids128, user0, ALL caps dropped,
  no-new-privileges; only readonly skill/binary/relay/per-attempt socket mounts.
  No private grader/gold or host-network/Internet route is mounted into actors.
  Original grader replays use isolated immutable images and unchanged tests.
- Direct `127.0.0.1:9012`, `Qwen/Qwen3.8-27B`; correct `/v1/models` preflight
  and every window/round-start identity retained. Every receipt records the
  same model/backend/path. New admissions require a free slot and all load ranks
  waiting0. Initial `/load`404 and readonly OpenAPI metadata diagnostic remain;
  no diagnostic inference, alternate endpoint or external-system repair.

## Artifacts, cleanup and handoff

`audits/round1.json` reconstructs every actual original prompt, resource tree,
private grader, capture, payload, forwarded cap, response hash and all-attempt
cost. `audits/private-artifact-index.json` indexes784 original attempt artifacts,
6,660 private request/forwarded/SSE receipts and428 control logs. Raw native
traces, solutions, graders and controls remain in private `/tmp/solpi-g3-*`
roots indexed by the committed launches; **do not delete them**. Hash indices
are not a substitute for access to those private bytes. No raw answers/traces
were copied into the public-facing report.

All five schedulers, both control workers, the grade-only replay worker and
owned actor/grader/replay containers are absent. No owned custom networks were
created; socket files are retained artifacts, not live brokers. There are no
pending eligible retries. All inference allowances are retired by the negative
stop. Terminal-Bench remains sealed/unattempted.

Agent commits affect only G3 and `tests/STATUS.md`. The supervisor's independent
README-only commit `193494a` occurred during wave03; its exact metadata hash is
recorded in `external-readme-change.json`, without agent edit/restoration. README
is not any experimental input. G1/G2, shipped skill, archives and `tests/goal.md`
are unchanged; unrelated modified nginx.conf and its three backups remain
untouched. No push or shipment. The original shipped skill stays in place;
Claude may update README and report the final table to the user.

Closure evidence: `analysis/round1{,-boundary,-independent}.json`,
`audits/final-execution.json`, `inference-stop.json`, `requirements.md` and
`completion-audit.json`. Completion means audited negative experimental closure,
**not savings acceptance**.
