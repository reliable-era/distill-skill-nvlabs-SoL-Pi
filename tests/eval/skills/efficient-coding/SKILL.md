---
name: efficient-coding
description: Complete coding tasks with less repeated context, tool traffic, and coordination overhead while preserving required behavior and verification. Use when implementing, debugging, refactoring, or reviewing code; reducing coding-agent token cost; handling large build logs; or coordinating explicitly requested coding agents. Apply a lightweight single-agent path to small changes and load detailed resources only for the relevant bottleneck.
---

# Efficient Coding

Optimize the cost of a **verified completed task**. Preserve the user's requested scope, project constraints, actual exit status, and evidence. A shorter response or unfinished task is neither completion nor demonstrated savings.

Use these six rules. For a small local change, keep the contract in working memory, skip administrative files, and work with one agent.

## 1. Define completion before spending

- Express the requested behavior and its acceptance check in one or two sentences. Identify required outputs and dependencies.
- Inspect project instructions and the smallest relevant source slice. Use `rg --files`, targeted `rg -n`, then bounded reads. Expand when evidence requires it; avoid repeatedly dumping the repository or whole logs.
- State a consequential assumption. Ask only when missing information changes correctness or authorized scope; make routine implementation choices.
- For longer work, keep a short plan with one current integration owner. Mark steps complete only after acceptance checks pass.

## 2. Keep one useful context

- Retain the goal, current source version, key interfaces, unresolved errors, changed files, verification evidence, and next action.
- Read shared facts once. Give authorized workers task-local context and artifact paths; avoid forwarding the entire conversation.
- Archive large outputs exactly and reuse handles plus relevant excerpts. Recall missing lines before diagnosing from a summary or concluding absence.
- Use `scripts/evidence.py` for repeated long-log handling when ordinary tool archives are insufficient. Prefer existing tool artifacts for one-off reads.
- At a completed subtask, record a compact continuation note. Use native compaction only if supported and expected savings justify rewrite and summarization costs, or window pressure requires it.

See [execution.md](references/execution.md) for archive commands, continuation notes, the cost gate, and the limits of a prompt-only skill.

## 3. Fuse predictable actions; respect dependencies

- When a mutation and its next validation command are already determined, execute them sequentially in one orchestration turn if supported. Proceed to validation only when mutation succeeds.
- Separate actions when the next choice depends on inspecting the preceding result, authorization, or conflict resolution.
- Batch independent reads/searches and inspect every result. Serialize shared-file writes and dependency-sensitive operations.
- Distinguish edit success from test success. A failing command does not undo an edit. Do not infer global locking from a per-file queue.

## 4. Reduce evidence without inventing conclusions

- Prefer deterministic extraction for known log formats. Consider a cheaper available model only for bounded reading whose total cost is likely lower.
- Request exact diagnostic quotations and uncertainty, never the final repair or acceptance decision. Retain the original log and observed exit status.
- Check source hash, status, quote membership, and receipt size with `evidence.py verify`. Fall back to original evidence on failure.
- Quote presence proves provenance, not completeness or diagnosis. Read omitted regions when uncertainty, conflicting signals, or the decision requires them.
- Send logs to another provider only when the task and environment permit it. This bundle makes no remote model calls itself.

## 5. Delegate only a bounded, useful unit

- Start with one agent. Spawn workers only when the user or applicable higher instructions authorize delegation and independent scope justifies it.
- Before dispatch, assign an artifact, inputs, owner, dependencies, acceptance check, and progress/retry limit. Give shared-file integration one owner or use separate workspaces and explicit interfaces.
- Dispatch ready tasks; reuse relevant worker context. Return changed paths, evidence, unresolved issues, and next action rather than transcripts. Stop redundant investigations and idle workers.
- Treat worker output as proposed work until integration checks pass. Reopen unmet contracts, dependencies, or verification checks.
- After repeated failure without new evidence, change the hypothesis or method. A budget checkpoint requires reassessment, not abandonment. Report an unavoidable blocker and preserve partial artifacts.

Read [coordination.md](references/coordination.md) only for multi-step handoffs or authorized multi-agent work. Its scheduling rules are practical additions; SoL-Pi does not implement a general dispatcher.

Use [task-contract.md](assets/task-contract.md) and [handoff.md](assets/handoff.md) only when a shared contract is useful; keep small tasks in the current plan or message. Read [worked-examples.md](references/worked-examples.md) for a concrete small-fix, large-log, or handoff workflow.

## 6. Measure the whole task and close it honestly

- Run checks appropriate to the changed behavior, including required project checks and affected interfaces. Never invent passing results or weaken acceptance to save tokens.
- Count coordinator, worker, reducer, compaction, retry, and integration costs. Separate uncached input, cache reads, cache writes, and output.
- Measure verified completion and cost per solved task. Compare matched tasks, budgets, models, prices, and checks; include failures in total cost.
- Use `scripts/cost_audit.py` on normalized telemetry when available. Otherwise report unavailable cost, not guessed savings. Byte counts are not provider token accounting.
- Finish with changed behavior, validation performed, and material unresolved limitations. Continue until authorized required deliverables are handled.

See [measurement.md](references/measurement.md) for telemetry and rollout checks. Read [sol-pi-evidence.md](references/sol-pi-evidence.md) only for the paper digest, implementation mapping, empirical trade-offs, and provenance.

The bundle adapts SoL-Pi into coding practice and adds completion and dispatch contracts. It does not change weights, install a harness extension, alter API history, or promise the paper's savings.
