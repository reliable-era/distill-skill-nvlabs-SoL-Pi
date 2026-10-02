### Pruned campaign: diagnostics complete; real repository evaluation ongoing

Cost accounting uses the latest terminal `modelUsage` totals, as specified by the pinned CLI: these include the main loop and auxiliary query-pipeline calls. Main-loop `usage` is preserved separately and never added to those cumulative totals. This reconciles differences of 195 tokens (Django latest), 172 (Django Karpathy), and 670 (Astropy combined). These are reported estimates, not billing measurements; calls outside the query pipeline are excluded by the CLI. Runs without terminal accounting remain incomplete lower bounds.

The real-repository runs permit public network access. In the first Pylint comparison, Karpathy retrieved upstream versioned source through Bash and compared it with the checkout; the combined arm also retrieved source, commit histories and specific commit patches. This limits claims of unaided problem solving. Official grades remain scoring facts, and all scheduled runs remain included. The independent audit is checking returned external content across shell and web tools. In Django round 42, both passing arms (Latest SoL-Pi and Karpathy) retrieved upstream commit diffs through Bash; baseline and the combined arm had no external retrieval attempts detected. Retrieved repair-reference exposure is established, while exact identity with the full frozen gold patch is not demonstrated. Their quality advantage therefore cannot be attributed solely to unaided use of the skill. In Astropy round 42, baseline and Karpathy retrieved current upstream source through Bash. Latest SoL-Pi additionally retrieved upstream tests and the exact target PR 13033 diff; full gold-patch or final-patch identity was not established. The combined arm had failed WebFetch attempts but no successful shell source retrieval detected. All four passed, so this case also requires an external-reference qualification. In round 73, the combined configuration failed Astropy’s `test_required_columns` while all 20 pass-to-pass tests succeeded. The official grader exited normally; this is a functional failure retained in the comparison, not an infrastructure failure. Baseline, Latest SoL-Pi, and Karpathy passed Astropy in both rounds. In round 73, baseline retrieved upstream source, latest retrieved current and versioned source, and Karpathy retrieved source plus upstream tests; the combined configuration had no network attempts detected. The independent 20-run audit found no provenance or accounting errors.


The prospectively frozen subset covers five synthetic diagnostic presentations
(large log, producer/consumer interfaces, stale continuation, integration repair,
and a small-fix control). Each has a distinct related held-out variant. Four
unexposed SWE-bench Verified issues were selected from metadata with selection
seed42: pylint-4551, django-13195, astropy-13033, sympy-19637. They span four
repositories and human difficulty strata. No task was selected from arm outcomes.

Backend: Qwen3.8-27B-FP8 through local SGLang; pinned Claude Code2.1.286,
medium effort, 60-turn and1800-second limits, fresh containers/HOME, identical
skill-loading hint. Model calls are sequential. Round labels42/73/101 randomize
scheduling; they do not control backend sampling RNG. Five tasks ×two development
rounds ×four main arms=40 runs; original calibration adds5; one candidate adds10.
Held-out diagnostics are five tasks ×three rounds ×four arms=60 planned runs.
SWE is four tasks ×two rounds ×four arms=32 planned runs. Total planned147.

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

Development findings: latest solves9/10 versus baseline8/10 and has6.76% lower
aggregate tokens per verified solve, while using4.89% more total traffic. Its
baseline comparison fails consistent round direction: cheaper in round42,
costlier in round73. The task-cluster95% interval for its cost-per-solve
difference versus baseline is[-204,419,+15,421]. No newly failing matched cells
occur versus baseline, but the extra solve appears only in round42. Only the
Karpathy comparison narrowly excludes zero in the exploratory cost bootstrap.
These are development observations, not held-out validation or quality equivalence.

Development sensitivity: systematically omitting each of the five tasks once preserves the latest bundle's single extra solve in four omissions. Omitting the interface task makes latest and baseline both8/8, with latest2.63% more tokens per solve. The development efficiency advantage therefore depends on the extra interface solve. The primary comparison retains all five tasks; this sensitivity does not justify excluding a case or tuning against held-out outcomes. See `audit/dev-leave-one-task-out.json`.

Mechanism evidence from all40 development traces: latest successfully loads the efficient-coding skill in10/10 runs. Deduplicated model requests are110 for baseline,112 for latest,110 for Karpathy, and126 for the combined bundle. Tool-validation errors occur in all four arms (51/49/50/55), so their presence is not unique to the skill. No development run calls a helper script or emits a compaction event; the combined arm attempts one brief reference read. These are observations, not causal component ablations. Installed helper resources and upstream native runtime features cannot explain savings when their execution is absent from these traces.

A completed held-out execution illustrates cost variability: on the second-round stale-continuation case, latest uses20 deduplicated requests and11 tool-validation errors versus baseline's8 requests and6 errors. All four arms pass. Neither latest nor baseline calls helpers, compacts, or produces a tool result above10KiB in the serialized-size proxy. This describes extra requests in one observed path; it does not identify a causal instruction or justify tuning on the held-out result. See `audit/heldout-d3-r73-mechanism.json`.

Original calibration is one later round:5/5,221,166.4 tokens per solve, only0.34%
above latest's first-round220,425. It does not reproduce the earlier pilot's larger
revision gain and is not interleaved with the main development matrix.

The sole candidate changed rejected-read recovery and explicit shared-helper
contract verification. It passes skill structural validation but fails the
predeclared performance gate:8/10 versus latest9/10, a newly failing matched
interface case, and20.45% higher cost per solve. Both candidate interface attempts
fail; its maximum single-run cost is561,171 tokens. Candidate development occurred
in a subsequent sequential batch. It is rejected before any held-out feedback,
excluded from held-out evaluation, and not shipped. Canonical latest remains unchanged.

Interpretation limits: d1 and d5 share ceiling division, a controlled presentation
contrast rather than independent algorithmic abilities. The log prompt names the
defect, so functional success alone cannot establish log investigation. Fixtures
are tiny synthetic Python repositories, and related held-out variants share
structure and some helper code. A blind static review notes mild implicit Unicode
normalization wording in d2 and imprecise 'retain' wording for initially incorrect
empty-name behavior in d4. Preserve all frozen cases; disclose these limits rather
than change grading after outcomes. Process claims require separate trace evidence.
Four prospectively unexposed SWE issues provide separate repository validation;
execution is ongoing, and subsequent public retrieval must be qualified. The small sample cannot establish broad statistical noninferiority.

Economy measures provider-reported input plus output tokens across all matched
attempts, including failures, divided by independent verified solves. It is not
billed dollars or GPU energy. Prefix caching/shared throughput can affect wall
time without changing reported input traffic. Missing grades remain explicit.
No supporting-resource effectiveness claim follows from files merely being installed.
The portable skill cannot implement upstream Pi context packing or native compaction.

Official swebench4.1 gold preflight passes all four selected tasks. Official data
matches local pinned records; isolated Astropy grading with the frozen localJSONL
also passes. Prepared SWE runner corrections restore and verify the requested
base commit before each agent, avoiding Astropy's incidental image setup pin.
They were validated in disposable images with the same installed Python environment
and installed through the archived, audited transition after held-out diagnostics
and before the SWE stage. Completed diagnostic runs retain their historical runner
provenance.

Evidence: `eval/pruned/plan.v3-heldout.json`, `preregistration.txt`,
`candidate-decision.json`, `results/comparison.csv`, `audit/dev-complete.json`,
`audit/independent-candidate-complete.v3.json`, `audit/fixture-validity-review.txt`,
`audit/grader-preflight/summary.json`, `audit/grader-preflight-local/summary.json`,
and `next-runners/pristine-audit.json` (all under `eval/pruned/`).


Held-out diagnostics are complete (60 runs, three scheduling rounds). Latest SoL-Pi solved 14/15 versus baseline 13/15, Karpathy 12/15, and Karpathy plus latest SoL-Pi 14/15. Its tokens per solve were 259,838.79, versus baseline 218,599.31 (+18.87%), Karpathy 285,543.33 (−9.00%), and the combined bundle 271,959.50 (−4.46%). Latest was more expensive than baseline in every round; its advantage over Karpathy and the combined bundle reversed in round 73. All three paired task-cluster intervals for latest include zero, so these data do not establish a stable majority win. All 60 runs have verified grades, complete activated-file hashes, reconciled terminal usage, and no model or grader timeouts. Failed attempts remain in the cost totals.

The approved runner transition archived the historical runners and froze plan.v4-real-swe.json. The real repository stage has started: four metadata-selected issues, four configurations, and two scheduling rounds (32 runs). These results remain pending. Each agent starts from the exact task base commit with a clean checkout, and official grading uses the pinned local dataset.


Full held-out trace audit (`eval/pruned/audit/heldout60-mechanism.json`) records 151/180/172/188 model requests for baseline/latest/Karpathy/combined, respectively, and 71/85/81/93 tool validation error tags. Latest instructions were exposed in all 15 runs (14 explicit successful Skill launches and one verified direct read); the combined configuration launched efficient-coding successfully in all 15. Its 47 Skill attempts included 17 validation errors, versus latest’s 17 attempts and three errors. No configuration attempted the optional helpers or supporting references, and none compacted. These are descriptive counts, not causal component ablations or proof that any instruction caused the extra requests. They support treating helper effectiveness as unmeasured and checking interaction overhead before expanding the bundle.


The first real repository cell (latest SoL-Pi, Pylint, round 42) timed out at the fixed 1800-second model limit and produced an empty patch. The official harness classified that as unresolved without a grading infrastructure failure. Its 27 unique assistant request IDs report 762,427 input tokens and explicit zero output tokens despite generated text; there is no terminal usage summary. This recorded cost is a lower bound, not complete usage. The collector retains the failed attempt and marks fallback usage incomplete; comparisons involving such cells cannot pass the supported-efficiency or adoption screens. Affected table costs use ≥. No output-token estimate is substituted.

The [held-out family breakdown](eval/pruned/results/heldout-by-family.md) shows that latest uses more total tokens than baseline in every diagnostic family. Only the interface family changes correctness; on the other four families every configuration passes all three rounds and baseline uses the fewest tokens. This configuration-level evidence does not establish a causal instruction-level effect.

Repository execution has reached21/32 graded runs. The additional combined Pylint round73 attempt timed out at1800seconds, produced a2983-byte patch, and failed the official grader (normal exit0). Its2,628,282 recorded tokens are an incomplete lower bound. The unified table retains the20 completed matched cells until all four arms finish this task-round.

Independent21-cell verification found no provenance errors. The combined Pylint73 patch failed pytest collection because `get_annotation` was absent from `pylint.pyreverse.utils`; the official report consequently records zero of ten fail-to-pass tests passing. This is incomplete functional repair, not grading infrastructure failure. No shell/Python/Web network retrieval, Agent calls, or final test modifications were detected in this run. Its stream fallback reports49 deduplicated message IDs and2,628,282 input tokens; zero reported output-token fields do not mean zero generated output. See `eval/pruned/audit/independent-swe21-pylint73-supplement.json`.

Repository execution is now22/32 graded: Karpathy also passed Pylint round73 with normal model completion at1514.5seconds and complete reported query-pipeline usage of2,714,274 tokens. Baseline and latest remain pending on that task-round, so matched aggregates stay unchanged. Independent22-cell verification found no provenance errors, but confirms that Karpathy cloned upstream Pylint and read the task-linked repair commit `1e55ae64624d28c5fe8b63ad7979880ee2e6ef3f`, including source and test diffs. All10 official fail-to-pass tests passed. Exact frozen gold/test-patch identity and final-patch equality were not established. Temporary regression fixtures were created and removed; no final tracked test modifications or Agent calls were found. Terminal query-pipeline usage reconciles to2,714,274 tokens (main2,714,046 plus auxiliary228). This pass cannot establish unaided skill superiority. See `eval/pruned/audit/independent-swe22-pylint73-supplement.json`.

Repository execution has reached23/32 graded runs. Baseline passed Pylint round73 after725seconds with complete reported query-pipeline usage of1,952,281 tokens; independent23-cell verification found no provenance errors. Baseline retrieved the task-linked upstream repair commit `1e55ae6462` through GitHub API calls, including source and test patches, then ran and removed a temporary upstream-derived verification fixture. All10 official fail-to-pass tests passed; no final tracked test modifications or Agent calls remained. Terminal usage reconciles to1,952,281 tokens (main1,951,436 plus auxiliary845). This pass, like Karpathy’s, cannot establish unaided configuration superiority. See `eval/pruned/audit/independent-swe23-pylint73-supplement.json`. Latest is the remaining arm for this task-round, so the matched table still covers20 cells.

Repository evaluation now has24/32 graded runs and six matched task-rounds per configuration. Latest passed Pylint round73 despite stopping at the60-turn limit (`error_max_turns`, model exit1); official grading exited0 and passed. Its terminal accounting is complete at2,723,101 tokens. Current matched scores are baseline4/6, latest5/6, Karpathy6/6, combined2/6. Aggregate token totals remain lower bounds because round42 Pylint timed out in every arm and combined also timed out in round73. Eight repository runs remain. Independent24-cell verification found no provenance errors and confirmed all10 official fail-to-pass tests passed for latest. Its10 Bash network calls retrieved upstream versioned source and three test files, and local diffs exposed repair-relevant changes; its WebFetch failed500. No targeted commit clone/show or exact gold identity was established. Temporary upstream-derived tests were used, with no final tracked test modifications or Agent calls. Thus all three passing Pylint round73 configurations retrieved upstream repair-reference material; this task-round does not establish unaided skill superiority. The backward24-cell history scan covers local history/diff reads as well as network tools. See `eval/pruned/audit/independent-swe24-pylint73-supplement.json` and `eval/pruned/audit/independent-swe24-history-scan.json`.

Repository execution is now25/32 graded. Baseline passed Django round73 despite its1800-second model timeout, with a2728-byte patch and normal official grader exit0. Its2,418,791 recorded tokens are an incomplete lower bound; the terminal usage summary is absent. The matched table remains24 cells until the other three Django round73 configurations finish. Independent25-cell verification found no provenance errors and confirmed5 repair tests and382 regression tests passed. Baseline retrieved later upstream response/messages/session source and tests, and GitHub API history identified task-relevant commit `240cbb63bf99`. No returned direct repair-commit diff or local clone/show/history command was detected. This establishes upstream repaired source/test exposure, without exact gold identity. No temporary or final test writes or Agent calls were found. The48-message fallback has no terminal summary; zero reported output fields do not mean zero generated output. See `eval/pruned/audit/independent-swe25-django73-supplement.json`. Seven runs remain.

Repository execution has reached26/32 graded runs. Combined Karpathy + latest SoL-Pi passed Django round73 after its1800-second model timeout, with a3647-byte patch and official grader exit0. The recorded1,545,943 tokens are an incomplete lower bound, not a complete estimate. Independent26-cell verification found no provenance errors and confirmed5 repair tests and382 regression tests passed. Combined retrieved Django3.2 response/messages/session source and API documentation through four Bash calls; three WebFetch calls failed500. No returned upstream test or target commit diff was observed; local history reads stayed on the base checkout. No temporary/final test-write attempts or Agent calls were found. The42-message fallback lacks a terminal summary, and zero output fields do not mean zero actual output. See `eval/pruned/audit/independent-swe26-django73-supplement.json`. Latest and Karpathy remain on this task-round, so matched aggregates still cover24 cells. Six repository runs remain.

Repository execution has reached27/32 graded runs. Latest SoL-Pi passed Django round73 with a2662-byte patch despite its1800-second model timeout. The37-message fallback records1,763,908 tokens as an incomplete lower bound; official grading exited normally and resolved the issue. Independent27-cell verification found no provenance errors and confirmed5 repair tests and382 regression tests passed. Eight Bash network calls returned Django3.2 response/messages/session source and upstream tests plus release documentation; failed web calls were distinguished from successful content. No target commit diff or local fetched-history pathway was observed. No temporary/final test-write attempts or Agent calls were found. This pass therefore includes upstream repaired source/test exposure. The37-message terminal-less fallback remains an incomplete lower bound; zero output fields do not mean zero actual generated output. See `eval/pruned/audit/independent-swe27-django73-supplement.json`. Karpathy remains on this task-round; matched aggregates still cover24 cells, with five repository runs pending overall.

Repository execution has reached28/32 graded runs, completing seven matched task-rounds per configuration. Karpathy passed Django round73 with normal model completion at1727.4seconds, patch4947bytes and complete reported usage1,912,895 tokens. All four Django round73 configurations passed. The table now includes that matched task-round: baseline5/7, latest6/7, Karpathy7/7, combined3/7. Aggregate costs remain lower bounds and cannot establish savings; incomplete usage counts are2/2/1/3 respectively. Independent28-cell verification found no provenance errors and confirmed all5 repair tests and382 regression tests passed for Karpathy. Terminal query-pipeline usage reconciles to1,912,895 (main1,912,682 plus auxiliary213). Karpathy retrieved stable3.2 upstream source/tests and the task-relevant repair commit `240cbb63bf9965c63d7a3cc9032f91410f414d46` as a returned8468-character GitHub API diff. Wrong-SHA fetch failures were distinguished from successful retrieval. Local history reads stayed on the base checkout; no clone/local fetched-history pathway, temporary/final test-write attempts or Agent calls were found. This result includes returned repair-diff exposure and cannot establish unaided skill superiority. See `eval/pruned/audit/independent-swe28-django73-supplement.json`. The four final Sympy round73 cells remain.

Repository execution has reached29/32 graded runs. Baseline passed Sympy round73 with normal model completion at269.6seconds, patch417bytes and complete reported usage399,107tokens. Independent29-cell verification found no provenance errors and confirmed1 repair test and40 regression tests passed. The single terminal modelUsage reconciles to399,107 (main399,107, auxiliary0). No network/Web/local upstream-history/downloaded-read evidence, temporary/final test-write attempts or Agent calls were found. See `eval/pruned/audit/independent-swe29-sympy73-supplement.json`. Matched aggregates remain28 cells until the remaining three Sympy configurations finish.

Repository execution has reached30/32 graded runs. Latest SoL-Pi passed Sympy round73 with normal model completion at953.3seconds, patch417bytes and complete reported usage945,727tokens (33 requests), versus baseline269.6seconds and399,107tokens (14 requests). Independent30-cell verification found no provenance errors and confirmed1 repair test and40 regression tests passed for latest. The single terminal usage reconciles to945,727 (main same, auxiliary0). Neither baseline nor latest retrieved upstream source or history; both final patches contain only sympify.py. Latest made36 tool calls versus baseline17, including temporary verification/debug scripts, structural-expression equality debugging, repeated direct/suite/doctest checks and isolated-run memory writes. These are descriptive differences, not causal evidence against an individual instruction. See `eval/pruned/audit/independent-swe30-sympy73-supplement.json`. The final Karpathy and combined Sympy cells remain; matched aggregates still cover28 cells.

Repository execution has reached31/32 graded runs. Karpathy passed Sympy round73 with normal model completion at455.7seconds, patch417bytes and complete reported usage267,395tokens (12 requests). Independent31-cell verification found no provenance errors and confirmed1 repair test and40 regression tests passed. The single terminal accounting reconciles to267,395 (main same, auxiliary0). No network/Web/local upstream-history evidence, temporary/final test-write attempts, tracked test changes or Agent calls were found. See `eval/pruned/audit/independent-swe31-sympy73-supplement.json`. The combined Sympy cell is the final scheduled run; matched aggregates still cover28 cells until it completes.

All147 planned cells are now graded (115 diagnostics and32 repository attempts). Final combined Sympy round73 passed with normal model completion at997.1seconds, patch627bytes, complete reported usage574,643tokens and24 requests. Collector source_errors are empty; all stages are complete. Final repository scores are baseline6/8, latest7/8, Karpathy8/8 and combined4/8. Aggregate repository usage remains incomplete lower bounds, with2/2/1/3 incomplete runs respectively; no supported savings claim follows. The campaign PID1340531 is absent after terminal completion. Independent147-cell final audit and report consolidation remain pending.
