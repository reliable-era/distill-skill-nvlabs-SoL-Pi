# Distilled SoL-Pi

**Read less. Reuse evidence. Verify the fix.**

`efficient-coding` is a portable skill for coding agents. It adapts ideas from [NVlabs' SoL-Pi](https://github.com/NVlabs/SoL-Pi) into Markdown instructions for focused reads, reusable evidence, and verified fixes. The goal is to reduce tokens per verified solve without reducing the solve rate.

**Status · 2026-10-12:** The shipped skill is unchanged. Candidate 2 improved on the no-skill baseline in a small Aider evaluation, but did not pass the full comparison against Karpathy's guidelines. A larger, 196-task evaluation is running. **A general token-saving benefit has not yet been established.**

[Quick start](#quick-start) · [How it works](#how-it-works) · [Results](#results) · [Evaluation](#evaluation) · [Installation](#installation) · [Repository map](#repository-map)

## Quick start

Inside Claude Code:

```text
/plugin marketplace add reliable-era/distill-skill-nvlabs-SoL-Pi
/plugin install distill-sol-pi@sol-pi-skills
/distill-sol-pi:efficient-coding Fix the failing parser test and verify the change.
```

For a log-heavy task:

```text
Use efficient-coding to investigate logs/test-run.log, check the failure
against the source, fix it, and run the affected tests.
```

For Codex, Cursor, or manual setup, see [Installation](#installation). The installed version is [skills/efficient-coding/SKILL.md](skills/efficient-coding/SKILL.md); experimental candidates are evaluated separately.

## How it works

Long sessions repeatedly send earlier files, logs, and tool output back to the model. The skill encourages agents to reuse evidence while completing the task.

| Practice | Instruction |
|---|---|
| Focused reads | Search for the relevant symbol or diagnostic, read nearby source, and expand when needed. |
| Fewer tool turns | Batch independent reads; combine an edit with its predetermined check when the tool supports sequential execution. |
| Reusable evidence | Keep long output in an artifact, inspect decisive lines, and verify quotations against the source. |
| Reliable continuation | Check saved notes against current files and verification state before resuming work. |
| Verified completion | Preserve the true command exit status, correct rejected tool arguments, and run the affected checks. |

The skill guides tool use. Runtime features such as fused tools, replacement of past messages, and native compaction still require harness support. References and offline helpers load only when needed.

We compare four conditions: **no skill**, **Karpathy**, **our skill**, and **both skills loaded separately**.

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

[Full report](tests/report.md) · [Comparison chart](assets/benchmark-numbers.svg)

### Candidate 2: promising, but not promoted

Candidate 2 adds one rule to the shipped skill: make shell failures visible and confirm a write or test really happened before reasoning from it. [Frozen candidate](tests/framework/refinement/g2/frozen/candidate/SKILL.md).

**G2 completed:** Codex 0.160.0 · Qwen3.8-27B-FP8 · 9 sealed Aider tasks × 3 rounds.

| Condition | Solved attempts | Tokens / solve |
|---|---:|---:|
| No skill | 7/27 | 3.38M |
| **Candidate 2** | **13/27** | **1.27M** |
| Karpathy | 10/27 | ≥1.98M |
| Both | 11/27 | 2.04M |

Candidate 2 used 62.5% fewer tokens per solve than no skill; the cost-ratio interval was 0.11–0.85. Its advantage over Karpathy was **not established**: that interval reached 1.13. The full preregistered pass rule was not met, so the candidate was not shipped. No G2 run timed out.

**G3 running:** Codex · Qwen/Qwen3.8-27B, full precision · 196 Aider tasks × 4 conditions × 3 rounds. Results are **TBD** and will be reported separately from G2.

[G2 report](tests/framework/refinement/g2/report.md) · [G3 plans and audits](tests/framework/refinement/g3/)

<details>
<summary>G2 statistical comparisons and recorded G3 progress</summary>

Cost ratio = candidate or combined condition ÷ comparator. Below 1 means fewer tokens per solve.

| Comparison | G2 cost ratio | G2 95% interval | Verdict |
|---|---:|---|---|
| Candidate 2 vs no skill | 0.375 | 0.11–0.85 | Pass |
| Candidate 2 vs Karpathy | ≤0.64 | ≤0.31–1.13 | Not established |
| Both vs Karpathy | ≤1.03 | ≤0.35–2.95 | Not established |

Comparisons against Karpathy are upper bounds because its recorded cost is incomplete. The intervals use a paired task-cluster bootstrap.

Three tasks drove the G2 lead: alphametics, transpose, and accumulate. Resampling without them can push the ratio above 1.

Last recorded G3 progress: round 1 of 3 running; 169 of 784 round-1 runs audited at commit `5c6f69b`. See the G3 directory for subsequent audits.

</details>

### Limits of the evidence

- Completed evaluations use small task samples. Repeated attempts on a task are not independent; intervals resample whole tasks.
- Evidence covers one model family and two agents. Broader transfer remains unmeasured; the [native-agent pilot](tests/framework/trials/README.md) is exploratory.
- Public SWE-bench fixes may affect attribution. Incomplete cost records limit savings claims.
- G3 is still running. Terminal-Bench has not been run.

## Evaluation

### Benchmarks

| Benchmark | Sample used here | Verification | Status |
|---|---|---|---|
| Synthetic diagnostics | 10 fixtures: 5 development + 5 held-out | Hidden tests pass | Complete |
| [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) | 6 of 500 issues | Official grader resolves the issue | Complete; larger sample TBD |
| [Aider polyglot](https://github.com/Aider-AI/polyglot-benchmark) @ `7e0611e` | G2: 9 tasks; G3: 196 of 225 | Exercise tests pass | G2 complete; G3 running |
| Terminal-Bench 2.0 | 9 sealed tasks, from 78 eligible | Task verifier passes | Not run; G2 Aider stage did not pass |

Grading runs in isolated Docker containers. Before G2 and G3 model calls, each task's grader must accept the reference solution and reject an unchanged submission. G3 excluded 15 of 211 eligible tasks that failed this check.

The [evaluation framework](tests/framework/README.md) supports nine agent CLIs and six benchmark sources.

### Acceptance rule

A candidate must use **at least 5% fewer tokens per solve than both no skill and Karpathy**, with no fewer solves. The combined condition must also improve on Karpathy by at least 5%. Every required comparison must preserve the solve count, and its paired task-cluster bootstrap 95% interval must lie below 1.

Failures, timeouts, and cap hits stay in the totals. Candidates are frozen before confirmation; confirmation tasks are sealed and excluded from development. Infrastructure-only failures may be rerun once under the same rule for all conditions. Early stopping is for futility only.

Detailed contracts and history: [goal](tests/goal.md) · [G1 screening report](tests/framework/refinement/g1/report.md) · [19 rejected candidates](tests/archive/rejected-candidates/INDEX.md) · [original campaign](tests/eval/). Historical versions and current results are not pooled.

## Installation

### Claude Code marketplace

Use the [quick-start commands](#quick-start). The [marketplace and plugin manifests](.claude-plugin) are included. This installation route is tested in Docker and GitHub Actions.

### Skills CLI: Claude Code, Codex, or Cursor

These commands follow the [Skills CLI documentation](https://github.com/vercel-labs/skills). **These installation routes have not been validated in this repository.**

```bash
# Choose one client:
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent claude-code
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent codex
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent cursor
```

Add `--global` for a user-wide installation. In Codex, invoke the skill with `$efficient-coding`. Official marketplace listing is TBD.

### Manual project installation

```bash
gh repo clone reliable-era/distill-skill-nvlabs-SoL-Pi
cd distill-skill-nvlabs-SoL-Pi
TARGET_PROJECT=/absolute/path/to/your/project
mkdir -p "$TARGET_PROJECT/.claude/skills"
cp -R skills/efficient-coding "$TARGET_PROJECT/.claude/skills/"
```

Copy the whole directory, including references and helpers. Back up an existing installation before replacing it. A [ZIP distribution](.claude/skills/efficient-coding.zip) is also available.

### Validate an upgrade

From a checkout of this repository:

```bash
docker build -f tests/validation/Dockerfile -t sol-pi-validation .
docker run --rm --network none sol-pi-validation
```

The [validation workflow](.github/workflows/validate.yml) checks manifests, installs the plugin in a fresh non-root container, verifies installed resource bytes, and checks helper entrypoints. It makes no model calls. Performance changes require separate behavioral evaluation.

## Repository map

| Path | Contents |
|---|---|
| [skills/efficient-coding/](skills/efficient-coding/) | Shipped skill, references, and offline helpers |
| [tests/report.md](tests/report.md) | Shipped-skill evaluation report |
| [tests/eval/](tests/eval/) | Original campaign inputs, grades, and audits |
| [tests/framework/](tests/framework/) | Docker framework and benchmark adapters |
| [tests/framework/runtime/](tests/framework/runtime/README.md) | Runtime login instructions |
| [tests/framework/refinement/](tests/framework/refinement/) | G1–G3 plans, frozen candidates, analysis, audits, and reports |
| [tests/archive/rejected-candidates/](tests/archive/rejected-candidates/) | Rejected candidates and reasons |
| [tests/goal.md](tests/goal.md) | Preregistered goal contracts; G3 is active |

Runtime dependencies and agent binaries are excluded; manifests retain their hashes. Historical paths refer to the original execution workspace.

## Sources and license

This project independently distills SoL-Pi's ideas into instructions. No upstream code is copied.

- **Paper:** Liu et al., *SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness*, [arXiv 2609.20519v1](https://arxiv.org/pdf/2609.20519v1). The [evidence digest](skills/efficient-coding/references/sol-pi-evidence.md) maps mechanisms to source pages and explains what can transfer to instructions.
- **Implementation reference:** [NVlabs/SoL-Pi @ `1559b5c`](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19).
- **Comparison baseline:** [Karpathy guidelines](https://github.com/multica-ai/andrej-karpathy-skills), MIT; [frozen evaluation copy](tests/framework/refinement/g2/frozen/karpathy/SKILL.md). These guidelines are loaded as a separate comparison condition.

The paper's reported savings concern runtime mechanisms and are not results for this skill.

[License](LICENSE) · [Report an issue](https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi/issues/new/choose)
