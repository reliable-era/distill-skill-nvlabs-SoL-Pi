# Skill refinement campaign

Goal is active. No candidate has been promoted and no majority-harness win exists.

| Work | Evidence | Status |
|---|---|---|
| Native trace diagnosis | [Trace audit](README.md) | 40 saved attempts audited |
| Candidate | [Lean tools](candidates/lean-tools/efficient-coding/SKILL.md) | Development only; 1,182 bytes vs shipped 2,584 |
| SWE-bench grader | [Official sanity](grader-sanity/provenance.json) | Reference resolves; nonempty no-op rejects |
| Terminal-Bench grader | [Official sanity](grader-sanity/provenance.json) | Oracle reward 1; no-op reward 0 |
| Aider five-language grader | [Adapter protocol](../benchmarks/POLYGLOT.md) | Five starters reject; five reference examples pass; executed-test counts checked |
| Native development | [Frozen budget](development-budget.json) | Two stages complete: twenty accepted patches; no baseline win |
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
and [ten sanity checks](../benchmarks/polyglot-login-sanity.json). Previous corrected-Go jobs are terminal. The broader development stage below has separate bounded jobs; inspect its saved records for current completion.

Corrected-runtime results: [v2 comparison](development/README-v2.md). The single-change no-reread candidate now has native repository and agy development results. The automatic patch/official-grader bridge is implemented; native Flask repair ran twelve actors and twelve official grades.

## Broader development, 2026-10-04

Frozen [30-start budget](development-budget-broad.json) spans Flask repository repair, Terminal-Bench sanitize-git-repo, and native agy Go. One round only; sealed confirmation remains untouched.

- [Flask](development/swe-flask/README.md): all 12 official grades pass. No-reread candidate costs +78.3% Pi/+7.1% Codex vs No skill; no promotion. Shipped ours saves 19.5% on Codex but costs 23.9% more on Pi.
- [Native agy Go](development/agy-go/README.md): candidate passes but costs +3.1% vs No skill, and exceeds Karpathy/Both. Lean parent saves 27.5% on this one fixture. Shipped ours fails during SDK HTTP 503/internal timeout; complete usage TBD, partial counters retained.
- Terminal screen has finished its original twelve-start cap (ten model attempts and two startup/auth availability failures). One Pi startup failure consumes an attempt and is not replayed. Preserve original grades separately from complete final-state replay availability.

Canonical skill remains unchanged. Passing task checks is insufficient to show stable economic superiority; real dollars remain TBD.

New cross-harness trace audit found native agy No skill downloaded public official tests. Preserve that exposed development result, but do not treat it as clean withheld evidence. Uniform provider-only actor egress and test/solution exposure audit are required before confirmation. The locally withheld fixture alone does not enforce a sealed evaluator.

[Consolidated broader results](development/README-broad.md): no-reread candidate rejected. Prepared locate-first SWE plan has zero attempts and uses persistent private serialized credentials; do not launch before the new global stage and credential gate. Terminal replay audit completed: all twelve retained outcomes agree; six byte-exact full states, one missing-index state, and five tracked-diff-only reconstructions.

## Locate-first Codex development

Independent four-arm Codex screen completed on the reused Flask issue, order106: all four official grades resolved. Candidate84,948 tokens vs No skill112,352, Karpathy151,278, and Both128,199: descriptive savings24.4%,43.8%,33.7%. Root verified allfour patch/transcript/report hashes. [Evidence](development/swe-flask-locate-first/README.md). This positive single-issue round is not stable confirmation and does not justify promotion. Pi has zero starts, awaitingfreshlogin afterinvalid_grant; fourunused slots remain in the frozen eight-start budget. Canonical andsealedtasks unchanged; goalactive.

## Updated refinement checkpoint

The goal remains active: at least3/5 primary harnesses, three benchmark families and repeated matched confirmation rounds under the unchanged criteria in [goal.md](../../goal.md). Locate-first passes all three reused Codex development tasks but costs13.1% more than No skill overall; [consolidated evidence](development/README-locate-first-broad.md). Bounded-search terminal screen completed four starts and four agreeing full-state replays: No skill/Both pass, Karpathy/candidate fail. Lower candidate tokens do not qualify as a win. Canonical skill unchanged.

Four selected polyglot environments now pass nine offline grader controls, including a Java check that prevents private reference helpers entering candidate grading. Native actor readiness remains TBD. Eight mock Docker egress controls pass; native provider integration and cloud-tool restrictions remain TBD. Frozen Copilot supports native `--usage-output-file`; complete schema and cutoff accounting still need validation. Pi requires refreshed login. Prepared native agy Flask awaits classifier review before its separately capped four starts.
