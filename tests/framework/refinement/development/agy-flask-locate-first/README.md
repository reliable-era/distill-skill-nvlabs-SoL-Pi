# Native agy Flask development — results

Four native `agy` attempts completed with SDK SUCCESS and passed independent official grading. This reuses development issue `pallets__flask-5014` from SWE-bench Verified. One round, no confirmation and no promotion.

| Skill | Solved | SDK-reported total | Actor seconds |
|---|---:|---:|---:|
| No skill | 1/1 | 333,547 | 139.0 |
| Karpathy | 1/1 | 196,669 | 92.7 |
| Locate-first candidate | 1/1 | 168,379 | 61.7 |
| Candidate + Karpathy (Both) | 1/1 | 143,299 | 50.8 |

Locate-first uses **49.5% fewer** reported tokens than no skill and **14.4% fewer** than Karpathy, but **17.5% more** than Both. It does **not** beat every comparison here. Cross-task stability, actual billing and independently observed backend remain **TBD**.

Each official report records one fail-to-pass and 59 pass-to-pass successes, with no infrastructure failure. All four actors exited 0 within their caps; no SDK errors, timeouts or auth rejection occurred. The original marker no-op control was independently rejected before inference.

Requested native model: `gemini-3.8-flash-low`; actual backend routing is **TBD**, not inferred from the requested label. Native ELF 1.2.16 was mounted readonly and SHA pinned. The displayed metric is terminal SDK `usage.total_tokens`, retained once without assuming cache/thinking overlap. Cache-read counters exceed that total in some arms; complete gross token traffic, counter scopes and overlap require verification and remain **TBD**. These totals cannot yet satisfy the goal’s complete-token accounting gate. Billing components and invoice dollars are **TBD**.

The frozen local/global four-start budget, runner/classifier/bridge/accounting/collector hashes, original prompt/source, native ELF and image were verified before calls. Order seed 108 controls order, not model sampling. The pre-call auth classifier correction is preserved under `superseded-preparation/`. Classification tests distinguish terminal ERROR.error from benign source/tool text. An exclusive launch marker forbids automatic replay.

Actors received uniform inline SKILL.md text and complete readonly resources. Private dataset, original test patch/gold and grader credentials were not mounted into actors. Stopped snapshots were converted to patches against trusted original source, ignoring actor Git metadata, and independently graded with `swebench 5.0.2`. Three known unrelated source-suite cookie-domain failures remain disclosed; task grading passing does not prove full-suite cleanliness.

Google OAuth was seeded once into a private persistent HOME outside Git. Updated authentication persists under `agy.lock`; host seed was never written. Original/refreshed exact credential scans and frozen artifact/report hashes pass in [audit.json](audit.json).

[External-access audit](external-access-audit.json) retains native tool parameters and test/web/fetch candidate events. Local source/test mentions do not establish remote access. Native cloud-search gating and invisible network calls remain **TBD**; zero markers cannot establish clean held-out isolation. This is exposed public development, never confirmation.

Artifacts: [results](results.json), [CSV](summary.csv), [stage progress](stage-progress.json), raw transcripts/patches/workspaces under `agy/`, and official reports/test outputs under `official/`. Canonical skill and sealed tasks are unchanged.
