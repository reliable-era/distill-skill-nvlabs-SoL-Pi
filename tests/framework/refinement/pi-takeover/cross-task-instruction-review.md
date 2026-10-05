# Bounded cross-task instruction review — duplicate mechanism rejected

Read-only existing SPARQL and financial traces; no new actor/model calls, training, grading, resource changes, task replacement or retry. No private grader payloads/answers/parameters exported into a candidate. See reproducible `audit_cross_task_instruction_review.py` and hash-pinned `cross-task-instruction-review.json`.

## Actual observations

SPARQL behavior-first candidate executed five completed commands, No skill four; all original tests passed for each. Candidate native event16 wrote and successfully executed its query; event20 was a distinct diagnostic; event24 dumped source and executed the query again. Initial written payload hash `5e5909698a938f30983dc46d087a18a9084d89a7d6891a4755cc2d508bceaa98` matches the final captured artifact. The observed intermediate diagnostic was read-only; global ambient state unchanged is not independently proven. The final dump/re-run produced1739 native output bytes; this is NOT a token or marginal cost estimate. The distinct diagnostic is not automatically redundant.

Financial source-backed candidate executed four completed commands, stopping after mutation plus checks; No skill eight, including one failed image helper. Both had passing original grades and complete costs. Additional source checks can resolve real ambiguity: their necessity or avoidability is NOT proven just by a passing final result. This cohort is a counterexample to treating every verification call as wasted work. Candidates/task cohorts differ; no pooled or randomized-mechanism inference.

Initial strict whole-file JSONL inspection hit the CLI's leading non-JSON text: failure retained in `cross-task-instruction-review-parser-r1.json`. Current parser enumerates actual LF-delimited records, records the ignored leading line, and requires nonempty completed-command evidence. An initial empty financial diagnostic listing was not evidence that no commands ran; direct record parsing yields the four/eight counts above. Native headers/status/counts are separate from provider POST/usage.

## Decision

The actual repeated SPARQL check is already targeted by the existing coalesced clause: **“Do not add a separate artifact dump or repeat a successful check just to prepare the final report; retain source-backed checks needed to establish correctness.”** Adding another similar clause is not a materially different hypothesis. Removing every independent check would weaken verification and ignore the financial uncertainty counterexample. Static prompt compression and persisted delivery do not prove token economy, adherence or quality.

**Reject a duplicate verification clause and blanket check removal. No defensible new scored successor established by this bounded review.** Coalesced descendants' zero-solve fastText outcomes are retained separately; they neither establish promotion nor disprove every possible benefit of the existing repeat rule. Do not reinterpret earlier original passing grades or retry actors to force a favorable result.

This branch is blocked on a materially different, trace-supported portable mechanism that preserves correctness; further automatic variants have no evidence-backed decision basis. If none is available, stop scored execution with this evidence and require a new concrete hypothesis or explicitly approved revised experimental contract. Do not relax acceptance, choose easier outcomes, pool cohorts, borrow grades or raise budgets.

Canonical unchanged; no active worker. Majority harness, full representative/family confirmation, three independent rounds, paired95%ALL3/5%complete tokens-per-verified-solve/no-quality-loss, supported USD/exposure eligibility and promotion remain unverified. Goal incomplete; no completion update.
