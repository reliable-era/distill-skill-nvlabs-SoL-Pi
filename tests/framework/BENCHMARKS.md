# Benchmark selection

These are published benchmarks selected for the next economic evaluation. They are **not new performance results**. The first four metadata inventories and eight-task pilot are acquired and pinned in `examples/pilot-sources.json` and `examples/pilot-selection.json`. License review, task environments, and integration with each official grader remain **TBD**. The framework's offline smoke fixture checks framework execution only; it is not one of these benchmarks.

| Benchmark | What it adds | Source and external grader | Readiness |
|---|---|---|---|
| SWE-bench Verified | Python repository repair; comparable task family to previous measurements | [SWE-bench](https://github.com/SWE-bench/SWE-bench), official evaluation harness | Catalog + selection; integration TBD |
| SWE-bench Multilingual | Repository repair across languages | [Official benchmark](https://www.swebench.com/multilingual.html), SWE-bench harness | Catalog + selection; integration TBD |
| Terminal-Bench 2.0 | Terminal workflows and environment work | [Official tasks](https://github.com/harbor-framework/terminal-bench-2), Harbor verifier | Catalog + selection; integration TBD |
| Aider polyglot | Short multilingual exercises with lower setup cost | [Official exercises](https://github.com/Aider-AI/polyglot-benchmark), exercise test runners | Catalog + selection; integration TBD |
| BugsInPy | Controlled Python regression bugs | [Official repository](https://github.com/soarsmu/BugsInPy), BugsInPy test tools | Catalog + selection; integration TBD |
| Defects4J | Java regression repair and builds | [Official repository](https://github.com/rjust/defects4j), Defects4J test tools | Catalog + selection; integration TBD |

Start with Verified, Multilingual, Terminal-Bench, and Aider polyglot for breadth; add BugsInPy and Defects4J as repair diagnostics. Start at **two tasks per benchmark** for an eight-task pilot, Record any missing language/category coverage and define additional sampling before inference; the current eight-task selection is frozen. Eight tasks cannot support a broad performance claim. Choose task count and seeds before inference, and report uncertainty, failures, and the exact sampled identities.

## Freeze a small sample

Prepare metadata-only JSONL with `id` and `benchmark`; add `language`, `repo`, and externally supplied `difficulty` when available. Do not assign difficulty from our agents' success. `canonical_id` must identify the underlying issue across overlapping datasets: e.g. a Verified task and its Lite alias need the same canonical ID. Omit Lite from the default catalog to avoid spending budget twice on the same issue. Deduplication cannot infer aliases absent canonical IDs. Preserve a JSON list of previously exposed IDs to exclude from a fresh evaluation.

```json
{"id":"owner__project-123","canonical_id":"owner__project-123","benchmark":"swe-bench-verified","repo":"owner/project","language":"python"}
```

```bash
python3 tests/framework/benchmarks/select.py tasks.metadata.jsonl \
  --size 8 --seed 42 --strata benchmark --balance-within language repo \
  --exclude previously-exposed.json \
  --source 'dataset URL' --revision 'pinned dataset commit' \
  --output frozen-selection-42.json
```

The selector ranks task IDs by SHA-256 of seed and identity, then takes tasks round-robin across strata. Input ordering does not change the result. It writes the candidate metadata hash, original input file hash, selected task hash, source revision, exclusions, and whether every stratum fits the budget. With `--strata benchmark language`, the budget must cover every observed benchmark/language combination for full stratum coverage. This is balanced selection, not a probability-weighted estimate of the original benchmark population. An output file is created exclusively and cannot silently be replaced.

The selection manifest contains no grading implementation. A runnable task must separately provide its pinned environment, agent-visible prompt, and evaluator-owned grader. Keep reference solutions, hidden tests, and official gold patches out of the agent container. Confirm the unmodified task fails the relevant regression and the official reference repair passes before spending model budget. Record grader build/runtime costs separately from agent usage; count failed agent attempts in economic totals. For fresh repeat seeds, exclude previous selections if the purpose is new tasks; for stability repeats, keep task identities fixed and vary the run seed, recording whether the provider honors that seed.

Licensing is intentionally **TBD** in [the machine-readable catalog](benchmarks/catalog.json): the benchmark harness license does not automatically cover every bundled repository, exercise, or asset. Pin and review the selected release before redistribution or image publication.

Run selection checks:

```bash
python3 -m unittest discover -s tests/framework/benchmarks -p 'test_*.py'
```
