# G2 requirement-to-evidence checklist (execution ongoing)

This is a verification map, **not a completion or acceptance audit**. Final
closure must inspect each evidence surface, fill the remaining statuses and
verify the applicable conditional branch. Green startup/source/cost audits do
not prove the statistical acceptance requirements.

Current checkpoint: all36 round1 cells audited; exact candidate/None futility
survived (ratio0.259847, 5 vs2 solves), never early acceptance. Historical
first18/wave04 inventory below is superseded by audits/aider.json and the
round1 report. Independent round2 now started. Supervisor explicitly authorized
the request97 K lower-bound treatment in analysis-notes.md before the gate;
original complete-cost analysis is retained. Final audit must distinguish
unknown raw cost from conservative denominator-bound eligibility.

## Deliverable and criteria

Deliver a final accepted/negative/inconclusive **G2 experiment result**, with an
all-arm score table per attempted family. G1 remains closed and unchanged.
The preregistered round-1 futility branch can legitimately end G2 negative after
36 Aider cells, without the remaining 72 Aider cells or any Terminal calls.
Otherwise complete three independently scheduled Aider rounds (108 cells),
apply all three gates, and run the same 108-cell Terminal design only if Aider
passes. Negative/inconclusive experiment disposition is not a savings win.

| Explicit requirement | Evidence to inspect | Current verification status |
|---|---|---|
| New contract 1401e9a, separate from closed G1 f537bfa | Active G2 section of `tests/goal.md`; `freeze.md`; git diff since 1401e9a | Contract read completely; G1 results unchanged |
| Frozen candidate 2 SHA 39f7b309..., no edits/new candidates | `plan.json` full skill-tree hashes; `frozen/candidate`; original G1 candidate SHA | Checked before every wave/prompt; repeat at closure |
| Frozen Karpathy; Both is this same candidate plus Karpathy | Plan arm-skill mapping; per-cell private skill trees and exact prompt audit | First 18 completed cells independently verified |
| Exactly nine original sealed Aider tasks, no substitution | Original selection SHA; full 108-cell Aider schedule; task/source manifest checks | Preregistered; first 18 cells verified |
| Independent rounds and randomized per-task arm order | Plan family/round seeds, independently shuffled schedules; recorded source generator | Three schedules frozen; later rounds not yet eligible |
| Preregister seed/schedule/analysis before first model call | Commit 75ab79c; plan hashes; introducing commits and first provider UTC | Freeze committed before first window/call |
| 36-cell futility: candidate/None ≤.95 and no fewer solves | Complete round1 roster; original analysis and explicit bounded adapter; `analysis/round-1-gate-check.json` | Passed exact point/quality gate; no early win; notes cec6cb3 committed before computation |
| No early declaration of acceptance | Analysis requires rounds [1,2,3] for `family_accepted` | Mathematical test verified; no acceptance claim |
| Required final candidate/None, Both/K, candidate/K gates | Frozen analysis comparison set; each point ≤.95, paired 95% upper <1, solves ≥ comparator | Unmeasured until applicable complete panel |
| Candidate/Both informational only | Analysis `gate: false`; explicit report comparison | Mathematical test verifies it cannot veto acceptance |
| Paired task-cluster bootstrap | Frozen 20,000 replicates, seed by family, task resampling retaining all arms/rounds, nearest-rank 95% endpoints | Script preregistered/tested; actual analysis pending |
| Include failures, caps, unknowns, no favorable replicate filtering | All raw wave rows/receipts; +inf undefined bootstrap samples; no cost/grade borrowing | All36 retained; one request97 K cost unknown, not estimated/excluded/retried |
| Unknown/undefined evidence and explicit K-bound ruling | Original flags preserved; named K-only adapter, all other unknowns block; null nonfinite endpoints | Eleven math tests; unknown K denominator supports only conservative ≤ ratios/surrogate upper quantiles, never exact-cost claims |
| Conditional sealed nine-task Terminal stage only on Aider pass | Frozen Terminal selection SHA/schedule/analysis; Aider final gate; separately committed execution adapter/resources | Locked; no Terminal model attempt |
| Codex 0.160.0 and binary SHA; local Qwen3.8-27B-FP8 | Four-image offline checks, wave launch identities, source-backed normalized receipts | Verified for completed waves; retain future evidence |
| Direct18001 only; no fallback/shared-server changes | Every receipt backend; source/command fingerprint; git and operation scope audit | First 18 cells verified; no interventions |
| Admission running<8, waiting allowed; backoff≤600s | Per-cell admission JSON and start UTC/window latest-start; frozen queue helper | First 18 cells verified; no exclusion for heavy load |
| Per-run 60 requests / 7200s / 16384 output | Runtime source hashes, native invocation, request payload caps, deadline/cap records | First 18 cells verified; no budget changes |
| Load at start, before requests and every30s | Admission, receipt queue-before records, per-cell load-samples JSON | Runtime records retained; final temporal coverage audit still needed |
| Standing authorization and separately committed bounded windows | Contract/freeze, windows 01–04 introducing commits, immutable screen-window JSON | Four committed before use; previous unused allowances retired |
| One current worker; verified waits; no duplicate/rescore retries | Worker handles, launch/result files, durable unique cell IDs, PS observations | All round1 workers terminal; one round2 worker live; no model retry |
| Only separately recorded zero-model infrastructure retries allowed | Every native-start/POST roster and any future classification artifacts | No such retry needed or made so far |
| Original trusted graders and actor isolation | Source SHA, private manifest/support/tests, actor inspect guard, original verifier logs | First 18 cells verified; Queen-attack actual original failures diagnosed without edits |
| Grade-only repairs replay captured artifacts, never actor inference | Captured-work hashes, original grade/repair sidecar and audit_repairs.py | JS/K exact-artifact replay passed9 original tests; raw failure/null grade retained, zero new model requests |
| JS dependency/official runner provenance | `javascript-resource-provenance.json`, cache digest before wave04, read-only grader mount | Recorded before first JS cell; recheck after grading |
| Preserve all failures/costs/source/runtime/skill/image provenance | Raw wave results, launch source hashes, private ledgers/native/captures/verifiers, independent `audits/aider.json` | First three wave completion audits pass; fourth not yet terminal |
| Independent cleanup and no unknown workload cancellation | Wave completion audits, Docker prefix-specific absence checks, specific PID terminal observations | All seven round1 waves absent; never alter shared/unknown workloads |
| All-arm family scores and ratios with paired 95% intervals | Final report plus frozen analysis JSON and its input audit hash | Pending; never pool G1/calibration/tuning cohorts |
| Quality uncertainty, round variability and wall separate; no USD | Analysis Wilson caveat, round solves/tokens, audited native wall, final readable report | Data available for completed cells; final reporting pending |
| No canonical shipping without user approval | Canonical SHA/diff at closure; accepted-only recommendation if applicable | Canonical unchanged; no shipment authorized or made |
| G1 result/archive and excluded Copilot/agy/Cursor/mock paths untouched | Protected G1 hashes; scoped git diff and original archive/canonical hashes | Checked throughout; repeat final integrity audit |
| Commit stages, short STATUS, final prompt-to-artifact audit | Logical wave commits, `tests/STATUS.md`, final audit mapping and score report | Ongoing; final audit not yet performed |

## Closure verification policy

At closure inspect actual rows/receipts/original grades rather than treating an
empty or partial audit as success. Reconcile unique identities with the exact
applicable schedule, raw ledger POST counts, complete reported tokens, admitted
start times, caps, load coverage, all source/skill/resource identities and owned
cleanup. Recompute frozen analysis from the independently audited roster. Report
infinite/undefined ratios and unknown grades/costs honestly, including any
unresolved infrastructure artifacts. No replacement task or completed-model retry.

If the round-1 negative branch applies, publish the one-round score table and
paired intervals as descriptive, stopping-selected results; round-to-round
variability and confirmatory acceptance are unavailable. If final Aider fails,
Terminal stays unattempted and cannot be counted as a win. If both applicable
full-family stages pass, recommend the frozen candidate or cheapest Both, but do
not change canonical without explicit approval. No branch authorizes more tuning,
new variants, acceptance weakening or resumed G1 work.
