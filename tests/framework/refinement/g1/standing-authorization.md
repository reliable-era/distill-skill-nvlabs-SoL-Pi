# Standing user authorization, 2026-10-08

The user's current message reopens G1 after the operationally inconclusive
calibration and grants standing authorization until G1 ends. Claude supervises
on the user's behalf under workspace supervisor-policy.md (snapshot below).
This supersedes the per-window permission and mandatory post-Step-3 approval
stop only. It does not weaken B3(a), caps, task sealing, candidate limits,
quality/accounting rules or promotion requirements.

Bounded windows may be opened back to back without asking, each committed
before use. Direct 127.0.0.1:18001 only, no fallback; admit only with valid
metadata and fewer than eight running requests; waiting requests allowed.
Keep 60 requests / 7200 seconds / 16384 output and complete load/accounting
records. Preserve prior attempts, costs, failures and unknowns. No blind
resends, workload cancellation, shared-server changes or outcome-selected
retries. Expiring a window does not extend it: a subsequent window must be
separately committed and contain only remaining authorized cells.

Now execute food-chain and, conditionally, the five previously zero-model
fallback cells in frozen order (cpp/sublist, java/series, javascript/bowling,
python/proverb, rust/acronym). Stop the fallback as soon as three tasks are
verified solvable. The CODEX_HOME container-user fix was already committed
in 31da44f and verified offline on the three image types; the recovery commit
pins and uses it before inference. No completed model task is repeated.

The user additionally authorizes saved-log classification of regex/SPARQL,
with one separate retry only for a broken run. saved-log-classification.json
finds regex a real reasoning-only/output-limited failure, so no retry; SPARQL
reached the model but ended in fatal SDK 429 after two successful file reads,
so one separately accounted SPARQL retry is authorized. The local broker's
completion/persistence serialization is fixed without changing model caps,
provider requests, the shared backend, or replaying any prior request.

If the three-task gate passes, proceed through Steps 4–9: at most three new
candidates total, each screened on at least three verified control-solvable
tasks with four matched arms. Stop after two consecutive non-improving
candidates or no qualifying candidate. Freeze before sealed confirmation;
216 cells and original B3(a) analysis/audit before any promotion.

Stop and escalate only for: a gate still failing after actual Aider/Go tests;
a needed change to a goal rule; an action touching other workloads, nginx,
gpu01 or shared-server configuration; or a final G1 result. Routine local
infrastructure fixes and new bounded windows do not require fresh user input.
Commit and report plainly after each completed step. A negative/inconclusive
stop is not achievement of the savings objective. Canonical skill unchanged
until fully supported promotion.

## Supervisor policy snapshot

Claude may answer for bounded windows, local infrastructure fixes and cells
never reaching the model, routine /goal resume, and clarifications applying
existing rules. It escalates the four cases above and records a one-line note
each time it answers Pi. Pi does not edit that workspace policy or operate
other agents' tmux sessions.
