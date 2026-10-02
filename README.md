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

**Baseline means no skill installed.** “Latest” means the shipped 2,584-byte entrypoint; “original” means the earlier 6,573-byte entrypoint. Karpathy is frozen separately. The combined arm contains Karpathy and the explicitly named SoL-Pi version.

Tokens per verified solve = token traffic across **all attempts, including failures**, divided by verified solves. Lower is better when quality is comparable. These are token estimates, not dollar or energy measurements.

### Latest frozen bundle: pruned campaign

The final campaign contains **147 attempts**, including development, original calibration, candidate testing, held-out diagnostics, and repository repairs. All attempts completed grading and passed an independent provenance audit.

**Correctness — verified solves / attempts (higher is better)**

| Benchmark | No skill | Latest SoL-Pi | Karpathy | Karpathy + latest |
|---|---:|---:|---:|---:|
| Development | 8/10 | 9/10 | 7/10 | 8/10 |
| Held-out diagnostics | 13/15 | 14/15 | 12/15 | 14/15 |
| Repository repairs | 6/8 | 7/8 | 8/8 | 4/8 |

**Efficiency — tokens per verified solve (lower is better)**

| Benchmark | No skill | Latest SoL-Pi | Karpathy | Karpathy + latest |
|---|---:|---:|---:|---:|
| Development | 260k | 242k | 314k | 316k |
| Held-out diagnostics | 219k | 260k | 286k | 272k |
| Repository repairs | ≥1.42M | ≥1.63M | ≥1.32M | ≥2.40M |

`k` = thousand tokens; `M` = million tokens. Values are rounded. `≥` means incomplete accounting: repository costs cannot support an efficiency ranking.

Development used five cases over two rounds; held-out diagnostics used five cases over three rounds. Repository repairs used four SWE-bench Verified issues over two rounds.

The diagnostic cases cover large logs, producer/consumer interfaces, stale continuations, integration failures, and small fixes. The repository subset covers Pylint, Django, Astropy, and SymPy. It is a deliberately small diagnostic subset with limited generalization; two synthetic families share a mathematical defect.

- **Latest versus baseline:** one extra held-out solve, but **18.87% more tokens per solve**. Latest used more tokens in every diagnostic family and cost more per solve in every held-out round.
- **Latest versus Karpathy/combined:** lower diagnostic cost point estimates, with advantages reversing in one round and uncertainty intervals including zero.
- **Repository correctness:** Karpathy solved 8/8; latest 7/8; baseline 6/8; combined 4/8. Model timeouts were respectively 1, 2, 2, and 3. A passing patch can still come from a timed-out attempt.
- **Repository costs:** eight runs lack complete terminal usage summaries. Every arm's aggregate is a lower bound (`≥`), so these values cannot establish an economy ranking.
- **Candidate improvement:** tested only on development, solved 8/10 versus latest 9/10 and cost 20.45% more per solve. It was rejected before held-out feedback and is not the shipped skill.

The original-only calibration scored 5/5 at 221,166 tokens per solve. It was a separate single round and is not a repeated comparison with all four arms.

### Original bundle: earlier benchmark matrix

This historical matrix used the **original SoL-Pi bundle**, not the current shipped revision. It is kept separate from the latest campaign.

**Correctness — verified solves / attempts**

| Benchmark | No skill | Original SoL-Pi | Karpathy | Karpathy + original |
|---|---:|---:|---:|---:|
| Stress suite | 15/15 | 15/15 | 15/15 | 15/15 |
| Repository repairs | 19/24 | 19/24 | 19/24 | 19/24 |

**Efficiency — tokens per verified solve**

| Benchmark | No skill | Original SoL-Pi | Karpathy | Karpathy + original |
|---|---:|---:|---:|---:|
| Stress suite | 194k | 209k | 226k | 244k |
| Repository repairs | 2.40M | 2.55M | 2.30M | 2.39M |

The stress suite used five cases over three rounds. Repository repairs used twelve SWE-bench Verified issues over two rounds.

The original bundle increased SWE-bench tokens per solve by 6.5% versus baseline with equal observed resolution. The subsequent simplification shortened the entrypoint by 60.7%. A separate one-round, in-sample smoke comparison is documented in the report; it does not establish held-out savings.

### Backend and interpretation

All reported campaigns used **Qwen3.8-27B-FP8**, served locally through SGLang's Anthropic-compatible endpoint with DFlash speculative decoding. The agent was **Claude Code**, not a Claude model: version 2.1.285 for the original matrix and pinned 2.1.286 for the latest campaign. Latest repository attempts used medium effort, a 60-turn limit, and a 1,800-second model limit.

Runs used fresh containers and HOME directories with identical skill-loading hints. Inference was sequential on a single-request server. Scheduling labels 42/73/101 vary order; they are **not controlled model sampling seeds**.

Public network access was allowed. Some repository attempts retrieved upstream repaired source, tests, or task-relevant repair diffs. Official grades therefore do not establish unaided repair superiority. Small task counts, correlated fixtures, uncontrolled sampling, and incomplete repository usage also limit claims of stability and savings. No held-out outcome-driven skill revision was promoted.

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
