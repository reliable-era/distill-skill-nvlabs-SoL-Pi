# Shared local Qwen native feasibility

2026-10-04 initial read-only metadata inspection. Its first HTTP request was GET `http://127.0.0.1:8000/v1/models`, without credentials. No inference, server restart/configuration change, authentication refresh or model call.

Observed server `ykw-qwen38-dflash2-tp2` is running, host-networked, image label `lmsysorg/sglang:dev-cu12-qwen38-27b-dflash2`, immutable image ID `sha256:6305caa4b7bb7159ae4f079e24fdf628fafa5c208fe048ddfb44a8652e7c8efd`. Metadata advertises `Qwen3.8-27B-FP8`, owned_by sglang, max_model_len262144. The unauthenticated model listing works; this does **not** establish inference authentication, Responses support, streamed tool calls, usage completeness or thinking compatibility.

Pi1.0.0 frozen image documentation `docs/models.md` explicitly supports SGLang-compatible endpoints via models.json: provider-specific baseUrl, api `openai-completions`, apiKey and models list. A proposed fresh private-home configuration is provider `local-qwen`, baseUrl `http://<authorized host route>:8000/v1`, api `openai-completions`, apiKey `dummy-local-only`, model id `Qwen3.8-27B-FP8`. Native selection is `--provider local-qwen --model Qwen3.8-27B-FP8`; this does not need ChatGPT OAuth. Dummy auth is a local-server hypothesis, not proven by GET alone. Do not activate compatibility toggles based merely on the server name.

Codex0.160.0 supports native custom providers (`model_provider`, `model_providers.<id>.base_url`, env_key, wire_api="responses", requires_openai_auth=false, supports_websockets=false), documented in the [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) and exercised separately by the owned mock transport protocol. A fresh empty Codex HOME plus a custom provider and dummy environment key avoids reusing the ChatGPT OAuth route. **Its actual compatibility with this server is TBD:** GET models does not prove POST/v1/responses exists; advertising OpenAI chat completions/Anthropic alone is insufficient. No pinned-source evidence establishes a native chat-completions mode in this version; do not change wire_api to an assumed legacy chat setting or silently insert a replacement harness.

Host-network server localhost is not actor-container localhost. Hardened isolated actor topology additionally needs an explicitly authorized proxy/provider-network route to the existing server, without exposing host services or opening general internet. Existing mock proxy success cannot certify this real host transport. A future separately authorized, bounded readiness phase must validate exact server APIs/tool streaming/native usage and network policy before any comparison.

A feasible new comparison would freeze this explicit new backend/model consistently for all four arms, identical prompts/full resource sets/model options/limits and failure-inclusive accounting. It must stay separate from historical ChatGPT/subscription results. Local model economic measurement is reported native gross token traffic and wall time, with dollars TBD; no inherited cloud pricing assumptions. This does not narrow or satisfy the original five-harness objective by itself.

Additional bounded GET `/openapi.json` (<8MiB,10s) advertises POST `/v1/responses`, POST `/v1/chat/completions`, POST `/v1/messages` and model GET routes. Thus Codex's required route is advertised, though request/tool-stream compatibility remains untested. OpenAPI reports FastAPI version0.1.0; this is not a verified SGLang package version. Read-only server command metadata confirms max-running-requests1; it remains unchanged. Models/OpenAPI cannot establish current request idleness, so root scheduling confirmation/shared lock is mandatory.

Frozen Pi1.0.0 `openai-completions.js` lines1161–1184 reads prompt_tokens and cache breakdowns, subtracts cacheRead/cacheWrite from inclusive prompt, preserves completion_tokens (including reasoning), and returns totalTokens as the four exclusive categories' sum. Its initialization/default fallbacks produce zeros for absent fields, so arithmetic alone does not establish that SGLang actually reported cache counters or complete traffic. Capture and validate provider-specific usage before certification. Prepared-only `local-qwen-readiness-plan.json` has at most2starts/30seconds each and no execution authorization.

Two subsequent, separately frozen GET-only Docker transport attempts failed.
The first did not retain probe stderr; that logging defect was repaired while
preserving the consumed sources and plan. The second retained an HTTP response
read timeout on the allowed metadata request. The failing network hop is still
TBD; it does not establish a provider API incompatibility. Both attempts made
zero POST/model calls and verified owned container/network cleanup. Numeric
hop instrumentation is being prepared before another diagnostic.

The installed scheduler `/get_load` contract is source-verified in
[server observation](local-qwen-server-observation.json). At 06:36:06 UTC,
rank zero reported one active request and zero waiting requests. This is a
point-in-time sample, not an idle guarantee. Native inference must acquire both
existing inode-pinned locks and require zero requests on every reported rank;
unknown jobs must remain untouched. No local Qwen native inference has run.

Native SSE components now exist, but launch readiness remains incomplete.
The existing metadata proxy buffers response bodies and is unsuitable for
incremental SSE. A separate bounded streaming proxy and lifecycle runner are
being implemented; their offline tests do not prove real native tool behavior
or complete provider usage.

The subsequent AF_UNIX transport phase passed in 2.59 seconds. Two metadata
GETs completed; authority/path denial controls passed. Actual helpers ran at
1 CPU/512 MiB on one internal IPv4 bridge with no gateway and IPv6 disabled.
Only the trusted proxy mounted the private socket directory read-only; the
actor had no mounts. Socket, worker, container and network absence were verified.
See [Unix routing audit](local-qwen/unix-routing-audit.json). This resolves the
metadata transport gate. It does not certify native inference, SSE/tool behavior,
complete usage or current idleness. Earlier bridge failures remain preserved.
