# G1 Step 3: admission expired; calibration remains incomplete

The direct18001 route amendment is committed as 5795c61. The No-skill runner,
its runtime copies, and offline cap checks are committed as baeb409. The runner
retains the fixed ten exposed tasks, 60 requests per run, 600 total requests,
60-minute wall safety cap, and 16384-token provider output cap. It makes no
candidate calls, takes no exclusive server lock and has no endpoint fallback.
The actual direct18001 container and accounting implementation source checksums
were independently recorded before launch, without changing any shared server.

Worker 2272285 attempted the approved bounded admission for the first task.
Thirteen metadata observations were retained. No observation admitted the run.
The final recorded observation had four active requests and one waiting request
on 18001. After the ten-minute admission allowance expired, the worker stopped
and cleaned up only its own created actor, proxy and isolated network.

Results:

- Native starts: 0. Model requests: 0. Model tokens: 0.
- All ten tasks remain unstarted. No grades or solve observations exist.
- The five-of-ten verified-solve threshold was not established. No budget was
  frozen as successfully calibrated.
- The worker is terminal. Owned containers and network are absent; cleanup
  errors are empty. No automatic wait renewal, relaunch or endpoint fallback.
- The canonical skill is unchanged. No candidate, confirmation, savings,
  quality-loss, or performance claim follows from this admission attempt.

Evidence: calibration-launch.json, calibration-result.json,
calibration-admission-expiry.json, and calibration-stop-audit.json. Raw private
transport metadata is retained under the launch's /tmp root. The stop audit
verifies accounting and cleanup only; it is not a successful calibration.

Next input needed: once capacity is available, explicitly authorize a new
bounded admission attempt for the still-unstarted calibration pool. The expired
attempt must remain preserved; do not overwrite it or automatically retry it.
The original window still ends at 2026-10-06 09:30 +08 and is not extended.
If that deadline passes, a new window requires explicit authorization.

Paused at the required admission boundary. Step 3 remains incomplete; Step 4
and later steps have not started and remain unauthorized.
