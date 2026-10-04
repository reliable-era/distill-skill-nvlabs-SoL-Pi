# Active goal: economical skill refinement

Set 2026-10-04. Refine `skills/efficient-coding` so Ours beats No skill,
Karpathy, and Both in most harnesses across different benchmark families,
without sacrificing verified task completion. The goal is active, not achieved.

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
reconciled provider usage. Codex's repaired development cohort is running; Pi
is queued behind it on the shared server. Preserve the earlier partial cohort
and zero-start Pi stage separately. These development tasks cannot establish
fresh wins, and the current candidate has already failed its Terminal task.

The six development grading controls pass. All eight intended selected SWE
controls now pass across four tasks, with fourteen actual attempts retained.
Requests uses a documented isolated HTTP/HTTPS fixture and public CA adaptation;
this is not the public leaderboard protocol. Selected Terminal and polyglot
controls also pass. Fresh confirmation remains sealed and unexecuted.

References are pinned in `framework/refinement/references.json`; Jev's intended
identity remains TBD. Evaluate one mechanism at a time, preserving unfavorable
results. Candidate performance, most-harness superiority, and billing remain TBD.
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
