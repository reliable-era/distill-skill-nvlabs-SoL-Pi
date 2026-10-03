# Token telemetry contracts

`terminal_usage` uses terminal snapshots and ignores streaming deltas. Unknown
counts remain `None`; they are never converted into zero-dollar runs. These are
schema fixtures and source checks, not authenticated agent observations. Every
installed client's first authenticated transcript still needs comparison with
its provider's usage report. Subscription dollars and external tool charges are
TBD regardless of token completeness.

| Agent | Supported source | Completeness rule |
| --- | --- | --- |
| Codex | One `turn.completed.usage` | Input minus cached input; explicit zero cache-write count required. Older missing write fields and nonzero writes remain incomplete until their input inclusion contract is verified. Multiple terminal events are ambiguous and rejected. |
| Pi | One `agent_end.messages`, assistant messages only | Sum per-message `input`, `output`, `cacheRead`, `cacheWrite` once. Require nonzero `totalTokens` matching their sum and a completed stop reason. Ignore duplicate representations in `message_end` and `turn_end`. |
| Claude Code | One `result.modelUsage` | Sum each model's four explicit counters once, including auxiliary models. Do not also add top-level `usage` or assistant events. |
| Gemini CLI | TBD | Streaming result `output_tokens` currently uses candidate tokens; its formatter omits thought-token breakdown. A terminal result does not by itself prove complete billable output accounting. |
| Copilot, OpenCode, Cursor, Hermes, OpenClaw | TBD | Usage adapter needs an authenticated transcript and a verified complete-run schema. |

Primary source checks (2026-10-03):

- [Codex exec events](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs): usage includes input, cached input, cache-write input, output and reasoning output. Reasoning is a subset of output, never added again.
- [Pi agent events](https://github.com/badlogic/pi-mono/blob/main/packages/agent/src/types.ts): `agent_end` contains the messages for the run.
- [Pi usage types](https://github.com/badlogic/pi-mono/blob/main/packages/ai/src/types.ts) and [OpenAI response normalization](https://github.com/badlogic/pi-mono/blob/main/packages/ai/src/api/openai-responses-shared.ts): exclusive uncached input, separate cache read/write, reasoning already included in output. Provider adapters initialize missing usage to zeros, so an all-zero placeholder is not evidence of a free run.
- [Claude SDK usage/result types](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/types.py): `ModelUsage` passes the CLI's camelCase counters through verbatim; `ResultMessage` supplies terminal per-model accounting.
- [Gemini stream formatter](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/output/stream-json-formatter.ts): aggregates prompt/candidate/cache counters, not a complete thinking breakdown.

These moving-source references describe the checked schemas. Runtime versions are
pinned in `agents.json`; unsupported differences remain TBD rather than silently
accepting a guessed schema. Incomplete/aborted runs still contribute their
observed counters when available through future adapters, and never qualify for
complete priced totals.
