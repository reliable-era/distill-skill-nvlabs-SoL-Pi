# Trace-supported next mechanism

Read-only review; no candidate, frozen plan, raw result, or canonical skill modified. One exposed development task and one ordering round support a hypothesis, not a causal finding or confirmation win.

| Arm | Unique completed tool steps | run_command steps | git history queries |
|---|---:|---:|---:|
| No skill |44|26|6|
| Karpathy |26|16|4|
| Locate-first |17|9|1|
| Both |14|8|0|

Counts deduplicate native step updates by step index. All four traces execute `git status` at step 2 and a Blueprint symbol search at step 4: [No skill lines 5 and 8](agy/none/stdout.jsonl), [Karpathy](agy/karpathy/stdout.jsonl), [candidate](agy/candidate/stdout.jsonl), [Both](agy/both/stdout.jsonl). These reads are independent and can share one shell invocation. That removes one potential model/tool round trip without dropping either observation. Actual token or latency savings are unmeasured; shorter traces correlate with lower SDK totals but do not prove this mechanism caused the difference.

**One proposed portable instruction for a future candidate:** When two or more necessary read-only observations are already known and independent, issue them in one available shell/tool call, preserving labeled output and each command’s exit status. Keep dependent searches sequential. Do not fuse unrelated mutations, suppress failures, truncate required evidence, or skip verification. Use existing tools; do not introduce a batching helper for a trivial pair.

This is a prompt-level command batching hypothesis, not native SoL-Pi ActionFusion. The frozen [SoL-Pi README](https://github.com/NVlabs/SoL-Pi/blob/e1a586af0ad8956f42ae5b26bba20e48fbf30e00/README.md) motivates reducing tool round trips while preserving verification and evidence. [Ponytail](https://github.com/dietrichgebert/ponytail/blob/c982cd411abb53323c4baa1baa3c2f020b8d0b08/README.md) supports using existing platform primitives. The provisional [Jev reference](https://github.com/lazniak/jevskill/tree/923e521b0521061637bbc486d9f9c2a3683e0374) motivates grouping decisions from the same state with recoverable evidence; intended Jev identity remains TBD. Reference hashes are frozen in `../../references.json`.

Two other observed confounds should not become fixture-specific skill rules. First, actor Git history contains one original snapshot commit. Repeated historical searches provide little evidence; expose this history limitation uniformly in future harness contracts, rather than rewarding a skill for guessing it. Second, No skill resets source/tests after full-suite failures (step 76, raw line 116), checks pristine failures, then reconstructs its patch (steps 82/84) and reruns Blueprint tests (86). Karpathy reruns the full suite with warnings ignored (32, raw line 50). All arms encounter the same original cookie failures; first baseline attribution is useful, but destructive reconstruction or an unchanged full-suite rerun has avoidable overhead. Preserving a patch while doing a focused scratch-baseline comparison is a separate hypothesis, not tested here.

Economic interpretation follows [accounting-scope-audit.md](accounting-scope-audit.md): cached counters are separate; SDK totals are not verified gross traffic or dollars. Test the proposed batching instruction prospectively against all four arms, preserving full correctness and attempt cost, before promotion.
