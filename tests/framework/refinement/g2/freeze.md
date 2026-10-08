# G2 preregistration and frozen candidate

Contract: active G2 in `tests/goal.md`, user commit `1401e9a`. G1's negative
result at `f537bfa` stands unchanged. Standing bounded-window authorization is
explicitly extended to G2 by the user's new contract. No exclusive server time
is assumed. Supervisor policy remains applicable without shared-server changes.

Frozen candidate is an exact tree copy of G1 candidate 2; SKILL SHA256
`39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`.
Frozen Karpathy is copied from the same G1 frozen source. Complete tree hashes,
all closed G1 file hashes, source-task hashes, immutable image IDs, implementation
hashes, seeds and full schedule are in `plan.json`. No new mechanisms or skill
edits. Canonical remains untouched and cannot ship without user approval.

## Design and scheduling

Stage 1: original sealed nine Aider tasks, four arms, three rounds (108 runs).
Each round has its own recorded RNG seed, independently shuffled task order and
per-task arm order. The complete schedule is frozen before any model call.
Rounds do not interleave; each later round starts only after the earlier roster
completes and the round-1 gate is resolved. Bounded waves take at most the next
six remaining cells in schedule order. Wave fragmentation cannot change cell
identity, select outcomes, replace a task, or increase per-run caps.

Stage 2: original sealed nine Terminal tasks with the same 108-cell design,
independent family/round seeds and identical analysis. Eligible only after Aider
acceptance. Task IDs and schedule/analysis are frozen now; the conditional
Terminal execution adapter/resource manifest must be committed and verified
before any Terminal inference. This is local grader/isolation implementation,
not permission to retune, choose tasks, alter metrics or change arm order.

Direct `127.0.0.1:18001` only, Codex 0.160.0 and local Qwen3.8-27B-FP8.
Admission valid running <8 (waiting allowed), bounded backoff ≤600s.
60 requests / 7200 seconds / 16384 output tokens per run. Preserve start,
per-request and 30-second load records; retain heavy flags without exclusions,
load-selected reruns, adjustment or causal wall claims. Every window is separately
committed before inference; opening it retires any previous unused allowance.

## Frozen decision and analysis

Required pairs are **candidate/No skill, Both/Karpathy, candidate/Karpathy**.
Each needs complete tokens per verified solve ≤0.95 comparator, no fewer solves,
and paired task-cluster bootstrap 95% ratio interval upper endpoint strictly <1.
Both always uses this same frozen candidate plus the same frozen Karpathy.
Candidate/Both is **informational only**, even if it favors Both.

`analyze.py` includes every attempted cell's tokens, including failures/caps.
Resample nine task IDs with replacement, preserving all matched arms and all
rounds within each selected cluster; 20,000 deterministic replicates using the
family's frozen bootstrap seed. Nearest-rank 2.5/97.5 percentiles. Undefined
resampled ratios become +infinity, never disappear from the distribution; a
null endpoint means nonfinite/unverified and blocks acceptance. Point thresholds
use exact integer cross-multiplication. All-arm score tables also report ratios
against No skill; the three required pairs and candidate/Both get explicit
paired intervals. No-skill self ratio is 1 only when its solve-normalized cost
is defined. No pooled family estimate replaces separate-family gates.

After **all 36 Aider round-1 cells**, stop negative if candidate/No-skill point
ratio is undefined or >0.95, or candidate has fewer solves. No interval is needed
for futility and round 1 can never establish a win. Unknown cost/grade evidence
cannot resolve this check or support acceptance: attempt exact-artifact local
grader repair; if evidence remains unavailable, close inconclusive rather than
pretend the costs/solves are known. Only if round 1 passes futility run rounds 2/3.
If final Aider fails any gate, stop negative; do not run Terminal tasks.

Original trusted adapter/graders and source pins remain unchanged. Grader exit 0
requires positive original accepted-test evidence; exit 1 is solution rejection,
including compilation/missing-solution failures; infrastructure exit 2 is unknown,
not a quality failure. Tests/reference solutions never enter actor mounts. Final
work is captured before checking provider completion so infrastructure-interrupted
cells retain artifacts for grade-only replay. Never repeat a cell that reached
the model; only proven zero-model infrastructure attempts may be separately retried.

Quality uncertainty (descriptive Wilson intervals with dependence caveat),
per-round variability and native wall/solve are separate from token efficiency.
No USD claim. Report all costs/failures/unknowns and audit every explicit G2
requirement at closure. Green offline tests/provenance/controls are not savings.

## Offline validation

Six analysis-only mathematical tests cover required vs informational comparisons,
no early acceptance, quality-loss futility, zero solves, unknown costs, and
incomplete/duplicate roster rejection. These are not benchmark/provider mocks.
The controller initially refused an uncommitted implementation as intended;
no inference occurred. After the freeze commit, verify guarded compilation and
container-only Codex startup on the frozen image IDs before opening inference.
