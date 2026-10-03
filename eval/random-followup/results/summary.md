# Random small follow-up

Qwen3.8-27B-FP8; Claude Code 2.1.286. Two randomly selected new easy issues, four configurations, two scheduling rounds. Scheduling seeds do not control model RNG.

Graded: 16/16. Complete.

## Correctness

| Task | No skill | SoL-Pi (ours) | Karpathy | Both skills |
|---|---:|---:|---:|---:|
| django__django-11964 | 1/2 | 2/2 | 1/2 | 2/2 |
| sympy__sympy-12481 | 2/2 | 2/2 | 2/2 | 2/2 |

## Token traffic across all attempts

| Task | No skill | SoL-Pi (ours) | Karpathy | Both skills |
|---|---:|---:|---:|---:|
| django__django-11964 | ≥3,116,597 | 2,376,995 | ≥3,569,075 | 3,305,259 |
| sympy__sympy-12481 | 2,911,593 | 1,875,082 | 1,816,843 | 2,599,409 |

## Aggregate efficiency and stability

| Configuration | Solves | Tokens / solve | Model timeouts | Incomplete usage runs |
|---|---:|---:|---:|---:|
| No skill | 3/4 | ≥2,009,397 | 1 | 1 |
| SoL-Pi (ours) | 4/4 | 1,063,019 | 0 | 0 |
| Karpathy | 3/4 | ≥1,795,306 | 1 | 1 |
| Both skills | 4/4 | 1,476,167 | 0 | 0 |

Costs include failed attempts. ≥ indicates incomplete recorded lower bounds and cannot establish savings. Aggregate tables use only complete matched task-rounds. Two task clusters cannot establish broad superiority. Public repair retrieval limits unaided attribution. See the retrieval audit and full report.
