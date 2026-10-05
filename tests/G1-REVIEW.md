# Review of the Pi agent and a corrected path to the goal

Audited 2026-10-05 23:25 (+08). The agent is now paused by the user. This was a read-only audit: no files, processes or the shared Qwen server were changed.

- **Part A** is the audit of what went wrong.
- **Part B** is how to correct it.
- **Part C** is a step-by-step path to a reachable goal, with a check for each step.

---

# Part A — Audit

## Verdict

The agent was **not on a path to reach the final goal**. It is rigorous and honest: it claims no win, keeps every failure, and left the shipped skill unchanged (`skills/efficient-coding/SKILL.md` SHA `68ea78dc…`). However:

1. Two acceptance criteria cannot be met under the user's scope.
2. The intended confirmation panel has been used up as development data.
3. The per-run budget is so small that most tasks fail in every arm.
4. In its last hours it ran candidate screens with no signal, then drifted into offline Copilot mock infrastructure.

## Distance from the goal

The acceptance criteria are in `distill-skill-nvlabs-SoL-Pi/tests/goal.md`.

| Criterion | Current state | Reachable as scoped? |
|---|---|---|
| Wins in ≥3 of 5 harnesses | Only Codex is scored. Copilot has 0 real model calls. agy and Cursor have no proven local-Qwen route | **No** |
| 3 families (SWE-bench, Aider polyglot, Terminal-Bench 2) | Scope is frozen at 2 sources; the third is "deferred" | **No** |
| ≥5 % lower tokens/solve vs all 3 comparators, paired 95 % CI < 1 | No candidate has qualified | **Not with 9 tasks** (see B3) |
| Sealed confirmation, separate from development | The 9 sealed tasks were all used in development (see A1) | **No**: a new sample is needed |
| 3 confirmation rounds, frozen promoted candidate | None started; no candidate promoted | Only after the fixes above |

## Findings

**A1. The confirmation panel is contaminated (critical).** The frozen 10 % Terminal-Bench selection (`pi-takeover/terminal-10pct-selection.json`) has 9 tasks. All 9 were used in development screens: break-filter-js-from-html, build-cython-ext, build-pmars, financial-document-processor, make-doom-for-mips, overfull-hbox, regex-log, sparql-university, train-fasttext. Candidates were designed from those traces. The goal says *"Keep development and sealed confirmation tasks separate."* These 9 tasks can no longer serve as confirmation.

**A2. The budget creates a floor effect (high).** The development runs allow each run 600 s and **16 model requests**. The original Claude Code campaign needed about 44 requests per SWE-bench task. Under 16 requests, most arms fail. On train-fasttext, 5 panels produced 1 verified solve in total, and controls also scored 0 on html and cython. When every arm fails, a screen cannot tell a good candidate from a bad one. About 4 M tokens were spent on such screens.

**A3. It kept tuning one exposed task (high).** On 10-05, at least 7 one-clause variants were screened on train-fasttext. These were feasible-first, documented-baseline, scratch-capacity, recovery-context, measured-feasibility, byte-bounded and output-contract-preflight. Repeating this on one task overfits to that task and gives almost no information.

**A4. It contradicted its own decisions (high).**
- At 20:50 its review said to *"stop scored execution… require a new concrete hypothesis or explicitly approved revised experimental contract"*.
- At 21:05 it launched another fastText variant anyway.
- From 21:25 to 23:24 it built about 10 offline Copilot mock gates. This went against `candidate-decision-review.md` ("do not build generalized infrastructure") and `optmization.md` §3.

**A5. It did not escalate when blocked (medium).** It waits until both Qwen replicas are idle. That wait expired on unknown load, and the request for a reserved server window is buried in JSON. Seven other `pi` agents from other projects run on this host.

**A6. Its status files are no longer readable (medium).**
- `pi-takeover/` has 825 files, and `continuation-checkpoint.md` is 186 KB.
- Recent text runs words together without spaces (`Canonicalunchanged/candidateunstarted/…`).
- There are 49 uncommitted changes; the last commit was 10-04 16:57.

**A7. Strengths to keep.** No task substitution, no pooling of separate run groups, no retries chosen because of the result. Unknown costs are reported as unknown, never 0. Audits are hash-pinned and cleanup is verified. No false win has been claimed.

---

# Part B — Corrections

## B1. Make the goal consistent with the scope (user decision, required first)

The written goal and the later scope override contradict each other. Pick one target and record it in `tests/goal.md`.

| Option | Harnesses | Families | Effort (model time) | Recommendation |
|---|---|---|---|---|
| **G1, narrowed** | Codex (+ Pi if cheap) | Terminal-Bench 2 + one more (Aider/Go or SWE-bench) | ~30–60 h | **Recommended.** It is reachable and answers the real question |
| G2, full | ≥3 of 5 | 3 | ≥150 h, plus unknown harness routing work | Only if agy, Cursor and Copilot routes are funded |
| G3, stop | — | — | 0 | Report the current result as negative/inconclusive |

Historical evidence is weak: +6.5 % tokens on SWE-12, +18.9 % on held-out, and one favourable result on 2 easy tasks. G3 is therefore a legitimate outcome. The rest of this review assumes **G1**.

## B2. Throw away contaminated tasks and draw fresh, separate samples

- **Development pool:** the 9 tasks already used, plus the earlier Go fixtures. Candidates may be tuned on these freely.
- **Confirmation pool:** draw a **new** sample of 9 tasks from the 78 remaining eligible Terminal-Bench tasks. Use the same metadata-only selector (`select_subset.py`) with a new, recorded seed and the same difficulty quotas (1 easy, 5 medium, 3 hard). Seal it; no agent reads its traces until the candidate is frozen.
- Draw the second family's confirmation sample the same way.

## B3. Make the statistical target achievable

Here is an estimate from the existing SWE-12 data (sol-pi vs baseline, per-task log token ratio, mean of 2 rounds). The standard deviation between tasks is about **0.30**.

With n = 9 tasks, the standard error is about 0.10. For an 80 % chance that the 95 % CI excludes 1, the true reduction must be about **27 %** or more, and against *each* of the 3 comparators. Confirming a 5 % effect would need roughly 350 tasks.

Therefore choose one of the following and freeze it before confirmation:
- **(a)** Keep "CI < 1" but accept that only a large-effect mechanism (≥25 %) can pass. Screen candidates for that size of effect in development.
- **(b)** Make the decision rule: point estimate ≥5 % lower vs all 3 comparators, CI reported, and no observed solve-rate loss. State plainly that this is a screening-level, not confirmatory, win.
- **(c)** Enlarge the confirmation sample, e.g. 18–27 tasks, if compute allows.

## B4. Use a realistic budget, the same for every arm

Replace 600 s and 16 requests with a budget near what solving actually needs. A suggested starting point, taken from the original campaign, is **30 min and 60 turns/requests**, with the 16 K output cap kept. Calibrate it once on the development pool with No-skill only.

**Check:** at least half of the development tasks are solved by at least one control arm. Freeze the budget before any candidate is run.

## B5. Rules to stop the drift

- **One owner, one queue.** No harness onboarding or mock infrastructure until G1's matched panel is complete.
- **Candidate budget:** at most **3 candidates** in total. Each one is screened on **≥3 development tasks** that controls can solve, never on a single task.
- **When stuck:** if two consecutive candidates show no improvement, stop and report to the user. Do not invent a new clause.
- **Server time:** ask the user, in plain text, for a reserved window on the shared Qwen server. Do not loop on idle checks.
- **Housekeeping:** commit after each completed stage. Keep a ≤1-page `STATUS.md` (one row per stage: starts, solves, tokens, decision). The large checkpoint files are archive only.

---

# Part C — Path to the goal (G1)

Each step is written as `step → check`, with a rough model-time estimate. Runs are sequential on the shared server, at about 15 min per run.

| # | Step | Check (done when…) | Est. time |
|---|---|---|---|
| 0 | Commit current work; write a short `STATUS.md`; record the G1 goal and the B3 decision rule in `tests/goal.md` | `git status` is clean; goal states the harness, families, rule and budget | 1 h, no model use |
| 1 | Reserve a window on the shared Qwen server with its owner (or confirm the other agents use a different server) | Written window/time slots exist | — |
| 2 | Draw fresh sealed confirmation samples (B2) for Terminal-Bench and the second family; validate their environments with official positive/negative grader controls only | 9 + N tasks frozen with hashes; every gold control passes and every no-op control fails | ~3–5 h of grading, no model use |
| 3 | Calibrate the budget (B4) on the development pool, No-skill only, 1 round | ≥50 % of dev tasks solvable by a control; budget frozen | ~3 h |
| 4 | **Find a mechanism from evidence.** Take all existing traces on the development pool and rank the biggest token sinks: repeated reads, re-running tests, timeouts, turn-limit hits. The original data showed input/trajectory length, not output, drives cost, and timeouts are expensive. Write ≤3 candidate mechanisms, each tied to a measured sink | Each candidate names the sink, the trace evidence, and the expected token reduction (≥25 % if using B3a) | 2–4 h, no model use |
| 5 | Screen the candidates on ≥3 solvable dev tasks × 4 arms × 1 round (Both = candidate + Karpathy) | Pick the best candidate on tokens per solve with no solve loss; if none beats all 3 comparators by the target, **stop and report (G3)** | ~3 × 12 runs ≈ 9 h |
| 6 | Freeze the winner (hash, budget, images, schedule, retry policy, accounting rules) | Freeze file committed before any confirmation run | — |
| 7 | **Confirmation:** sealed tasks × 4 arms × 3 independently scheduled rounds, all families in G1 | All runs graded, costs complete or marked ≥, cleanup verified | 9 tasks: 108 runs ≈ 27 h per family |
| 8 | Analyse: paired task-cluster bootstrap of cost ratio vs each comparator, solve-rate difference, round variability; tokens and wall time per solve reported separately (no USD claim) | Decision rule from B3 applied exactly as frozen | 1 h |
| 9 | Report and decide: promote the skill only if the rule passes; otherwise keep the canonical skill and publish the negative result | `report.md` updated, independent audit passes, skill hash recorded | 1–2 h |

**Total for G1:** about 45–70 h of sequential model time, plus about 10 h of offline work.

**Optional G2 extension, only after step 9 passes on Codex:** repeat steps 7–9 on the Pi harness, which already has passing native-Qwen readiness evidence. Continue to a third harness only if a real local-Qwen route exists. Copilot needs real Qwen stream and accounting validation, not more mock gates.

## Instructions to give the agent when you resume it

> Stop all Copilot/mock infrastructure work. Follow `review.md` Part C from step 0. Do not run any model call until steps 0–3 are complete and committed. Use at most 3 candidates, each screened on ≥3 solvable development tasks. Never use the old 9 Terminal-Bench tasks for confirmation. If step 5 finds no candidate meeting the target, stop and report; do not invent new variants. Report to me in plain readable text at each completed step.

## Evidence index

All paths are relative to `distill-skill-nvlabs-SoL-Pi/tests/`.
- Goal and acceptance criteria: `goal.md`
- Frozen 9-task selection: `framework/refinement/pi-takeover/terminal-10pct-selection.json`
- Development results on the same tasks: `pi-takeover/{matched-html,matched-cython,matched-pmars,matched-financial,source-backed-doom,16k-tex,16k-regex,behavior-first-sparql,*-fasttext}-results.md`
- Stop decisions: `pi-takeover/candidate-decision-review.md`, `pi-takeover/cross-task-instruction-review.md`
- Current stage: `pi-takeover/current-decision-stage.json`
- Historical cost data used in B3: `../../report.md` (SWE-12 per-task table)
