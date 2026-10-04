# Native trace audit

One observed call event per native tool id/step. Read/test flags match explicit tool names/argument strings and can overlap. They are not a full semantic classification. AGY output often reports a byte/line summary, not actual returned text. Unknown output is null. No token overhead attribution or causality inferred.

| Harness | Arm | Calls | Explicit reads | Test commands | Skill-path calls |
|---|---|---:|---:|---:|---:|
| pi | none | 17 | 8 | 3 | 0 |
| pi | karpathy | 21 | 10 | 4 | 2 |
| pi | ours | 20 | 10 | 4 | 2 |
| pi | both | 24 | 12 | 4 | 4 |
| codex | none | 10 | 4 | 2 | 0 |
| codex | karpathy | 14 | 3 | 4 | 5 |
| codex | ours | 10 | 4 | 2 | 3 |
| codex | both | 13 | 2 | 4 | 3 |
| copilot | none | 14 | 8 | 1 | 0 |
| copilot | karpathy | 13 | 8 | 1 | 0 |
| copilot | ours | 15 | 8 | 1 | 0 |
| copilot | both | 16 | 9 | 2 | 0 |
| agy | none | 24 | 10 | 5 | 0 |
| agy | karpathy | 34 | 16 | 5 | 2 |
| agy | ours | 29 | 11 | 7 | 2 |
| agy | both | 32 | 18 | 4 | 4 |
| cursor | none | 25 | 8 | 2 | 0 |
| cursor | karpathy | 30 | 9 | 6 | 2 |
| cursor | ours | 22 | 9 | 2 | 2 |
| cursor | both | 21 | 12 | 3 | 7 |

Counts sum two reused synthetic tasks, one round. Paired per-task records and transcript hashes are in trace-audit.json. Complete token totals remain the trial collector’s responsibility.

The candidate is a development hypothesis only: shorten always-loaded guidance, avoid unnecessary process/output, and retain verification. These traces cannot prove any instruction caused the observed token gap. Do not promote or call it a winner before fresh public benchmark confirmation.
