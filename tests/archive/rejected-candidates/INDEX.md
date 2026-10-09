# Rejected skill candidates

These are experimental variants of `efficient-coding` that were tested and **not** shipped. The shipped skill is `skills/efficient-coding/` (SKILL.md SHA-256 `68ea78dc…`). These files are kept as evidence of what was tried and are not maintained.

| Candidate | SKILL.md SHA-256 | What it tried | Why it was rejected |
|---|---|---|---|
| lean-tools | `bcb25e08d073…` | Shorter entrypoint with fewer tool instructions | Did not meet the token target against No skill in the first native screen |
| lean-tools-no-reread | `9deb3cc1edbc…` | lean-tools plus "do not re-read files" | Same screen; did not meet the token target |
| locate-first | `8c753e5093f7…` | Locate the relevant code before reading broadly | Passed 3 Codex development tasks, but used 13.1% more tokens than No skill |
| bounded-search | `f0ca50300588…` | Cap the breadth of searches | Used fewer tokens but failed correctness |
| acceptance-first | `4be6bafc3df1…` | Start from the acceptance check | No qualifying development result |
| independent-reads | `d9d83894c0cb…` | Batch independent file reads | All four arms failed the Terminal development cells; screen left incomplete |
| scope-coverage | `603e81e6eba2…` | Match evidence coverage to local vs. exhaustive scope | Passed the Go smoke test but failed Terminal with no file change |
| source-backed-verification | `e4277c3220d8…` | One source-backed verification bullet | Single-task point win (financial); failed quality on regex |
| behavior-first-progress | `94647e4415a3…` | Behaviour-first progress bullet | All arms passed SPARQL, but it was not cheaper than all comparators |
| coalesced-verification | `cff132600efd…` | Keep changes and their required checks together; skip re-report checks | Zero-solve fastText panel; inconclusive |
| feasible-first | `3dea5744e152…` | Feasible end-to-end baseline first | 0/4 solves on fastText; no signal |
| documented-baseline | `13a20eb574dd…` | Use an existing tool or library baseline early | 0/4 solves on fastText; no signal |
| measured-feasibility | `d0cd1c882966…` | Cheap feasibility measurement before expensive work | Candidate 0 vs Both 1 solve: quality loss |
| byte-bounded-observations | `aca1e098a1a1…` | Return byte-bounded log observations | Partial panel; size limit, no grade |
| scratch-capacity | `fe06df173c33…` | Check output/scratch capacity before large writes | 0/4 solves on fastText; no signal |
| recovery-context | `7a1ec1071675…` | Keep context after a successful recovery | 0/4 solves on fastText; stop |
| output-contract-preflight | `03f47302defb…` | Conditional output-contract preflight | Never started (server admission blocked); abandoned |
| g1-c1-bounded-reasoning | `e11948951958…` | G1 candidate 1: bound reasoning/action loops | G1 screen: lost a solve vs No skill; +45% tokens per solve |
| g1-c2-effect-checked-transitions | `39f7b30993b0…` | G1 candidate 2: effect-checked state transitions | G2 sealed confirmation (Aider, 108 runs): 62.5% fewer tokens per solve than No skill (95% CI ratio 0.11–0.85, passed), but the Karpathy comparisons were not established (one Karpathy cost unknown; conservative CIs include 1). Negative under the G2 contract |

Final reports: G1 `tests/framework/refinement/g1/report.md`, G2 `tests/framework/refinement/g2/report.md`.

## Old paths

These directories moved here on 2026-10-10. Historical plans, audits and runner scripts still use the old paths. They were left unchanged on purpose, because other audits pin them by hash. File contents are byte-identical (61 files verified).

| Old path | New path |
|---|---|
| `tests/framework/refinement/candidates/<name>/` | `tests/archive/rejected-candidates/<name>/` |
| `tests/framework/refinement/g1/candidates/bounded-reasoning/` | `tests/archive/rejected-candidates/g1-c1-bounded-reasoning/` |
| `tests/framework/refinement/g1/candidates/effect-checked-transitions/` | `tests/archive/rejected-candidates/g1-c2-effect-checked-transitions/` |

The G2 frozen copy at `tests/framework/refinement/g2/frozen/candidate/` is part of the G2 experiment record and stays in place.
