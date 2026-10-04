# Cursor native local-route readiness

**Native local Qwen route: TBD. Complete gross usage ledger: TBD.** No model, authentication, installation or credential-content read was performed.

Pinned Cursor CLI `2026.10.01-e373342` exposes `--endpoint` / `CURSOR_API_ENDPOINT`, defaulting to Cursor’s API. Its bundled implementation passes that endpoint to a Cursor RPC client; the generated `agent.v1.AgentService` includes Run/RunSSE/RunPoll. This establishes a Cursor backend endpoint override. It does not establish acceptance of an OpenAI `/v1/chat/completions` server. Source hashes, character offsets and short excerpts are retained in [audit.json](audit.json) and [source-evidence.json](source-evidence.json).

The current official [parameters](https://cursor.com/docs/cli/reference/parameters), [authentication](https://cursor.com/docs/cli/reference/authentication) and [configuration](https://cursor.com/docs/cli/reference/configuration) references reviewed provide no demonstrated native local-Qwen recipe. This is an evidence gap, not a proof that every possible native configuration is unsupported. IDE settings or an SDK wrapper cannot establish this CLI route.

The official [output reference](https://cursor.com/docs/cli/reference/output-format) describes successful terminal results with timing and response identifiers, without a complete provider token ledger. The pinned bundle has per-response hook counters for input/output/cache reads/cache writes, but their coverage of retries, auxiliary calls, cache overlap and reasoning remains TBD. Saved prior trial stdout files contained no parsed terminal result events. Neither durations nor these unverified counters support complete gross traffic or dollar comparisons.

Cursor remains one of the fixed primary harnesses. No wrapper substitutes for it, and the denominator remains unchanged. Before any screen, require a documented native provider route plus a ledger covering all actual provider requests, including failed/partial attempts; preserve category semantics instead of blindly summing cache or reasoning.
