# Exposed security fixture contract audit

Evidence: `development-contract-review.json`, original public instruction and pinned original verifierSHA57e4904177acac5807b51f7c32444bde1968ba0445855fa4333d9eb73865b59e. No model calls, edits, alternate grades or confirmation task inspection.

## What the verifier actually covers

1. Removal checks five known values in three fixed current files, not all repository files/history.
2. Replacement compares entire files against three exact references, not solely semantic replacement correctness.
3. Other-file checking requires a fixed original Git commit and diffs against it. It does not independently compare the captured original file manifest.

The prompt requires API-key removal and protecting uncontaminated files, without explicitly defining Git-history scope or exact formatting preservation. Therefore official scores certify their checked conditions, not exhaustive historical eradication or credential revocation.

## Actual completed-cell diagnosis

- Original Ours: two changed worktree files match their references exactly; the third still contains a known secret and differs semantically. This is substantive incomplete sanitization, not merely a formatting false negative.
- Both: all three affected current files match reference bytes exactly and known values are absent. Captured manifests show three non-.git changed files. The original verifier's required fixed commit no longer exists after history rewriting; the other-files test fails its Gitdiff precondition. This is not proof of unauthorized worktree edits. Comprehensive history cleanup itself still needs separate evidence.

Keep every original failure unchanged. Do not relabel Both as solved, revise tests after outcomes, use the diagnostic as a winning metric, or copy the reference/secret values into a candidate. The current five-arm panel must finish unchanged. These limitations make further outcome-driven tuning on this development fixture weak evidence; a positive official score alone cannot prove full security semantics. Any next development/confirmation decision must explicitly account for this contract limitation and preserve the fixed nine-task allocation without substitutions.
