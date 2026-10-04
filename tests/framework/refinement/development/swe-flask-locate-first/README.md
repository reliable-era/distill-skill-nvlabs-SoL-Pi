# Locate-first SWE development — Codex results

Four Codex attempts completed and passed official grading. Pi has **zero starts** and awaits fresh login. This is one round on previously exposed SWE-bench Verified issue `pallets__flask-5014`; no candidate is promoted.

| Skill | Solved | Reported tokens | Actor seconds |
|---|---:|---:|---:|
| No skill | 1/1 | 112,352 | 38.5 |
| Karpathy | 1/1 | 151,278 | 57.4 |
| Locate-first candidate | 1/1 | 84,948 | 31.6 |
| Candidate + Karpathy (Both) | 1/1 | 128,199 | 41.3 |

Locate-first uses **24.4% fewer** reported tokens than no skill, **43.8% fewer** than Karpathy and **33.7% fewer** than Both in this Codex substage. Actual dollars, Pi results, repeated-round stability and cross-benchmark superiority remain **TBD**.

The four starts had no cutoffs or auth errors. Each official report records one fail-to-pass and 59 pass-to-pass successes, with no infrastructure failure. The no-op marker baseline was independently rejected before inference. The same frozen eight-start budget reserves four unspent Pi slots. Order seed 106 controls order, not model randomness.

Configured backend: ChatGPT OAuth `gpt-6.1-sol`, native default effort; a separately observed actual model label is **TBD**. Reported complete terminal counters include cached usage and are summed once. They are not invoice dollars.

Saved traces show 4 command executions and 13,218 returned characters for candidate versus 5 and 22,790 for no skill. Karpathy runs the full source suite and encounters the three documented unrelated cookie-domain failures. This supports further testing of focused context; it does not establish causality. Other variability and instruction overhead remain possible contributors.

Full records: [codex-results.json](codex-results.json), [summary-codex.csv](summary-codex.csv), [trace audit](trace-audit-codex.json), [stage progress](stage-progress.json), and [security/grading audit](audit.json).

## Frozen setup and remaining Pi stage

Exact native image, original snapshot/public issue, configured models, uniform inline delivery and readonly skill resources match the preceding SWE development screen. Pi selects OpenAI `gpt-6.1-sol` with thinking low; Codex selects `gpt-6.1-sol` with native default effort and ChatGPT OAuth. Actual separately observed backend labels remain **TBD** until recorded. Candidate instruction changes only the first context/read bullet; canonical skill and sealed tasks stay unchanged.

`plan.json` freezes image, source/skill/prompt hashes, runner source, standalone bridge, accounting and transcript collector before model calls. Frozen runtime files are loaded at launch; altered hashes abort. The launch command requires a frozen global stage file and writes its digest before any model calls. Root must first verify the preceding terminal stage has stopped and freeze the global eight-start stage.

Preparation runs a trusted empty snapshot-to-patch check without models. At launch, official `swebench 5.0.2` independently grades a harmless marker no-op and must reject it before actors begin; empty patches are not used as grader controls. Each stopped actor's patch is rebuilt against the trusted source snapshot and graded separately by the official harness. Dataset/gold/tests and credentials are never shared into the actor/grader across that boundary. Three known unrelated cookie-domain source-suite failures remain disclosed. Dollar costs are **TBD**.

Launch only when authorized for this stage:

```sh
python3 tests/framework/refinement/development/swe-flask-locate-first/run_screen.py --launch --harness codex --global-stage tests/framework/refinement/development-budget-locate-first.json
```

Independent exclusive `launch-codex.json` and `launch-pi.json` prevent automatic replay; each harness gets four starts and the combined total stays eight; a started attempt counts even when authentication fails. Stop remaining attempts in the affected harness on auth/quota rejection. Use `SOLPI_PRIVATE_AUTH_CACHE` pointing outside the repository, with one writable persistent HOME per harness. Seed each cache once externally, then preserve refreshed credentials across attempts under a per-harness `fcntl` lock; never recopy the stale host seed. Actor workspace temporary files are removed; private auth remains available for later attempts. Original host credentials are never written. `audit.py` checks frozen hashes, the eight-start cap, duplicate records, patch/transcript/report hashes, scores and exact secret values without model calls. Independent confirmation and economic superiority are unproven.

Availability gate: the preceding terminal Pi Both startup reported `invalid_grant` with zero model calls. The Pi portion remains unstarted. Root must verify the private auth cache or obtain a fresh human login before any explicit Pi launch; Codex may proceed independently after its credentials are verified. File presence alone does not establish valid credentials. No auth refresh or model probe is run by preparation/audit.

The superseded prepared plan and runner remain under `superseded-preparation/`; this revision happened before any actor start. Each actor writes an exclusive start ledger before invoking Docker. Root must audit the updated local/global hash binding before launching; Codex is complete; Pi remains unstarted.
