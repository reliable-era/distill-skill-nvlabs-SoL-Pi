# G4 Part B — descriptive results

All108 control-valid cells are attempted. No gate, early stop, promotion, shipment or push. G1–G3 and Part A remain separate.

| Arm | Cells | All attempts | Solves | Failures | Unknown grades | All-attempt provider tokens | Known lower bound | Unknown-cost attempts | Tokens/verified solve | Native/grader timeouts | Provider POSTs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
|none|27|27|11|16|0|Unavailable|26097229|1|Unavailable|0/0|649|
|K|27|27|13|14|0|Unavailable|20777165|1|Unavailable|0/0|581|
|ours|27|27|12|15|0|Unavailable|28021193|3|Unavailable|0/0|713|
|Both|27|27|14|13|0|Unavailable|28997365|1|Unavailable|0/0|713|

## Paired task-cluster comparisons

20,000 draws; seed2026101212. All rounds/retries retained together. Undefined draws stay null, not zero. Ratios are tokens-per-verified-solve arm/baseline; no savings gate.

| Comparison | Point |95% interval on defined draws | Defined | Undefined | Conditional interval |
|---|---:|---|---:|---:|---|
|none/K|Unavailable|[0.772813,2.522772]|7013|12987|True|
|K/none|Unavailable|[0.396389,1.293974]|7013|12987|True|
|ours/none|Unavailable|[0.547121,2.141412]|500|19500|True|
|ours/K|Unavailable|[0.804823,4.506364]|500|19500|True|
|Both/none|Unavailable|[0.677348,1.264304]|7013|12987|True|
|Both/K|Unavailable|[0.804026,2.213085]|7013|12987|True|

## Scope and limitations

Conditional intervals use only defined bootstrap draws and are not unconditional95% intervals or evidence for savings when full-panel points are unavailable. Known token lower bounds are not estimates of missing costs. TPS means tokens per verified solve, not serving throughput. Admission histories verify sampled waiting counts and reported occupied slots, combined with frozen16-worker/exclusive-lock and cleanup/launch proofs; they are not a continuous independent slot trace, and shared runtime clocks are not externally notarized.

Codex0.160.0, unchanged shipped ours SHA68ea78dc and frozen G2 K. Same logical Qwen model including the two user-declared labels; available response model/usage and explicit missing identities/usage remain in every receipt, no variant shares. Route127.0.0.1:8000 only; shared16 rolling occupied slots, fresh all-backends waiting0 admission. Caps60 requests/7200s/16384 output. All attempts, errors, caps and infrastructure retries are charged; no model-error/cap reruns or cost imputation. Unknown grades are not asserted failures or solves. Runtime/load and execution-window effects limit causal claims. HTTP gateway failures without usage are unknown costs, never zero-model assumptions; metadata endpoint200 does not establish a healthy provider POST route. Native CLI errors and caps remain in raw logs even when the outer attempt error is null.

Nine original newly unsealed Terminal tasks×3 rounds×4 arms. Original gold/no-op controls retained. Missing tmux and Python relay-runtime environment prerequisites repaired neutrally before inference, paired controls rechecked; identical immutable task image across arms. Quality is conditional on these nine tasks and repaired cached environments, not the full Terminal benchmark. The late HTTP502 execution window confounds efficiency and runtime comparisons; no missing costs are repriced or treated as zero. Hidden original verifier is mounted only after native capture.

## Evidence

Canonical input SHA `e6b2d69ea7b80c3a004120433a011e3b24b567e959e83a926cdc64519142d7ed`; frozen analyzer SHA `8c8ef41e2badb13f7f5fa9fafa5520b71259605fb9188a37eb265fb428291262`; primary analysis SHA `b20c68441915ee91cc0d54e405385a6ef9d877daa5c1ae5f3e769cb0b2c2f79a`; independent analysis SHA `12b395390fb62124bf8728923a94ef7c8572375bbb7162c43b7f4dfa39e0702b`. Independent task-weight resampling verifies every draw/all-attempt metric. Canonical provenance links each audited window, raw receipts, native/capture hashes and explicit grade repairs. Original controls/graders and actual cleanup/integrity must also pass the final requirement audit; these tables alone are not completion.
