# SWE trace diagnosis

The no-reread candidate regressed against no skill by 78.3% reported tokens in Pi and 7.1% in Codex. The lean parent regressed by 63.5% and 60.7%, respectively. All twelve patches passed official task grading. These are observations from one development issue and one round, not causal estimates.

## Observable differences

Character counts below measure returned text, not model tokens. Pi counts all tool-result text; Codex counts command stdout/stderr only. Call counts are Pi tool starts and Codex command executions, respectively; Codex also records one file-change operation in each listed arm. Compare within a harness, not between harnesses.

| Harness | Arm | Returned characters | Calls counted | Reported tokens |
|---|---|---:|---:|---:|
| Pi | No skill | 8,396 | 9 | 23,428 |
| Pi | Lean parent | 22,364 | 11 | 38,296 |
| Pi | No-reread candidate | 14,765 | 12 | 41,779 |
| Pi | Shipped ours | 9,258 | 9 | 29,029 |
| Codex | No skill | 11,888 | 4 | 82,389 |
| Codex | Lean parent | 31,415 | 5 | 132,404 |
| Codex | No-reread candidate | 17,685 | 4 | 88,212 |
| Codex | Shipped ours | 12,096 | 4 | 66,343 |

The narrowest common opportunity is **locate first, then read the relevant block**:

- Pi lean parent loaded 260 lines of `blueprints.py`, the first 160 lines of `test_blueprints.py`, 180 lines of `pyproject.toml`, and 70 lines of `CHANGES.rst`. The relevant test was around line 254, so a later grep and another test-file read were still necessary. Its first implementation read alone returned 10,665 characters. No skill read 75 implementation lines and 22 nearby test lines after locating the symbols.
- Pi candidate used the broad grep terms `name|def test` and returned 8,040 characters across source/tests plus configuration discovery. It then searched names again with `tail -35`, which did not locate the relevant dotted-name test, followed by another `dot|invalid|blueprint_name` search and a local read. This is a concrete extra locator step; a targeted search for the adjacent validation/test could avoid the broad result and recovery chain. Whether different wording reliably induces that behavior remains unproven.
- Codex candidate loaded both complete `pyproject.toml` and `tox.ini`, combined with a broad `name` search. That command returned 11,721 characters. No skill's corresponding search returned 7,436 characters; its subsequent focused read/config command returned 4,159 versus 5,663 in candidate. Both used four command executions, so fewer calls alone cannot explain this difference.
- Codex lean parent ran the full suite after the blueprint suite passed, returning 13,614 further characters and exposing the three documented unrelated cookie-domain failures. The additional command/output is directly observable, but its necessity cannot be decided from token counts. No evidence permits dropping project-required checks; no proposed candidate below removes verification.

Pi candidate and no skill both attempted an ambiguous `CHANGES.rst` edit (`Unreleased` occurs twice), then repaired it. This is avoidable matching work but is not unique to the candidate. All Pi arms encountered unavailable `rg` and recovered; Codex command tools resolved `rg`. The mechanism is TBD, and this shared Pi condition does not isolate a skill effect.

No arm reread `SKILL.md`, so the added no-reread sentence targeted a behavior absent here. Shipped ours uses more returned characters than no skill in Codex yet fewer reported tokens. Output volume therefore does not account for the full economics: prompt overhead, replay timing, reasoning/output, caching and sampling remain possible contributors. No percentage of token regression can be attributed to a single operation from this round.

Evidence: per-arm [transcripts](pi/candidate/stdout.jsonl), [command trace](codex/leanparent/stdout.jsonl), [trace audit](trace-audit.json), [results](results.json), and official reports referenced in each result. Read/edit operations were inspected directly; no new model calls were made for this diagnosis.

## One proposed candidate, not installed

Start from the frozen lean parent and **replace only its first read/context bullet** with:

> Locate the affected definition and relevant test before broad reads. Read their coherent local blocks; expand to additional files or wider ranges only to resolve an identified uncertainty. Reuse already-read content unless edits or new evidence require another read.

Leave verification, failure repair, output-integrity and completion clauses intact. Do not combine this change with the no-reread sentence, tool installation, external routing, or a weaker grader. The hypothesis is that an explicit locator-to-block rule reduces broad observations and later recovery searches. It is not a claim that a smaller read is always adequate, or that this candidate will win.

## Frozen reference basis and limits

[SoL-Pi, frozen commit e1a586a](https://raw.githubusercontent.com/NVlabs/SoL-Pi/e1a586af0ad8956f42ae5b26bba20e48fbf30e00/README.md) targets repeated turns and large observations while retaining archived evidence. Our proposal prevents unnecessarily broad initial reads; it does not implement ObservationPack, native compaction or action fusion. A prompt cannot retroactively remove earlier messages.

[Ponytail, frozen commit c982cd4](https://raw.githubusercontent.com/DietrichGebert/ponytail/c982cd411abb53323c4baa1baa3c2f020b8d0b08/README.md) favors existing code/platform primitives after understanding the relevant flow and preserves validation. This fixture already had a minimal adjacent validation guard, so speculative abstractions or code reduction are not the measured problem. Locating that existing guard is the useful transferable behavior.

[Provisional Jev reference, frozen commit 923e521](https://raw.githubusercontent.com/lazniak/jevskill/923e521b0521061637bbc486d9f9c2a3683e0374/README.md) describes selective reduction with recoverable rejected material and warns through its own examples that retained material can miss salient items. Exact intended Jev identity remains TBD. We borrow recoverability/expansion as a constraint; these small source observations do not justify adding an unmeasured external decision call.

A future development test should freeze this single delta, preserve all prior negative results, and use unchanged runtime/grading/skill delivery across every comparison arm. Require complete token accounting and unchanged verified quality across additional tasks and repeated rounds before any promotion. The frozen confirmation set remains untouched.
