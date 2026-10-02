### Resolution rate (solved / runs)

| Benchmark | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| Stress suite (5 cases) | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% | 100% (15/15); by round 100%/100%/100% |
| SWE-bench Verified (12 tasks) | 79% (19/24); by round 75%/83% | 79% (19/24); by round 83%/75% | 79% (19/24); by round 75%/83% | 79% (19/24); by round 75%/83% |

### Tokens (input + output, all runs incl. failures)

| Benchmark | Metric | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|---|
| Stress suite (5 cases) | mean tokens / run | 209k | 194k | 226k | 244k |
| Stress suite (5 cases) | mean output tokens / run | 3k | 3k | 4k | 5k |
| Stress suite (5 cases) | **tokens / verified solve** | 209k | 194k | 226k | 244k |
| Stress suite (5 cases) | mean requests / run | 10.2 | 9.1 | 10.8 | 11.5 |
| Stress suite (5 cases) | mean wall min / run | 0.8 | 0.9 | 1.6 | 0.9 |
| SWE-bench Verified (12 tasks) | mean tokens / run | 2,022k | 1,898k | 1,821k | 1,890k |
| SWE-bench Verified (12 tasks) | mean output tokens / run | 24k | 28k | 28k | 26k |
| SWE-bench Verified (12 tasks) | **tokens / verified solve** | 2,553k | 2,397k | 2,300k | 2,388k |
| SWE-bench Verified (12 tasks) | mean requests / run | 44.4 | 43.8 | 41.4 | 42.3 |
| SWE-bench Verified (12 tasks) | mean wall min / run | 14.3 | 12.7 | 12.7 | 13.0 |

### Behaviour

| Benchmark | Metric | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|---|
| Stress suite (5 cases) | false completion claims | 0 | 0 | 0 | 0 |
| Stress suite (5 cases) | hit turn/time limit | 0 | 0 | 0 | 0 |
| Stress suite (5 cases) | runs that invoked a skill | 15 | 0 | 15 | 15 |
| SWE-bench Verified (12 tasks) | false completion claims | 2 | 0 | 3 | 2 |
| SWE-bench Verified (12 tasks) | hit turn/time limit | 7 | 9 | 5 | 8 |
| SWE-bench Verified (12 tasks) | runs that invoked a skill | 23 | 0 | 24 | 24 |

### Paired differences (matched task × round; bootstrap 95% CI)

| Benchmark | Comparison | n | Δ resolve rate [CI] | wins/losses | Δ tokens / run [CI] |
|---|---|---|---|---|---|
| Stress suite (5 cases) | sol-pi - baseline | 15 | +0% [+0%, +0%] | 0/0 | 15k [-20k, 54k] |
| Stress suite (5 cases) | karpathy+sol-pi - karpathy | 15 | +0% [+0%, +0%] | 0/0 | 18k [-19k, 50k] |
| Stress suite (5 cases) | sol-pi - karpathy | 15 | +0% [+0%, +0%] | 0/0 | -17k [-50k, 24k] |
| SWE-bench Verified (12 tasks) | sol-pi - baseline | 24 | +0% [-12%, +12%] | 1/1 | 124k [-157k, 414k] |
| SWE-bench Verified (12 tasks) | karpathy+sol-pi - karpathy | 24 | +0% [+0%, +0%] | 0/0 | 69k [-218k, 380k] |
| SWE-bench Verified (12 tasks) | sol-pi - karpathy | 24 | +0% [+0%, +0%] | 0/0 | 201k [-68k, 447k] |

### Per task: Stress suite (5 cases) (solved/runs, mean tokens)

| Task | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| s1_small_fix | 3/3, 137k | 3/3, 123k | 3/3, 164k | 3/3, 231k |
| s2_large_log | 3/3, 170k | 3/3, 162k | 3/3, 194k | 3/3, 273k |
| s3_fabricated_quote | 3/3, 280k | 3/3, 289k | 3/3, 279k | 3/3, 236k |
| s4_edit_then_fail | 3/3, 236k | 3/3, 210k | 3/3, 288k | 3/3, 235k |
| s5_continuation | 3/3, 222k | 3/3, 186k | 3/3, 204k | 3/3, 243k |

### Per task: SWE-bench Verified (12 tasks) (solved/runs, mean tokens)

| Task | 1 sol-pi | 2 baseline | 3 karpathy | 4 karpathy+sol-pi |
|---|---|---|---|---|
| astropy__astropy-7336 | 2/2, 1,052k | 2/2, 568k | 2/2, 547k | 2/2, 355k |
| django__django-11149 | 2/2, 3,207k | 2/2, 2,165k | 2/2, 2,832k | 2/2, 3,326k |
| django__django-11292 | 2/2, 2,756k | 2/2, 2,978k | 2/2, 2,653k | 2/2, 3,054k |
| django__django-13128 | 2/2, 2,788k | 2/2, 2,189k | 2/2, 1,885k | 2/2, 2,365k |
| django__django-14155 | 2/2, 1,637k | 2/2, 2,266k | 2/2, 979k | 2/2, 1,961k |
| django__django-14752 | 2/2, 966k | 2/2, 677k | 2/2, 640k | 2/2, 596k |
| django__django-15380 | 2/2, 916k | 2/2, 1,171k | 2/2, 947k | 2/2, 866k |
| pytest-dev__pytest-8399 | 2/2, 2,415k | 2/2, 2,010k | 2/2, 1,770k | 2/2, 1,974k |
| sphinx-doc__sphinx-7440 | 0/2, 2,705k | 0/2, 2,958k | 0/2, 3,070k | 0/2, 2,624k |
| sphinx-doc__sphinx-8265 | 0/2, 2,327k | 0/2, 2,770k | 0/2, 3,014k | 0/2, 2,290k |
| sympy__sympy-16886 | 2/2, 293k | 2/2, 187k | 2/2, 470k | 2/2, 208k |
| sympy__sympy-19040 | 1/2, 3,197k | 1/2, 2,835k | 1/2, 3,043k | 1/2, 3,063k |
