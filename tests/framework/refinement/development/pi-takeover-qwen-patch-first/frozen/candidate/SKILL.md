---
name: efficient-coding
description: Reduce avoidable tool calls and repeated context during repository changes while preserving required verification.
---

# Efficient Coding

For a clear local change, keep the acceptance condition in memory and work directly.

- Match evidence coverage to the requested scope. For a local change, locate the affected definition and relevant test before broad reads. For an exhaustive repository change, inventory matching files before editing and verify remaining matches afterward; do not silently exempt examples or data. Read coherent local blocks, expanding only to resolve an identified uncertainty. Reuse already-read content unless edits or new evidence require another read.
- Once evidence supports a reversible correction, apply and check it before optional deeper investigation. For broad work, make verified progress in batches and retain a final coverage check; do not postpone every edit until forensic analysis is complete. Expand investigation to resolve remaining acceptance conditions, not to invent additional scope.
- When necessary read-only observations are already known and independent, collect them in one available tool or shell call, preserving labeled results and each command’s exit status. Keep dependent searches sequential; retain required evidence and verification. Use existing tools rather than building a helper for a trivial pair.
- Keep commands and returned output focused. For long logs, preserve the original result and inspect the relevant failure context; a successful output filter does not establish the command's success.
- Apply the necessary change, then run the checks required by its behavior and the project. Repair failures. Repeat passing checks when subsequent edits affect them or unresolved evidence requires it.
- Finish once the requested behavior and required checks are satisfied. Report the change, observed verification, and unresolved limitations briefly.
