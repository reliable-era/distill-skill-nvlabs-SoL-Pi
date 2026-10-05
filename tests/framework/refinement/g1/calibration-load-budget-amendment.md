# Authorized second admission attempt and shared-load budget amendment

The user explicitly authorizes a fresh bounded Step 3 attempt. Preserve the
first expired attempt and its zero-call accounting; do not overwrite its files.
New evidence belongs under calibration-attempt-2/.

Direct 127.0.0.1:18001 remains the only model backend. No endpoint fallback,
nginx or server changes, or interference with other workloads is permitted.
Admit when the backend reports 0 <= num_reqs < 8. A waiting queue is allowed.
If capacity is unavailable, back off for at most ten minutes, then pause/report.
Malformed or unavailable metadata never establishes admission.

The primary budget remains 60 requests per run. The wall safety cap increases
to 7200 seconds for every run. All ten exposed tasks, No skill only, one round,
600 total requests, 16384 output tokens, source identity and original grading
remain unchanged. No full-actor retries or blind provider resends.

Record running and waiting counts at admission, before each model request, and
periodically every 30 seconds during the native run. A descriptive heavy-load
flag means any observation with at least six running requests or any waiting
requests. This flag is not a causal slowdown estimate or an exclusion rule.
Retain runs, grades and costs under heavy load; never discard or rerun them.

The window still ends 2026-10-06 09:30 +08. Check the full 7200-second allowance
before preparation and again after admission. No native start after 07:30 +08.
Report remaining tasks as unstarted. Do not extend the window. Commit results,
report per-task solves/tokens/wall/load and whether the budget can be frozen,
and stop before Step 4. Green cap checks are not calibration success.
