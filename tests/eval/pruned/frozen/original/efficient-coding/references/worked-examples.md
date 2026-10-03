# Worked workflows

Use the minimum workflow that resolves the bottleneck. Substitute the actual
skill directory for `SKILL_DIR` in commands.

## Small local fix

1. State the required behavior and its acceptance check in the current plan.
2. Read project instructions, search the affected symbol, and inspect its
   callers or tests only as needed.
3. Make the focused change. Run the relevant check after mutation succeeds.
4. Inspect its actual outcome and finish the requested deliverable.

Use one agent. Skip archives, task cards, and cost reports when they add no
value. Batch independent reads; keep output-dependent decisions sequential.

## Long failing test log

1. Keep the observed command exit status and the exact full-output artifact.
2. Search that artifact for the failing test or diagnostic. Read neighboring
   lines; do not assume the final log lines contain the failure.
3. Archive only if repeated handling benefits from a stable handle:

```bash
python3 "$SKILL_DIR/scripts/evidence.py" store \
  --input test.log --store-dir task-evidence --exit-code 1 \
  --command "the command actually run"
python3 "$SKILL_DIR/scripts/evidence.py" recall \
  --record task-evidence/run-<id>.json --offset 0
```

4. Supply the actual observed status to `store`; this helper does not run the
   command. Follow returned `next_offset` values for exact UTF-8 pages.
5. If using a proposed receipt, verify it before relying on its quotations.
   A verified quotation can still omit a different failure. Read original
   evidence when the diagnosis or acceptance decision requires it.
6. Repair from that evidence, rerun the relevant checks, and retain failures.

The offline helper archives and validates evidence. It does not rewrite the
host's API transcript or reproduce ObservationPack automatically.

## Two dependent coding tasks

Suppose a parser change affects a client and tests. If delegation is authorized:

1. Give the parser and its output interface one owner.
2. Agree the interface or produce the prerequisite artifact before dependent
   writes. Independent fixture analysis can proceed while it is produced.
3. Dispatch the client patch with the agreed interface, source version,
   expected artifact, and acceptance check. Avoid a full transcript handoff.
4. Receive results as `submitted`; inspect artifacts and local evidence.
5. Integrate both changes and check their interaction before marking `accepted`.

Use the task and handoff assets only if persistent shared tracking helps. If
worker-local tests pass but integrated tests fail, return the affected result
to work and keep the parent task open.

## Compare costs

Collect real usage for main, coordinator, worker, reducer, retry, and compaction
calls. Normalize inclusive provider counters into exclusive token categories.
Use the actual prices for the corresponding model and request:

```bash
python3 "$SKILL_DIR/scripts/cost_audit.py" usage.jsonl \
  --attempted 5 --solved 4
```

Keep the solved count externally verified. Include failed-task costs in the
numerator. Report unavailable telemetry rather than estimated savings; a lower
bill accompanied by missed requirements does not satisfy a zero-loss contract.
