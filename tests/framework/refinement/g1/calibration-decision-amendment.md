# Decision amendment: finish calibration, then stop before Step 4

The user explicitly approves decision.md section 4 (Option A). This supersedes
only the old calibration five-of-ten solve gate and elapsed window. It does not
change B3(a), comparative acceptance, sealed allocations or promotion rules.

The Git committer timestamp of the commit introducing this file starts a new
four-hour window. Its end is that timestamp plus 14400 seconds; latest native
start is that timestamp plus 7200 seconds. The runner records the exact commit,
start, latest start and end before any inference. No window extension or new
start that cannot fit its full 120-minute allowance is permitted.

Run only the five previously unstarted primary tasks, in their committed order:
overfull-hbox, regex-log, sparql-university, train-fasttext, and
 go/exercises/practice/food-chain. The five completed runs and their failed or
repaired grades remain unchanged in calibration-attempt-2; never rerun them.
The new cohort is calibration-continuation. Preserve separate request ledgers
and schedules; a screening eligibility union is not performance-cohort pooling.

The route stays direct 127.0.0.1:18001, without fallback. Admission is running
requests below eight, with waiting requests allowed, and at most ten minutes
backoff per run. Keep 60 requests / 7200-second safety / 16384 output tokens,
No skill only, one attempt per task, provider-only actor isolation, original
graders, and start/per-request/30-second periodic load observations. Retain all
failures, unknown costs and heavy-load runs; never discard or rerun by load.
No nginx, server, gpu01 host or other workload may be changed.

After the five remaining primary runs, or at window end if some cannot start,
freeze the nominal budget independent of solve count, subject to the cap check.
Any new run reaching 60 requests, its wall safety limit, or a typed local
per-run/deadline budget denial is a cap hit: report it and do not freeze. Missing
accounting, uncertain provider completion or cleanup also cannot prove the cap
check. Do not infer a cap hit from a failed original grade or a failed dependency
preload, and never count an unstarted task as a failed model attempt.

The Step 5 eligible pool is exactly tasks verified solved by No skill in these
calibration cohorts, including the independently regraded prior HTML solve.
If at least three are available, Step 3's screening-pool gate passes. If fewer
than three remain after the primary schedule, run at most five additional
exposed, non-sealed Aider fixtures, each once, in task-ID order and inside the
same window. Stop adding fixtures once the pool reaches three. Their frozen
IDs, exposure evidence and images are in calibration-fallback-fixtures.json:
cpp/sublist, java/series, javascript/bowling, python/proverb and rust/acronym.
These are all remaining explicitly excluded pilot/smoke fixtures, not an
outcome-selected replacement set. None belongs to the current sealed sample.
Only bowling's existing adapter preparation guard is locally extended; its
original npm/Jest runner and the already verified public dependency cache are
reused. The canonical benchmark adapter and sealed grader controls are unchanged.
The new window authorizes at most ten new starts and 600 new model requests
(five pending tasks plus at most five fixtures); prior 123 requests remain
separately accounted and are not relabeled as new starts or resends.

If the final pool has fewer than three tasks, report G1 as inconclusive, not
successful. If a cap is hit, report the no-freeze result. No mechanism derivation,
candidate calls, screening, sealed confirmation or promotion is authorized here.

Advance uncertainty notice: the observed low Terminal-Bench solve rate may
leave only a few verified solves in each sealed round. Tokens per solve and
paired ratio intervals may therefore be noisy or inconclusive under unchanged
B3(a). This is a risk, not a forecast established by representative sampling.
Aider may have more signal, but cannot replace Terminal-Bench's separate
acceptance gate. Do not weaken intervals, substitute tasks or claim USD savings.

Commit the final accounting and per-task/plain-English report, update STATUS,
and stop before Step 4. Passing preparation or cleanup checks does not establish
G1's savings objective. Only full verified comparison/confirmation could do so.
