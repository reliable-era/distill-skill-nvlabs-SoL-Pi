# G4 final results (Parts A, B, C)

Contract: [tests/goal.md](../../../goal.md) G4 (commits 049ab2a, 5b8e715). Descriptive measurement:
no gate, no early stop, nothing shipped. Scores: [results.json](results.json), produced by
[score.py](score.py). Raw runs stay outside the repository.

Model: Qwen3.8-27B through the shared route 127.0.0.1:8000 (FP8 and full precision treated as one
model by user amendment). Tokens per solve = all charged tokens, failures included, divided by
verified solves. `≥` = at least one charged request has no usage record; missing costs are not
imputed.

## Part A: NVlabs SoL-Pi on the Pi harness

Pi 0.85.1 with NVlabs/SoL-Pi at `1559b5cb`, unmodified, all four mechanisms on
([config](../g4/sol-pi.full-stack.json)); reducer helper model = the same route. Same tasks,
prompts, caps (60 requests, 1800 s) and graders as the Claude Code campaign. Runner:
[run_A.py](run_A.py) with the logging relay [proxy.py](proxy.py).

| Arm | Synthetic solved | Synthetic tokens / solve | SWE-bench solved | SWE-bench tokens / solve | Timeouts |
|---|---:|---:|---:|---:|---:|
| NVlabs SoL-Pi | 21/25 | ≥39k | 5/12 | ≥621k | 1 + 4 |
| NVlabs SoL-Pi + Karpathy | 19/25 | ≥56k | 5/12 | ≥473k | 0 + 4 |

- Not comparable on tokens with the Claude Code rows: the harnesses send very different system
  prompts and tool definitions on every turn. Cross-harness comparisons are informational only.
- 9 runs hit the 1800 s cap. Requests waited 300-700 s each in the shared queue during those
  runs, so the wall-clock cap was tighter in practice than in the Claude Code campaign.
- The Evidence-Preserving Reducer was enabled but never fired: none of the 90 test-command
  outputs reached its 4 KB threshold, so the helper model made 0 calls.
- Costs are lower bounds: Pi's client abandoned and retried some long-queued requests, whose
  usage was never returned.
- 7 SWE-bench grades first failed because the runner passed a four-issue dataset file lacking
  two issues; they were regraded with the full SWE-bench Verified file (identical records for
  the shared issues). One run (g4-A-037) recovered from a single HTTP 502 by Pi's own retry.
- `npm audit` in the upstream checkout reported advisories; the user chose to run it anyway.

## Part B: Terminal-Bench 2.0 (Codex 0.160.0)

9 sealed tasks × 3 rounds × 4 arms = 108 runs; caps 60 requests / 120 min / 16K output.

| Arm | Solved | Tokens / solve |
|---|---:|---:|
| No skill | 11/27 | ≥2.40M |
| Karpathy | 13/27 | **≥1.75M** |
| Ours | 12/27 | ≥2.34M |
| Both | **14/27** | ≥2.16M |

## Part C: SWE-bench Verified, fresh sample (Codex 0.160.0)

30 issues drawn with a recorded seed; 12 failed the official gold/no-op grader controls and were
excluded, leaving 18 issues × 4 arms = 72 runs. Same caps as Part B.

| Arm | Solved | Tokens / solve |
|---|---:|---:|
| No skill | **14/18** | ≥918k |
| Karpathy | 9/18 | **≥721k** |
| Ours | 13/18 | ≥903k |
| Both | 13/18 | ≥1.22M |

### Cost ratios (paired task-cluster bootstrap, 20,000 draws)

Ratio of tokens per solve; below 1 = fewer tokens. Lower-bound costs make these surrogates.

| Comparison | B point | B 95% interval | C point | C 95% interval |
|---|---:|---|---:|---|
| Ours / No skill | 0.975 | 0.46-2.49 | 0.983 | 0.67-1.69 |
| Ours / Karpathy | 1.342 | 0.67-4.16 | 1.252 | 0.61-2.41 |
| Both / No skill | 0.900 | 0.65-1.21 | 1.333 | 0.86-2.23 |
| Both / Karpathy | 1.239 | 0.76-2.07 | 1.699 | 0.89-3.27 |

Every interval includes 1: no arm is shown to be cheaper per solve than another.

## Infrastructure reruns and one deviation

- 29 B/C runs (6 B, 23 C) were killed by HTTP 502 responses from the route. As preregistered
  ([BC-retry-preregistration.json](../g4/BC-retry-preregistration.json)), each got one fresh
  attempt 2, run by [rerun_BC.py](rerun_BC.py) with Pi's unchanged cell runners. By user
  instruction, admission no longer waited for an idle queue.
- **Deviation.** Without that wait, 21 of the 29 attempts were dropped by Codex's 5-minute
  client idle timeout while their request was still queued. These 21 got an attempt 3 with only
  `stream_idle_timeout_ms` raised to 1800 s; two attempt-3 runs hit a 502 within a second and got
  an attempt 4. Pi's preregistration allowed only attempt 2. All attempts' costs are charged and
  the latest attempt is scored. Tables above use attempts 3-4; the preregistered attempt-2 view:

| Arm | B solved | B tokens / solve | C solved | C tokens / solve |
|---|---:|---:|---:|---:|
| No skill | 11/27 | ≥2.37M | 11/18 (1 ungraded) | ≥1.02M |
| Karpathy | 13/27 | ≥1.60M | 7/18 (1 ungraded) | ≥648k |
| Ours | 12/27 (1 ungraded) | ≥2.34M | 12/18 | ≥904k |
| Both | 14/27 | ≥2.07M | 10/18 (1 ungraded) | ≥1.35M |

Pi's [report-B.md](../g4/report-B.md) and [report-C.md](../g4/report-C.md) predate these reruns.
