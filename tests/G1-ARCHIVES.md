# G1 archive boundary

The active specification is the G1 section of `tests/goal.md`. The user selected
Codex with local Qwen, Terminal-Bench 2.0 and Aider polyglot. The former
multi-harness goal and all its execution plans are superseded. No old stage may
resume, including output-contract-preflight. G1 has used zero new candidates.

`tests/STATUS.md` is the current, short status file. Workspace `review.md` is
snapshotted unchanged as `tests/G1-REVIEW.md` for a committed audit trail.

## Frozen checkpoints

These files remain at their original paths so historical links still work.
Their contents were not changed during Step 0. They are archives, not current
instructions, queues or authorization. Do not append to either file:

- `tests/framework/refinement/pi-takeover/continuation-checkpoint.md`
- `tests/framework/refinement/pi-takeover/completion-requirements.md`

Their exact hashes and sizes are recorded in `tests/G1-archive-manifest.json`.
Both local files are read-only. Git preserves their contents; the manifest, not
an assumed filesystem permission on another checkout, defines the freeze.
Historical development evidence is in commit `9cb6b1f`; excluded diagnostics
were preserved unchanged in `13e65d8`. Those commits authorize no further work.
Existing whitespace defects were preserved rather than editing historical or
excluded files. G1's new files pass the whitespace check.

## Historical stage evidence

The status table summarizes Codex development experiments only. Raw results,
per-arm costs, original grades, failures and distinct plans remain in
`tests/framework/refinement/pi-takeover/`. Table rows are not pooled estimates.
Primary audit references, relative to that directory:

- Go, sanitize, patch-first: `smoke-audit.json`, `terminal-audit.json`,
  `patch-first-audit.json`.
- Incremental coverage: `incremental-coverage-audit.json`.
- Terminal prefix: `terminal-prefix-result.json` and its protocol failure record.
- HTML, Cython, PMARS, financial: `matched-html-audit.json`,
  `matched-cython-audit.json`, `matched-pmars-audit.json`,
  `matched-financial-audit.json`.
- Source-backed financial and Doom: `source-backed-financial-audit.json`,
  `source-backed-doom-audit.json`.
- TeX: `16k-tex-audit.json`, later `16k-tex-K-grade-repair.json` and
  `tex-cache-grade-phase-audit.json`. The first audit covers three completed
  cells; the status total also includes K's retained costs, not a new actor.
- Regex and SPARQL: `16k-regex-audit.json`, `behavior-first-sparql-audit.json`.
- FastText: `coalesced-fasttext-failure-audit.json`,
  `byte-bounded-fasttext-audit.json`, `measured-feasibility-fasttext-audit.json`,
  `feasible-first-fasttext-audit.json`, `documented-baseline-fasttext-audit.json`,
  `scratch-capacity-fasttext-audit.json`, `recovery-context-fasttext-audit.json`.
- Abandoned output-contract launch and resume: their original results and
  `output-contract-preflight-resume-blocked-audit.json`.

All nine previously selected Terminal-Bench tasks are exposed development data.
Passing gold controls and positive development results do not restore sealing.
Older antecedents, readiness tests and grader controls remain in their original
cohorts; they are not extra G1 candidates or confirmation observations.

## Excluded work and current stop

No Copilot, agy, Cursor or mock-infrastructure development is allowed. Staging
existing diagnostic files for archival commits did not modify their contents,
launch an actor or perform inference. No shared server was queried or changed.

Step 1 needs a written server reservation from the user. Do not poll for idle
availability, draw the Step 2 samples early, or make any model call while waiting.
The wording about committing Steps 0–3 before model calls conflicts with model
calibration in Step 3. Ask the user to explicitly authorize No-skill calibration
under the reserved window after the sealed controls and calibration plan are
committed; do not infer permission from the old goal.
