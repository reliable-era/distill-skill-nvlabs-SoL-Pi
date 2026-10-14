# Evaluation and development history

This document records the evidence and development process for **`efficient-coding`**, the single skill described in the [README](../README.md).

**Snapshot · 2026-10-12.** The current entrypoint is 2,584 bytes. Experimental snapshots remain in the evaluation archive; the installed skill is [skills/efficient-coding/SKILL.md](../skills/efficient-coding/SKILL.md).

This repository's distinctive research question is whether instructions alone can reduce tokens per verified solve while preserving success. The comparisons below keep the current skill's evidence separate from exploratory changes.

## What the comparison conditions mean

| Condition | Instructions available during one agent task |
|---|---|
| No skill | No skill instructions |
| Current skill | `efficient-coding` alone |
| Karpathy | `karpathy-guidelines` alone |
| Both | `efficient-coding` and `karpathy-guidelines`, loaded as separate resources |

In the Claude Code evaluation, the [runner](../tests/eval/run_swe.py) installs the directories selected by the [frozen plan](../tests/eval/pruned/plan.v4-real-swe.json), then starts **one agent process for one task**. The identical prompt asks it to load every installed skill with the Skill tool. Skill-loading calls may occur in sequence; this does not create a two-stage task-solving pipeline.

The current skill independently distills SoL-Pi ideas. It is not a fused SoL-Pi–Karpathy implementation. “Both” tests adding Karpathy's instructions alongside it, rather than a deliberately engineered merger. In the later portable framework, frozen skill texts are prepended and resources are mounted; see the [framework contract](../tests/framework/README.md).

### What the standalone-versus-stacked results support

On synthetic diagnostics, the current skill solved 23/25 attempts versus 22/25 for Both, using 253k versus 288k tokens per verified solve: **about 12.2% fewer**, calculated from the rounded published values. On SWE-bench, it solved 11/12 versus 8/12; incomplete cost records do not establish an exact relative token saving.

These observations give a practical reason to try the focused skill before adding another instruction set. They do not show that fewer instructions, reduced redundancy, or instruction conflict caused the difference.

A claim about *integrated design versus sequential execution* would require an experiment with those implementations. A claim about *instruction stacking overhead* would require a controlled ablation that separates instruction length, content, and loading method. The present comparison varies the available guidelines as a whole.

## Results

**Primary metric:** tokens per verified solve = total provider tokens across all attempts, including failures, divided by verified solves.

All tables report **solved attempts**, not unique tasks. `k` means thousand tokens; `M` means million. `≥` marks a lower bound because one run's cost was not fully recorded. Different agents, models, and task sets are reported separately.

### Shipped skill: mixed results

Claude Code 2.1.286 · Qwen3.8-27B-FP8.

| Condition | Synthetic solved | Synthetic tokens / solve | SWE-bench solved | SWE-bench tokens / solve |
|---|---:|---:|---:|---:|
| No skill | 21/25 | **234k** | 9/12 | ≥1.62M |
| **Shipped skill** | **23/25** | 253k | **11/12** | **≥1.42M** |
| Karpathy | 19/25 | 296k | **11/12** | ≥1.45M |
| Both | 22/25 | 288k | 8/12 | ≥1.94M |

The skill solved more attempts than no skill on both benchmarks, but used more tokens per solve on synthetic diagnostics. SWE-bench costs are lower bounds; exact savings cannot be claimed.

Synthetic: 10 fixtures, 25 attempts per condition, including development data; no timeouts. SWE-bench: 6 issues × 2 rounds; 3, 2, 2, and 3 timeouts in table order.

[Full report](../tests/report.md) · [Comparison chart](../assets/benchmark-numbers.svg)

### Candidate 2: not promoted

Candidate 2 adds one rule to the shipped skill: make shell failures visible and confirm a write or test really happened before reasoning from it. [Frozen candidate](../tests/framework/refinement/g2/frozen/candidate/SKILL.md).

**G2 completed:** Codex 0.160.0 · Qwen3.8-27B-FP8 · 9 sealed Aider tasks × 3 rounds.

| Condition | Solved attempts | Tokens / solve |
|---|---:|---:|
| No skill | 7/27 | 3.38M |
| **Candidate 2** | **13/27** | **1.27M** |
| Karpathy | 10/27 | ≥1.98M |
| Both | 11/27 | 2.04M |

Candidate 2 used 62.5% fewer tokens per solve than no skill; the cost-ratio interval was 0.11–0.85. Its advantage over Karpathy was **not established**: the conservative upper-bound surrogate interval reached 1.13. The full preregistered pass rule was not met, so the candidate was not shipped. No G2 run timed out.

**G3 completed, negative:** Codex · Qwen/Qwen3.8-27B, full precision · 196 Aider tasks × 4 conditions. The preregistered futility rule stopped G3 after round 1 (784 runs), so rounds 2–3 were not run.

| Condition | Solved / 196 | Tokens / solve |
|---|---:|---:|
| No skill | 56 | **456k** |
| Candidate 2 | 52 | 526k |
| Karpathy | **57** | 568k |
| Both | 55 | 521k |

On the larger task set, candidate 2 solved fewer tasks than no skill and used 15.5% more tokens per solve. The four conditions are statistically indistinguishable: every cost-ratio interval includes 1. The large G2 saving did not replicate. G3 used a different model variant from G2, so the two are not pooled. No G3 run timed out, hit the 60-request cap or was retried.

[G2 report](../tests/framework/refinement/g2/report.md) · [G3 report](../tests/framework/refinement/g3/report.md)

<details>
<summary>G2 and G3 statistical comparisons</summary>

Cost ratio = candidate or combined condition ÷ comparator. Below 1 means fewer tokens per solve.

| Comparison | G2 cost ratio | G2 95% interval | Verdict |
|---|---:|---|---|
| Candidate 2 vs no skill | 0.375 | 0.11–0.85 | Pass |
| Candidate 2 vs Karpathy | ≤0.64 | Surrogate: 0.31–1.13 | Not established |
| Both vs Karpathy | ≤1.03 | Surrogate: 0.35–2.95 | Not established |

Comparisons against Karpathy use upper-bound surrogates because one run's recorded cost is incomplete. Their intervals describe those conservative surrogates, not exact intervals for the unknown true cost ratios. Failure to pass a surrogate gate does not prove the true effect is absent. The intervals use a paired task-cluster bootstrap.

Three tasks drove the G2 lead: alphametics, transpose, and accumulate. Resampling without them can push the ratio above 1.

G3 has complete cost records, so its intervals are exact paired task-cluster bootstrap intervals (20,000 draws).

| Comparison | G3 cost ratio | G3 95% interval | Solves | Verdict |
|---|---:|---|---|---|
| Candidate 2 vs no skill | 1.155 | 0.89–1.49 | 52 vs 56 | Fail |
| Candidate 2 vs Karpathy | 0.927 | 0.73–1.19 | 52 vs 57 | Fail |
| Both vs Karpathy | 0.918 | 0.72–1.17 | 55 vs 57 | Fail |
| Candidate 2 vs Both (informational) | 1.010 | 0.78–1.30 | 52 vs 55 | — |

</details>

### G4: open measurements filled (descriptive)

G4 measured the remaining TBD cells; it has no pass/fail gate. Qwen3.8-27B (FP8 and full precision treated as one model). [G4 report](../tests/framework/refinement/g4-A/report.md).

**NVlabs SoL-Pi** (Pi 0.85.1, unmodified extension, all four mechanisms; same tasks, prompts, caps and graders as the Claude Code table above):

| Condition | Synthetic solved | Synthetic tokens / solve | SWE-bench solved | SWE-bench tokens / solve |
|---|---:|---:|---:|---:|
| NVlabs SoL-Pi | 21/25 | ≥39k | 5/12 | ≥621k |
| NVlabs SoL-Pi + Karpathy | 19/25 | ≥56k | 5/12 | ≥473k |

Token counts are not comparable across harnesses. 9 of 74 runs hit the 1800 s cap, largely while queued at a shared model server; the evidence reducer never fired on these tasks.

**Terminal-Bench 2.0 and a larger SWE-bench Verified sample** (Codex 0.160.0; 60 requests / 120 min / 16K output):

| Condition | Terminal-Bench solved | Terminal-Bench tokens / solve | SWE-bench solved | SWE-bench tokens / solve |
|---|---:|---:|---:|---:|
| No skill | 11/27 | ≥2.40M | **14/18** | ≥918k |
| Karpathy | 13/27 | **≥1.75M** | 9/18 | **≥721k** |
| **Shipped skill** | 12/27 | ≥2.34M | 13/18 | ≥903k |
| Both | **14/27** | ≥2.16M | 13/18 | ≥1.22M |

Terminal-Bench: 9 sealed tasks × 3 rounds. SWE-bench: 30 fresh issues sampled, 12 excluded by failed gold/no-op grader controls, 18 run once. Every paired cost-ratio interval includes 1, so no condition is shown to be cheaper per solve. Runs killed by gateway errors were rerun; 21 needed a second, non-preregistered rerun after a client timeout, and the report gives both views.

### Limits of the evidence

- Completed evaluations use small task samples. Repeated attempts on a task are not independent; intervals resample whole tasks.
- Evidence covers one model family and two agents. Broader transfer remains unmeasured; the [native-agent pilot](../tests/framework/trials/README.md) is exploratory.
- Public SWE-bench fixes may affect attribution. Incomplete cost records limit savings claims.
- G3 stopped after round 1 under its futility rule. Terminal-Bench covers 9 tasks only.
- A full SWE-bench Verified run (500 issues × 4 conditions, Codex) started on 2026-10-14 (G5).

## Evaluation

### Benchmarks

| Benchmark | Sample used here | Verification | Status |
|---|---|---|---|
| Synthetic diagnostics | 10 fixtures: 5 development + 5 held-out | Hidden tests pass | Complete |
| [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) | 6 of 500 issues; G4: 18 more | Official grader resolves the issue | Complete; full 500 running (G5) |
| [Aider polyglot](https://github.com/Aider-AI/polyglot-benchmark) @ `7e0611e` | G2: 9 tasks; G3: 196 of 225 | Exercise tests pass | G2 complete; G3 complete (stopped after round 1) |
| Terminal-Bench 2.0 | 9 sealed tasks, from 78 eligible | Task verifier passes | G4 complete |

Grading runs in isolated Docker containers. Before G2 and G3 model calls, each task's grader must accept the reference solution and reject an unchanged submission. G3 excluded 15 of 211 eligible tasks that failed this check.

The [evaluation framework](../tests/framework/README.md) supports nine agent CLIs and six benchmark sources.

### Acceptance rule

A candidate must use **at least 5% fewer tokens per solve than both no skill and Karpathy**, with no fewer solves. The combined condition must also improve on Karpathy by at least 5%. Every required comparison must preserve the solve count, and its paired task-cluster bootstrap 95% interval must lie below 1.

Failures, timeouts, and cap hits stay in the totals. Candidates are frozen before confirmation; confirmation tasks are sealed and excluded from development. Infrastructure-only failures may be rerun once under the same rule for all conditions. Early stopping is for futility only.

Detailed contracts and history: [goal](../tests/goal.md) · [G1 screening report](../tests/framework/refinement/g1/report.md) · [19 rejected candidates](../tests/archive/rejected-candidates/INDEX.md) · [original campaign](../tests/eval/). Historical versions and current results are not pooled.


## Reproducing and inspecting the evidence

Use the [framework documentation](../tests/framework/README.md) for runner contracts, frozen inputs, benchmark adapters, and independent grading. [Runtime instructions](../tests/framework/runtime/README.md) cover agent setup and login.

The framework includes nine agent CLIs and six benchmark sources; integration and measured performance vary by benchmark. See the relevant campaign report for what actually ran.

Runtime dependencies and agent binaries are excluded; manifests retain their hashes. Historical paths identify the original execution workspace.

## Sources

- [SoL-Pi paper and implementation digest](../skills/efficient-coding/references/sol-pi-evidence.md)
- [SoL-Pi implementation reference](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19)
- [Karpathy baseline used in confirmation](../tests/framework/refinement/g2/frozen/karpathy/SKILL.md)
