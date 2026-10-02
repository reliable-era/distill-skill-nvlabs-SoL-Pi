# Continuation note (previous session was interrupted)

Goal: extend `tasks_cli/cli.py` with three options.

Requirements:
1. `--json` prints `{"items": [...]}`. **DONE** — implemented and tested in tests/test_cli.py. Do not change this output schema.
2. `--limit N` prints only the first N items (after sorting, if sorting is requested). N must be a positive integer; reject 0 or negatives with an argparse error.
3. `--sort {name,priority}` sorts items: `name` ascending alphabetically; `priority` ascending, ties broken by name ascending.

Constraints: stay with a single flat argparse parser (no subcommands); options combine with `--json`.

Next action: implement 2 and 3, add tests for them, run the suite.
