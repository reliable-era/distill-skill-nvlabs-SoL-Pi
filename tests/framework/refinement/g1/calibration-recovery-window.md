# Standing-authorized recovery window 1

This file's introducing Git commit starts a four-hour window. End = commit
committer timestamp + 14400 seconds; latest run start = commit + 7200 seconds.
Record exact bounds in calibration-recovery/calibration-window.json before
inference. No implicit extension. Later windows require their own pre-use
commit under standing-authorization.md; no renewed window reuses this cohort.

The permission fix, local broker serialization repair, saved-log decisions and
recovery driver are committed in 7d1eca5. The original HOME permission fix was
already committed in 31da44f. Runtime cap checks pass offline; they establish
neither model quality nor isolation/performance acceptance.

Execute No skill only, direct 127.0.0.1:18001, valid running count < 8 before
start, waiting allowed, at most 600 seconds admission backoff per attempt.
Keep 60 requests / 7200 seconds / 16384 output and start/per-request/30-second
load observations. Full 7200-second allowance must fit before every start.
Preserve all costs, failures, source hashes, role isolation and exact outputs.

Predeclared schedule: (1) go/exercises/practice/food-chain, which never reached
Codex; (2) sparql-university, one user-authorized separate retry of the saved
infrastructure-interrupted attempt. Then conditional fallback, in frozen order:
cpp/sublist, java/series, javascript/bowling, python/proverb, rust/acronym.
Stop fallback before its next start once the accumulated verified No-skill pool
has at least three tasks. Initial pool is retained HTML and TeX. No regex retry;
its one-request reasoning-only output-limited attempt was real. No reruns of
other completed tasks. At most seven new native starts and 420 requests in this
schedule, also guarded by the existing global 10-start/600-request ceiling.

This window authorizes Step 3 only; source run_calibration_recovery.py records
a new cohort without overwriting any older attempt. If its gate passes,
audit/commit/report Step 3, then use separate precommitted bounded windows for
standing-authorized Steps 4–9. Sealed model tasks remain untouched until winner
freeze. B3(a), three-candidate limit and matched-arm constraints stay unchanged.
