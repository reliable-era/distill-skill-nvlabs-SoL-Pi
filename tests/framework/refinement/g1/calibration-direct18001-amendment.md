# Authorized direct18001 amendment

The user's response to calibration-route-question.md resolves the route blocker.
Port 8000 balances four replicas with potentially different numerical behavior.
G1 must not use port 8000. Every model call in calibration and, if separately
approved later, screens and confirmation must use 127.0.0.1:18001 directly.
There is no endpoint fallback. No nginx, gpu01 host or server may be changed.

Admission now observes only http://127.0.0.1:18001/get_load. A run may start when
num_waiting_reqs is zero; active requests need not be zero. The bounded ten-minute
wait and existing backoff remain unchanged. Unavailability or admission expiry
means pause and report. Record this replica's observed load per request and
retain contention-affected runs. The replica supports eight running requests
and remains shared with other agents through nginx; no exclusive lock is used.

No other calibration-contract parameter changes: the same ten exposed tasks,
one No-skill round, 60 requests per run, 3600-second wall safety cap, 16384 output
tokens, no actor retries, original graders, and five verified solves threshold.
The window still ends 2026-10-06 09:30 +08. Stop at a clean run boundary rather
than starting another run after that deadline; do not extend the window.
Commit and report Step 3, then stop before Step 4. Canonical skill unchanged.

The prior route-question evidence is retained. This amendment, the updated
contract and the one-replica queue rule are committed before any model call.
