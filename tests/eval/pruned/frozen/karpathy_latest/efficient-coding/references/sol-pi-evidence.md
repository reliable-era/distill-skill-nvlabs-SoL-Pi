# SoL-Pi: evidence and implementation notes

Read this reference when explaining the source of these rules, choosing harness
mechanisms, or evaluating a claimed saving. Keep it out of ordinary small-fix
context. Coding and scheduling recommendations in this bundle are adaptations;
they have not inherited the paper's measured improvements.

Contents: [Paper digest](#paper-digest), [Code cross-check](#code-cross-check),
[Cost interpretation](#cost-interpretation), [Transfer boundaries](#transfer-boundaries),
[Sources](#sources).

## Paper digest

Page locators use the 15-page arXiv v1 PDF. `FOUND` means present in the source,
not independently reproduced. `inferred` identifies reconstructed research
questions. Results below are author-reported point estimates.

### N0 Metadata

Status: FOUND. Source: extracted, p.1, title and abstract region.

- Title: *SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness*.
- Authors: Haozhe Liu, Tian Ye, Sensen Gao, Qihang Cao, Yitong Li, Mingchen Zhuge,
  Duomin Wang, Ruihua Zhang, Ping Luo, Jiawang Bian, Lei Zhu, Ligeng Zhu,
  Enze Xie, Song Han.
- arXiv: 2609.20519v1, submitted September 17, 2026; manuscript header August 17,
  2026. Pages: 15. Research area: AI/ML. DOI: not stated in the PDF.

Abstract (verbatim from the supplied PDF, p.1):

> As coding agents move from supervised code completion to unattended, around-the-clock exploration, their work expands from isolated predictions into long trajectories of reasoning, tool use, and feedback. Token efficiency therefore becomes important for scaling recursive self-improvement. We take an RSI-inspired approach at the harness layer, scaling auto-research loops across increasingly numerous and diverse environments for harness rollouts. At this scale, the process yields reusable improvements that transfer beyond their development setting, moving automated harness discovery toward production-level outcomes. Four mechanisms survive selection and form SoL-Pi, spanning action execution, context compaction, observation handling, and delegated reading. On the 51-task EdgeBench evaluation, SoL-Pi achieves performance comparable to Pi across GPT-5.6 Sol and Opus 5 while reducing recorded token traffic by 44.7–49.0% and API cost by about one third. In other words, estimated hourly savings are $8.75–$13.50 relative to native Codex and Claude Code harnesses, and $4.36–$5.71 relative to Pi.

### N1 Problem formulation

Status: PARTIAL. Source: extracted, pp.2–3, §2.1.

Objective: discover reusable coding-agent harness changes that reduce declared
execution costs across development environments while keeping every capability
metric within a fixed tolerance, then evaluate frozen candidates on unseen work.
Inputs: base harness, development tasks and traces, fixed acceptance metrics.
Outputs: accepted mechanisms and a combined harness. Constraints: fixed underlying
model during search, protected acceptance criteria, isolated final evaluation.

Absence comment — What missing: Numerical capability tolerances and a complete
executable selection contract are not specified in the main text. Why matters:
The permitted capability loss cannot be reconstructed solely from the prose.
Implication: Do not equate passing their gates with zero performance loss.

### N2 Motivation

Status: FOUND. Source: extracted, p.2, §1.

- Long-horizon autonomous work makes task-level token efficiency consequential
  for scaling execution and recursive improvement.
- Optimizing interaction between a fixed model and its environment complements
  cheaper models and inference infrastructure without requiring weight training.
- Human inspection and repair of long harness traces is expensive to scale.

### N3 Related works

Status: FOUND. Source: extracted, pp.11–12, §§4.1–4.3. Citation markers match
the paper; this describes the authors' discussion, not independent novelty audits.

| citation_key | approach_summary |
| --- | --- |
| [2], SWE-agent | Studies agent-computer interfaces for repository engineering. |
| [17], Meta-Harness | Searches executable harness programs with a frontier over quality and context cost. |
| [19], RHI | Refines prompt-level agent-loop specifications for individual tasks. |
| [42], GEPA | Uses reflective trajectory feedback to optimize prompts. |
| [50], AgentDiet | Removes redundant/outdated trajectory content. |
| [51], ACON | Optimizes observation/history compression. |
| [20], Wang et al. | Evaluates evolved harnesses on held-out tasks and reports limited transfer for evaluated methods. |

### N4 Prior limitations

Status: FOUND. Source: extracted, p.2 §1 and p.11 §4.2.

- Existing efficiency work primarily targets per-token infrastructure/model
  cost; affects_works: [] (a broad framing, not a specific limitation of an N3
  entry).
- Evolved harnesses may overfit development tasks and show marginal held-out
  gains; affects_works: [[20]].

Grounding check: false; the first framing is not linked to a particular N3 work.

### N5 Challenges

Status: FOUND. Source: extracted. Conflation check: true.

- C1: Coupled tool use, context, verification, recovery, and termination can turn
  local savings into downstream failures or deferred costs (p.2, §1).
- C2: Generalizing discovered harness artifacts remains difficult (p.12, §5.1,
  “Pre-Training the Harness”).

### N6 Methodology

Status: FOUND. Source: extracted, pp.3–6, §§2.2–2.5.

Overview: A broad-to-deep search proposes mechanisms from execution traces,
implements and reviews isolated candidates, tests capability then efficiency,
combines retained candidates, and freezes the result before independent evaluation.

- M1 Action Fusion: mutation plus predefined follow-up command, eliminating
  an intermediate model round trip (p.4, §2.4).
- M2 Online Context Compact: evaluate native compaction at plan boundaries using
  projected savings and cache-rewrite cost (pp.4–5, §§2.4–2.5).
- M3 ObservationPack: archive large observations, initially retain full results,
  then substitute handles with exact paged recall (p.4, §2.4).
- M4 Evidence-Preserving Reducer: cheaper-model evidence extraction, deterministic
  provenance/status/size checks, and fallback to original logs (p.5, §2.4).
- M5 Search and validation funnel: 152 directions in six proposal families,
  535 environments (495 repository tasks, 40 verifier tasks), isolated search,
  independent review, fixed gates, and one-way held-out acceptance (pp.3–4 §2.2,
  p.6 §2.5).

Challenge arguments: C1 ← [M1, M2, M3, M4], complementary points in the workflow
reduce repeated work while preserving needed evidence (p.5, §2.4). C2 ← [M5],
diverse discovery and held-out isolation target transferable improvements (p.3,
§2.2; p.11, §4.2). Unaddressed challenges: [C2]; the authors acknowledge that
generalization remains persistent and evidence is preliminary (p.12, §5.1).

### N7 Contributions

Status: FOUND. Source: extracted, p.2 §1, pp.4–5 §2.4, p.12 §5.

- CO1 [conceptual_framework, testable=true, has_rq=true]: isolated broad-to-deep
  auto-research for reusable harness efficiency changes.
- CO2 [technical_artifact, testable=true, has_rq=true]: four retained extensions
  combined into SoL-Pi.
- CO3 [empirical_finding, testable=true, has_rq=true]: cost/traffic gains across
  evaluated tasks and backends, plus one swarm experiment.

### N8 Research questions

Status: PARTIAL. Source: inferred from evaluation headings, pp.6–10, §3.
The paper does not explicitly number RQs.

Absence comment — What missing: An explicit author-defined RQ list. Why matters:
The mapping below reconstructs evaluation intent and is not a quotation of the
paper's research questions. Implication: Use the `RQ_INF` labels as analytical
navigation, not as claims about the authors' stated RQs.

- RQ_INF_1: How does the full stack compare with baseline/native harnesses in
  cost and score? evaluates [M1–M4], addresses [C1], tests [CO2, CO3]; §3.1–3.2.
- RQ_INF_2: Do mechanisms transfer to another backend and task families?
  evaluates [M1–M5], addresses [C2], tests [CO1, CO3]; §3.1–3.3.
- RQ_INF_3: What do individual mechanisms and activation patterns explain?
  evaluates [M1–M4], addresses [C1], tests [CO2, CO3]; §3.4.
- RQ_INF_4: What does the Action Fusion lineage show about discovery?
  evaluates [M1, M5], addresses [C1, C2], tests [CO1]; §3.5.

Datasets: EdgeBench public 51-task set, Terminal-Bench 4 CPU-only 63 tasks,
IMO 2026 six Lean-verified problems, kernel optimization. Baselines: Pi, Codex,
Claude Code, other listed third-party harnesses, add-one variants. Metrics:
recorded token categories, API cost, aggregate score, solved tasks, cost per
solved task/score, verified cycles, trigger rates/intensities. Sources: pp.6–10.

### N9 Results

Status: FOUND. Source: extracted. Quantitative evidence strength: moderate;
reported comparisons have no accompanying significance tests in these sections.

| Result / rq_id | Baseline Pi | Full SoL-Pi | Evidence |
| --- | ---: | ---: | --- |
| GPT-5.6 Sol token traffic / RQ_INF_1 | 2.1538 B | 1.0990 B | p.6, Table 1 |
| GPT-5.6 Sol API cost / RQ_INF_1 | $1,339 | $894 | p.6, Table 1 |
| GPT-5.6 Sol average score / RQ_INF_1 | 44.833 | 42.003 | p.6, Table 1 |
| Opus 5 token traffic / RQ_INF_2 | 2.3697 B | 1.3101 B | p.7, Table 2 |
| Opus 5 API cost / RQ_INF_2 | $1,741 | $1,158 | p.7, Table 2 |
| Opus 5 average score / RQ_INF_2 | 44.756 | 42.224 | p.7, Table 2 |
| Terminal-Bench solved / RQ_INF_2 | 18/63 | 15/63 | p.7, Table 3 |
| Terminal-Bench cost per solved / RQ_INF_2 | $15.91 | $14.07 | p.7, Table 3 |
| IMO passed / RQ_INF_2 | 3/6 | 3/6 | p.7, Table 3 |

RQ_INF_1 is partially answered: measured savings accompany score losses.
RQ_INF_2 is partially answered: one held-out backend and limited task sets do
not establish universal transfer. RQ_INF_3 is partially answered: add-one
ablations support individual effects, while differing triggered-task subsets
do not isolate causal interactions. RQ_INF_4 is partially answered: one lineage
case study illustrates the search without proving its necessity or scaling law.

GPT-5.6 Sol's ObservationPack-only point costs $1,271 and scores 47.208;
Action Fusion-only costs $1,235 and scores 46.664 (p.9, Table 4). The largest
Sol standalone cost reduction is Online Context Compact ($935), with score
41.993. The efficiency/performance profiles are different configurations.

The swarm comparison uses one two-hour run each (pp.7–8, §3.3): single agent
1,333 cycles/$39.20; Pi swarm 1,366/$82.12; SoL-Pi swarm 1,127/$60.11. Lower
cycles are better. Cost falls 26.8% relative to the Pi swarm, but exceeds the
single-agent cost. All final candidates pass correctness checks.

RQ_INF_4's projected 11.5% token saving under full triggering is an opportunity
estimate, not the overall measured saving (pp.10–11, Fig.8 and §3.5).

### N10 Author-acknowledged threats

Status: FOUND. Source: extracted, p.12 §5.1 unless otherwise located.

- t1 [external]: Harness generalization remains a challenge; broader environment
  and idea exposure is proposed for future study.
- t2 [external]: Search uses one model backend; multi-backend development is
  proposed to improve robustness.
- t3 [conclusion]: Recursive compounding efficiency is a long-term vision,
  not demonstrated by this study.
- t4 [scope]: Controlled breadth/depth comparisons at a fixed search budget are
  computationally expensive and deferred.
- t5 [conclusion]: Triggered-task subset comparisons do not isolate mechanism
  interactions (p.8 §3.4, pp.9–10 Figs.6–7).
- t6 [scope]: GPU-dependent Terminal-Bench tasks are excluded due to infrastructure
  limits (p.7, Table 3 note).

### N11 Artifacts

Status: FOUND. Source: extracted, p.1, Code/Blog links.

- a1 [code_repo]: [NVlabs/SoL-Pi](https://github.com/NVlabs/SoL-Pi).
- a2 [other]: [Project blog](https://nvlabs.github.io/SoL-Pi/).

has_code=true; has_data=false; has_model=false. No separate dataset or model
artifact is identified by these links. The inspected release contains the four
extensions and tests, not the complete 535-environment discovery corpus or a
general swarm scheduler. The paper's full search has not been reproduced here.

### N12 Contribution type

Value: system. Source: inferred classification.
Rationale: The central contribution is an automated harness-discovery process
and combined four-mechanism harness, evaluated for task-level efficiency and
transfer. It is neither a new model-training algorithm nor a proven scaling law.

### Claims and evidence boundaries

- Roughly halved traffic and one-third cost reduction: Tables 1–2, pp.6–7,
  quantitative point estimates with lower full-stack scores.
- Transfer: Table 2 and §3.4, pp.7–9, preliminary evidence for one unseen backend.
- Swarm benefit: §3.3, pp.7–8, one run per configuration; no scheduling ablation.
- Complementarity: §3.4, pp.8–10, descriptive pattern, not isolated interactions.
- Recursive compounding improvement: §5.1, p.12, explicitly future work.

## Code cross-check

Inspected September 30, 2026, commit `1559b5cb12c72da4a485bc50fe326586b216fb19`.
Fetched 26 source/configuration files and inspected the core extension,
configuration, and compatibility paths through the GitHub connector.
This is source inspection; no upstream live-provider benchmark was rerun.

| Mechanism | Source under `src/sol-pi/` | Actual behavior |
| --- | --- | --- |
| Registration | `index.ts`, `config.ts` | Registers enabled features at session start; all default false. |
| Action Fusion | `extensions/action-fusion/index.ts`, `then-run.ts`, `file-queue.ts` | Adds optional `then_run` to public edit/write definitions; serializes fused operations on a resolved file; checks for observed content interference; retains the edit if the command fails. |
| ObservationPack | `extensions/observation-pack/index.ts`, `observation.ts` | Projects successful pure-text results larger than 10 KiB; retains full results for two requests, then a handle with up to 1 KiB whole-line head/tail excerpts. Original session history remains intact. |
| Recall | Same ObservationPack files | `obs_recall` uses byte offsets and next-offset/eof metadata, with output capped at 16 KiB/400 lines including headers; stored object integrity is checked on creation/reuse. |
| Evidence reducer | `extensions/evidence-preserving-reducer/index.ts`, `candidate.ts`, `receipt.ts`, `config.ts` | Targets allowlisted diagnostic commands and logs at least 4 KiB, retrieves permitted full bash artifacts when available, validates schema/hash/status/exact quotes, and falls back on failure or no reduction. |
| Online compaction | `extensions/online-context-compact/economics.ts`, `extension.ts`, `state.ts`, `tools.ts` | Plan-boundary economics, carried cache debt, native compaction, persistent state and automatic continuation after successful boundary compaction. |

Reducer receipts bypass ObservationPack to retain checked quotations. File reads
and searches bypass the reducer. The small model chooses evidence; the main
agent keeps diagnosis and acceptance. Quote validation cannot prove semantic
completeness. ObservationPack alone makes no auxiliary model calls.

Configuration is a single trusted project or user configuration, not a merge.
The standalone compaction ratio is user-configured; switching the main model
does not automatically reprice that ratio. Public Pi compatibility and session
continuation differ from the paper's discovery setup; distinguish release
defaults from experimental settings.

## Cost interpretation

Token traffic sums uncached input, cache read, cache write, and output; it is
not generated text alone. In Table 1, Pi's cached-read traffic is 2.1326 of
2.1538 billion tokens. Full SoL-Pi reduces cached reads to 1.0605 billion while
cache writes increase from 0.0141 to 0.0316 billion and output remains similar.
Shorter replay saves work even when cache reuse is imperfect. Monetary cost
must still use each category's price and count helper calls.

Illustration, not a paper measurement: a 20,000-token observation included in
20 requests contributes 400,000 replayed tokens. Keeping it twice and replacing
it with a hypothetical 300-token handle for 18 requests yields 45,400 tokens
before any recalls/cache effects. This is the main mechanism behind the idea;
it does not imply an 88.7% reduction in total task cost.

The paper fixes prices to August 17, 2026. Its full-stack scores retain 93.7%
and 94.3% of Pi's backend scores. Terminal-Bench solves fewer tasks despite
lower cost per solved task. A production zero-loss requirement needs its own
matched evaluation rather than accepting the headline percentages.

## Transfer boundaries

Borrow action sequencing, bounded observations, verified receipts, and cost-aware
continuation. Add contract ownership, ready-task dispatch, retry reassessment,
and integrated acceptance to address confused or partial multi-agent work.
These additions are engineering recommendations, not experimentally established
SoL-Pi innovations.

The strongest contribution is reusable harness optimization under capability
and efficiency checks with independent evaluation. Individual ideas have related
prior work; the paper alone does not justify claiming that batching, compression,
or small-model extraction is newly invented. Its research promise is improving
the cost/quality frontier of long-running systems; optimum agent count, learning
dispatch policies, and recursive compounding remain open.

## Sources

- [Paper v1](https://arxiv.org/pdf/2609.20519v1), read in full with PDF page locators.
- [Pinned repository](https://github.com/NVlabs/SoL-Pi/tree/1559b5cb12c72da4a485bc50fe326586b216fb19).
- [Configuration](https://github.com/NVlabs/SoL-Pi/blob/1559b5cb12c72da4a485bc50fe326586b216fb19/docs/configuration.md).
- [Compatibility](https://github.com/NVlabs/SoL-Pi/blob/1559b5cb12c72da4a485bc50fe326586b216fb19/docs/compatibility.md).
- [Karpathy packaging reference](https://github.com/multica-ai/andrej-karpathy-skills),
  inspected only as a concise coding-guideline/skill packaging example. No
  rules or implementation were copied into this bundle.
