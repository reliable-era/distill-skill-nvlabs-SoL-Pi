---
name: efficient-coding
description: Reduce avoidable tool calls and repeated context during repository changes while preserving required verification.
---

# Efficient Coding

For a clear local change, keep the acceptance condition in memory and work directly.

When these instructions are already supplied, do not reread their file. Open supporting resources only for a concrete current need.

- Read the affected implementation and relevant callers or tests together when independent. Reuse their contents; reread only when edits or new evidence make that useful.
- Choose each next call to resolve a specific uncertainty or advance the patch. Avoid separate planning artifacts, status calls, or repository-wide exploration for an already understood change.
- Keep commands and returned output focused. For long logs, preserve the original result and inspect the relevant failure context; a successful output filter does not establish the command's success.
- Apply the necessary change, then run the checks required by its behavior and the project. Repair failures. Repeat passing checks when subsequent edits affect them or unresolved evidence requires it.
- Finish once the requested behavior and required checks are satisfied. Report the change, observed verification, and unresolved limitations briefly.
