# Bounded-search Terminal development result

**No promotion: observed quality drops.** Bounded-search fails the official exact-replacement check while no skill and Both pass. Its lower raw token count therefore does not establish economic superiority. Karpathy fails the unrelated-file check.

| Instructions | Solved | Reported tokens per attempt | Actor seconds |
|---|---:|---:|---:|
| No skill | 1/1 | 252,618 | 144.0 |
| Karpathy | 0/1 | 186,036 | 127.6 |
| Bounded-search candidate | 0/1 | 216,037 | 144.2 |
| Karpathy + bounded-search | 1/1 | 282,498 | 151.0 |

All four authorized starts completed within the cap; no retry, timeout, or availability result was discarded. Candidate and Karpathy have zero verified solves on this task, so their tokens per verified solve are **TBD**, not a finite efficiency score. Actual billing USD, server-resolved model, and stability remain **TBD**. Requested model is OpenAI `gpt-6.1-sol` via Codex, native effort defaults.

The candidate removes all tested credentials and preserves unrelated files, but adds quotes around AWS placeholders instead of the exact frozen reference text. Karpathy removes/replaces credentials correctly but also changes `tools/eval_expdb.py`. Both original failures remain unchanged and replayed; there are no repaired results.

## Reported token split

| Instructions | Uncached input | Cached input | Output |
|---|---:|---:|---:|
| No skill | 19,406 | 229,632 | 3,580 |
| Karpathy | 29,531 | 153,472 | 3,033 |
| Bounded-search candidate | 21,199 | 191,616 | 3,222 |
| Karpathy + bounded-search | 24,451 | 254,336 | 3,711 |

Reasoning tokens are included in output and are not added again. Cache-write counters are explicitly zero. These native counters are not actual subscription charges. Candidate’s raw total is 14.5% below no skill, principally from fewer cached tokens; its uncached input increases. Quality prevents treating that reduction as a win.

## Evidence and limits

This is one reused `sanitize-git-repo` development task, one round, order seed 109. Model sampling seed is TBD. It is not fresh held-out confirmation or evidence of stable performance across families/harnesses. The canonical skill is unchanged, and earlier negative stages remain intact.

The [plan](plan.json) and separate [global budget](global-budget.json) freeze four starts of at most 180 seconds, no retries, complete selected resources mounted read-only, and inline Markdown. [Root authorization](execution-authorization.json) matches the exact plan/budget hashes. The same pinned native image, public task, offline official pytest grader, and persistent private Codex HOME/shared `codex.lock` are used; host credential seeds are never written.

The task and official tests come from [Terminal-Bench 2, pinned commit 2fd12b8](https://github.com/harbor-framework/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/sanitize-git-repo). The native image preserves Python 3.13 and full Git history; dependencies are preinstalled rather than installed through Harbor/uvx. Baseline/oracle controls fail/pass as expected. Actor containers cannot access verifier tests or solutions. Original and replayed graders have no credentials and no network.

Every actor’s complete Git, working-tree, and untracked file contents are captured before its original verifier, from the first actor. [Replay audit](replay-audit.json) reconstructs the pristine pinned baseline plus compact deltas, verifies original patch SHA256 and every reconstructed file hash, and confirms all four original grader outcomes without model requests.

[Publication audit](publication-redaction-audit.json) records digest redactions and original/published hashes. Raw originals remain privately outside Git; replay restores patch markers only from pinned public baseline values. No push-protection bypass is used. [Credential scan](credential-scan.json) checks currently available host/private auth strings and decompressed delta members; earlier rotated strings absent from these files remain outside scope.

[Trace metrics](trace-metrics.json) measure original unredacted command output and split counters. Returned characters are not tokens or independently verified model-visible payload. [Normalized results](results.json) · [CSV](summary.csv).
