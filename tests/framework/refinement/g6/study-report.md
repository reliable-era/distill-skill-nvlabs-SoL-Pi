# G6 — completed150-task paired study

**Result:no supported solve-rate or token-per-solve improvement from explicit efficient-coding in this pinned native-Claude configuration.** All300 cells/150 pairs completed;no exclusions or unstarted/unknown outcomes. Control solved141/150 (94%);treatment138/150 (92%). Treatment used almost the same reported token volume,but slightly more tokens per solve and more of the specified cache proxy per solve. This is not an equivalence/non-inferiority result or a promotion decision.

## Results

| Arm | Known outcomes | Solves | Reported tokens,all attempts | Cache-adjusted proxy |
|---|---:|---:|---:|---:|
| Stock control |150|141 (94%)|15,587,905|3,145,164.85|
| Explicit efficient-coding |150|138 (92%)|15,452,049|3,354,867.05|

- **Primary paired solve difference,treatment−control:−2.00 percentage points**,95% task-bootstrap CI **[−4.67,0.00]pp**. Exact two-sided McNemar **p=0.25**;discordants:treatment-only0,control-only3. Control-only solves:`django__django-14140`,`sympy__sympy-13852`,`pylint-dev__pylint-4551`. The result does not establish preserved quality.
- Secondary all-attempt **tokens-per-solve ratio,treatment/control:1.0128**,95% CI **[0.9073,1.1091]**:no demonstrated token-per-solve saving.
- Secondary **cache-proxy-per-solve ratio:1.0899**,95% CI **[1.0074,1.1658]**:higher under this proxy,not an estimate of dollar cost or actual cache TTL.
- Ratios below1 favor treatment. All CIs use the preregistered20,000 paired task-bootstrap draws,seed2026101704,linear percentiles. Zero undefined secondary draws. Inference is descriptive/unadjusted;no multiplicity-adjusted promotion claim.

## Accounting and independent scope reconciliation

Study:300 native invocations plus one retained **zero-native** quota-refused setup attempt (`django__django-13410/ours-a1`). All charged native attempts are retained;ordinary outcomes were not retried. All300 outcomes are valid official Boolean grades,including failures.

Total reported study tokens **31,039,954** =3,118 uncached input +2,568,308 cache creation +27,979,999 cache read +488,529 output. Proxy **6,500,031.90** =U+1.25C+0.1R+O;volume=U+C+R+O. No missing counters are imputed.

The frozen runtime parser still marks the historical multi-result SymPy control `usage_complete=false`,and its generated efficiency fields remain null in `study-results.json`. **Those raw flags,counters and nulls were not changed.** A separate zero-call audit of every one of the300 native receipts proves that each root `result.usage` is segment-local and every `result.modelUsage` is its cumulative prefix sum. The final aggregate equals the reported counters for each invocation;compare the two scopes,never add both. Only that historical invocation has a runtime false flag. The secondary ratios above are the preregistered calculation on these independently reconciled,unchanged reported counts;see `study-usage-reconciliation.json` and `scope_reconciliation` in `study-results.json`.

Prior smoke remains separate:812,369 tokens/7 native calls;no quality pooling. Study+smoke bookkeeping=31,852,323 tokens,not a pooled efficacy estimate. The failed read-only OAuth validation was one non-model HTTP403,not an inference probe or a token-bearing study cell.

## Execution and quota history

- Fixed150 Hamilton repository-stratified issues from444 G5-eligible issues;sample/order unchanged and chosen without G5 outcomes. Binding `9341ed43fb126642ba4dd8e9a6894be6e9692096537a243d9c1e61e0aa84c89a`. No G1–G5 quality pooling.
- Executed allowances:initial3 cells `671d86c770c00e8d305e39a175e58d8d72bae914`;next9 `6d36e9a9182418bd07bbac35f3ac60d11e08dbfc`;last288 **`123723733e800ba97007fb8af858434e018b5849`**. All were committed before their calls. All original12 native/context/grade hashes,outcomes and1,873,521 reported tokens remain unchanged. The initial stale-anchor defect and approved first-live/idle-learning correction are retained historical disclosures,not silently rewritten.
- Supervisor confirmed the setup-token is inference-only and OAuth403 was expected. The OAuth quota client was deleted under1237237;the specifically superseded stop marker was archived with its hash. **No controller quota-endpoint validation/polling after that GO.** No host credential/refresh-state access or paid probes.
- Cell13 (`django__django-11728/ours`) started2026-10-18 22:24:20.530572 UTC. Two issue workers through20 clean completions,then four;no observed429/5xx/overloaded event.
- **Live automatic reset episode:**pause23:20:20 UTC on the last native five-hour reset epoch1792365600 (23:20). After reset+120s and prior native/grading work drained,exactly one next frozen normal cell,`astropy__astropy-13398/ours`,was admitted23:23:58. Its control partner was already valid and was not rerun. Its own native headers reported weekly6%/five-hour0% with a later five-hour reset and passing projections. The pair completed and normal scheduling **automatically resumed23:31:17**,without supervisor intervention. No other new native cell entered during this hold. Reset utilization was measured,not inferred from the clock;the used reset permission is durable.
- **Complete2026-10-19 00:55:51 UTC**,300 cells/150 pairs,zero half-pairs,controller exited. Last observed weekly7%/five-hour7%;no actual weekly60% crossing. These are observations,not guarantees of future headroom.

The retained running policy uses first-live anchors,positive deltas within native-active intervals,unobserved-idle exclusion and a1pp/cell estimate cap,without clipping actual account utilization. Initial rate0.25pp/cell,no5pp floor or full-N veto. Whole pairs reserve headroom;pending partners count. Weekly projected ceiling70% after1792353600,five-hour90%,all reported temporal/model scopes guarded. Ordinary holds use one next frozen study cell after binding reset+120s,then its fresh native-header guards and partner before normal concurrency;no reuse for another cell on the same reset. Unknown/rejected/unrelated guards are not bypassed. Completion,actual weekly60%,429/subscription rejection,terminal5xx exhaustion,isolation/guard/harness/cleanup failure or credential hit remain reportable;no automatic restart across reportable stops.

## Configuration,activation and limitations

Pinned CLI2.1.302,primary `claude-opus-5-5`,no fallback;60-turn/7200s native caps,not G5 per-request equivalence. Observed maximum33 summed root-segment turns/5,567.19s. Both arms have the same17 authenticated stock skills/commands and exact CLI-bound built-ins (`cc-plugin-agents-md@builtin`,`cc-plugin-plugin-authoring@builtin`,versions absent/null). Treatment alone adds frozen plugin `920c32eb69fff4227fe1e3991046b43a805ec61e` version1.0.0 and the ASCII `/distill-sol-pi:efficient-coding ` prefix plus the same canonical task.

All300 native/context receipts verify the exact model,plugins,prompt/task bytes and treatment's full frontmatter-stripped skill body before assistant output;advertisement/SDK envelope alone is insufficient. CLI outer argument-newline trimming is disclosed. **The explicit-activation amendment followed two already-known solved natural treatment outcomes.** Natural/explicit smoke is excluded from scoring;this amendment was not outcome-blind. The150-task sampling was outcome-blind. Scope is this eligible cohort and pinned CLI configuration;model contamination cannot be ruled out. Shared-account quota observations are confounded by other account use.

## Final audit and retained evidence

`study-final-audit.json` independently verifies all300 model/plugin/activation/grade/artifact bindings,all12 retained cells,and the one-cell automatic resume episode. **75 tests pass.** No owned actors,graders,source/proxy containers,network or runtime environment files remain.151 image leases released;574 owned stage image IDs absent;29 preexisting bases preserved. No forced image removal or parent pruning.

Literal credential scan passed across **7,444,210 regular study files**;2,143 symlinks skipped,zero native/context redactions. This is a literal scan,not a guarantee against arbitrary encodings. No host HOME/config/refresh-state mounts;owned API-only CONNECT egress and nonroot resource/capability restrictions preserved. Unrelated README/G4/backend work untouched. No push.

Per-attempt counters,time,models,exact plugins,expansion,quota and artifact hashes remain in `study-results.json`;scope receipts in `study-usage-reconciliation.json`;raw native/context/patch/grading evidence remains private at `/tmp/solpi-g6-09e98b4cb8f4`. Generated raw analysis and pre-annotation report/results are preserved in `study-checkpoints/final-004/`,along with prior pause/guard checkpoints. No automatic restart or additional inference is authorized by this completed report.
