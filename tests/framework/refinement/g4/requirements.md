# G4 execution requirement map — ongoing, not completion

Contract5b8e715 amends049ab2a before any G4 model call. Descriptive measurements,
no gate, early stop, promotion or shipment. G1–G3 stay closed and unpooled.

| Requirement | Actual evidence / next verification | State |
|---|---|---|
| Read amended Active G4 in full | tests/goal.md lines1–85; original/amended commits | Read; active goal replaced explicitly |
| Only8000;16 total occupied run slots; all backend waiting0 admission | route-preflight.json; future shared scheduler and raw admission records | GET/get_load and/v1/models200;0 model calls |
| Treat both response labels as one model; retain response model/usage every call | Amendment applied to selection/preflight; future raw broker receipts including helper | No mixed-pool labels or per-variant share report |
| Part A only SoL-Pi and SoL-Pi+K,74 fresh runs | selection.json, original pruned/followup task plans | Original10 diagnostics/6 SWE issues identified; no redundant four arms |
| Reuse four Claude Code2.1.286 rows; cross-harness ratios informational | Original Claude campaign/report files, separate reused-row provenance | Pending exact original row/attempt accounting; no historical rewriting |
| Unmodified upstream1559b5cb…; all four full-stack mechanisms; helper8000 | Private /tmp/solpi-g4-upstream clone, original checks/logs; eventual config hash | Source clean; npm11 check158 tests passes; required high-severity audit fails; no patch |
| A blocked rather than upstream patch if cannot safely validate/run | Upstream agents-install.md mandatory stop and original audit report | Preparation halted at audit; route compatibility not tested; B/C preparation continues |
| B9 newly unsealed Terminal tasks, gold/no-op first,3 rounds | Original g1/terminal-selection.json and pinned terminal source2fd12b88… | All9 paths/source pin verified; controls pending |
| C fresh random30 excluding six+18, no replacement or readiness filtering | selection.json dataset500 hash, full482 eligible IDs, seed2026101204 |30 frozen before calls; six are already in exposed18, overlap explicitly recorded |
| Ours shipped68ea78dc; K frozen; no edits | protected-baseline.json and actual shipped SHA | Confirmed; historical/README/docs530-file baseline recorded |
| Reuse G3 runner/broker/adapters where possible without editing G3 | Future G4 scoped copies/imports and hash provenance | Pending; no source edits to G3 |
| Preregister all parts' seeds/queues/resources/analysis before first call | selection.json is explicitly selection-only, not full preregistration | Pending runtime/controls/config/analysis; no inference yet |
| B/C first while A prepares, then A; uniform once-only infra retry | Future shared16-slot queue and retained all-attempt records | Pending; no paid compatibility probe allowed before full freeze |
| Scores/TPS/timeouts/ratios vs none/K;20k paired task clusters | Future frozen descriptive analyzer and independent checks | Pending; no pass/fail or futility code |
| Original artifacts/caps/failures/unknowns retained; no imputation | Future control/native/grader/provider/model/helper receipt audit | Pending |
| No protected/external edits, no push | baseline includes allG1–G3/skill/archive/README/docs and unrelated nginx hashes | Preserved so far; user-only goal amendment hash updated explicitly |
| Actual final per-part tables, cleanup and requirement audit | Future part reports/completion evidence | Not complete |

Only local zero-model preparation has run. The first upstream attempt with
npm12.2 had156 passing tests and two package-JSON failures. A clean source check
with isolated npm11.6.2 passed all158 tests and package/type checks, without edits.
It then stopped at required `npm audit --audit-level=high`: three high-severity
locked-dependency advisories. No `npm audit fix`, dependency lock change or upstream
patch was made; subsequent install/compatibility/real-provider phases were not
silently reported as passed. Keep both failed-validation logs. Part A's current
blocker is source-install security validation, not a proven8000 incompatibility.
