# Corrected-runtime development: no baseline win

One reused public Go task, one newly frozen round, two harnesses, five configurations.
Both uses lean-tools plus Karpathy. Scheduling seed104 is not a model sampling seed.
All ten patches pass parent independent official tests. No actor retries/timeouts.

| Configuration | Pi reported tokens | Codex reported tokens |
|---|---:|---:|
| No skill | 11,429 | 62,164 |
| Karpathy | TBD | 65,766 |
| Shipped ours | 13,877 | 64,000 |
| Lean candidate | 12,544 | 63,481 |
| Lean candidate + Karpathy | 16,895 | 83,097 |

Lean candidate is +9.8% in Pi and +2.1% in Codex versus no skill. Do not promote.
Pi confirms GPT-6.1-Sol/thinking low; Codex config requests GPT-6.1-Sol but observed
backend ID remains TBD. Compare within each harness; effort differs across harnesses.
All actual dollar billing is TBD. Pi Karpathy's final assistant response failed
with content_filter and missing usage; a correct patch does not make its tokens free.

The old Codex grader wrapper lacked __file__ and failed before tests; original
records are preserved as ungraded infrastructure failures. Direct trusted
independent grading provides the authoritative patch outcomes, bound to original
result hashes. No model attempt was repeated to repair this infrastructure issue.

[Pi evidence](pi-go-v2/README.md), [Codex evidence](codex-go-v2/README.md),
[parent independent audit](independent-grade-audit-v2.json).
