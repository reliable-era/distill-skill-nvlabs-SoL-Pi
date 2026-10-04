# Broader native development results

Thirty frozen actor-start slots; one round on three public development tasks. Twelve Flask repairs, six native agy Go exercises, and twelve terminal starts. Two terminal starts failed before model calls. No retries or promotion; sealed confirmation untouched.

## Verified task completion

| Configuration | Pi · Flask | Codex · Flask | agy · Go | Pi · Terminal | Codex · Terminal |
|---|---:|---:|---:|---:|---:|
| No skill | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| Karpathy | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| Shipped ours | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| Lean parent | 1/1 | 1/1 | 1/1 | TBD | 1/1 |
| No-reread candidate | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| Candidate + Karpathy (Both) | 1/1 | 1/1 | 1/1 | TBD | 1/1 |

agy No skill fetched public tests; its passing grade is exposed development evidence. Terminal TBD means startup/auth availability, not a task failure.

## Complete reported tokens per attempt

| Configuration | Pi · Flask | Codex · Flask | agy · Go | Pi · Terminal | Codex · Terminal |
|---|---:|---:|---:|---:|---:|
| No skill | 23,428 | 82,389 | 200,303 | 77,835 | 496,186 |
| Karpathy | 32,577 | 92,639 | 152,832 | 200,483 | 324,770 |
| Shipped ours | 29,029 | 66,343 | TBD | 83,932 | 231,951 |
| Lean parent | 38,296 | 132,404 | 145,196 | TBD | 261,263 |
| No-reread candidate | 41,779 | 88,212 | 206,546 | 189,311 | 180,561 |
| Candidate + Karpathy (Both) | 31,632 | 89,211 | 190,675 | TBD | 175,414 |

These are attempt costs, including failed tasks. Lower tokens with failed quality is not a win. Complete attempt usage is TBD for the agy provider-error/internal-timeout run; its observed partial SDK total 263,286 remains in raw records. Actual billing USD is TBD throughout.

The no-reread candidate does not beat all comparators: Flask +78.3% Pi/+7.1% Codex vs No skill; terminal Pi fails where Karpathy passes; terminal Codex saves 63.6% vs No skill but uses 2.9% more than Both. Do not promote. The next untested locate-first candidate replaces only the lean parent context-read bullet, based on saved trace diagnosis.

Pi uses observed `gpt-6.1-sol` with low thinking. Codex requests `gpt-6.1-sol`, native default effort; independently observed backend ID TBD. Native agy requests `gemini-3.8-flash-low`; observed backend ID TBD. Compare within each harness/task; no pooled cross-backend token ranking.

[Flask evidence](swe-flask/README.md), [agy evidence](agy-go/README.md), [terminal evidence](terminal-sanitize/README.md), [cross-harness diagnosis](trace-diagnosis.md), [Flask diagnosis](swe-flask/refinement-diagnosis.md), [frozen budget](../development-budget-broad.json). Resource delivery differs: terminal supplied inline text without supporting-resource mounts; Flask/agy mounted resources. Some terminal attempts retain only tracked diffs or an incomplete Git index snapshot; consult its replay audit. Before confirmation, enforce uniform resource delivery, private serialized credential refresh, and provider-only network access. One task per family and one round cannot establish generality or stability.
