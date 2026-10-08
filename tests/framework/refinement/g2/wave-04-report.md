# G2 Aider round 1 — partial wave 04, accounting interruption

Four of the six scheduled cells reached the model; 97 provider requests.
Two were verified solves and two failed original tests. The two unstarted
JS/Both and JS/No-skill cells remain in their exact original schedule order.

| Cell | Solved | Requests | Token lower bound | Cost complete |
|---|---:|---:|---:|---:|
| g2-aider-r1-t1-candidate | True | 35 | 937,914 | True |
| g2-aider-r1-t1-none | False | 33 | 894,337 | True |
| g2-aider-r1-t5-candidate | False | 3 | 39,464 | True |
| g2-aider-r1-t5-K | True | 26 | 722,256 | False |

Request 97 (JS/K) lacks terminal response and usage; broker recorded
AttributeError following native stream disconnect. Native exit 1 occurred
before the 7200-second wall cap. Preserve this incomplete request, not zero cost.
The actor work was captured before transport checks. Its exact original-grader
replay passed all nine accepted tests; the original null grade/error remain in
the unmodified raw result, with a hash-verified repair sidecar. **No model retry.**

Wave known-token lower bound: 2,593,971; one unknown-cost cell. Cumulative G2:
22 cells / 653 requests / ≥21,870,256 tokens; 6 solves / 16 failures; all grades
now valid, one request cost unknown. Worker 2176181 and owned resources absent.

Frozen candidate, core auditor/analysis, runtime and schedule remain unchanged.
`audit_repairs.py` verifies and projects only the grade replay/mechanical receipt
fields for the frozen auditor, preserving unknown cost and raw failure.
Complete the remaining round-1 roster before applying its preregistered gate.
Unknown accounting blocks acceptance; if unrecoverable, report inconclusive
rather than estimating, discarding or rerunning this completed model cell.

Evidence: raw wave result, `grade-and-accounting-repair.json`, wave completion
audit, `diagnostics/w04-transport-accounting-check.json`, and `audits/aider.json`.
G1 and canonical are untouched.
