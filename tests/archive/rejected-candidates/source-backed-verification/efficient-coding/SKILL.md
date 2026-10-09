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
- Apply the necessary change, then run the checks required by its behavior and the project. Repair failures. Repeat passing checks when subsequent edits affect them or unresolved evidence requires it.
- Before accepting a result, identify decisions that could be wrong despite a successful command. Check those against their original sources or relevant behavior; do not validate a generated artifact only against the assumptions used to create it. Resolve missing or ambiguous evidence with a focused read or check before reporting completion.
- Finish once the requested behavior and required checks are satisfied. Report the change, observed verification, and unresolved limitations briefly.
