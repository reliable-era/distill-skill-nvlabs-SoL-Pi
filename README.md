# Distilled SoL-Pi

**Bring SoL-Pi's efficiency ideas to the coding agent you already use.**

`efficient-coding` is a lightweight skill for focused reads, long-log debugging, and verified repairs. It turns [NVlabs' SoL-Pi](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19) research into practical instructions that fit an existing coding workflow.

Use it when an agent keeps rereading files, drowning in test output, repeating failed tool calls, or losing track of work after an interruption.

[Quick start](#quick-start) · [Why use it](#why-use-it) · [Comparison](#how-it-compares) · [Results](#measured-results) · [Evaluation details](docs/evaluation.md)

## Why use it?

- **A small core with useful depth.** The entrypoint is just **2,584 bytes**. References and helpers load when needed, keeping ordinary fixes simple.
- **One workflow from source to verification.** Focus reads on relevant source, check diagnostic evidence, make the targeted edit, and run the affected checks. Batch independent searches and reconcile prior work before resuming.
- **Offline tools for trustworthy log handling.** Archive exact output, recall bounded pages, and check source hashes, recorded status, and exact quotations with the bundled Python helper.
- **Public evidence behind the design.** Inspect comparisons against no skill and Karpathy, frozen inputs, independent grades, failure-inclusive costs, and the reasons earlier revisions were rejected.

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

In two pilot benchmarks, `efficient-coding` solved more attempts than the no-skill baseline:

| Benchmark | No skill: solved | `efficient-coding`: solved | Tokens / solve: no skill → skill |
|---|---:|---:|---:|
| Synthetic diagnostics | 21/25 | **23/25** | 234k → 253k |
| SWE-bench Verified | 9/12 | **11/12** | ≥1.62M → ≥1.42M |

Claude Code 2.1.286 · Qwen3.8-27B-FP8. These are **solved attempts**, not unique tasks: 10 synthetic fixtures, including development data, and 6 SWE-bench issues. Tokens per solve include the cost of failed attempts. `k` = thousand; `M` = million; `≥` marks incomplete cost accounting.

Compared with loading our skill **together with Karpathy**, the standalone skill solved 23 vs 22 synthetic attempts and 11 vs 8 SWE-bench attempts. Synthetic tokens per solve were **253k vs 288k—about 12% lower**. “Together” means both instruction sets loaded in one agent task; the setup is explained in the [evaluation document](docs/evaluation.md#what-the-comparison-conditions-mean).

Token results against no skill are mixed: synthetic cost per solve increased, and the SWE-bench lower bounds do not establish an exact saving. These small pilots support further evaluation; they do not establish a general performance advantage.

[Full comparison and development history](docs/evaluation.md) · [Original report](tests/report.md) · [Comparison chart](assets/benchmark-numbers.svg)

## Installation

### Skills CLI: Claude Code, Codex, or Cursor

Choose one client:

```bash
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent claude-code
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent codex
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent cursor
```

Add `--global` for a user-wide installation. In Codex, invoke with `$efficient-coding`.

These commands follow the [Skills CLI documentation](https://github.com/vercel-labs/skills); these installation routes have not been validated in this repository. Official marketplace listing is TBD.

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
| [tests/report.md](tests/report.md) | Original skill evaluation report |
| [tests/eval/](tests/eval/) | Frozen inputs, grades, and audits |

## Sources and license

The design independently distills ideas from Liu et al., [*SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness*](https://arxiv.org/pdf/2609.20519v1). The [source digest](skills/efficient-coding/references/sol-pi-evidence.md) connects instructions to paper pages and inspected code. No upstream code is copied.

Karpathy's guidelines are a separate comparison baseline. The SoL-Pi paper's runtime savings belong to that system; this skill's results are measured separately.

[License](LICENSE) · [Report an issue](https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi/issues/new/choose)
