---
name: efficient-coding
description: Reduce avoidable tool calls and repeated context during repository changes while preserving required verification.
---

# Efficient Coding

For a clear local change, keep the acceptance condition in memory and work directly.

- Locate relevant files or symbols before broad reads. When a repository-wide search may return many or very long matches, preserve its full scope but show paths or counts first, then bounded context around actual matches rather than entire long lines. Read coherent local blocks and expand for an identified uncertainty. Reuse already-read content unless edits or new evidence require another read.
- Choose each next call to resolve a specific uncertainty or advance the patch. Avoid separate planning artifacts, status calls, or repository-wide exploration for an already understood change.
- Keep commands and returned output focused. For long logs, preserve the original result and inspect the relevant failure context; a successful output filter does not establish the command's success.
- Apply the necessary change, then run the checks required by its behavior and the project. Repair failures. Repeat passing checks when subsequent edits affect them or unresolved evidence requires it.
- Finish once the requested behavior and required checks are satisfied. Report the change, observed verification, and unresolved limitations briefly.
