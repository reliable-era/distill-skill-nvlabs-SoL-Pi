---
name: efficient-coding
description: Reduce repeated reads and avoidable tool turns in coding tasks, especially when debugging long logs or resuming work. Use focused context and verify the requested behavior.
---

# Efficient Coding

Spend fewer requests on repeated work while completing and verifying the task.
For a small fix, keep the acceptance check in working memory and edit directly.

- Search for the affected symbol or diagnostic, then read its relevant source,
  callers, or tests. Expand when needed; reuse what you have already learned.
- Batch independent reads. Combine a mutation with a predetermined check only
  when the available tool can execute them sequentially after mutation succeeds.
  With separate Edit and Bash calls, run them in order; that still uses two calls.
- Keep long command output in its existing artifact or a local log. Search for
  the decisive error and inspect nearby lines, including the middle of the log.
  Capture the command's actual exit status before shortening output; a successful
  `tail` or `grep` does not prove the original command passed.
- Check a quoted diagnostic against its original source before relying on it.
  A matching quote can still omit another failure. Read more evidence when needed.
- If a tool rejects its arguments, retry once with a single, fully specified
  call. If a file read is rejected again, use an available bounded shell read
  instead of replaying the payload. Never copy parser error metadata into arguments.
- On resumption, read the existing continuation note and check current files and
  verification state. Reuse completed work; rerun checks affected by new edits.
- Check existing shared helpers against every explicit requested behavior; reuse
  does not establish correctness. Choose regression cases that distinguish the
  incomplete behavior from the full contract. Run required checks and continue
  repairs when they fail. Report the behavior, validation, and remaining blockers.

Use supporting resources only for a current need:

- Repeated long-log handling: [execution.md](references/execution.md), including
  the offline `scripts/evidence.py` archive, recall, and receipt checker.
- Authorized worker handoffs: [coordination.md](references/coordination.md).
- Requested efficiency evaluation: [measurement.md](references/measurement.md).
- Workflow examples: [worked-examples.md](references/worked-examples.md).
- SoL-Pi provenance and implementation: [sol-pi-evidence.md](references/sol-pi-evidence.md).

This skill guides tool use. It cannot replace past API messages, register fused
tools, or trigger native compaction. Summaries do not remove existing context;
those savings require runtime support. Do not add task cards, cost reports, or
extra agents merely to demonstrate that this skill was followed.
