# Context, actions, and evidence

## Runtime boundary

A skill guides bounded reads, orchestration, selective delegation, and continuation notes. Only the host harness can replace observations in future provider requests, preserve cache prefixes, intercept tool results, or perform native compaction. Writing a summary does not remove the original transcript from API context. Never claim otherwise.

SoL-Pi is a Pi extension using public tool definitions and event handlers. All four mechanisms are opt-in. Do not install or configure it merely because this skill is invoked.

## Action fusion

Use an edit/write with a predefined follow-up command only when the runtime exposes that capability, or orchestration that awaits mutation success and then validation in one turn. Otherwise keep the ordinary edit and validation calls separate. Two calls are not fusion merely because they share a plan step. Keep operations sequential and failure-sensitive. Do not choose the next command based on output not yet inspected.

Batch independent reads and inspect all results. A build depending on two edits waits for both. Shared-file writes require one owner, separate workspaces, or serialization. Action fusion is not transaction rollback or a global lock.

## Archive and recall

Prefer an existing tool's full-output artifact. Keep exact originals in the designated work directory; reuse handles rather than repeating full reads. For repeated long diagnostic logs, use this dependency-free helper; substitute the actual skill directory for `SKILL_DIR`:

```bash
python3 "$SKILL_DIR/scripts/evidence.py" store \
  --input build.log --store-dir task-evidence --exit-code 1
python3 "$SKILL_DIR/scripts/evidence.py" recall \
  --record task-evidence/run-<id>.json --offset 0
```

`store` takes an existing UTF-8 file and a **previously observed** exit code. It does not execute a command or certify a caller-supplied status. It archives exact bytes, records SHA-256, and returns paths, status, size, and bounded head/tail lines. `recall` checks the hash and returns an exact UTF-8 page bounded by bytes and lines, with `next_offset` and `eof`. Use returned offsets; offsets inside multibyte characters are rejected. Small logs need no archive workflow.

Omitted sections remain unread. Recall or search the relevant middle region before diagnosing. Tail truncation cannot establish that tests passed. Retain exit status independently of summaries.

## Verify a proposed receipt

Select quotations deterministically, with the main agent, or through an authorized bounded reader:

```json
{
  "schema": "efficient-coding-receipt/1",
  "source_sha256": "<hash from stored record>",
  "status": "failure",
  "uncertain": false,
  "evidence": [
    {"kind": "failure", "quote": "<exact archived diagnostic>"}
  ]
}
```

```bash
python3 "$SKILL_DIR/scripts/evidence.py" verify \
  --record task-evidence/run-<id>.json --receipt receipt.json
```

Kinds: `fatal`, `failure`, `warning`, `target`, `summary`. Check archive integrity, exact schema/fields, source hash, exit-derived status, nonempty bounded quotes, and size reduction. A failing log requires fatal/failure evidence. Reject fabricated quotes, wrong hashes/status, malformed or enlarged receipts, and altered archives. On rejection, read original evidence. Keep archive handles after acceptance.

These checks establish origin and recorded status, not completeness, correct quote categorization, or a valid fix. Retain uncertainty; the implementation owner diagnoses and reruns acceptance checks. A record is not a signed certificate.

## Compaction economics

When the task requires context management and the runtime exposes native compaction, estimate remaining requests, context removed, cache rewrite cost, and summary cost. Compact if useful and roughly:

`remaining_requests * saved_input_cost_per_request > rewrite_cost + summary_cost`.

Keep recent unresolved interactions. Avoid repeated warm-cache rewrites with little work left. Without native controls, use host context policy. Write a continuation note when a handoff or interruption needs it, rather than at every subtask boundary. A note adds context until the runtime actually replaces history; do not count it as context removed. Do not fabricate an economic decision or alter system/tool messages.

SoL-Pi approximates break-even requests as `write_tokens * max(0, cache_write_read_ratio - 1) / (archive_tokens - memo_tokens)`. The horizon uses requests between plan boundaries and remaining steps, capped by context growth. First compaction scales the horizon by 2; later ones require a 1.5 margin and repayment of carried rewrite debt. Window protection reserves 16,384 tokens. These are source defaults, not universal values. Its gate omits a separate price for the summarization call; full accounting must include it.

## Continuation note

```text
Goal and acceptance:
Current source/snapshot:
Completed behavior and changed paths:
Verified checks and artifact references:
Decisions and required constraints:
Open failures or uncertainty:
Next action and remaining deliverables:
```

Keep the parent task active until required deliverables are verified. After compaction, rebuild the remaining plan and continue. Preserve user corrections and blocked dependencies. Never mark unfinished work complete to force compaction.
