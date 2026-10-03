# Held-out results by diagnostic family

Each cell shows verified solves out of three rounds, followed by total reported query-pipeline tokens. Failed attempts are included. Latest means the frozen latest SoL-Pi; the combined arm uses that same latest version. These five related synthetic families do not establish broad repository performance.

| Family | No skill | Latest SoL-Pi | Karpathy | Karpathy + latest SoL-Pi |
|---|---:|---:|---:|---:|
| d1_large_log | 3/3; 612,731 | 3/3; 769,286 | 3/3; 691,278 | 3/3; 809,984 |
| d2_interfaces | 1/3; 623,207 | 2/3; 773,271 | 0/3; 758,384 | 2/3; 835,157 |
| d3_stale_resume | 3/3; 589,940 | 3/3; 1,002,345 | 3/3; 811,039 | 3/3; 739,528 |
| d4_integrated_failure | 3/3; 639,061 | 3/3; 651,135 | 3/3; 700,795 | 3/3; 902,466 |
| d5_small_control | 3/3; 376,852 | 3/3; 441,706 | 3/3; 465,024 | 3/3; 520,298 |

Latest SoL-Pi uses more total tokens than baseline in every family. The sole correctness difference is the interface family: latest and combined solve two rounds, baseline one, and Karpathy none. On the other four families all configurations solve every round, with baseline using the fewest tokens in each family. This is a descriptive configuration comparison; it does not identify which individual skill instruction caused a difference. The stale-continuation family has the largest latest-versus-baseline token increase (about 69.9%).

Source: `../audit/current.json`, complete 60-cell held-out stage. Schedule seeds 42/73/101 do not control model sampling.
