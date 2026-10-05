# G1 authorization update

The user accepted Step 0 and explicitly authorized Step 2 immediately, without
waiting for a server reservation. Step 2 is metadata-only selection and gold/no-op
grader controls, with no model calls or access to confirmation model traces.

There is no exclusive reservation. Port 8000 balances replicas 18001 and 18002.
The user identifies 18001 as ykw-qwen38-dflash2-tp2 and 18002 as
jev-pi-qwen38-replica. Another project, token_economiy, shares port 8000.
Do not interrupt, cancel or slow down that workload. Before calibration, verify
current endpoint identity using metadata rather than assuming historical labels.

Step 3 No-skill calls are authorized only after Step 2 is complete and committed
and the calibration contract is committed. The eight-hour calibration window
starts at the Step 2 completion commit. Keep runs sequential. The primary
per-run budget is 60 requests, with a 60-minute wall-clock safety cap and the
existing 16K output cap. Candidate calls remain forbidden until calibration
passes and its budget is frozen; later screens need separate approval.

Before each calibration run, read /get_load on both replicas. Admit when
num_waiting_reqs is zero on both; active requests need not be zero. Otherwise
use bounded backoff for at most ten minutes per run, then pause and report.
Record per-request backend identity and observed queue state. Flag clear
contention-inflated wall times; retain those runs, costs and grades without
rerunning or discarding them. Do not restart or reconfigure the shared server.

After Step 3, commit its results, report calibration in plain English, and stop
before Step 4. This authorization supersedes the earlier exclusive-window
request and the circular prohibition on model calls before calibration finished.
