# Step 1: server window request — awaiting user response

Please reserve an initial **eight-hour window** on the existing shared local
Qwen3.8-27B-FP8 route for one sequential Codex 0.160.0 queue. The documented
route is port 8000 with Qwen backends on 18001 and 18002; please confirm which
current endpoints and other agents share that capacity. No server restart,
configuration change, workload cancellation or parallel actor execution is requested.

The first window is for Step 3 No-skill calibration only, after Step 2's fresh
sealed samples and gold/no-op grader controls have been completed and committed.
Those environment controls use no model and should finish before the reservation
starts. Calibration begins at 30 minutes, 60 requests and a 16K output cap per
run. Nine Terminal-Bench development tasks require at most 4.5 actor-hours;
including the reused Go/polyglot development fixtures may bring that to roughly
six actor-hours. The requested margin covers bounded receipt draining and safe
handoffs, not extra candidates, retries or a higher per-run budget. The exact
development pool and calibration contract must be committed before calls.

Please provide the start and end times with timezone, the reserved endpoint(s),
and confirmation that other queues will not contend for this window. Smaller
scheduled blocks are acceptable if they accommodate complete bounded runs.
If the window is unavailable, provide an alternative; I will not poll for idle
availability or interrupt another workload.

Please also explicitly authorize the No-skill model calls within Step 3 after
its preparation plan is committed. The instruction to commit Steps 0–3 before
any model call is otherwise circular because calibration itself uses the model.
No candidate calls occur before calibration passes and the budget is frozen.

Later screens and confirmation need separate approved windows. At the review's
15-minute estimate, the 216 confirmation runs alone take about 54 actor-hours;
at the initial 30-minute limit they could take 108. Calibration will inform a
better estimate. No later window or inference is authorized by this request.

**State:** no slot reserved, no idle checks, no new model calls. Stop here and
wait for the user's written answer. Step 1 is not yet complete.
