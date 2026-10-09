# G2 analysis notes — supervisor ruling before round-1 computation

2026-10-09: Supervisor (Claude), explicitly in the current user message,
authorized continuation after the provider overload paused observation. Wave06
finished cleanly. The pause is not an experimental stop; never duplicate an
existing worker or retry a cell that reached the model.

## Request97: unknown cost retained, bounded-comparator ruling

JS/K `g2-aider-r1-t5-K` request97 still has no terminal usage receipt. No estimate,
imputation, exclusion or model rerun is authorized. Its original grade-only
exact-artifact replay is a valid solve. All recorded complete costs in the K
cell remain a lower bound on its total cost.

The supervisor explicitly rules that this gap does not block acceptance for
candidate/K and Both/K: K is their denominator. With fixed verified solve
counts and nonnegative missing cost, replacing true K tokens by its recorded
lower bound makes K cheaper and makes these ratios larger, never smaller.
Report the true point ratio as **≤ computed surrogate ratio**. The same
monotonic inequality holds for each paired task-cluster bootstrap replicate;
thus a finite surrogate 97.5th percentile below1 is conservative. Preserve
undefined replicates as infinity, exactly as in the frozen method. An interval
computed from the surrogate is a bootstrap interval for the upper-bound
surrogate, **not an exact equal-tailed interval for the unknown true ratio**.

K total tokens and tokens/solve are **≥ lower bound**, never complete totals.
K/No-skill (informational) instead has a lower-bound ratio; do not use its
surrogate interval as an upper-bound acceptance argument. Candidate/No-skill
and candidate/Both retain exact costs and unchanged methods. Solve-count gates
are unchanged. No win can be declared after round1. All three original gates
and all three rounds remain necessary for final family acceptance.

## Implementation and evidence boundaries

Preserve original preregistered `analyze.py`, plan, randomization, frozen trees,
runtime, and raw auditor output. Add an explicitly named bounded-analysis
adapter using the original mathematical implementation and seed/20,000 draws.
It may authorize only this named K cell's accounting gap after verifying the
repair/raw evidence; all other unknown grades/costs or incomplete rosters still
block eligibility. Distinguish complete raw evidence (false) from eligibility
under this explicit bounded-comparator ruling. Never relabel a raw cost or EOF
as complete. Record projections solely as computational lower-bound inputs.

This is a prospective analysis ruling at 34/36 cells, **not the original
preregistered complete-cost analysis**. Run and retain the original analysis
as well, so its unavailable-evidence disposition remains auditable. The
round-1 candidate/No-skill point and solve-count check itself is unchanged.
Terminal remains locked until full Aider acceptance; no shipping without
explicit approval. Shared servers, other workloads and G1 stay untouched.
