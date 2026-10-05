# Observed timeout-accounting gap and bounded recovery proposal

## Actual evidence

Active Terminal development plan: `ed8e5e60b8e7f5fb1a901cf3f90c9b24a2e3a3d2e682c3d5042b7de96fb22238`.

- No skill reached its16POST cap, but captured work passed the original grader. All16request costs are complete:413911provider tokens. Native terminal reconciliation is missing.
- Karpathy reached its actor deadline at589.797seconds. Captured work also passed, but at least one request has incomplete usage.203972tokens are a **lower bound**, not total cost. Its missing cost must not be replaced by zero.
- The runner safely graded stopped work and continued to the next fixed arm. This is the intended partial-quality fallback; no actor was retried.

The current stage remains frozen and active. Do not change it, reconstruct missing exact usage from guessed tokenization, or pair a favorable retry with old controls. Unknown costs prevent a complete all-comparator economy inference, although independent quality grades remain usable.

## Next critical-path question

After all four cells finish and are audited, decide whether a **single prospective accounting repair** is warranted before preparing the nine new benchmark environments. This is a concrete observed blocker, not permission for general harness expansion.

A possible fallback is a bounded **issued-request completion grace**:

1. Keep the actor wall/request caps uniform and unchanged. At cutoff, stop only the owned actor and preserve its immutable stopped state.
2. Keep only the already-issued provider request alive for a separately declared finite grace (for example180seconds). Issue no new model requests, tool calls, or actor continuation.
3. Decouple a disconnected native/proxy consumer from the provider reader: continue preserving the upstream response and final usage if available. A client write failure alone must not silently erase the remaining provider receipts.
4. Require EOF, one valid usage terminal, exact counters, and owned-worker cleanup before reporting cost complete or starting another actor. If grace expires, abort only the owned connection, retain unknown cost, and stop/continue only under the frozen policy.
5. Count all provider generation, including output that the stopped actor never consumed. Report actor execution, extra accounting grace, scheduler wait and total elapsed time separately. The policy changes issued-request cost measurement and therefore requires a **new matched cohort**, not pooling with the current one.

This is not a retry and cannot recover the current already-closed request. It may consume additional server time and generated tokens without improving quality; the tradeoff must be measured and bounded. It does not guarantee complete usage under arbitrary stalls.

## Review/tests required before any implementation launch

- Offline mocked upstream tests for late headers, client disconnect, complete terminal usage after cutoff, grace expiry, duplicate/missing usage, provider errors, and exact request caps.
- Verify that no actor receives verifier feedback or post-cutoff model output, and no actor remains able to modify the captured state.
- Verify frontend/broker timers, parent drain logic and response-byte limits implement the same declared deadlines; test cross-layer behavior, not only helper functions.
- Confirm no untracked SDK retries or alternate model route; native missing reconciliation remains separate from complete provider receipts.
- Freeze a finite total stage budget and exact authorization. At most one matched repair panel is proposed; failure does not authorize indefinite timeout increases or actor retries.

## Subsequent verified actions

The original Terminal panel completed and audited; candidate failed, controls passed, and both incomplete costs remain lower bounds. Original requests explicitly set `store=false`. Read-only retrieval of the unique owned response.created IDs returned404 for both requests (no modelPOSTs), recorded in `cache-recovery-review.json`; no cost recovery was claimed.

A separate patch-first matched cohort is now launched under plan1fc1b1b1c78b8e08685c73bc03aaf01ffccc8bff83d9137732ffa21c6a9780f2. It uses240s passive issued-request grace (110completed service observations:max214.9s,p95 87.9s), unchanged600s actors,16POST each and no continuation/retries.53offline tests pass, including cross-layer late-header/disconnect receipt retention. Source review verifies capture→harvest→grade. Production accounting remains pending; old missing costs are not rewritten. See `patch-first-prelaunch-review.json` and active process metadata. No additional repair panel or indefinite timeout increase is authorized.
