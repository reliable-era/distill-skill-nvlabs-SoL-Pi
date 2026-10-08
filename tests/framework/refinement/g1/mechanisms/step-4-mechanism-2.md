# Mechanism / candidate 2: effect-checked shell transitions

Candidate 1's complete twelve-cell screen failed: observed Go quality loss,
1.4467 tokens-per-solve ratio against No skill, and no defined ratio against
zero-solve Both. It is retained unchanged and is the first non-improvement.

## Measured exposed-development sink

Read only the twelve completed candidate-1 native traces and provider receipts.
`candidate-1-sink-inventory.json` retains request-growth and native-command
metadata; `candidate-1-error-sink-audit.json` joins by directory index and cell ID
(not by arbitrary filesystem enumeration order). No sealed trace was read and
no inference was used to diagnose these attempts.

The four Go arms had respectively:

| Arm | Requests | Commands with permission-error text | Those/other visible failures masked by exit 0 | Solved |
|---|---:|---:|---:|---|
| No skill | 20 | 3 | 2 | Yes |
| Karpathy | 26 | 6 | 5 | No |
| Candidate 1 | 22 | 4 | 2 | No |
| Both | 18 | 5 | 5 | No |

All four incurred environment-error detours. Saved traces show writes followed
by later successful shell commands obscuring the failed write, repeated checks
of unchanged permissions, and test binaries failing to execute in temporary
storage. These are model-visible operating conditions in valid completed runs,
not the earlier zero-model startup failures. No old attempt will be rerun or
regraded into a different result. All roles had the same existing isolation,
capability and resource settings. This candidate does not change them.

Go input tokens accounted for 96.40–96.77% of complete token cost. Every avoidable
extra request can retransmit growing history. The command/error counts do not
identify exactly which tokens were caused by a detour and do not establish that
any skill caused the original failure. Masked-failure classification is a text
proxy, not an exhaustive shell parser. HTML and TeX also had some visible failure
markers masked by exit 0, but effect size across tasks remains unknown.

## Hypothesis and single change

Copy the unchanged canonical skill and support resources. Add one bullet:
make shell transitions fail loudly, verify the requested effect, and handle an
environment error with one focused prerequisite inspection followed by the
smallest authorized local repair. Never repeatedly retry an unchanged failure,
conduct broad speculative audits, or alter protected/shared/security boundaries.

This targets **error-state propagation and recovery**, not candidate 1's
reasoning-length mechanism. It contains no Go-specific operation, target output,
hidden test expectation, fixture solution or runtime permission change. It is
not a restart of an archived candidate or infrastructure stage. Candidate 1's
extra bullet is absent. Correctness checks and repairs remain mandatory.

Reducing dead-end state transitions might reduce accumulated input cost by
approximately 25%, but could instead add checks, change behavior adversely, or
save nothing. None of those outcomes is assumed in advance.

## Frozen second screen

Use the same three fixed exposed control-solvable tasks: HTML, food-chain, TeX.
Four **fresh** arms each: No skill, frozen Karpathy, candidate 2, same candidate 2
plus Karpathy. One round / twelve cells. The balanced ordering, two six-cell
waves, route, caps, resource profiles, original graders, public verifier cache,
role isolation and accounting are identical to candidate 1. Do not borrow its
controls, retry completed cells, substitute tasks, adjust loads or increase caps.

`candidate-2-screen-plan.json` freezes full skill trees, schedule and resource
specifications before calls. Each new four-hour window must be committed before
use; latest start leaves the full 7200-second wall cap. Direct18001 only; valid
running <8; waiting allowed; admission backoff <=600 seconds.

Qualification keeps the preexisting approximately 25% target: candidate total
complete tokens / verified solves <=75% of each comparator, without observed
solve loss overall or in either represented family. Undefined ratios and unknown
costs/grades prevent qualification. Report wall and uncertainty separately.
An improvement below the target requires strictly lower finite ratios against
all comparators with no solve loss; it does not qualify a winner. If this candidate
also fails to improve, stop after two consecutive non-improvements, even with a
third slot unused. If it improves but misses the target, at most one final
measured candidate may be considered. No acceptance rule is changed.

Two of at most three candidate slots are now defined. No second-candidate model
call has occurred at this writing. No winner, sealed confirmation or promotion
is authorized by mechanism definition alone.
