# Distilled SoL-Pi

**Bring SoL-Pi's efficiency ideas to the coding agent you already use.**

`efficient-coding` is a lightweight skill for focused reads, long-log debugging, and verified repairs. It turns [NVlabs' SoL-Pi](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19) research into practical instructions that fit an existing coding workflow.

Use it when an agent keeps rereading files, drowning in test output, repeating failed tool calls, or losing track of work after an interruption.

[Quick start](#quick-start) · [Why use it](#why-use-it) · [Comparison](#how-it-compares) · [Results](#measured-results) · [Evaluation details](docs/evaluation.md)

## Why use it?

- **A small core with useful depth.** The entrypoint is just **2,584 bytes**. References and helpers load when needed, keeping ordinary fixes simple.
- **One workflow from source to verification.** Focus reads on relevant source, check diagnostic evidence, make the targeted edit, and run the affected checks. Batch independent searches and reconcile prior work before resuming.
- **Offline tools for trustworthy log handling.** Archive exact output, recall bounded pages, and check source hashes, recorded status, and exact quotations with the bundled Python helper.
- **Measured on full SWE-bench Verified.** Across 444 issues it solved 40.8% versus 32.9% with no skill, at about the same tokens per solve. Inspect comparisons against no skill and Karpathy, frozen inputs, independent grades, failure-inclusive costs, and the reasons earlier revisions were rejected.

The package combines [one skill](skills/efficient-coding/SKILL.md), [worked examples](skills/efficient-coding/references/worked-examples.md), and optional [evidence tools](skills/efficient-coding/references/execution.md). Install the skill to use the workflow; explore the evaluation framework when you want to assess it.

## How it compares

| Approach | Main strength | How you adopt it |
|---|---|---|
| **This repo: `efficient-coding`** | Focused context, reusable execution evidence, and verified completion | Load a portable skill in your existing agent; use offline helpers as needed |
| [NVlabs SoL-Pi](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19) | Runtime action fusion, observation archives, log reduction, and context compaction | Install and configure an extension for Pi |
| [Karpathy guidelines](tests/framework/refinement/g2/frozen/karpathy/SKILL.md) | Clear assumptions, simple code, surgical changes, and explicit success criteria | Load general coding guidelines |

The specialization here is **how an agent reads, reuses, and checks evidence during a coding task**. Its instructions work at the skill layer; fused tools and replacement of past context still require runtime support.

## Quick start

Inside Claude Code:

```text
/plugin marketplace add reliable-era/distill-skill-nvlabs-SoL-Pi
/plugin install distill-sol-pi@sol-pi-skills
/distill-sol-pi:efficient-coding Fix the failing parser test and verify the change.
```

For a task with a long test log:

```text
Use efficient-coding to investigate logs/test-run.log, locate the failure,
inspect the relevant source, fix it, and rerun the affected tests.
```

The Claude Code marketplace installation is tested in Docker and GitHub Actions. For other clients, see [Installation](#installation).

## Measured results

**On the full SWE-bench Verified benchmark, `efficient-coding` raised the solve rate from 32.9% to 40.8%** without increasing tokens per solve. No token saving has been established on any benchmark.

### Full SWE-bench Verified

All 444 SWE-bench Verified issues that pass the official gold/no-op grader controls (56 of 500 fail them), one run per issue and condition. Codex 0.160.0 · Qwen3.8-27B.

| Condition | Solved ↑ | Tokens / solve ↓ |
|---|---:|---:|
| No skill | 146/444 (32.9%) | ≥553k |
| Karpathy | 161/444 (36.3%) | **≥541k** |
| **Ours: `efficient-coding`** | **181/444 (40.8%)** | ≥555k |
| Ours + Karpathy | 161/444 (36.3%) | ≥606k |

Our skill solved **7.9 percentage points more issues than no skill** (paired 95% interval +2.9 to +12.8; exact McNemar p = 0.002) at about the same tokens per solve. Its lead over Karpathy (+4.5 points, interval −0.5 to +9.5) is not conclusive, and adding Karpathy to our skill did not help. No tokens-per-solve difference is established.

Scope: one model, one agent and one run per issue. About 5% of runs per condition have incomplete usage records, so costs are lower bounds. Results vary by repository; for example, our skill solved fewer scikit-learn issues than no skill (13 vs 19 of 31). [G5 report](tests/framework/refinement/g5/report.md)

### Terminal-Bench 2.0

Codex 0.160.0 · Qwen3.8-27B · 9 sealed tasks × 3 rounds.

| Condition | Solved ↑ | Tokens / solve ↓ |
|---|---:|---:|
| No skill | 11/27 | ≥2.40M |
| Karpathy | 13/27 | **≥1.75M** |
| **Ours: `efficient-coding`** | 12/27 | ≥2.34M |
| Ours + Karpathy | **14/27** | ≥2.16M |

This sample is too small to separate the conditions: every paired cost-ratio interval includes 1. [G4 report](tests/framework/refinement/g4-A/report.md)

### Earlier pilots: synthetic diagnostics and 6 SWE-bench issues

Compare `efficient-coding` with standalone and combined baselines. **SoL-Pi below means NVlabs' original Pi extension**; our portable skill is listed separately.

| Condition | Synthetic solved ↑ | Synthetic tokens / solve ↓ | SWE-bench solved ↑ | SWE-bench tokens / solve ↓ |
|---|---:|---:|---:|---:|
| No skill | 21/25 | **234k** | 9/12 | ≥1.62M |
| Karpathy | 19/25 | 296k | **11/12** | ≥1.45M |
| NVlabs SoL-Pi † | 21/25 | ≥39k † | 5/12 | ≥621k † |
| NVlabs SoL-Pi + Karpathy † | 19/25 | ≥56k † | 5/12 | ≥473k † |
| **Ours: `efficient-coding`** | **23/25** | 253k | **11/12** | **≥1.42M** |
| Ours + Karpathy | 22/25 | 288k | 8/12 | ≥1.94M |

**Completed comparisons:** Claude Code 2.1.286 · Qwen3.8-27B-FP8. † NVlabs SoL-Pi rows: Pi 0.85.1 harness · Qwen3.8-27B (FP8 and full precision treated as one model), same tasks, prompts, caps and graders. These are solved attempts, not unique tasks: 10 synthetic fixtures, including development data, and 6 SWE-bench issues. Tokens per solve include failed attempts. `k` = thousand; `M` = million; `≥` marks incomplete cost accounting.

**Baseline definitions:** “Ours + Karpathy” is the condition called “Both” in the existing reports: two skills loaded into one agent task. NVlabs SoL-Pi is the unmodified extension at the pinned commit, with all four mechanisms enabled, and needs the Pi runtime. **† Its token counts are not comparable with the Claude Code rows:** the harnesses send very different system prompts and tools on every turn. Compare solve counts only, with caution. 9 of its 74 runs hit the 1800 s cap, mostly while waiting in a shared model-server queue. The upstream paper's results use a different setup and are not substituted here.

Our standalone skill solved more attempts than no skill and than Ours + Karpathy on both pilot benchmarks. Compared with Ours + Karpathy, its synthetic tokens per solve were **about 12% lower** (253k vs 288k). Compared with Karpathy alone, it solved more synthetic attempts and the same number of SWE-bench attempts.

Token results against no skill remain mixed: synthetic cost per solve increased, and SWE-bench lower bounds do not establish an exact saving. On solve counts, NVlabs SoL-Pi matched no skill on synthetic diagnostics and solved fewer SWE-bench attempts than every Claude Code condition, but its harness differs. These small pilots do not establish a general performance advantage or superiority to NVlabs SoL-Pi.

[Full comparison and development history](docs/evaluation.md) · [Evaluation report](tests/report.md) · [Comparison chart](assets/benchmark-numbers.svg)

## Installation

### Skills CLI: Claude Code, Codex, or Cursor

Choose one client:

```bash
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent claude-code
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent codex
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent cursor
```

Add `--global` for a user-wide installation. In Codex, invoke with `$efficient-coding`.

These commands follow the [Skills CLI documentation](https://github.com/vercel-labs/skills). All three were validated on 2026-10-12 with Skills CLI 1.7.2 on Node 22: every installed file is byte-identical to the repository copy ([check script](tests/validation/skills_cli_check.sh)). Claude Code installs to `.claude/skills/`; Codex and Cursor install to `.agents/skills/`. The CLI needs Node 22 or newer. Official marketplace listing is TBD.

<details>
<summary>Manual installation and upgrade validation</summary>

Copy the full skill directory into your Claude Code project:

```bash
gh repo clone reliable-era/distill-skill-nvlabs-SoL-Pi
cd distill-skill-nvlabs-SoL-Pi
TARGET_PROJECT=/absolute/path/to/your/project
mkdir -p "$TARGET_PROJECT/.claude/skills"
cp -R skills/efficient-coding "$TARGET_PROJECT/.claude/skills/"
```

Include references and helpers; back up an existing installation before replacing it. A [ZIP distribution](.claude/skills/efficient-coding.zip) is available.

From a checkout, validate installation and packaging:

```bash
docker build -f tests/validation/Dockerfile -t sol-pi-validation .
docker run --rm --network none sol-pi-validation
```

The [workflow](.github/workflows/validate.yml) checks manifests, installation, resource bytes, and helper entrypoints without model calls. Behavioral performance is evaluated separately.

</details>

## Repository map

| Path | What you will find |
|---|---|
| [skills/efficient-coding/](skills/efficient-coding/) | The product: instructions, references, and offline helpers |
| [docs/evaluation.md](docs/evaluation.md) | Detailed results, comparison conditions, development history, and limitations |
| [tests/framework/](tests/framework/) | Docker evaluation framework, benchmark adapters, and analysis |
| [tests/goal.md](tests/goal.md) | Preregistered evaluation contracts |
| [tests/report.md](tests/report.md) | Evaluation report, from the first pilots to the current conclusion |
| [tests/eval/](tests/eval/) | Frozen inputs, grades, and audits |

## Sources and license

The design independently distills ideas from Liu et al., [*SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness*](https://arxiv.org/pdf/2609.20519v1). The [source digest](skills/efficient-coding/references/sol-pi-evidence.md) connects instructions to paper pages and inspected code. No upstream code is copied.

Karpathy's guidelines are a separate comparison baseline. The SoL-Pi paper's runtime savings belong to that system; this skill's results are measured separately.

[License](LICENSE) · [Report an issue](https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi/issues/new/choose)
