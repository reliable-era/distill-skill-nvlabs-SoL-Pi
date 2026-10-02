# Distilled SoL-Pi: efficient coding skill and benchmarks

This project turns ideas from [NVlabs/SoL-Pi](https://github.com/NVlabs/SoL-Pi) into a portable `efficient-coding` skill and measures whether it helps a coding agent finish verified tasks with fewer tokens. It compares the skill with **no skill**, **andrej-karpathy-skills**, and **Karpathy + SoL-Pi**.

The purpose is to test useful workflow guidance, improve it from development evidence, and publish the failures as well as the successes. **The latest bundle has not demonstrated a stable, economical majority win.** It improved some interface-repair outcomes, while the no-skill baseline was cheaper on held-out diagnostics and Karpathy scored highest on the small repository subset.

## What the skill does

The instructions encourage the agent to:

- Search and read the relevant source, callers, and tests; reuse findings instead of repeatedly reading them.
- Batch independent reads and inspect decisive sections of long logs.
- Preserve a command's actual exit status when shortening its output.
- Check quoted diagnostics against their source and correct rejected tool arguments.
- Reconcile continuation notes with current files when resuming work.
- Verify the requested behavior and report remaining failures.

Supporting references and offline evidence/accounting scripts are included for tasks that need them. Routine fixes do not require extra task cards, telemetry, or workers.

The upstream SoL-Pi runtime includes capabilities that this instruction bundle cannot provide: replacing provider context, registering fused tools, and native compaction. Writing a summary alone does not remove earlier API messages. This project evaluates the portable skill, not a reproduction of the upstream runtime's savings.

## Install

### Option A: Claude Code plugin

Inside Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add reliable-era/distill-skill-nvlabs-SoL-Pi
/plugin install distill-sol-pi@sol-pi-skills
```

Then invoke the skill with your task:

```text
/distill-sol-pi:efficient-coding Fix the failing parser test and verify the change.
```

This follows the plugin installation approach used by [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills). Plugin metadata lives in [.claude-plugin/](.claude-plugin/); packaging does not change the benchmarked skill instructions.

### Option B: manual project installation

Clone the repository:

```bash
gh repo clone reliable-era/distill-skill-nvlabs-SoL-Pi
cd distill-skill-nvlabs-SoL-Pi
```

Run from this cloned repository, replacing the target path with your project:

```bash
TARGET_PROJECT=/absolute/path/to/your/project
mkdir -p "$TARGET_PROJECT/.claude/skills"
cp -R skills/efficient-coding "$TARGET_PROJECT/.claude/skills/"
```

The complete directory is needed because `SKILL.md` links to references and scripts. If an older `efficient-coding` directory exists, back it up before replacing it.

## Use

After manual installation, open Claude Code in the target project and explicitly ask it to load the skill:

```text
Load .claude/skills/efficient-coding/SKILL.md and use its guidance.
Fix the failing parser test. Inspect the relevant code and verify the change.
```

For long logs or resumed work:

```text
Use efficient-coding to investigate logs/test-run.log. Find the relevant failure,
check it against the source, make the fix, and run the affected tests.
```

```text
Use efficient-coding to resume from HANDOFF.md. Check the current files and
verification state before continuing the remaining work.
```

Explicit loading matters: the evaluated model did not reliably discover skills unaided. A skill file being installed does not prove the agent read or followed it.

The clone also contains a project-local `.claude/skills/efficient-coding` symlink and a [ZIP distribution](.claude/skills/efficient-coding.zip). The canonical source is [SKILL.md](skills/efficient-coding/SKILL.md). To compare with Karpathy, install its `karpathy-guidelines` alongside this directory and load both; the combined configuration is evaluated below.

## Performance across benchmarks

**Model:** Qwen3.8-27B-FP8 on SGLang. **Agent:** Claude Code 2.1.286.

“Ours” is the latest shipped SoL-Pi-inspired skill. “Both skills” loads Karpathy and ours together. Baseline uses no skill.

### Correctness

Verified solves / attempts. Higher is better.

| Benchmark | No skill | SoL-Pi (ours) | Karpathy | Both skills |
|---|---:|---:|---:|---:|
| Development | 8/10 | **9/10** | 7/10 | 8/10 |
| Held-out diagnostics | 13/15 | **14/15** | 12/15 | **14/15** |
| Repository repairs | 6/8 | 7/8 | **8/8** | 4/8 |

### Efficiency

Tokens per verified solve, including failed attempts. Lower is better.

| Benchmark | No skill | SoL-Pi (ours) | Karpathy | Both skills |
|---|---:|---:|---:|---:|
| Development | 260k | **242k** | 314k | 316k |
| Held-out diagnostics | **219k** | 260k | 286k | 272k |
| Repository repairs | ≥1.42M | ≥1.63M | ≥1.32M | ≥2.40M |

`k` = thousand; `M` = million. Repository costs are incomplete lower bounds (`≥`) and cannot support a cost ranking.

**What we learned:** ours solved one more held-out attempt than baseline, but cost **18.87% more per solve**. Karpathy had the highest repository score. Loading both skills did not improve on ours. A stable efficiency win is **not established**.

**Scope:** five diagnostic cases, repeated twice in development and three times on held-out variants; four SWE-bench Verified issues, repeated twice. Public upstream repair retrieval limits repository attribution. Results apply to this small subset and backend; round labels are scheduling seeds, not controlled model sampling seeds.

All **147 campaign attempts** were graded and independently audited. The development candidate was rejected; the shipped skill remains unchanged. See the [full report](report.md) for original-version comparisons, per-round variability, uncertainty, and retrieval audits.

## Explore the evidence

| Resource | Contents |
|---|---|
| [Full report](report.md) | Results, uncertainty, behavioral diagnosis, historical smoke comparisons, and limitations |
| [Final comparison CSV](eval/pruned/results/comparison.csv) | Clearly versioned stage-level grades and costs |
| [Held-out family breakdown](eval/pruned/results/heldout-by-family.md) | Which diagnostic families contributed gains and overhead |
| [Frozen campaign plan](eval/pruned/plan.v4-real-swe.json) | Tasks, arms, rounds, limits, and integrity pins |
| [Final independent audit](eval/pruned/audit/independent-final147-audit.json) | All 147 cells, provenance, accounting, grading, and protocol verification |
| [Completion checklist](eval/pruned/audit/completion-requirements.md) | Requirement-by-requirement evidence |
| [Candidate decision](eval/pruned/candidate-decision.json) | Development gate and rejection evidence |

`eval/` includes benchmark runners, frozen inputs, results, and traces. The virtual environment and downloaded Claude Code binary are excluded; manifests preserve the expected binary hashes. Historical records contain paths from the original execution workspace. Reproducing the campaign requires its Docker/SWE-bench dependencies and compatible local model server; installing the skill itself only requires copying its directory.

## Validate an upgrade

GitHub Actions builds and runs our [Docker validation container](validation/Dockerfile) on pushes and pull requests. Run the same checks locally:

```bash
docker build -f validation/Dockerfile -t sol-pi-validation .
docker run --rm --network none sol-pi-validation
```

The container runs as a fresh non-root user with Claude Code 2.1.286. It validates both manifests, registers the local marketplace, installs the plugin, checks every installed skill resource against the source bytes, and checks helper entrypoints. It needs no model credentials or inference server. These installation checks do not measure coding performance; behavioral upgrades still require separate development and held-out evaluation.

Use the repository's [issue chooser](https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi/issues/new/choose) for bug reports, installation problems, feature/contribution proposals, or upgrade/performance validation. The forms ask for focused reproduction steps and evidence, following the structure of the [cuTile Rust](https://github.com/NVlabs/cutile-rs/tree/main/.github/ISSUE_TEMPLATE) and [Pi](https://github.com/earendil-works/pi/tree/main/.github/ISSUE_TEMPLATE) examples.
