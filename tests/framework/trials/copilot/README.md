# Copilot four-arm pilot

Same two held-out synthetic fixtures and four instruction configurations as Codex, one round. Native GitHub Copilot subscription backend with automatic model selection; cross-harness model equality is not assumed.

`campaign.json` / `plan.json` / `results/` preserve availability probes: the installed help advertised `gpt-5.4`, but this account rejected that model before inference. These are **availability failures, not skill quality failures**; use `availability.json` for classification and do not use that campaign summary as performance evidence.

`campaign-auto.json` / `plan-auto.json` / `results-auto/` contain the actual native automatic-model pilot. Explicit `auto` requests automatic routing; actual observed model is TBD unless transcript telemetry identifies it. Token or billing fields absent from the CLI remain unknown.

Credential isolation imports one OAuth token through a mode-0600 env-file outside the repository, with no host config/preferences. Actor and independent network-disabled grader use the shared pinned trial image. No model random seed is controlled.

```bash
python3 tests/framework/run.py freeze tests/framework/trials/copilot/campaign-auto.json --output /private/new-plan.json
python3 tests/framework/run.py run /private/new-plan.json --output /private/new-results --env-file /private/copilot.env
```

See `results-auto/summary.md` for actual pilot outcomes.

Real Copilot events identify automatically selected `gpt-6-luna`. Completed terminal `result` events expose `usage.premiumRequests`, API duration, session duration, and code changes, but no LLM token totals. `session.usage_checkpoint` carries native `totalNanoAiu` and last-call cache details; those cache details do not establish cumulative session tokens. `annotate.py` retains observed native quota values without assigning token or dollar prices.

All eight actual native-auto attempts finished: no skill 2/2, Karpathy 1/2, ours 2/2, both 2/2. Three 120-second cutoffs occurred in total (no skill 1, Karpathy 1, ours 1, both 0); actors can time out after a passing edit, so grade and timeout are separate. Automatic routing used `mai-code-1.1-flash` for one both-arm task and `gpt-6-luna` otherwise. This routing difference prevents a controlled causal skill claim. Temporary credential env-file was removed after execution.
