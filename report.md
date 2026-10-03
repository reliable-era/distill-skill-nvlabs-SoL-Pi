# Report: efficient-coding (nvlab-sol-pi-skills) vs. karpathy-guidelines

Final original matrix, 2026-10-02: 60/60 stress and 96/96 SWE-bench runs graded. Plan: [goal.md](goal.md). Raw data: `eval/runs/` and `eval/results/`.

## Setup

- **Agent:** Claude Code 2.1.285, `claude -p … --allow-dangerously-skip-permissions --dangerously-skip-permissions --output-format stream-json --verbose --effort medium --max-turns 60`, one fresh Docker container and fresh `HOME` per run (no host CLAUDE.md / plugins).
- **Model:** `Qwen3.8-27B-FP8` on sglang at `127.0.0.1:8000` (Anthropic `/v1/messages`, `--max-running-requests 1`, DFlash speculative decoding, reasoning parser qwen3).
- **Arms:** 1 `sol-pi` (efficient-coding), 2 `baseline` (no skill), 3 `karpathy` (karpathy-guidelines), 4 `karpathy+sol-pi` (both). Original entrypoint SHA-256: efficient-coding `75e5df83…`, karpathy-guidelines `6e22cc54…`; the original efficient-coding file hashes are recorded in `eval/revision_eval/manifest.json`.
- **Prompt:** identical in every arm; it ends with one sentence asking the agent to load any skills in `.claude/skills` (no-op for baseline), because the 27B model never auto-triggered a skill in smoke tests.
- **Seeds / rounds:** task sample and arm order fixed with seed 42; Claude Code exposes no sampling seed, so rounds (stress: 3, SWE-bench: 2) measure run-to-run variance.
- **Tokens:** the server reports no cache fields, so every request's full prompt counts as input. Numbers are token traffic, not dollars.

- **Server launch arguments:** [recorded full arguments](eval/results/server_args.txt).
- **Scored scope:** 12 seeded, difficulty-stratified SWE-bench tasks × 2 rounds and 5 stress cases × 3 rounds. The original 50-task target was reduced after the single-slot throughput pilot; see [goal.md](goal.md).
- **Scored artifact:** the original bundle in `eval/skills/efficient-coding/`, preserved in [the original ZIP](eval/diagnostics/original-efficient-coding.zip). The current distributable contains a later revision and was not used in this matrix.

## Results

### Total token traffic across all attempts

| Benchmark | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---:|---:|---:|---:|
| Stress suite | 3,132,909 | 2,909,873 | 3,386,822 | 3,656,776 |
| SWE-bench Verified | 48,516,048 | 45,548,652 | 43,698,878 | 45,362,748 |

### Resolution rate (solved / runs)

| Benchmark | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| Stress suite (5 cases) | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% |
| SWE-bench Verified (12 tasks) | 79% (19/24); by round 75%/83% | 79% (19/24); by round 83%/75% | 79% (19/24); by round 75%/83% | 79% (19/24); by round 75%/83% |

### Tokens (input + output, all runs incl. failures)

| Benchmark | Metric | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|---|
| Stress suite (5 cases) | mean tokens / run | 209k | 194k | 226k | 244k |
| Stress suite (5 cases) | mean output tokens / run | 3k | 3k | 4k | 5k |
| Stress suite (5 cases) | **tokens / verified solve** | 209k | 194k | 226k | 244k |
| Stress suite (5 cases) | mean requests / run | 10.2 | 9.1 | 10.8 | 11.5 |
| Stress suite (5 cases) | mean wall min / run | 0.8 | 0.9 | 1.6 | 0.9 |
| SWE-bench Verified (12 tasks) | mean tokens / run | 2,022k | 1,898k | 1,821k | 1,890k |
| SWE-bench Verified (12 tasks) | mean output tokens / run | 24k | 28k | 28k | 26k |
| SWE-bench Verified (12 tasks) | **tokens / verified solve** | 2,553k | 2,397k | 2,300k | 2,388k |
| SWE-bench Verified (12 tasks) | mean requests / run | 44.4 | 43.8 | 41.4 | 42.3 |
| SWE-bench Verified (12 tasks) | mean wall min / run | 14.3 | 12.7 | 12.7 | 13.0 |

### Behaviour

| Benchmark | Metric | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|---|
| Stress suite (5 cases) | normal-ending unresolved runs (completion proxy) | 0 | 0 | 0 | 0 |
| Stress suite (5 cases) | hit turn/time limit | 0 | 0 | 0 | 0 |
| Stress suite (5 cases) | runs that invoked a skill | 15 | 0 | 15 | 15 |
| SWE-bench Verified (12 tasks) | normal-ending unresolved runs (completion proxy) | 2 | 0 | 3 | 2 |
| SWE-bench Verified (12 tasks) | hit turn/time limit | 7 | 9 | 5 | 8 |
| SWE-bench Verified (12 tasks) | runs that invoked a skill | 23 | 0 | 24 | 24 |

### Paired differences (matched task × round; bootstrap 95% CI)

| Benchmark | Comparison | n | Δ resolve rate [CI] | wins/losses | Δ tokens / run [CI] |
|---|---|---|---|---|---|
| Stress suite (5 cases) | sol-pi - baseline | 15 | +0% [+0%, +0%] | 0/0 | 15k [-20k, 54k] |
| Stress suite (5 cases) | karpathy+sol-pi - karpathy | 15 | +0% [+0%, +0%] | 0/0 | 18k [-19k, 50k] |
| Stress suite (5 cases) | sol-pi - karpathy | 15 | +0% [+0%, +0%] | 0/0 | -17k [-50k, 24k] |
| SWE-bench Verified (12 tasks) | sol-pi - baseline | 24 | +0% [-12%, +12%] | 1/1 | 124k [-157k, 414k] |
| SWE-bench Verified (12 tasks) | karpathy+sol-pi - karpathy | 24 | +0% [+0%, +0%] | 0/0 | 69k [-218k, 380k] |
| SWE-bench Verified (12 tasks) | sol-pi - karpathy | 24 | +0% [+0%, +0%] | 0/0 | 201k [-68k, 447k] |

### Per task: Stress suite (5 cases) (solved/runs, mean tokens)

| Task | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| s1_small_fix | 3/3, 137k | 3/3, 123k | 3/3, 164k | 3/3, 231k |
| s2_large_log | 3/3, 170k | 3/3, 162k | 3/3, 194k | 3/3, 273k |
| s3_fabricated_quote | 3/3, 280k | 3/3, 289k | 3/3, 279k | 3/3, 236k |
| s4_edit_then_fail | 3/3, 236k | 3/3, 210k | 3/3, 288k | 3/3, 235k |
| s5_continuation | 3/3, 222k | 3/3, 186k | 3/3, 204k | 3/3, 243k |

### Per task: SWE-bench Verified (12 tasks) (solved/runs, mean tokens)

| Task | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| astropy__astropy-7336 | 2/2, 1,052k | 2/2, 568k | 2/2, 547k | 2/2, 355k |
| django__django-11149 | 2/2, 3,207k | 2/2, 2,165k | 2/2, 2,832k | 2/2, 3,326k |
| django__django-11292 | 2/2, 2,756k | 2/2, 2,978k | 2/2, 2,653k | 2/2, 3,054k |
| django__django-13128 | 2/2, 2,788k | 2/2, 2,189k | 2/2, 1,885k | 2/2, 2,365k |
| django__django-14155 | 2/2, 1,637k | 2/2, 2,266k | 2/2, 979k | 2/2, 1,961k |
| django__django-14752 | 2/2, 966k | 2/2, 677k | 2/2, 640k | 2/2, 596k |
| django__django-15380 | 2/2, 916k | 2/2, 1,171k | 2/2, 947k | 2/2, 866k |
| pytest-dev__pytest-8399 | 2/2, 2,415k | 2/2, 2,010k | 2/2, 1,770k | 2/2, 1,974k |
| sphinx-doc__sphinx-7440 | 0/2, 2,705k | 0/2, 2,958k | 0/2, 3,070k | 0/2, 2,624k |
| sphinx-doc__sphinx-8265 | 0/2, 2,327k | 0/2, 2,770k | 0/2, 3,014k | 0/2, 2,290k |
| sympy__sympy-16886 | 2/2, 293k | 2/2, 187k | 2/2, 470k | 2/2, 208k |
| sympy__sympy-19040 | 1/2, 3,197k | 1/2, 2,835k | 1/2, 3,043k | 1/2, 3,063k |

### Sensitivity: paired bootstrap by whole task

Repeated rounds share the same task. This additional bootstrap resamples whole tasks, preserving rounds and paired arms (5,000 samples, seed 42). The preceding tables retain the originally specified task × round bootstrap.

| Benchmark | Comparison | Δ tokens/run [95% CI] | Δ tokens/verified solve [95% CI] |
|---|---|---:|---:|
| Stress | sol-pi - baseline | +15k [+1k, +28k] | +15k [+1k, +28k] |
| Stress | karpathy+sol-pi - karpathy | +18k [-30k, +66k] | +18k [-30k, +66k] |
| Stress | sol-pi - karpathy | -17k [-37k, +4k] | -17k [-37k, +4k] |
| SWE-bench | sol-pi - baseline | +124k [-140k, +394k] | +156k [-199k, +470k] |
| SWE-bench | karpathy+sol-pi - karpathy | +69k [-184k, +328k] | +88k [-305k, +371k] |
| SWE-bench | sol-pi - karpathy | +201k [-61k, +453k] | +254k [-102k, +499k] |

## Findings

The original bundle does not meet the goal's win condition. Every arm solves 19/24 SWE-bench runs and 15/15 stress runs, while adding the bundle increases the point estimate of tokens per verified solve: **+6.5% versus baseline** on SWE-bench and **+3.8% on top of karpathy**; stress increases are +7.7% and +8.0%. Karpathy alone has the lowest SWE-bench cost point estimate. SWE-bench token intervals include zero, so neither savings nor a cost regression is statistically established. Equal observed resolution is not proof of noninferiority.

SWE-bench sol-pi uses +127,720 input tokens/run and -4,078 output tokens/run versus baseline. The increase concerns replayed input and trajectory length, rather than generated output. The original skill does not implement upstream SoL-Pi's provider-context replacement, native compaction, fused tool schemas, or automatic reducer interception. No explicit efficient-coding reference reads, helper calls, or compaction events occur in the SWE-bench skill-bearing traces. Details and counterevidence are in [the reviewed diagnosis](eval/diagnostics/FINDINGS.txt).

Cost differences are noisy. One Django task-round accounts for 79% of the net sol-pi token increase; removing the whole task reduces the difference from +124k to +40k tokens/run. More sol-pi cells are expensive (14/24) than cheap (10/24), but the combined arm is cheaper in 13/24 cells despite a higher mean. Malformed tool calls occur in all arms and are more numerous with sol-pi; the evaluation does not establish that the skill causes those failures.

Stress sol-pi-minus-baseline remains positive when dropping any one case. Its five-task cluster bootstrap interval excludes zero, unlike the originally specified cell bootstrap. With only five task clusters and a resolution ceiling, this is a sensitivity result rather than a broad efficiency conclusion.

## Limits, grading, and behavior

SWE-bench agent limits: sol-pi 5/24 max-turn endings plus 2/24 wall timeouts; baseline 9/24 max-turn endings and no wall timeouts; karpathy 5/24 max-turn endings and no wall timeouts; combined 7/24 max-turn endings plus 1/24 wall timeout. Stress has no agent-limit hits. A max-turn ending can still yield a verified fix. The completion column is a proxy for normal endings that fail grading, not a semantic audit of the final text.

The combined arm's `sympy__sympy-19040/r1` was recorded unresolved after the official grader timed out at 1,800 seconds. Its `graded.json` preserves the manual note and the harness log preserves the timeout. This grading timeout is separate from agent wall limits. All other scored SWE-bench runs have official harness grades. Stress grades come from hidden tests; their original runner used a passing-output heuristic, while the revision smoke runner records pytest exit codes directly.

The explicit skill-loading instruction changes activation behavior. One sol-pi run read SKILL.md directly rather than invoking Skill; every other SWE-bench skill run contains a named Skill invocation. No native sampling seed is exposed; repeated rounds measure uncontrolled run variance. The server reports no cache fields, so these token totals cannot establish dollar savings or transfer to cached frontier-model workloads. Wall times are observations on a shared single-request server, not isolated inference latency.

Only one backend and a small issue subset were tested. SWE-bench runs can fetch online source in every arm, and traces include upstream-source lookup; this is not a network-isolated evaluation. Repeated rounds and few task clusters limit uncertainty estimates. Zero-width empirical resolution intervals occur when paired outcomes, or paired task averages, agree; they do not establish population-level equivalence. No noninferiority margin was specified in advance. The SoL-Pi paper's savings and its runtime extensions were not reproduced by this prompt-only evaluation.

## Revision after evaluation

The revised source is [skills/efficient-coding/SKILL.md](skills/efficient-coding/SKILL.md), with an updated distributable in `.claude/skills/efficient-coding.zip`. Its entrypoint is 60.7% shorter by bytes, removes ordinary-task bookkeeping and telemetry instructions, preserves evidence and verification, and clarifies runtime prerequisites. A separate in-sample, one-round behavioral check compares baseline, the original, and the revision in `eval/revision_eval/`. Those observations are not mixed into this original matrix and do not establish held-out savings.

### Revision smoke observations

The consolidated smoke comparison covers the same five stress cases, one round per condition. Original and latest refer to the two efficient-coding versions, not the upstream Pi runtime extension. Baseline/original/latest were run in the initial stage; Karpathy-only and both combinations were measured in a subsequent stage with the same prompts, model, limits, and graders. [Measurement data](eval/revision_eval/summary.json), [manifest](eval/revision_eval/manifest.json), and [CSV](eval/revision_eval/comparison.csv) are separate from the original multi-round matrix.

Observed agent version: 2.1.286; model: Qwen3.8-27B-FP8.

| Metric | Baseline (no skills) | Original sol-pi | Latest sol-pi | Karpathy only | Karpathy + original sol-pi | Karpathy + latest sol-pi |
|---|---:|---:|---:|---:|---:|---:|
| Verified solves | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| Tokens per verified solve | 175,815 | 242,563 | 212,601 | 251,784 | 279,889 | 233,269 |
| Change versus baseline | +0.0% | +38.0% | +20.9% | +43.2% | +59.2% | +32.7% |
| Mean model requests/case | 9.0 | 12.2 | 9.2 | 11.6 | 11.8 | 11.0 |

This one-round, in-sample comparison does not establish savings, transfer, or noninferiority. The largest revised standalone regression reads a full log before the skill loads; shortening instructions cannot retroactively replace that history.

### Pruned campaign: completed and independently audited

The frozen campaign completed all147 planned attempts:40 development,5 original calibration,10 candidate development,60 held-out diagnostics and32 repository repairs. Latest SoL-Pi did not demonstrate the requested stable majority win in correctness and economy. Its small held-out correctness gain came with higher token cost than baseline; Karpathy obtained the highest repository score, and the combined bundle lagged on repository correctness. These are configuration comparisons, not causal instruction-level effects.

Five diagnostic presentations cover large logs, producer/consumer interfaces, stale continuations, integration repair and small fixes. Each has one related held-out variant. Four prospectively unexposed SWE-bench Verified issues were selected from metadata before outcomes: pylint-4551, django-13195, astropy-13033 and sympy-19637, spanning four repositories and human difficulty strata. Selection and all failed attempts remain unchanged. The diagnostic fixtures are tiny and related; large-log and small-control tasks share ceiling division. The log prompt names the defect. Blind review also notes mild Unicode-normalization ambiguity and imprecise empty-name wording. This subset supports targeted diagnosis, with limited generalization to broad maintenance.

Backend: local Qwen3.8-27B-FP8 through SGLang, pinned Claude Code2.1.286, medium effort,60-turn/1800-second model limits, fresh containers/HOME and identical skill-loading hint. Calls ran sequentially. Labels42/73/101 randomize scheduling, not backend sampling RNG. Diagnostics use three held-out rounds; repository repairs use two. Archived runners preserve diagnostic provenance; the audited transition restored and verified exact clean repository base commits before SWE actors. Official swebench4.1 grading uses the frozen local dataset; all four gold preflights passed.

Costs below include failed matched attempts. The latest terminal modelUsage is a cumulative query-pipeline estimate including main and auxiliary calls; main usage is preserved separately and never added again. Calls outside the query pipeline are excluded by the CLI. These are reported token estimates, not billed money or GPU energy. Missing terminal summaries remain recorded lower bounds, marked≥. Every repository configuration has at least one such run, so repository aggregate savings and adoption claims are unsupported.

| Stage | Configuration | Version | Status | Verified / matched | Total tokens | Tokens / solve |
|---|---|---|---|---:|---:|---:|
| dev | No skill | baseline | complete | 8/10 | 2,077,844 | 259,730.50 |
| dev | SoL-Pi | latest frozen | complete | 9/10 | 2,179,469 | 242,163.22 |
| dev | Karpathy | frozen Karpathy | complete | 7/10 | 2,197,310 | 313,901.43 |
| dev | Karpathy + SoL-Pi | latest frozen SoL-Pi | complete | 8/10 | 2,527,898 | 315,987.25 |
| original_calibration | SoL-Pi | original frozen | complete | 5/5 | 1,105,832 | 221,166.40 |
| candidate_dev | SoL-Pi candidate | rejected development candidate | complete | 8/10 | 2,333,390 | 291,673.75 |
| heldout | No skill | baseline | complete | 13/15 | 2,841,791 | 218,599.31 |
| heldout | SoL-Pi | latest frozen | complete | 14/15 | 3,637,743 | 259,838.79 |
| heldout | Karpathy | frozen Karpathy | complete | 12/15 | 3,426,520 | 285,543.33 |
| heldout | Karpathy + SoL-Pi | latest frozen SoL-Pi | complete | 14/15 | 3,807,433 | 271,959.50 |
| real_swe | No skill | baseline | complete; incomplete usage | 6/8 | ≥ 8,517,203 | ≥ 1,419,533.83 |
| real_swe | SoL-Pi | latest frozen | complete; incomplete usage | 7/8 | ≥ 11,399,553 | ≥ 1,628,507.57 |
| real_swe | Karpathy | frozen Karpathy | complete; incomplete usage | 8/8 | ≥ 10,542,511 | ≥ 1,317,813.88 |
| real_swe | Karpathy + SoL-Pi | latest frozen SoL-Pi | complete; incomplete usage | 4/8 | ≥ 9,584,170 | ≥ 2,396,042.50 |

Latest frozen SoL-Pi is the2584-byte revision; original is the6573-byte bundle. Original calibration is a separate later single round and cannot establish repeated comparative superiority. Historical experiments above use different task sets/CLI versions and are not pooled with this campaign. The candidate is explicitly rejected, not the shipped latest version.

On development, latest solved9/10 versus baseline8/10 and reduced aggregate tokens per solve6.76%, while increasing total traffic4.89%. The advantage reversed direction across rounds and its exploratory task-cluster interval versus baseline crossed zero. Omitting the interface task makes both8/8 and latest2.63% more expensive. The extra solve drives the apparent gain; no case was removed from the primary result.

The sole experimental candidate added explicit shared-helper contract verification and bounded rejected-read recovery. It passed structural validation but failed the preregistered development quality gate:8/10 versus latest9/10, a newly failing matched interface cell, and20.45% higher tokens per solve. Both candidate interface attempts failed. It was rejected before held-out feedback; canonical latest remained unchanged. See [candidate decision](eval/pruned/candidate-decision.json).

Held-out latest solved14/15 versus baseline13/15, Karpathy12/15 and combined14/15. Latest cost18.87% more per solve than baseline in aggregate and was more expensive in every round. Its point estimates were9.00% cheaper than Karpathy and4.46% cheaper than combined, but both advantages reversed in round73. All three latest comparison intervals include zero. All60 diagnostic validation runs have complete accounting and no timeouts. Latest used more total tokens than baseline in every family; only interfaces changed correctness. Every configuration passed the other four families, where baseline had the fewest tokens. See [family breakdown](eval/pruned/results/heldout-by-family.md).

Repository correctness is6/8 baseline,7/8 latest,8/8 Karpathy and4/8 combined. Round42 scores were2/4,3/4,4/4,2/4; round73 scores4/4,4/4,4/4,2/4. Model timeouts were2/2/1/3 respectively. Latest also stopped at the turn limit on Pylint73 while producing a passing patch. The32 outcomes comprise29 official reports and3 valid empty-patch failures, with zero grading infrastructure errors and no retries. Timeout outcomes and functional failures remain included. A passing final patch does not imply timely model completion.

Public network access was permitted. Pylint passing attempts retrieved upstream repair-reference material through shell calls, including versioned source/tests or repair history/diffs. Both passing Django42 arms retrieved repair commit diffs; all Django73 arms passed after upstream repaired-source exposure, with baseline/latest also retrieving tests and Karpathy retrieving the task-relevant repair diff. Latest Astropy42 retrieved the exact target PR13033 diff and upstream tests. Other Astropy passes include upstream-source/test exposure; combined Astropy73 failed its required-column repair test with all20 regression tests passing. No full gold-patch/final-patch identity claim is needed to recognize returned repair-reference exposure. These official scoring facts cannot establish unaided skill superiority. Audits cover Bash/Python/Web retrieval and subsequent local history/diff/source reads, distinguishing successful content from failed calls.

All eight Sympy attempts passed. No external repair retrieval was found in any of the eight audited traces. Round73 complete token totals are baseline399,107, latest945,727, Karpathy267,395 and combined574,643. Latest took953.3seconds versus baseline269.6 and Karpathy455.7; combined997.1. Latest's trace used36 tool calls versus baseline17, including temporary verification/debug scripts, structural-equality debugging, repeated direct/suite/doctest checks and isolated memory writes. Both faced malformed-tool JSON and absent pytest. This describes an expensive path without proving which skill instruction caused it.

The useful configuration-level signal for latest is interface correctness and better diagnostic point estimates than Karpathy/combined. Baseline is the stronger economy result on these held-out diagnostics. Karpathy is strongest on repository grades, qualified by repair retrieval and incomplete aggregate cost. Combined adds no held-out correctness advantage over latest, costs more there, and has the lowest repository score with the most model timeouts. Optional helpers/supporting references were not used in any held-out diagnostic run, and none compacted; their effectiveness is unmeasured. Portable instructions also do not implement upstream Pi's native context packing or compaction.

Held-out traces record151/180/172/188 model requests and71/85/81/93 tool-validation errors for baseline/latest/Karpathy/combined. Latest instructions were exposed in all15 runs; combined launched efficient-coding in all15, but required47 Skill attempts with17 validation errors versus latest17 attempts with3 errors. No helpers or supporting references were attempted. The stale-continuation round73 latest path used20 requests versus baseline8, with all arms passing. These observations support investigating interaction overhead, but do not constitute causal ablation or justify tuning against held-out outcomes.

The desired efficient, economical and stable majority win is not established. No further outcome-selected benchmark search or held-out-driven revision was applied. The evidence-supported development candidate was tested and rejected; the existing simplified revision is retained without a new superiority claim. Final independent verification passed all147 cells with no provenance errors: full frozen pins, activated skill sets, CLI and archived runners, grades, usage, tool traces and backend configuration were checked. The execution queue exited and the model lock is free. See [final independent audit](eval/pruned/audit/independent-final147-audit.json). Evidence and interim audit detail are retained in [checkpoint history](eval/pruned/results/pruned-checkpoint-history.md), the frozen [plan](eval/pruned/plan.v4-real-swe.json), [comparison CSV](eval/pruned/results/comparison.csv), and [completion requirements](eval/pruned/audit/completion-requirements.md).

## Random-small follow-up (2026-10-03)

A separate frozen campaign sampled two new issues with seed20261003: Django11964 and SymPy12481. The draw used13 metadata-labelled `<15 min fix` tasks from33 eligible pre-pulled issues, excluded all16 previous exposures, and required distinct repositories. This is conditional random sampling, not a uniform sample of all SWE-bench Verified. Both prospective gold grader preflights passed with clean exact base commits and preserved environments. No selection changes, actor retries, skill revisions or backend changes were applied.

All16 attempts completed: two issues × four configurations × two schedule rounds42/73. Qwen3.8-27B-FP8/SGLang and Claude Code2.1.286, medium effort,60 turns and1800-second limits remain identical to the prior pruned campaign. The queue exited and model lock is free.

| Configuration | Verified solves | Tokens / solve | Model timeouts |
|---|---:|---:|---:|
| No skill | 3/4 | ≥2,009,397 | 1 |
| Latest SoL-Pi (ours) | 4/4 | 1,063,019 | 0 |
| Karpathy | 3/4 | ≥1,795,306 | 1 |
| Both skills | 4/4 | 1,476,167 | 0 |

Every configuration solved both SymPy attempts. Ours and both skills solved both Django attempts; baseline and Karpathy failed Django42 after model timeouts. Fifteen outcomes have official reports; baseline Django42 is a valid empty-patch failure. Failed attempts remain in token totals. Baseline and Karpathy each have one incomplete timeout accounting record; their values are lower bounds and no exact percentage savings against them is supported. Ours and both skills have complete query-pipeline usage; ours uses27.99% fewer tokens per solve than both with the same observed correctness. This is a descriptive result on two task clusters, not a population-level or causal savings claim. Ours has the lowest recorded tokens per solve in each round; do not pool this campaign with the earlier task sets.

Successful reference exposure was present. Ours Django42, baseline Django73 and both-skills Django73 fetched Django's task-relevant `dbcd7b064e` source/test repair diff. Both-skills SymPy42 fetched exact PR12481 source/test diffs; baseline SymPy42, Karpathy SymPy73 and both-skills SymPy73 retrieved current repaired source/tests. Ours SymPy42 WebSearch returned model-generated guidance rather than verified web results. Failed WebFetch500, missing tool returns and synthetic WebSearch outputs are distinguished from actual successful shell downloads. Karpathy Django73 fetches failed. Ours Django73 and SymPy73 had no external retrieval attempts. These traces qualify unaided-repair attribution and cannot establish that particular skill instructions caused improvements.

Detailed results: [per-task tables](eval/random-followup/results/summary.md), [collection](eval/random-followup/results/collection.json), [standalone verification](eval/random-followup/audit/root-verification.json), and [selection/prelaunch audit](eval/random-followup/audit/independent-prelaunch.json). The independent audit agent completed the final16-cell review after its session recovered: all148 pins, full activated skill sets, CLI, clean bases, image/backend configuration, dataset, predictions, grades, accounting and all tool/retrieval traces passed with no provenance errors. See [final independent audit](eval/random-followup/audit/independent-final16.json).
