# Step 3 continuation: operationally inconclusive

The user's decision amendment was committed before new inference as dc768c3.
Its four-hour window is 2026-10-07 03:18:43–07:18:43 +08; latest start 05:18:43.
The route remains direct18001, admission running below eight, 60 requests per
run, 120-minute wall safety and 16384 output tokens. No shared server changed.
All five completed prior runs remain unchanged. B3(a) is unchanged.

## New primary results

| Task | Result | Model requests | Complete tokens | Native wall | Heavy-load flag |
|---|---|---:|---:|---:|---|
| overfull-hbox | Solved | 33 | 1,246,477 | 27.65 min | Yes |
| regex-log | Not solved | 1 | 23,075 | 6.81 min | Yes |
| sparql-university | Not solved | 2 | 14,663 | 0.17 min | No |
| train-fasttext | Not solved | 35 | 476,070 | 43.55 min | Yes |
| go/exercises/practice/food-chain | Startup failure; model untested | 0 | 0 | 0.44 sec shell attempt | No |

No valid new model run hit the request or wall cap. Each original Terminal
verifier executed tests and produced a valid reward. All 71 provider requests
have complete accounting, EOF/status receipts and the fixed backend.

The screening pool after the primary phase was HTML (retained prior solve) and
TeX. The conditional fallback therefore attempted the frozen task-ID order:
cpp/sublist, java/series, javascript/bowling, python/proverb and rust/acronym.
Each launch failed before Codex started; each made zero model requests. Their
starter-grader failures are preserved but are not model-quality observations.

## Runner fault and responsibility

The Aider/Go images default to user evaluator, while the runner set CODEX_HOME
to /root/solpi-home/.codex. All six affected shell logs contain:

    mkdir: cannot create directory '/root': Permission denied

This was a runner defect, not a model failure or budget exhaustion. The model
never received those six tasks. A scoped explicit container-user fix is prepared
and verified on all three affected image types using mkdir and codex --version
with network none, no model calls and no task retries. No host privilege, server
configuration, mounts or capabilities were expanded. The failed launches have
not been silently retried. An explicit new retry/timing decision would be needed
before executing those tasks with the prepared fix.

The raw runner report mechanically graded the unchanged starters as failures
and marked empty request sets cost-incomplete. Those raw reports remain intact.
reconciled-calibration-audit.json instead records the six results as model
untested and their provider costs as proven zero, supported by the complete
provider-only ledger and startup logs. No unknown cost is silently zeroed.

## Budget and eligibility disposition

The window closed at 07:18:43 +08. The final window-close-decision-audit.json
freezes the nominal budget at 60 requests / 7200 seconds / 16384 output tokens,
independent of solve count, under the user's amended rule. No new request or
wall cap was hit, all 71 provider requests have complete costs, and the six
pre-Codex failures have proven zero provider cost. This nominal freeze is not
proof that the budget prevents model or harness failures, nor a screening-gate
pass. The finite closure job verified its locked result/startup-audit hashes
and terminated without contacting any server or making actor/model calls.

The verified screening pool has only two tasks: break-filter-js-from-html and
overfull-hbox. Thus the three-task gate does not pass and Step 4 must not start.
Report G1 as inconclusive, not successful. Because six launches were invalid,
this is operationally inconclusive: it does not establish that the 27B model
cannot solve Aider tasks or that the development tasks cannot separate skills.

Across the two calibration cohorts there are nine valid model runs: two solved
and seven failed. The new cohort used 71 requests / 1,760,285 tokens; the prior
cohort used 123 requests / 4,078,674 tokens. Their combined accounting inventory
is 194 requests / 5,838,959 tokens, not a pooled performance estimate. Six
additional shell-start attempts had zero provider requests. Three offline
codex --version invocations are separately recorded as diagnostics, not task
runs. The expired zero-call admission remains its own preserved attempt.

## Load, uncertainty and limits

Start running/waiting loads were TeX 4/2, regex 0/0, SPARQL 0/0 and fastText 0/0.
Their periodic sample counts were 55, 13, 0 and 87; per-request observations are
also retained. Heavy load means any observation with at least six running or
any waiting requests. No run was excluded or rerun because of load. Native wall
is separate from preparation, admission, grading and window-close waiting.
Load flags do not causally quantify slowdown.

Advance warning remains in force: low Terminal-Bench solve rates may leave few
solves in sealed rounds, making tokens per solve and paired 95% ratio intervals
noisy or inconclusive under unchanged B3(a). This exposed calibration subset is
not representative confirmation evidence. Aider might provide more signal,
but its results cannot replace the separate Terminal-Bench acceptance gate;
these six startup failures provide no Aider model-quality evidence.

## Evidence and stop

Evidence under calibration-continuation/: calibration-window.json,
calibration-result.json, request-accounting-audit.json, per-run-load-records.json,
aider-startup-failure-audit.json and reconciled-calibration-audit.json. The final
window-close-decision-audit.json is authoritative for the nominal freeze at
window end. Private model/native traces and captured outputs remain under the
launch's /tmp root. Initial failures and raw summaries are not overwritten.

The model worker and no-inference closure worker are terminal. The model
worker's owned containers/network are absent with no cleanup errors. No job is
pending. The canonical skill is unchanged. No candidates, screens, sealed model
calls, confirmation results or savings claims exist. Stop before Step 4.
