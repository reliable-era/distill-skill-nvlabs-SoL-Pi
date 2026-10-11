# G3 prompt-to-artifact completion audit

**Final disposition: negative mandatory round1 futility; not savings acceptance.**
The deliverables are the separate G3 result, round/total four-arm scores and all
ratios/paired95% intervals, original grading/cost/provenance artifacts, owned
cleanup and this requirement-by-requirement audit. Contract source is unchanged
`tests/goal.md` Active G3, committed `68cff75`. Completion does not mean completing
ineligible rounds or changing that immutable contract file.

Each row identifies inspected actual evidence, not merely a planned manifest.
`audits/round1.json` reconstructs private bytes; `audits/final-execution.json`
checks live cleanup, original controls, resource mounts and independently summed
raw terminal SSE usage; `analysis/round1-independent.json` reproduces statistics.
None of these proxy certificates alone proves all the rows below.

| ID | Explicit requirement / success criterion | Concrete evidence inspected | Disposition |
|---|---|---|---|
|G3-01| Contract68cff75; separate G3 cohort | Active G3 lines1–77; plan contract/model/route; report.md | Complete; Qwen3.8 direct9012, no historical pooling |
|G3-02| Preserve closed G1/G2 results | Protected file hashes, git diff68cff75..HEAD for g1/g2 empty; final-execution scoped commit checks | Complete; historical results unchanged |
|G3-03| Frozen candidate SHA39f7b309… and Karpathy | Actual full skill trees and per-cell copies/prompts checked by audit.py; final-execution identities | Complete; no skill edit |
|G3-04| Exactly four arms none/K/candidate/Both=same candidate+K | Plan arm_skills plus reconstructed actual prompts/resource tree,196 cells per arm | Complete; none has no resources, Both has same two trees |
|G3-05| Pinned7e0611… source;225 enumerated | Actual source git HEAD and all six language directory lists re-enumerated in final-execution | Complete;225 |
|G3-06| Exactly14 original development exclusions leave211 | Original g1/polyglot-selection.json SHA/list matches controls-plan; set subtraction rechecked | Complete; no substituted exclusions |
|G3-07| Gold/no-op on all211 before any model call |211 original rows plus6 setup/count repairs;428 original log hashes, manifests and positive accepted-test counts; three original preparation errors retained | Complete; latest original-test pairs cover all211 |
|G3-08| Failed-controls-only exclusions, explicit records | Actual final controls map196 valid/15 failed; exclusion sets equal plan/control audit; per-mode exits/logs | Complete; no model-based task exclusion |
|G3-09| Record local control repairs without weakening tests | b587ceb, original and repair results/old errors; reference-only C++/Java mappings, Jest counts | Complete; six pre-inference repairs, original test semantics preserved |
|G3-10| Preregister sources/resources/skills/analysis before calls |5d9ca19/7257c9d Git blobs match immutable plan/original analyze.py; controls/runtime/freeze commits precede first actual POST | Complete; original source bytes preserved in frozen-v1 |
|G3-11| Full three-round queues/seeds, task shuffle and adjacent random arms | plan.json full2352 queue; round_boundary.py independently regenerates all rounds with seeds2026101200/1300/1400 | Complete; no outcome-selected schedule |
|G3-12| Three rounds conditional on full round1 futility, maximum2532 before controls |196×4×3=2352 frozen after valid-control exclusions;784 actual round1 roster; inference-stop.json | Complete under negative stop;1568 future cells ineligible |
|G3-13| Rolling18 occupied run slots, start only free slot+all waiting0 | Actual maximum_active_slots, serialized admission events, per-attempt admission.json, source behavior and full order certificate | Complete; peak18, no old running<8 rule |
|G3-14| Direct127.0.0.1:9012 only, modelQwen/Qwen3.8-27B |6,660 receipt backend/model/path and forwarded payload checks; actual actor network-none relay/socket mounts | Complete; no alternate route/fallback |
|G3-15| GET/v1/models preflight and every round start | route-preflight/runtime-preflight and each of five window identities; boundary certificate | Complete; only round1 eligible and started |
|G3-16| Record backend every request | Original private ledgers/receipt hashes indexed; all6,660 direct9012 | Complete; none missing |
|G3-17| Codex0.160.0 fixed binary | Actual binary SHA equals plan; codex --version returned codex-cli0.160.0; all readonly binary mounts | Complete |
|G3-18|60 requests/7200s/16384 output caps unchanged | Original implementation/caps; all actual requests≤60, payload cap16384, raw output usage≤16384; final cap counts | Complete; zero run caps,114 individual output-cap responses retained |
|G3-19| Infra never-model/refused/reset uniformly once-from-scratch, preserve both costs | Original classification/next_attempt source, all784 actual attempt1 records, none infra_retry_eligible, no cleanup errors | Complete; zero eligible or actual retries, none suppressed |
|G3-20| Never rerun model errors/caps; keep failures | Original784 attempt hashes,564 failures,114 output-cap responses retained; first36 not retried/excluded | Complete; no completed-model rerun |
|G3-21| Specific owned live handle before waits, no observation-timeout restart | Launch PIDs and explicit bounded polling through terminal; wave reports and durable ledgers | Complete; original schedulers reused, never restarted |
|G3-22| Committed bounded windows before inference; retire unused allowance |88afe49/2461722/d5c6ea3/e983287/a21fb66, launches and actual request timestamps;4h end/+2h latest; inference-stop | Complete; all actual admissions/requests within windows, all future allowance retired |
|G3-23| Full boundary before any futility or round2 |784 unique cells,196/arm, all admissions exact frozen order, original grades/repairs and owned cleanup checked by round1-boundary | Complete; no partial analysis/gate or round interleaving |
|G3-24| Futility candidate/none OR candidate/K point≤.95 and no fewer solves; no early win | Original round1.json and independently reproduced integer gates:52<56 and52<57, C/none1.154659615 | Complete; mandatory negative stop; no round2 call |
|G3-25| Final3 comparison gates, all3 rounds required | Frozen original analyze.py GATES and acceptance predicate; round1 observed comparisons in report | Correctly not eligible; no final acceptance or early success claimed |
|G3-26| Candidate/Both informational only | Original PAIRS/GATES and report ratio table | Complete; never used as acceptance gate |
|G3-27|20k paired task-cluster95%, recorded seed; undefined+∞ retained | Original analysis plus independent Counter-weighted vectors, seed2026101111, all six exact intervals/endpoints/counts match | Complete; zero undefined draws observed, none discarded |
|G3-28| Include all failed attempts/provider costs; no cost imputation | Every request/response hash checked; independent direct terminal-SSE input+output=total sum equals each audited cell | Complete;6,660 requests/113,901,577 exact tokens |
|G3-29| Unknown costs only conservative treatment; cannot prove acceptance with unknown numerator/undefined ratios | Original tests/conservative rule, raw12 flags retained and exact captured usage projections; all final costs physically complete | Complete; no surrogate needed, no estimated missing usage |
|G3-30| Original graders/artifacts/grades preserved; no solve rescue | Captured final-work/original private grader/verifier SHA checks; two named180s timeout replays with passing gold, raw2/null preserved | Complete; derived failed-test outcomes explicitly marked,0 model calls added |
|G3-31| All-arm per-round and total scores, requests/tokens/TPS/timeouts/ratios/CIs | report.md, original analysis, private-artifact index, independent/bootstrap/final-execution outputs | Complete; round1=total; future rounds labeled unattempted/ineligible |
|G3-32| Quality/round/runtime/wall uncertainty, distinguish disposition from savings | Report descriptive Wilson intervals, no quality-equivalence claim, missing round variability, native wall sums, first36 regime confound | Complete; no homogeneous-runtime/pure-skill causal or universal-savings claim |
|G3-33| Actual prompt/resource/test/image/binary/native/receipt provenance | Original audit plus private-artifact index784 captures/6,660 receipts/428 control logs; immutable images, readonly mounts,8,154 load samples | Complete; original private bytes retained, not replaced by hashes |
|G3-34| Owned cleanup and no pending eligible work | Actual ps on seven original worker handles plus replay, Docker owned namespace empty, no custom networks; all terminal windows | Complete; no live owned broker/actor/grader or retry; artifacts retained |
|G3-35| Terminal-Bench sealed/unattempted; no other-task substitutions | Exact225/211/196 task-set reconstruction;784 actual cells all frozen Aider roster | Complete; no Terminal-Bench inference |
|G3-36| No prohibited infrastructure/workload intervention;9012 outage pauses, no repair/fallback | Recorded scoped actions, isolated actor mounts, fixed direct backend; no admin/config/other-route calls | Complete; no outage requiring final blocker; readonly /load404/OpenAPI diagnostics disclosed |
|G3-37| Agent changes only G3/STATUS; no shipped/README/archive/excluded edits or push | Every agent commit path since68cff75 checked; g1/g2/skills/archive/goal diff empty; unrelated nginx modification+three backups still present | Complete; explicit external supervisor README-only193494a exception, no agent README edit/restoration or push |
|G3-38| Final prompt-to-artifact audit before goal complete | This checklist, report.md, completion-audit.json and actual final-execution/independent evidence hashes | Complete only after final cross-check and committed certificate |

## Qualifications that remain in the final result

- The first36 startup-owner-affected cells are permanently included. Prospective
  byte-identical UID0 starter repair does not erase heterogeneous runtime exposure.
- Raw12 early cost flags are parser failures, not physically absent usage. Original
  byte/hash-verified terminal usage recovers actual totals without model calls.
- Two raw exit2/null grades remain. Exact captured zero-step loops fail original
  tests at the unchanged180s deadline twice; original gold passes. Derived failures
  are documented, not successful-grade imputation or infrastructure model retries.
- Three pre-control preparation failures had no executed checks on their initial
  attempt; all three received original gold/no-op pairs before inference. Another
  three existing Jest pairs were rerun only to correct pass-count parsing. Final
  controls cover all211; original failures are not discarded.
- Supervisor README-only commit193494a is outside this agent's work and outside
  experimental inputs. Its exact old/new hashes are explicitly recorded; every
  other protected-source check remains strict. No agent restoration or edit.
- Negative means the preregistered experiment stopped on its observed gates.
  It does not establish savings, universal inferiority, quality equivalence or
  the result of the forbidden future rounds. No candidate is promoted.
