# Locate-first Terminal-Bench development screen

**No promotion.** All four patches pass the official tests, but locate-first uses **34.1% more reported tokens than no skill** and **34.2% more than Karpathy**. It saves tokens relative to Both on this round.

| Instructions | Solved | Reported tokens | Actor seconds |
|---|---:|---:|---:|
| No skill | 1/1 | 235,386 | 122.2 |
| Karpathy | 1/1 | 235,145 | 131.5 |
| Locate-first candidate | 1/1 | 315,603 | 144.9 |
| Karpathy + locate-first | 1/1 | 435,312 | 171.7 |

This is one reused development task (`sanitize-git-repo`), one round, order seed 107. Model sampling seed, actual billing USD, and stability are **TBD**. These results do not establish performance on fresh held-out tasks or a majority of harnesses. The canonical skill is unchanged.

The actor is Codex requesting OpenAI `gpt-6.1-sol` with native effort defaults. Server-resolved model ID is TBD. All arms receive frozen inline Markdown and complete selected resources mounted read-only at `/skills`; automatic retries are zero. The private persistent Codex HOME is locked through the same `codex.lock` as the Go experiment; host credentials are never written.

The [plan](plan.json) binds the [global budget](global-budget.json): four actor starts capped at 180 seconds each. All four completed; no timeout, failure, or availability outcome was discarded. Immutable runtime, bundle, prompt, source, and image hashes are recorded before actors.

The task and official tests come from [Terminal-Bench 2, commit 2fd12b8](https://github.com/harbor-framework/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/sanitize-git-repo). The same pinned native image from the previous stage preserves Python 3.13 and the task’s Git history. Baseline/oracle controls fail/pass as expected. The unchanged official pytest tests run in separate credential-free, network-disabled Docker containers; dependencies are preinstalled rather than installed through Harbor/uvx.

Every actor’s complete Git, working-tree, and untracked file contents are captured before grading, including original Git metadata. Compact deltas and file hashes reconstruct the pinned pristine baseline; no full repository trees are published. [Replay audit](replay-audit.json) checks the original patch SHA256 and all reconstructed file hashes, then reruns the official tests without model requests.

GitHub token-shaped fixture strings are published as digest markers in text evidence. [Publication audit](publication-redaction-audit.json) records original/published hashes; originals stay outside Git under restrictive permissions. Replay restores patch markers only from freshly pinned public baseline content and never hardcodes credentials or bypasses push protection. [Credential scan](credential-scan.json) covers current host/private auth strings and decompressed delta members; earlier rotated strings no longer available are outside its scope.

[Normalized results](results.json) · [CSV](summary.csv).
