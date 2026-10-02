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

## Install and use

Clone the repository:

```bash
gh repo clone reliable-era/distill-skill-nvlabs-SoL-Pi
cd distill-skill-nvlabs-SoL-Pi
```

### Claude Code: install in a target project

Run from this cloned repository, replacing the target path with your project:

```bash
TARGET_PROJECT=/absolute/path/to/your/project
mkdir -p "$TARGET_PROJECT/.claude/skills"
cp -R skills/efficient-coding "$TARGET_PROJECT/.claude/skills/"
```

The complete directory is needed because `SKILL.md` links to references and scripts. If an older `efficient-coding` directory exists, back it up before replacing it.

Open Claude Code in the target project and explicitly ask it to load the skill:

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

Each table cell shows **verified solves / attempts · tokens per solve**.

| Benchmark / stage | Baseline: no skill | Latest SoL-Pi | Karpathy only | Karpathy + latest SoL-Pi |
|---|---:|---:|---:|---:|
| Development: 5 cases × 2 rounds | 8/10 · 259,731 | 9/10 · 242,163 | 7/10 · 313,901 | 8/10 · 315,987 |
| Held-out diagnostics: 5 cases × 3 rounds | 13/15 · 218,599 | 14/15 · 259,839 | 12/15 · 285,543 | 14/15 · 271,960 |
| SWE-bench Verified: 4 issues × 2 rounds | 6/8 · ≥1,419,534 | 7/8 · ≥1,628,508 | 8/8 · ≥1,317,814 | 4/8 · ≥2,396,043 |

The diagnostic cases cover large logs, producer/consumer interfaces, stale continuations, integration failures, and small fixes. The repository subset covers Pylint, Django, Astropy, and SymPy. It is a deliberately small diagnostic subset with limited generalization; two synthetic families share a mathematical defect.

- **Latest versus baseline:** one extra held-out solve, but **18.87% more tokens per solve**. Latest used more tokens in every diagnostic family and cost more per solve in every held-out round.
- **Latest versus Karpathy/combined:** lower diagnostic cost point estimates, with advantages reversing in one round and uncertainty intervals including zero.
- **Repository correctness:** Karpathy solved 8/8; latest 7/8; baseline 6/8; combined 4/8. Model timeouts were respectively 1, 2, 2, and 3. A passing patch can still come from a timed-out attempt.
- **Repository costs:** eight runs lack complete terminal usage summaries. Every arm's aggregate is a lower bound (`≥`), so these values cannot establish an economy ranking.
- **Candidate improvement:** tested only on development, solved 8/10 versus latest 9/10 and cost 20.45% more per solve. It was rejected before held-out feedback and is not the shipped skill.

The original-only calibration scored 5/5 at 221,166 tokens per solve. It was a separate single round and is not a repeated comparison with all four arms.

### Original bundle: earlier benchmark matrix

This historical matrix used the **original SoL-Pi bundle**, not the current shipped revision. It is kept separate from the latest campaign.

| Benchmark | Baseline: no skill | Original SoL-Pi | Karpathy only | Karpathy + original SoL-Pi |
|---|---:|---:|---:|---:|
| Stress suite: 5 cases × 3 rounds | 15/15 · 193,992 | 15/15 · 208,861 | 15/15 · 225,788 | 15/15 · 243,785 |
| SWE-bench Verified: 12 issues × 2 rounds | 19/24 · 2,397,297 | 19/24 · 2,553,476 | 19/24 · 2,299,941 | 19/24 · 2,387,513 |

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
