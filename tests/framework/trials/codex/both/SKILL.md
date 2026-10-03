---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
license: MIT
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.


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
- If a tool rejects its arguments, correct or simplify the next call instead of
  repeating the malformed payload. Reassess repeated failed attempts from evidence.
- On resumption, read the existing continuation note and check current files and
  verification state. Reuse completed work; rerun checks affected by new edits.
- Run the checks required by the change and project. Continue repairs when they
  fail. Report the changed behavior, observed validation, and remaining blockers.

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
