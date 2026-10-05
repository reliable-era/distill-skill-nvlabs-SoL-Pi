# Calibration preflight: route differs from the authorization facts

No model-agent request has been sent. Calibration has not started.

The user described port 8000 as balancing the two loopback replicas at 18001
and 18002, and specified admission observations on those two replicas.
However, a bounded live /healthz GET reports two additional backends:
10.193.104.97:18001 and 10.193.104.97:18002. The checked-in nginx configuration
also lists those servers in its active upstream pool. This is not merely an
unused image or an unrelated service.

Read-only /v1/models GETs on both additional backends advertise
Qwen3.8-27B-FP8 with a 262144 context limit. The local frontend's metadata GET
also advertises that model. These observations identify advertised model names;
they do not independently establish matching model weights, implementation
source or the intended scope of the authorization. Their metadata is retained
in calibration-route-preflight.json. No server configuration or workload changed.

Before model calls, please confirm whether the two additional backends are part
of the authorized self-hosted Qwen pool. If so, confirm whether admission should
remain based on the two loopback queues or cover all four, and provide/authorize
read-only source identity verification for the additional replicas. Alternatively,
identify an existing approved endpoint restricted to the intended two replicas.
I will not silently redirect to a different endpoint or reconfigure port 8000.

The original eight-hour calibration window still ends at 2026-10-06 09:30 UTC+08.
It is not automatically extended while awaiting this clarification. If approval
arrives after that deadline, a new window must be explicitly authorized.

Step 2 is complete (53dd11a). The ten-task No-skill contract is committed
(fcf806b), and the finite queue rule is committed (7071e63). The calibration
runner is not yet finalized; confirmation and candidate calls remain forbidden.
