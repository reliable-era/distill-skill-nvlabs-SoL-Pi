# Distilled SoL-Pi

**Read less. Reuse evidence. Verify the fix.**

A portable `efficient-coding` skill inspired by [NVlabs/SoL-Pi](https://github.com/NVlabs/SoL-Pi), designed to reduce repeated reads and avoidable tool turns. Includes reproducible comparisons against no skill and Karpathy guidelines.

## Numbers

**LLM:** Qwen3.8-27B-FP8 · **Runtime:** SGLang + DFlash · **Agent:** Claude Code 2.1.286.

![Benchmark comparison: solve rates, failure-inclusive tokens per solve, and model timeouts](assets/benchmark-numbers.svg)

[PNG download](assets/benchmark-numbers.png) · [Reproduce the plot](tests/scripts/plot_numbers.py). Hatched cost bars are incomplete lower bounds; token-axis scales differ by benchmark.

| Benchmark | Configuration | Solved attempts ↑ | Tokens / solve ↓ | Timeouts ↓ |
|---|---|---:|---:|---:|
| Our synthetic diagnostics | No skill (baseline) | 21/25 | 234k | 0 |
| Our synthetic diagnostics | SoL-Pi (ours) | 23/25 | 253k | 0 |
| Our synthetic diagnostics | Karpathy | 19/25 | 296k | 0 |
| Our synthetic diagnostics | Both skills | 22/25 | 288k | 0 |
| SWE-bench Verified | No skill (baseline) | 9/12 | ≥1.62M | 3 |
| SWE-bench Verified | SoL-Pi (ours) | 11/12 | ≥1.42M | 2 |
| SWE-bench Verified | Karpathy | 11/12 | ≥1.45M | 2 |
| SWE-bench Verified | Both skills | 8/12 | ≥1.94M | 3 |

**Sample sizes:** SWE-bench Verified has **6 unique issues × 2 rounds = 12 attempts per configuration**. Our synthetic diagnostics have **10 fixtures**: 5 development × 2 rounds + 5 held-out × 3 rounds = **25 attempts per configuration**. Fractions in the table and plot count solved attempts, not unique tasks.

**Ours** is the latest shipped revision. **Both skills** loads Karpathy and ours separately. Tokens include failed attempts; `k` = thousand, `M` = million, `≥` = incomplete lower bound. Unmeasured or unverified items are marked **TBD**.

Ours ties Karpathy at 11/12 SWE-bench Verified solves; baseline is cheaper on our synthetic diagnostics. **A stable general efficiency win is not established.** Public repair retrieval limits repository attribution; incomplete costs do not support exact savings claims.

**Benchmark sources:** Our synthetic diagnostics combine custom development and held-out fixtures. This aggregate includes development data and is not a pure held-out score. [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) combines six distinct issues, each repeated twice: the original four-issue sample plus two new randomly selected easy issues. Totals sum all attempts across both samples; their selection rules differ, so this is a descriptive six-issue aggregate. Five diagnostic cases ×2 development / ×3 held-out rounds. Scheduling seeds do not control model sampling. [Full results and limitations](tests/report.md) · [Random subset details](tests/eval/random-followup/results/summary.md).

<details>
<summary>Original-version results</summary>

The original entrypoint was 6,573 bytes; ours is the 2,584-byte revision. These earlier measurements use different tasks and Claude Code 2.1.285 and are not pooled above.

| Benchmark | Configuration | Solved attempts ↑ | Tokens / solve ↓ |
|---|---|---:|---:|
| Stress suite | No skill | 15/15 | 194k |
| Stress suite | Original SoL-Pi (ours) | 15/15 | 209k |
| Stress suite | Karpathy | 15/15 | 226k |
| Stress suite | Both skills, original ours | 15/15 | 244k |
| Repository repairs | No skill | 19/24 | 2.40M |
| Repository repairs | Original SoL-Pi (ours) | 19/24 | 2.55M |
| Repository repairs | Karpathy | 19/24 | 2.30M |
| Repository repairs | Both skills, original ours | 19/24 | 2.39M |

The later development candidate was rejected and is not shipped. Original calibration and smoke comparisons are in the full report.

</details>

## Evaluation framework

[Docker framework](tests/framework/README.md): nine agent CLIs, six benchmark sources, a frozen eight-task pilot, cost accounting, and isolated grading. [A four-configuration native pilot](tests/framework/trials/README.md) is complete for Pi, Codex, Copilot, Cursor Auto, and Antigravity `agy`: 40 real attempts on two reused synthetic fixtures. It does not establish a general efficiency win. [Native public-benchmark development](tests/framework/refinement/development/README-broad.md) now covers official Flask repair grading, a Go exercise and terminal sanitization. The no-reread candidate was rejected; a [new locate-first candidate](tests/framework/refinement/development/swe-flask-locate-first/README.md) reduced tokens in one matched Codex Flask round. A stable economic win remains **TBD**. [Human login steps](tests/framework/runtime/README.md).

## Quick start

Inside Claude Code:

```text
/plugin marketplace add reliable-era/distill-skill-nvlabs-SoL-Pi
/plugin install distill-sol-pi@sol-pi-skills
/distill-sol-pi:efficient-coding Fix the failing parser test and verify the change.
```

For another task:

```text
Use efficient-coding to investigate logs/test-run.log, check the failure
against the source, fix it, and run the affected tests.
```

## Install for your agent

### Claude Code marketplace

Use the commands above. The repository supplies the [marketplace and plugin manifests](.claude-plugin). Installation is tested in Docker and GitHub Actions.

### Skills CLI — Claude Code, Codex, Cursor

**Repository-specific installation validation: TBD.** The commands below follow the Skills CLI documentation; these client installation paths have not been tested here.

Using the [open Skills CLI](https://github.com/vercel-labs/skills), choose your client:

```bash
# Claude Code
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent claude-code

# Codex
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent codex

# Cursor
npx skills add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent cursor
```

These commands target this GitHub repository. Official marketplace listing: **TBD**. Performance on Codex/Cursor and other LLM backends: **TBD**. Add `--global` for a user-wide installation. In Codex, invoke with `$efficient-coding`.

### Manual project installation

```bash
gh repo clone reliable-era/distill-skill-nvlabs-SoL-Pi
cd distill-skill-nvlabs-SoL-Pi
TARGET_PROJECT=/absolute/path/to/your/project
mkdir -p "$TARGET_PROJECT/.claude/skills"
cp -R skills/efficient-coding "$TARGET_PROJECT/.claude/skills/"
```

Copy the whole directory; references and helpers are part of the skill. Back up any existing installation before replacing it. A [ZIP distribution](.claude/skills/efficient-coding.zip) is also available.

## How it works

Focused source reads, bounded log inspection, exact evidence checks, recovery from rejected tool arguments, and relevant verification. On resumption, reconcile continuation notes with current files before repeating work.

This is instruction-level guidance. It does not implement upstream Pi's native context replacement, fused tools, or compaction. Supporting resources are optional; routine fixes need no extra bookkeeping or agents. [Read the skill](skills/efficient-coding/SKILL.md).

## Validate an upgrade

```bash
docker build -f tests/validation/Dockerfile -t sol-pi-validation .
docker run --rm --network none sol-pi-validation
```

The [GitHub workflow](.github/workflows/validate.yml) checks manifests, installs the plugin in a fresh non-root container, verifies installed resource bytes, and checks helper entrypoints. No model calls are made; performance upgrades need separate behavioral evaluation.

## Evidence and contributions

[Full report](tests/report.md) · [147-attempt audit](tests/eval/pruned/audit/independent-final147-audit.json) · [16-attempt follow-up audit](tests/eval/random-followup/audit/independent-final16.json) · [Comparison CSV](tests/eval/pruned/results/comparison.csv) · [Issue templates](https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi/issues/new/choose).

Benchmark code, frozen inputs, grades, and traces live in `tests/eval/`. Runtime dependencies and the downloaded Claude Code binary are excluded; manifests retain their hashes. Historical paths identify the original execution workspace.
