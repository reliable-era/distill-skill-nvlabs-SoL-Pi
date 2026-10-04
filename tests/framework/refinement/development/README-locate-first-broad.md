# Locate-first across three Codex development families

One public reused task per family, one matched round per task. All twelve patches pass their independent official-test graders. These are development results; no promotion or held-out confirmation.

| Configuration | Flask repair | Go exercise | Terminal sanitization | Total tokens |
|---|---:|---:|---:|---:|
| No skill | 112,352 | 61,542 | 235,386 | 409,280 |
| Karpathy | 151,278 | 63,839 | 235,145 | 450,262 |
| Ours (locate-first candidate) | 84,948 | 62,228 | 315,603 | 462,779 |
| Candidate + Karpathy (Both) | 128,199 | 83,034 | 435,312 | 646,545 |

Each cell is complete reported tokens for one passing attempt. All variants solve3/3 across these tasks. Total tokens are a descriptive sum of these three matched cells, not a frozen confirmation aggregate or an uncertainty estimate. Candidate costs **13.1% more than No skill**, **2.8% more than Karpathy**, and **28.4% less than Both** overall. Its Flask savings do not establish a cross-family win.

Codex requests `gpt-6.1-sol`, native default effort; independently observed backend ID and actual billing USD remain **TBD**. Terminal token excess is mostly cached input; reported tokens do not establish a dollar-cost increase. Task scheduling seeds106/107 do not set model sampling seeds. Each task retains its own frozen source/image/skill/prompt/runner plan. Go bound the broader global budget after two starts, while its local eight-start budget was frozen before calls; this timing limitation is preserved.

[Flask](swe-flask-locate-first/README.md), [Go](go-locate-first/README.md), [Terminal](terminal-locate-first/README.md), [terminal trace diagnosis](terminal-locate-first/refinement-diagnosis.md).

A separately frozen **bounded-search candidate** changes only the context-read bullet: preserve full search scope, use paths/counts for potentially oversized scans, then inspect bounded match context. All verification rules remain unchanged. Its four-arm terminal screen is now complete: No skill and Both pass; candidate and Karpathy fail. Candidate uses216,037 tokens versus252,618 for No skill, but violates exact replacement requirements, so this is not an eligible efficiency win. All four full-state replays agree; no retry or promotion. [Evidence](terminal-bounded-search/README.md). Native agy Flask has a separate prepared four-start budget; its error classifier must pass review before launch. Pi login remains unavailable; no unmeasured harness counts as a win.
