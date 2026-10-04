# Copilot native accounting gate

Investigated 2026-10-04 without model calls, credential refresh, or SDK actor substitution. **A native collection path exists; complete native accounting is not yet validated. Existing pilot token totals remain TBD.** This investigation does not change the frozen primary denominator, thresholds, or harness allocation.

## Installed native evidence

Host Copilot and the frozen pilot Docker image both report GitHub Copilot CLI **1.0.91**. Both native `--help` outputs expose `--usage-output-file <file>`, described as writing final usage statistics as JSON. Frozen image: `sha256:d6d79bfad41b1fbac8288fc90fbc5d0412851fa355fcb9efcddae06531d2fd70` (`trials/copilot/plan-auto.json`). These checks used version/help only, with no actor prompt or authentication operation.

Host loader: `/home/wangjian/.local/lib/node_modules/@github/copilot/npm-loader.js`; installed package version 1.0.91. The implementation shipped as a stripped native ELF in the platform package, not inspectable JavaScript accounting code. Absence of particular strings in that binary does not establish absent functionality.

The official [CLI changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) records per-agent usage metrics in `--usage-output-file` for 1.0.81 (2026-08-27), preceding this installed version. Version 1.0.51 (2026-05-20) records that input usage includes cached tokens. Thus cache counts must not automatically be added to inclusive input totals. Neither help nor the inspected saved artifacts establishes the complete usage-file schema or forced-cutoff behavior for 1.0.91.

## Saved pilot evidence

The native command in `trials/copilot/plan-auto.json` requests `--output-format json` but not `--usage-output-file`. Inspection of all eight `results-auto/*/agent.log` files found:

| Saved signal | Runs containing it | Meaning |
|---|---:|---|
| Native terminal `result` | 5/8 | `usage` keys: codeChanges, premiumRequests, sessionDurationMs, totalApiDurationMs; no cumulative token fields |
| `session.usage_checkpoint` | 5/8 | Cost/context-cache checkpoint, not evidence of cumulative full-run input/output |
| `assistant.usage` | 0/8 | No recoverable per-call token stream |
| `session.shutdown` | 0/8 | No saved cumulative per-model shutdown record |

The first three logs lack terminal result/checkpoint events. All eight contain model-call results, which alone do not supply complete input/output accounting. Checkpoint `promptCacheBreakState` includes prompt/cache/context snapshot fields; summing those would confuse context occupancy with traffic and cannot reconstruct missing output. Preserve observed premium-request/nano-AI-unit billing indicators separately from token totals and USD billing. Auto selected different native models in the pilot; preserve actual per-model identities rather than treating Auto as a fixed model.

## Official SDK evidence and its limits

The official [usage guide](https://github.com/github/copilot-sdk/blob/main/docs/features/usage-and-billing.md) documents `assistant.usage` once per model call, including subagents; it is ephemeral and not replayed on resume. `session.usage_info` is current context occupancy. Experimental `session.usage.getMetrics` aggregates main-agent and subagent API calls, exposing per-model input/output and nano-AI-unit totals. The guide requires pinning SDK and CLI and points to generated types for the authoritative current schema.

The official [streaming event reference](https://github.com/github/copilot-sdk/blob/main/docs/features/streaming-events.md) documents `session.shutdown.modelMetrics` and cache/reasoning fields on usage events. These public SDK capabilities establish a possible diagnostic cross-check, **not** proof that native prompt-mode JSON logs emit those events or that the native 1.0.91 usage file has identical layout. Launching an SDK actor instead would change the harness; this investigation did not do so. A separately approved passive SDK attachment would also require demonstrating supported connection to the same native session, without creating/replaying turns or changing actor behavior.

## Minimal next gate

On the next separately authorized development-only native CLI run, preserve the same binary/model/permissions and add only `--usage-output-file <private run artifact>`. Freeze that instrumentation before outcomes and apply it identically across arms. Capture binary/image identity, native JSONL, final usage file, exit/cutoff state, and actual model IDs. Inspect the actual native output before implementing a parser.

Validate a normal exit plus interruption/error case. Require cumulative per-model input/output, explicit cache semantics, and evidence that main, helper/subagent, and compaction traffic is included exactly once. Do not sum per-agent breakdowns again into already inclusive session/model totals. Distinguish absent optional fields from measured zero. If cutoff prevents a trustworthy final file, mark traffic incomplete/lower-bound rather than treating successful grading as cost completeness. Reconcile any native aggregate with independently available same-session call metrics where supported; current SDK documentation alone cannot certify the pinned binary's behavior.

Only after these checks can native Copilot count as the third accounting-complete primary harness. No parser or synthetic schema tests were added: there is no captured native usage-file fixture to validate, and guessing its schema would give false assurance. The existing collector and all frozen assets remain unchanged. Actual dollar billing remains a separate unresolved measurement.
