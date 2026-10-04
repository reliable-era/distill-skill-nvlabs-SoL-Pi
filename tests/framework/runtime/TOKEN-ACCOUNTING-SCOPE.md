# Native token accounting scope

Read-only audit, 2026-10-04. No model/authentication calls or frozen-data changes. **Pi/OpenAI and Codex cache arithmetic is supported; universal main/helper/compaction completeness is a separate gate.** Reported tokens are not subscription dollars or all external-tool costs.

## Provider overlap

[OpenAI's usage documentation](https://developers.openai.com/api/docs/guides/agents-api/observability) identifies cached tokens as part of input and reasoning tokens as part of output. The [Responses schema](https://developers.openai.com/api/reference/typescript/resources/beta/subresources/responses/methods/create) provides the corresponding breakdown. Gross traffic is inclusive input plus inclusive output, not input plus cache plus output plus reasoning. Provider-specific adapters must be checked individually; this does not settle Antigravity cache semantics.

## Pi: verified normalization, bounded scope

Offline inspection of frozen image `sha256:d6d79bfad41b1fbac8288fc90fbc5d0412851fa355fcb9efcddae06531d2fd70` reports Pi **1.0.0**. Its installed `@earendil-works/pi-ai/dist/api/openai-responses-shared.js`, lines 440–453, normalizes input as `max(0, input_tokens - cached_tokens - cache_write_tokens)`, retains output, and separates cacheRead/cacheWrite and reasoning. Provider total remains `response.usage.total_tokens`. Therefore summing normalized input + output + cacheRead + cacheWrite restores gross input/output exactly once. Reasoning is already in output and must not be added again. Current host Pi 1.0.1 agrees on that mapping, but the frozen-image inspection is the historical evidence.

`tests/framework/accounting.py` sums assistant usages from a unique `agent_end.messages` record and requires each positive total to equal those four components. It rejects absent fields and error/aborted placeholders. Saved `trials/pi_openai` eight runs contain 57 assistant usage messages: all 57 satisfy the equality; no terminal nonassistant message carries usage, and no compaction event is present. Their actual API is openai-responses/provider openai/model gpt-6.1-sol. This validates arithmetic for the recorded assistant calls, not every conceivable provider or auxiliary call.

Important scope gap: frozen Pi compaction source returns separate summary `usage` (`core/compaction/compaction.js` lines 538, 696–719), while the collector only reads assistant messages. Current native session code also attaches nested-tool usage to toolResult messages, which this collector ignores. Thus assistant-only accounting cannot be called universally complete when compaction or nested/helper traffic occurs. These mechanisms were not observed in the eight pilot terminal records. Future scope certification must capture session compaction/branch-summary and toolResult/nested-call usage, reconcile their representation with assistant totals, and include each actual model call once. Do not blindly add aggregates that already contain nested usage.

## Codex: inclusive input split, terminal scope

Saved eight `trials/codex` runs each contain one `turn.completed`. All have cached_input_tokens <= input_tokens and explicitly zero cache_write_input_tokens. Example recorded terminal: input 78,275, cached 70,016, output 774, reasoning output 11. Collector normalization gives uncached 8,259 + cached 70,016 + output 774 = **79,049**, with no second addition of reasoning. The zero-write requirement avoids inventing missing cache-write counts or mishandling a nonzero inclusive category.

The native [Codex token model](https://github.com/openai/codex/blob/main/codex-rs/tui/src/token_usage.rs) subtracts cached input to calculate noncached input. Its displayed blended total can exclude cache; that display is not the gross traffic measure used here. Source and native session usage distinguish cumulative total_token_usage from last_token_usage: repeated cumulative snapshots must never be summed. The collector's unique-terminal requirement deliberately rejects ambiguous multi-terminal streams. A resumed session must not be assumed to have fresh-run totals.

Scope gate remains: a unique root terminal is not, by itself, proof that independent native helper sessions or separately recorded compaction requests are included. Check actual pinned native source/rollouts for those paths and reconcile per-session call ledgers before classifying an auxiliary-heavy run as fully complete. Assistant/agent message item names alone do not demonstrate subagent execution. This audit does not assert that current upstream main source is bit-for-bit the frozen 0.160.0 binary implementation.

## Required completeness classifications

Distinguish (1) arithmetic-valid recorded main-stream totals, (2) complete gross model traffic across main/helper/compaction/retries, and (3) actual billing. A good terminal and cache split can establish the first without proving the other two. Preserve raw fields and scope labels. Interrupted/missing terminal traffic stays unknown/lower-bound; no successful grade repairs accounting. Provider-dependent cache semantics require an explicit contract rather than assuming cache is always additive or always a subset.

Pi/Codex pilot arithmetic is unchanged by this investigation. No candidate effectiveness, savings, or additional accounting-complete primary-harness certification is inferred from these offline checks. Copilot's native usage-file gate is documented separately; Antigravity's cache/thinking ambiguity is under a separate investigation.
