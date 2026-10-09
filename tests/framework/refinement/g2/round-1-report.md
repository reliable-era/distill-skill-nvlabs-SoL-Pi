# G2 Aider round1 score and futility gate

**Futility survived; no acceptance.** All36 unique cells completed; 830 requests,
≥25,189,801 tokens, 15 solves / 21 failures. Every original grade valid.
One K request cost remains unknown; explicit supervisor ruling is recorded
before computation in analysis-notes.md (cec6cb3). No estimate or model retry.

| Arm | Solves /9 | Tokens | Tokens / verified solve | Native wall seconds |
|---|---:|---:|---:|---:|
| none | 2/9 | 6,782,379 | 3,391,189.50 | 4100.15 |
| K | 3/9 | ≥7,225,667 | ≥2,408,555.67 | 5146.37 |
| candidate | 5/9 | 4,405,945 | 881,189.00 | 2848.80 |
| Both | 5/9 | 6,775,810 | 1,355,162.00 | 3329.07 |

| Comparison | Ratio | Paired bootstrap 95% interval | No fewer solves |
|---|---:|---|---:|
| candidate/none | 0.259847 | [0.122491, ∞ (undefined)] | True |
| Both/K | ≤0.562645 | [0.203381, 1.505999] | True |
| candidate/K | ≤0.365858 | [0.112484, ∞ (undefined)] | True |
| candidate/Both | 0.650246 | [0.362345, 1.283728] | True |
| K/none | ≥0.710239 | [0.325201, ∞ (undefined)] | True |
| Both/none | 0.399613 | [0.170632, ∞ (undefined)] | True |

K-denominator intervals describe conservative upper-bound surrogates, not
exact true-ratio intervals. K/none instead uses a lower-bound surrogate.
Undefined bootstrap replicates retained as +infinity, not dropped. Seeds,
20,000 task-cluster draws, nearest-rank endpoints and mathematical core unchanged.

Candidate/none ratio0.259847, 5 vs2 solves: the exact mandatory round1 point
and quality check passes. This does **not** establish savings or interval gates;
all three required intervals fail at round1. Continue independent rounds2/3
in preregistered order; no Terminal until final Aider acceptance.

Quality descriptive Wilson intervals and native wall totals are in the JSON;
one round cannot establish round variability or population quality equivalence.
Load flags stay unexcluded; no causal slowdown or USD claims. Original complete-
cost analysis remains separately unavailable (aider-round-1-original.json).
Raw audit is still incomplete; bounded analysis eligibility is explicitly separate.
