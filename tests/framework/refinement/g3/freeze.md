# G3 pre-inference freeze

Separate contract68cff75. G1/G2 stay closed and unchanged; no pooled historical
costs/solves, shipped skill/README/archive edits or push. All211 eligible task
controls completed with zero model calls:196 valid;15 exclusions only for
recorded failed gold/no-op checks. Original211 results plus six diagnosed
adapter/count-repair results remain immutable. No task score-based exclusion.

`plan.json` records full2352-cell conditional queue (784 per round), independently
seeded task shuffles and adjacent random4-arm order, bootstrap seed2026101111,
20,000 task-cluster replicates, frozen analysis/implementation/test SHA, full
G2 candidate/K trees, private trusted grader/starter/prompt hashes, immutable
images, original controls/exclusions, binary and protected G1/G2/source hashes.
Round seeds2026101200/2026101300/2026101400. No inference occurred during any
plan generation. Codex0.160.0 binary12eb3e81…; caps60/7200/16384 unchanged.

Runtime: one --network none actor per attempt; only container-loopback relay
to its unique host Unix broker socket, no host network or Internet/DNS route.
Only socket directory mounted; private request/receipt directory is not visible
to actor. Broker forwards only fixed streaming modelQwen/Qwen3.8-27B Responses
POSTs to direct127.0.0.1:9012, adds only standard16384-output cap, retains
original/forwarded payloads, response bytes and provider standard terminal usage.
No speculative FP8 gross-token normalization or usage estimation is reused.
All25 offline unit tests passed, including18-slot admission/once-only retry,
bounds/futility/unknown-numerator handling, usage/caps and refusal accounting.
Four immutable image startup/relay probes passed without POST; initial zero-model
socket-permission failure and fix retained separately.

Rolling queue18 allocated runs; admission serialized by frozen primary dispatch
order; all /get_load ranks must have num_waiting_reqs==0 (not running<8).
Slot is occupied through preparation/inference/grading and any uniform once-only
infra retry. Primary task arms are adjacent in queued order, not artificial
barrier-synchronized matched starts. Same-slot infra retries may admit between
primary starts; no scheduling selection based on model success/failure/cost.
Model identity is checked at every window start, hence every round start.
Receipt backend always9012. Every bounded window is separately committed before
inference, commit+4h end/+2h latest native start; future fixed queued cells remain
pending after allowance ends. No round interleave.

Infra once-only from-scratch retry: zero-provider attempt or explicit connection
refused/reset; no model HTTP error/cap/wall-limit retry. Both attempt records/all
provider costs remain. Proven connect refusal before any POST is zero-model/
zero-cost; reset after possible delivery is unknown cost, never inferred zero.
Final cell solve is final attempt's original grade, never count a failed first
attempt's solve twice or select the better attempt. Grade validity/complete
accounting independent of infrastructure classification. Unclassified prepared
attempt roots stop startup for artifact reconciliation, not silent rerun.

Futility after full round1 tests candidate/none and candidate/K point≤.95 and
no fewer solves than either; no early success. Full3-round all-comparator final
rule requires candidate/none,Both/K,candidate/K each point≤.95,95% upper<1,
no fewer solves; candidate/Both informational. Undefined draws are+∞, retained.
Unknown denominator costs permit conservative upper-bound surrogate; unknown
numerator costs never support upper-bound acceptance. Failure of conservative
bounds does not prove true-ratio failure; original accounting completeness is
reported separately. No new cost estimates, threshold or sample exclusions.

Final reports must include per-round and total all-arm tokens/solves/TPS/timeouts,
ratios/95% intervals, quality/Wilson caveats, round variability/wall separately,
complete attempted receipt/grade/provenance/owned cleanup and actual requirement
mapping. A passed math/startup check is not a savings claim. No Terminal runs.
9012 outage pauses/report without touching tunnel/honey/nginx/8000/18001/18002/
gpu01 or unknown workloads. Unrelated nginx.conf/backups remain untouched.
