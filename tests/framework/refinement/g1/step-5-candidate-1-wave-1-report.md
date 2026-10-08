# Step 5 — candidate 1, wave 1 completed

Six of the twelve preregistered matched development cells completed. This is
an intermediate wave report, not the completed screen or a savings result.
The worker terminated and all owned containers/network were independently
confirmed absent. The remaining six fixed cells must run under a new committed
bounded window; none of these completed model cells will be rerun.

| Task | Arm | Original verified result | Requests | Complete tokens | Native wall seconds |
|---|---|---|---:|---:|---:|
| HTML | No skill | Failed | 60 | 3,366,659 | 2290.22 |
| food-chain | Karpathy | Failed | 26 | 494,641 | 248.87 |
| TeX | Candidate | Solved | 50 | 2,799,220 | 1089.07 |
| HTML | Karpathy | Failed | 60 | 4,917,989 | 2609.93 |
| food-chain | Candidate | Failed | 22 | 401,684 | 184.18 |
| TeX | Candidate + Karpathy | Failed | 60 | 3,867,730 | 884.77 |

Inventory: **278 requests / 15,847,923 complete tokens, one solve / five
failures, zero unknown-cost cells**. This inventory is not a pooled performance
comparison with calibration. All provider receipts passed direct18001 and
200/EOF accounting checks. Original grader evidence is available in all six
cells; Go quality was checked from original JSON pass/fail test events.

HTML / No skill, HTML / Karpathy and TeX / Both reached the fixed 60-request
cap. Their failures and full costs remain included. Caps remain
60 requests / 7200 seconds / 16384 output tokens for every arm; no budget raise
or outcome-selected retry. Load flags and native wall times remain descriptive,
without adjustment or a causal slowdown claim.

Evidence: `screen-candidate-1-wave-1/calibration-result.json`,
`screen-candidate-1-wave-1/wave-completion-audit.json`, and
`mechanisms/candidate-1-screen-audit.json`. The independent audit explicitly
reports an incomplete screen: all ratios and quality comparisons remain
unavailable until the six fixed wave-2 cells have complete, valid evidence.
No sealed model call, winner freeze, canonical edit or promotion occurred.
