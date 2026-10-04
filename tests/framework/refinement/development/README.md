# First candidate screen: not promoted

One metadata-selected Aider Go food-chain task, one round, two native harnesses.
Each configuration passed independently restored official exercise tests.
Both means lean candidate plus frozen Karpathy. All five arms used uniform inline
skill text; source and image hashes are in each harness plan. These are development
results under an adapted Aider protocol, not leaderboard or confirmation results.

| Configuration | Pi reported tokens | Codex reported tokens |
|---|---:|---:|
| No skill | 11,421 | 61,433 |
| Karpathy | 15,499 | 101,214 |
| Shipped ours | 14,216 | 97,443 |
| Lean candidate | 11,877 | 97,578 |
| Lean candidate + Karpathy | 16,691 | 103,654 |

The candidate uses **4.0% more** reported tokens than No skill in Pi and
**58.8% more** in Codex. It improves on shipped ours in Pi but slightly worsens
Codex. This fails the baseline target: do not promote or run this candidate on
sealed confirmation. Ten attempts, no automatic retries or timeouts. All actual
billing dollars remain TBD. Pi confirms GPT-6.1-Sol; Codex config selects that
model but its transcript does not expose an independently observed backend ID.
Effort controls differ between harnesses; compare within each harness.

[Pi plan/results](pi-go/README.md), [Codex plan/results](codex-go/README.md),
[independent regrading](independent-grade-audit.json).

Codex runtime limitation: `/bin/sh -lc` resets PATH and could not find the
installed `/usr/local/go/bin` tools. No skill stopped after the lookup error;
the candidate located the binaries and continued checks, adding calls. This is
a verification/tool-discovery confound. Future images must expose tools to login
shells and freeze a new comparison; do not interpret the gap as pure prompt overhead.

Next development work should inspect new traces for extra tool calls and scope,
then test a different mechanism on a broader development panel. Do not claim
causal savings from the shorter entrypoint or replace the sealed task allocation
with tasks that favor a revision. Canonical shipped skill remains unchanged.
