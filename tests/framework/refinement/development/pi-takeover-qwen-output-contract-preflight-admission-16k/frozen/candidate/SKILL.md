---
name: efficient-coding
description: Reduce avoidable tool calls and repeated context during repository changes while preserving required verification.
---

# Efficient Coding

For a clear local change, keep the acceptance condition in memory and work directly.

- Match evidence coverage to the requested scope. For a local change, locate the affected definition and relevant test before broad reads. For an exhaustive repository change, track matching files as discovery proceeds and make reversible, checked updates to confirmed matches in batches; a complete inventory is not a prerequisite for every edit. Continue until the requested scope is covered, then verify remaining matches; do not silently exempt examples or data or claim completeness while coverage is unresolved. Read coherent local blocks, expanding only to resolve an identified uncertainty. Reuse already-read content unless edits or new evidence require another read.
- Choose each next call to resolve a specific uncertainty or advance the patch. Avoid separate planning artifacts, status calls, or repository-wide exploration for an already understood change.
- When necessary read-only observations are already known and independent, collect them in one available tool or shell call, preserving labeled results and each command’s exit status. Keep dependent searches sequential; retain required evidence and verification. Use existing tools rather than building a helper for a trivial pair.
- Keep commands and returned output focused. For long logs, preserve the original result and inspect the relevant failure context; a successful output filter does not establish the command's success.
- Once a plausible approach is clear, make a small reversible, end-to-end change and inspect its actual behavior. Use that evidence to refine the change rather than exhaustively debating hypothetical cases before producing anything. Before expensive upstream work, cheaply exercise unverified result-handling steps with disposable inputs; dependency imports alone do not verify the output contract. For irreversible actions, check the required safeguards first; do not weaken final acceptance or verification.
- Apply the necessary change with its required checks in one tool or shell call when they can run together safely; keep labeled results and each exit status. Use the results to decide the next action. Repair failures, and rerun checks affected by later edits or unresolved evidence. Do not add a separate artifact dump or repeat a successful check just to prepare the final report; retain source-backed checks needed to establish correctness.
- Before accepting a result, identify decisions that could be wrong despite a successful command. Check those against their original sources or relevant behavior; do not validate a generated artifact only against the assumptions used to create it. Resolve missing or ambiguous evidence with a focused read or check before reporting completion.
- Finish once the requested behavior and required checks are satisfied. Report the change, observed verification, and unresolved limitations briefly.
