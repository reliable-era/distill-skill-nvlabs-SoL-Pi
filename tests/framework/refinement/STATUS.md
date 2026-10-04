# Skill refinement campaign

Goal is active. No candidate has been promoted and no majority-harness win exists.

| Work | Evidence | Status |
|---|---|---|
| Native trace diagnosis | [Trace audit](README.md) | 40 saved attempts audited |
| Candidate | [Lean tools](candidates/lean-tools/efficient-coding/SKILL.md) | Development only; 1,182 bytes vs shipped 2,584 |
| SWE-bench grader | [Official sanity](grader-sanity/provenance.json) | Reference resolves; nonempty no-op rejects |
| Terminal-Bench grader | [Official sanity](grader-sanity/provenance.json) | Oracle reward 1; no-op reward 0 |
| Aider five-language grader | [Adapter protocol](../benchmarks/POLYGLOT.md) | Five starters reject; five reference examples pass; executed-test counts checked |
| Native development | [Frozen budget](development-budget.json) | Complete: ten passes; candidate fails baseline target in both harnesses |
| Sealed confirmation | [Metadata allocation](confirmation-selection.json) | Twelve tasks selected without outcomes; inference not launched |
| Stable economic win | [Goal](../../goal.md) | TBD |

[Development results](development/README.md) show no baseline win.

The development screen holds skill delivery constant within each harness,
uses frozen Karpathy and shipped controls, and compares the candidate with
candidate+Karpathy. One Go task cannot establish benchmark generality or stability. Codex login-shell
PATH hid installed Go tools; its no-skill arm stopped after the tool error while
the candidate recovered. Fix tool discovery and use a newly frozen matched stage
before interpreting prompt effects. Do not automatically replay completed attempts.
Aider uses an adapted native single-attempt protocol with physically withheld
trusted tests; it is not the official Aider two-attempt leaderboard protocol.

Confirmation initially has four tasks per family. The allocation excludes all
identified earlier exposed task IDs. Environments for the selected tasks,
per-selected-task validation, complete Copilot/Cursor accounting, fixed native
model routes, the final candidate and numeric inference budget remain unfinished.
Do not silently replace unsupported or failing selected tasks. The predefined
extension rule adds four tasks per family if results are inconclusive.

`compare.py` includes all failed attempts in reported token costs and computes
paired task-cluster intervals. It rejects incomplete counters/grades, duplicated
cells and unmatched panels. Zero-solve bootstrap draws yield inconclusive
intervals. Statistical output cannot independently prove sealed task allocation,
correct model routing, source fidelity or grader independence; audit those first.
Actual subscription/billing dollars remain TBD.

Reproduce official grader checks in a dedicated venv with
`integration-requirements.txt` using `preflight.py --output NEW_DIRECTORY terminal
--task PINNED_TASK_DIRECTORY` or `... swe --dataset PRIVATE_DATASET_JSON --instance
INSTANCE_ID`. Original gold and oracle files stay outside actor workspaces.
Source revisions and image IDs for executed checks are in `grader-sanity/`.

Corrected runtime images pass six root/evaluator login-shell probes; original
failed-discovery image/data remain frozen. See [tool probes](../benchmarks/polyglot-login-probes.json)
and [ten sanity checks](../benchmarks/polyglot-login-sanity.json). All current
model and infrastructure jobs are terminal; no background inference remains.
