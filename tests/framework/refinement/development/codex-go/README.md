# Codex public-task development screen

One Aider polyglot Go food-chain exercise, five frozen arms, one round. This is development/integration evidence, never held-out confirmation. No post-grade repair or retries. Tests and reference implementations are physically absent from the actor workspace. The official tests are restored in a separate network-disabled grader.

Backend: OpenAI ChatGPT OAuth, configured gpt-6.1-sol, native default effort. Recorded model seed: TBD; the seed controls schedule only. All skill arms use inline entrypoint text and read-only resources. Both is Karpathy plus the lean candidate, not shipped Ours. Token totals use the verified exclusive Codex terminal counter; actual subscription dollar billing is TBD.

Frozen campaign/plan include a five-attempt cap, 120 seconds per actor, and hashes for workspace, grader, image, and skills. Grader path adaptation is recorded in argv: framework mounts /grade; trusted grader source expects /grader. HOME/GOCACHE use disposable /tmp. Credentials are imported from auth.json alone into a dedicated temporary read-only volume, excluded from plan/logs, then removed.

Run collect.py after terminal completion for reproducible results and observed calls.

| Arm | Official tests | Reported tokens | Calls | Seconds |
|---|---|---:|---:|---:|
| none | Pass | 61433 | 4 | 38.6 |
| karpathy | Pass | 101214 | 6 | 66.1 |
| ours | Pass | 97443 | 6 | 54.0 |
| candidate | Pass | 97578 | 8 | 75.8 |
| both | Pass | 103654 | 6 | 81.8 |

The candidate used 58.8% more reported tokens than no skill in this single development task. It did not outperform shipped Ours (97,578 versus 97,443 tokens). No promotion or economic win is supported. All five attempts completed; no retries or timeouts.
