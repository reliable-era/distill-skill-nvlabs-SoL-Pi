# Bounded coordination

## Decide whether a worker helps

Use one agent for small fixes, shared-file edits, sequential dependencies, or work whose setup exceeds its independent benefit. Parallelize only when authorized and outputs are independent. Estimate setup, context transfer, duplicated inspection, integration, and review costs before adding workers. Do not copy the paper's experimental 20-worker count as a default.

Use cheaper available models for bounded extraction or mechanical work with executable checks. Keep diagnosis, interfaces, integration, and acceptance with the owner. A lower unit price may create more expensive retries.

## Task card

Use [task-contract.md](../assets/task-contract.md) for a persistent handoff. Keep
the same fields in the dispatch message for small tasks: owner, goal, inputs and
version, output, scope, dependencies, acceptance, and progress checkpoint. Record
a concrete command or inspection criterion; a worker's confidence is not a check.

Keep simple contracts in the plan/message. Create a board only when owners or handoffs need shared state. Share artifact paths and evidence, not transcripts. A worker may challenge an invalid contract with source evidence; explicitly revise the contract.

## Dispatch ready work

1. Identify dependencies and shared interfaces.
2. Assign only tasks whose inputs/interfaces exist.
3. Give shared files one integration owner; use separate workspaces for competing patches. Read-only analysis may overlap deliberately.
4. Reuse a relevant worker for follow-ups; do not resend the repository.
5. Integrate verified results and stop redundant work.

A shared parser's output-schema change is a prerequisite for dependent client patches. Agree and record the schema first. Independent fixtures/client analyses can proceed together; dependent writes wait. If two workers touch `parser.py`, choose one writer or separate patches for owner integration.

These are scheduling recommendations added by this bundle. SoL-Pi supplies four extensions, not a task-DAG scheduler, allocator, or intelligent dispatch policy.

## Result receipt and acceptance

Use [handoff.md](../assets/handoff.md) when a result crosses an ownership boundary.
Preserve the source version, changed artifacts, actual verification outcome,
unmet conditions, and the next integration action. Return concise evidence and
paths, not the full worker transcript.

Treat `reported complete` as awaiting acceptance. Check artifact existence, source compatibility, interfaces, and required checks after integration. Reopen any failure with its unmet condition. Green worker-local tests do not establish combined correctness.

Distinguish these states when shared tracking is needed:

| State | Meaning | Evidence needed to advance |
| --- | --- | --- |
| `ready` | Inputs and dependencies permit work. | Assigned owner and available input artifact or agreed interface. |
| `running` | The owner is producing the artifact. | Observable progress toward the contract. |
| `submitted` | A worker reports a candidate result. | Changed paths, source version, check results, and remaining issues. |
| `verified` | The integration owner has checked the submitted artifact. | Required local acceptance evidence and compatible inputs. |
| `accepted` | The artifact is integrated and its required checks pass. | Integration evidence and no unmet acceptance condition. |
| `blocked` | A required input, permission, or check prevents progress. | Exact unmet condition and a recovery action. |

Let only the integration owner advance a result to `verified` or `accepted`.
Return failed or stale submissions to work with their unmet condition. Close the
parent task only after all required deliverables are accepted. State labels
record an evidence decision; they do not replace an executable verifier.

## Progress and retry control

Choose checkpoints for task complexity, not a universal turn limit. Reassess repeated errors without new evidence, missing artifacts, or exceeded agreed budgets. Request a targeted diagnosis, change methods, or take over blocked work.

A budget checkpoint cannot silently terminate required work. Continue through reasonable available paths within authorization. If a hard external limit or inaccessible dependency prevents completion, retain artifacts and report the blocker and unmet checks.

## Swarm lesson

The paper uses one coordinator and 20 workers in five groups, isolated workspaces, group evidence boards, and immutable globally verified improving candidates. This is useful evidence-sharing and acceptance design.

It is one two-hour run per configuration. The SoL-Pi swarm costs less than the Pi swarm but more than one agent. It establishes neither optimal worker count nor causal scheduling benefit. Lower worker overhead is an opportunity for exploration subject to whole-task measurement.
