# Step 3 second attempt: partial calibration; budget not frozen

The user-approved amendment was committed before model calls as 0a51120.
Every call used direct 127.0.0.1:18001, with no fallback. Admission required
fewer than eight running requests, allowing waiting requests. Each run retained
its 60-request primary cap, 16384 output cap and 120-minute wall safety cap.
No shared server, nginx, or other workload was changed.

## Results

| Task | Verified result | Requests | Complete tokens | Native wall time | Heavy-load flag |
|---|---|---:|---:|---:|---|
| break-filter-js-from-html | Solved after grader-only repair | 38 | 1,437,030 | 16.87 min | Yes |
| build-cython-ext | Not solved | 34 | 1,477,456 | 11.15 min | No |
| build-pmars | Not solved after grader-only repair | 18 | 407,960 | 7.68 min | Yes |
| financial-document-processor | Not solved | 13 | 149,087 | 1.45 min | No |
| make-doom-for-mips | Not solved | 20 | 607,141 | 4.73 min | No |
| overfull-hbox | Unstarted | 0 | 0; no calls | — | — |
| regex-log | Unstarted | 0 | 0; no calls | — | — |
| sparql-university | Unstarted | 0 | 0; no calls | — | — |
| train-fasttext | Unstarted | 0 | 0; no calls | — | — |
| go/exercises/practice/food-chain | Unstarted | 0 | 0; no calls | — | — |

Totals: five native starts, 123 requests, 4,078,674 complete tokens, one verified
solve, four verified failures, and five unstarted tasks. No request has unknown
cost. All failed attempts are included in the token total. Unstarted tasks are
not counted as failed attempts. The previous zero-call admission expiry remains
separate and unchanged.

The budget is not frozen as calibrated. The fixed ten-task pool requires at
least five verified solves; this attempt established only one. This is not a
savings result, comparison against another arm, or G1 completion.

## Load, timing and limitations

Running/waiting counts at admission were HTML 3/1, Cython 3/0, PMARS 3/0,
financial 2/0 and Doom 2/0. Periodic sample counts were 33, 22, 15, 2 and 9,
respectively, at a nominal 30-second interval. Per-request observations are also
retained. The predeclared descriptive heavy-load flag means any observation
with at least six running requests or any waiting requests. No run was excluded
or rerun because of load. These flags cannot causally measure wall-time inflation.

The first admission included ConnectionRefusedError observations before the
backend recovered; it admitted within the ten-minute allowance. Preparation
also encountered unusually slow host file access. These delays are separate
from the native wall times above, which do not include preparation, admission
or independent grading. The started tasks are an exposed development subset,
not a random quality sample or confirmation cohort; no population or repeated-
round variability claim follows from their outcomes.

Every native start was before 07:30 +08. The last start was admitted at
07:28:55 +08. When its run and grade finished, the other five tasks could no
longer fit their full 120-minute allowance before 09:30. The runner therefore
stopped at a clean boundary, without a new start or window extension.

## Grading failures preserved and repaired without model retries

The HTML grader's reused generic offline cache lacked the original verifier's
Selenium and BeautifulSoup dependencies. Its reward-zero/no-test report remains
an infrastructure failure, not a valid failure grade. A first repair also failed
because Docker cannot attach a none-network container to bridge. That failure
is preserved. The second repair preloaded only the original pinned public
verifier dependencies in a fresh owned original-image grader, disconnected its
network, replayed the exact captured HTML artifact and ran unchanged original
tests. One test passed and the official reward was one.

PMARS initially failed its trusted-preload topology guard because the runner
created its grader with network none rather than the helper's required setup
bridge. A fresh owned original-image grader replayed the same captured binary
and source directory, used the existing public-runner preload, disconnected
networking and ran unchanged original tests. Four tests executed; reward zero.

Neither repair reconstructed target output or made a model call. Raw initial
reports remain unchanged; calibration-summary-audit.json supplies the reconciled
view with explicit references to both repairs.

## Evidence and stop

Under calibration-attempt-2/: calibration-launch.json, calibration-result.json,
calibration-summary-audit.json, request-accounting-audit.json,
per-run-load-records.json and all grader-repair reports. Complete model/native
content and captured outputs remain private under the launch's /tmp root.

The audit verifies 123 receipts against the request counters, fixed backend,
output caps, EOF/status, source checksums, latest-start boundary, repaired grades
and canonical hash. The worker and repair jobs are terminal; owned containers
and network are absent, with no cleanup errors. Canonical efficient-coding is
unchanged. Stop before Step 4; no mechanism, candidate, screen or confirmation
was started. Completing the remaining calibration needs separately approved
next steps and timing, not automatic extension or actor retries.
