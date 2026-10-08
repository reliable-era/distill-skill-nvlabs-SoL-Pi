# G1 final development result: stop; savings goal not achieved

Two new mechanisms were screened on the same three fixed exposed tasks with
four fresh matched arms each. Neither met the all-comparator gate. Candidate 2
improved on No skill and Karpathy, but cost more per verified solve than its
own Both arm. The frozen stop rule now ends this search. The third candidate
slot is unused. No further window or inference is started.

## Score table — development only, separate cohorts

| Screen | Arm | Solves / 3 | Complete tokens, including failures | Tokens / verified solve |
|---|---|---:|---:|---:|
| Candidate 1 | No skill | 2 | 4,485,890 | 2,242,945 |
| Candidate 1 | Karpathy | 1 | 5,897,596 | 5,897,596 |
| Candidate 1 | Candidate | 1 | 3,244,909 | 3,244,909 |
| Candidate 1 | Both | 0 | 6,094,590 | Undefined |
| Candidate 2 | No skill | 1 | 6,740,629 | 6,740,629 |
| Candidate 2 | Karpathy | 2 | 5,797,995 | 2,898,997.5 |
| Candidate 2 | Candidate | 2 | 3,208,285 | 1,604,142.5 |
| Candidate 2 | Both | 2 | 2,319,543 | 1,159,771.5 |

| Candidate | Ratio vs No skill | Ratio vs Karpathy | Ratio vs Both | Quality / decision |
|---|---:|---:|---:|---|
| 1: bounded reasoning | 1.4467 | 0.5502 | Undefined | Lost food-chain solve; reject |
| 2: effect-checked transitions | 0.2380 | 0.5533 | 1.3832 | No observed count loss; fails Both; reject |

Candidate 2 uses 76.20% fewer tokens per solve than No skill and 44.67% fewer
than Karpathy, **but 38.32% more than Both**. These favorable partial comparisons
are not a goal win: G1 requires all three comparators. Candidate 1 also failed
that gate and lost quality. The preregistered candidate-2 definition therefore
records two successive non-improvements against the all-comparator goal gate;
this does not mean candidate 2 showed no improvement on any individual measure.

## What was and was not verified

Steps 0–3 completed under the recorded user amendments and standing authorization.
All 18 sealed gold/no-op control pairs pass. The calibrated nominal caps remain
60 requests / 7200 seconds / 16384 output tokens, with direct18001 only.
The verified development pool contains HTML, TeX, food-chain and SPARQL. The
fixed screens use HTML, food-chain and TeX, selected before their outcomes.
Two measured mechanisms and both complete twelve-cell screens were committed.

Screen inventory only: **24 starts / 798 requests / 37,789,437 complete tokens;
11 verified solves / 13 failures; zero unknown costs or grades**. Four
request-cap hits remain included. This is accounting inventory, not a pooled
performance estimate across tuned skills, calibration or historical protocols.
All four screen workers are terminal; their owned containers and networks are
independently absent. No completed screen cell was retried or replaced.

**No winner freeze, sealed model confirmation, three independent confirmation
rounds, paired task-cluster confidence interval, acceptance analysis or promotion
occurred.** All 216 confirmation cells remain unstarted. The separate
Terminal-Bench and Aider ≥5% savings criteria and 95% ratio intervals below 1
are unverified. The samples remain sealed from model attempts and unchanged.
Readiness, valid controls, complete costs and cleanup are not savings evidence.

## Quality, variability and wall time

Each screen has only one development round with two Terminal-Bench tasks and
one Aider task. Candidate 1 lost the Aider solve against its No-skill control.
Candidate 2 has one observed solve in each family, matching skilled comparators'
counts; task identities differ (candidate solved HTML, others solved TeX).
Small observed counts do not establish population-quality equivalence.

There is substantial variation across tasks and arms, including different fresh
control outcomes between screens. The screens are separate tuning cohorts, not
independently repeated rounds of one fixed candidate. Do not borrow their best
outcomes or combine them into a confidence claim. Round variability and
confirmatory quality uncertainty remain unmeasured.

Candidate-2 native wall per solve: No skill 33.74 min, Karpathy 20.55 min,
candidate 14.63 min, Both 8.59 min. Failed attempts are included. Candidate-1
native wall per solve: No skill 24.49 min, Karpathy 52.56 min, candidate 25.00
min, Both undefined. These descriptive wall results are separate from tokens.
Load flags were retained without adjustment, exclusion, reruns or causal
slowdown claims. Tokens are not dollars; **no USD claim**.

## Preserved state and evidence

Canonical `skills/efficient-coding/SKILL.md` SHA256 remains
`68ea78dcb9ee8a565f99c8a1b8bfec13f4c6d65c5695ce847eb5577b0449b1ef`.
Candidate 1 SHA: `e11948951958094ea411a5da55610c9ba8f68404d352950830a35d7c4161096d`.
Candidate 2 SHA: `39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25`.

Authoritative details: `step-5-candidate-{1,2}-report.md`, both
`mechanisms/candidate-*-screen-plan.json` and independent screen audits, all four
wave results/completion audits, `final-development-stop-audit.json`, and
`prompt-to-artifact-audit.md`. Raw native/provider/artifact/grader traces stay
private at the recorded launch roots. All prior failures, repaired original
grades, zero-model startup attempts and unknown historical costs remain separate.

Immutable archive hashes and sealed-selection hashes remain unchanged. No
excluded path changed after the accepted Step 0 archive boundary (99fdcb3).
The scope audit retained its initial incorrect-cutoff assertion: comparing from
7423ef8 included the accepted archival snapshots in 13e65d8/9cb6b1f. Git history
resolved the cutoff; no historical file was edited to make the audit pass.
No old stage resumes, shared server/nginx/gpu01 change or unknown-workload
intervention is part of this closure.

## Disposition

**Negative development stop; G1 savings objective not achieved.** Keep canonical
unchanged. Do not start a third candidate or confirmation under this exhausted
search contract. Continuing would require a new explicit work contract or a
user-authorized change to the search/stop rule; this report does not authorize
one and does not weaken final acceptance.
