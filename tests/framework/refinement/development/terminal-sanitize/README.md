# Terminal-Bench development screen

The no-reread candidate is **not a promotion candidate** on this screen. It saves reported tokens in Codex relative to no skill, but Both uses fewer tokens. In Pi, the candidate fails the official exact-replacement check while Karpathy passes.

One previously exposed development task, `sanitize-git-repo`, one round. These are development observations, not held-out confirmation or evidence of stable superiority.

| Instructions | Pi solved | Pi reported tokens | Codex solved | Codex reported tokens |
|---|---:|---:|---:|---:|
| No skill | 0/1 | 77,835 | 1/1 | 496,186 |
| Karpathy | 1/1 | 200,483 | 1/1 | 324,770 |
| Ours (shipped) | 0/1 | 83,932 | 1/1 | 231,951 |
| Lean parent (candidate) | TBD | TBD | 1/1 | 261,263 |
| No-reread (candidate) | 0/1 | 189,311 | 1/1 | 180,561 |
| Karpathy + no-reread | TBD | TBD | 1/1 | 175,414 |

Tokens are raw per-attempt totals, including failed patches; they are not tokens per verified solve for rows with no solves. Billing USD is **TBD**. Pi lean-parent and Both are unavailable authentication/runtime starts, not task failures or free attempts.

Codex no skill hit the 180-second process cap after emitting one complete terminal usage record; its saved patch passes all three official tests. Pi no skill, shipped, and no-reread remove credentials but fail the exact file-equality test, including added quotes around placeholders. These frozen grader outcomes are retained without repairs or retries.

Requested backend is OpenAI `gpt-6.1-sol` in both harnesses; Pi reports that model in events and uses low thinking. Codex uses native defaults and does not independently disclose a server-resolved model ID. Cross-harness totals are not controlled comparisons of identical prompts or effort.

## Method

The task and official tests come from [Terminal-Bench 2, pinned commit 2fd12b8](https://github.com/harbor-framework/terminal-bench-2/tree/2fd12b88aafdd04a52c298e3940bcb189f9766d6/sanitize-git-repo); image and runtime identities are in [provenance.json](provenance.json). Native CLI libraries were added to the official task image with [Dockerfile.terminal-native](../../../benchmarks/Dockerfile.terminal-native), preserving Python 3.13 and the original Git history. Actor containers have neither `/tests` nor `/solution`. Baseline fails and the official oracle passes all three tests.

The verifier runs the unchanged official test source with its exact pytest invocation and package pins, in a separate network-disabled Docker container with no authentication mounts. Its install/bootstrap phase is preinstalled through pip rather than Harbor/uvx. This is an official-test integration, not a complete Harbor native-agent run.

All arms receive frozen SKILL.md text inline. **Delivery deviation:** supporting resources were frozen but not mounted in this terminal stage. [Delivery audit](delivery-audit.json) found no invocation matching known supporting-resource paths or SKILL.md discovery. Indirect reads outside those parsed arguments are not ruled out. This stage must not be described as a full installed-bundle test. Future confirmation must provide complete resources consistently.

[Original plan](plan.json) freezes 12 starts, 180 seconds each, one round, shuffled order seed 105. Model sampling seed is TBD. [Resume plan](resume-plan.json) freezes the remaining nine slots after correcting private Pi credential import. Existing starts are never replayed; the original 12-start budget includes two failed availability starts. The host authentication seeds remain read-only or are copied into disposable writable Pi HOME outside the task tree.

## Audit limits

[Results](results.json), per-arm transcripts, original verifier outputs, diffs, and [availability records](availability.json) retain every start. [Replay audit](replay-audit.json) reconstructs saved states and reruns the official tests without models or credentials.

The first five records (Pi lean-parent availability; Codex Karpathy, shipped, no skill, and no-reread) retain tracked diffs and status only. Their official original grades and diff replay are available, but final untracked files and mutable Git metadata are not fully captured. No stronger completeness claim is made.

The remaining seven records retain per-file manifests and compressed deltas against [baseline-files.json](baseline-files.json), including full Git history and untracked files. Pi shipped has one explicit missing capture: `.git/index`; all other files, Git objects and refs are captured. Its replay restores the baseline index and is not a byte-exact original-index reconstruction. Full local snapshots stay outside the Git repository.

[Credential scan](credential-scan.json) checks exact values from available host auth seeds, including decompressed archive members; discarded private refresh values are outside that scan’s available scope. Task fixtures deliberately contain fake credential strings.

## Publication redaction

GitHub push protection rejected token-shaped strings in public task transcripts and removed lines of patches. Published evidence replaces those strings with digest markers; original execution hashes remain unchanged, and [publication-redaction-audit.json](../publication-redaction-audit.json) records original and published hashes. Original raw files remain outside Git under restrictive local permissions. Protection is not bypassed.

Replay reconstructs patch markers only from freshly copied pinned public baseline content, verifies the original patch SHA256 before applying it, and checks published transcript hashes against the redaction audit. It does not reconstruct original transcripts or hardcode credentials. All twelve verifier outcomes must still agree. The baseline verifier refreshed Git index stat-cache before the original baseline hash freeze; a compact preparation delta restores that index after replay verifies identical staged entries in the fresh image.
