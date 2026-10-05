# Restart-free accounting alternative — offline proposal

`prospective_reasoning_adapter.py` is NOT wired into any broker. No inference calls or shared-service changes were made. Historical eligibility remains unchanged.

Both live replicas' `scheduler_components/output_streamer.py` hashes match the reviewed source (`4f069f…90ecaa`). Read-only command inspection showed DFLASH with eight speculative draft tokens on each replica.

The proposal applies the reviewed emitted-reasoning bound in an owned evaluation adapter rather than modifying shared SGLang. It accepts only the recognized Qwen/source/peer/length-cap shape, literal EOF, a unique terminal, and overshoot1..7. The initial offline bound8 was tightened: an eight-token committed block can discard atmost7tokens because the unfinished prefix leaves at least one emitted position. Worker,utilities,Req andTriton-kernel hashes nowjoin the sourcepins. It changes only the derived reasoning subtype. The unchanged strict cost validator must accept the derived copy, rejecting other malformed totals/cache/terminal fields. Raw events and raw validation failures remain untouched and separately visible.

Offline diagnostic on the saved failed receipt: raw reasoning8193/output8190 remains invalid; the derived subtype8190 validates, with unchanged input8067/output8190/gross16257. Generation remains incomplete. This is NOT retrospective repricing or proof that historical costs are complete.

The legacy `protocol_valid` field in the derived cost result covers its existing numeric output-cap check, not native raw-provider conformance. The proposal explicitly records raw-provider protocol validity=false. Neither dollar billing nor speculative wasted compute is measured by this subtype correction.

## Remaining deployment gates

- Bound reviewed in `dflash-reasoning-bound-verification.json`:128exact CPU greedy commitcases and352exactReq boundary/think-end cases;min(rawreasoning,emittedoutput) equals expectedemittedreasoning throughout. Sampling/selector successfulscatter andTriton in-range counterprovide structural<=8commit bounds;GPU sampling/Triton were NOTexecuted. Bothreplicas match all reviewedsourcehashes. Adaptertests15pass,includingrejectingovershoot8. SSE/SDK integration andprospective conformance remainunverified.
- Freeze a separate prospective protocol: adapter hashes, source/config pins for both peers, raw and derived journals, strict raw failure retention, complete EOF accounting, no retries/fallback/continuation, and fresh cohort budgets.
- Integrate owned broker handling without rewriting archived responses or altering frozen old validators. Preserve SDK-facing stream content/status and label any metadata derivation explicitly.
- Freeze backend-matched comparison routing and native actor/capture/trusted-grader integration.
- Run only bounded, separately charged conformance/inference authorized by that new plan. Stop on unrecognized source/config/receipt shapes.

Do not use this proposal as a launch authorization, performance result, completed accounting gate, or final-goal certificate. It is a local-only path to review, avoiding shared-service restarts if the prospective gates are met.
