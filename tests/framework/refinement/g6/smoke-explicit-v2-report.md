# G6 replacement smoke — explicit invocation verified;study awaits go

**Replacement2x2 complete:4 native runs,4 valid official solves,0 study runs.** All original/replacement smoke issues remain excluded from scoring. N stays150;sample,seed and randomized arm order are unchanged. No natural/explicit effect estimates are pooled.

## Disclosure and frozen scope

Advisor-approved A/B/C amendment `32eac72` was committed before new calls. **B was motivated by activation observations after TWO natural-activation treatment outcomes (both solved) had been seen.** This is not an outcome-blind original design. The estimand is explicitly invoking efficient-coding incrementally over this pinned CLI/account's verified stock configuration,not natural activation or a universal claim about users' built-ins.

Runner allowance `5438dce` admitted the first explicit cell;metadata-only correction/remaining-three allowance `f70b07c` admitted the rest. CLI **2.1.302**,binary SHA256 `60d7eb7f12fbb28a52533fe8be5884097403562aa02dc73991a021c7067e29a5`;plugin snapshot **`920c32eb69fff4227fe1e3991046b43a805ec61e`**. Requested AND provider-reported primary model was **`claude-opus-5-5`** in all four runs. No fallback observed.60 Claude turns/7200s native cap,not G5 request equivalence.

## Per-run results

Complete CLI-reported token counts for all four runs. Native wall excludes image preparation and official grading.

| Held-out issue | Arm | Reported tokens | U / creation / read / output | Native wall | Provider model | Full skill body / full task in native context | Official grade |
|---|---|---:|---|---:|---|---|---|
| django__django-12663 | ours |80,329|8 /10,062 /68,534 /1,725|35.85s|claude-opus-5-5|yes / yes|solved|
| django__django-12663 | none |129,044|14 /8,392 /118,043 /2,595|61.29s|claude-opus-5-5|no / yes|solved|
| matplotlib__matplotlib-25311 | ours |149,287|16 /8,740 /138,763 /1,768|66.71s|claude-opus-5-5|yes / yes|solved|
| matplotlib__matplotlib-25311 | none |138,978|16 /7,562 /129,696 /1,704|76.06s|claude-opus-5-5|no / yes|solved|

Replacement total **497,638** reported tokens =54 uncached +34,756 creation +455,036 cache-read +7,792 output. Fixed5-minute cache-adjusted token-volume proxy **96,794.6**,not dollars or an inferred TTL/bill. Per-model counters and immutable native/context/attempt hashes are in `smoke-explicit-v2-summary.json` and `smoke-explicit-v2-audit.json`.

Prior natural smoke **314,731 tokens/3 runs** remains separate,including its ungraded guard-stopped control,which is **incomplete/unknown quality,not failure**. All-smoke cost bookkeeping is812,369 reported tokens across7 native runs;this sum is NOT pooled efficacy evidence. No solve-rate/token-ratio inference is drawn from these tiny held-out smoke runs.

## A — exact stock baseline and instruction sources

Every control advertised exactly these two verified native built-ins;every treatment advertised those identical entries plus `distill-sol-pi` only:

| Built-in ID/source | Path | Separate native-reported version | Code binding |
|---|---|---|---|
| cc-plugin-agents-md@builtin | builtin | not reported/null | CLI2.1.302 + frozen binary SHA |
| cc-plugin-plugin-authoring@builtin | builtin | not reported/null | CLI2.1.302 + frozen binary SHA |

Treatment additionally had `distill-sol-pi@sol-pi-skills`,version1.0.0,path `/opt/g6/marketplace`. Independent built-in versions were not invented. Both arms ENABLED slash commands and had identical17 stock skills;only treatment added efficient-coding. No assertion that every user has these built-ins/skills.

Disposable HOME,fixed settings,disabled hooks/auto-memory,empty MCP,no host home/credentials/config mounts,repo instruction-source hashes and API-only egress remained audited. Exact plugin/skill guards are not relaxed for external additions.

### Metadata guard correction,not a model retry

The network-none fake-token probe omitted stock `schedule`;the first authenticated explicit init included it,as prior authenticated runs had. The extra16-skill assertion false-stopped admissions despite the correct exact plugin set. After one explicit cell completed,the authenticated17-skill baseline was restored in preregistration before remaining calls. This correction was motivated by init metadata,not the solve value,and changed no model/prompt/plugin/CLI flags. Original guard flag,stop record,grade,charges and hashes are retained;the cell was re-adjudicated without a model or grader rerun. Only the remaining3 native cells ran. Pair timing was interrupted:about295.73s between the first Django native completion and control start;Matplotlib gap52.30s. Both issue workers were configured at concurrency2;actual native overlap depended on preparation/grade timing.

The post-smoke offline helper now explicitly distinguishes fake-token stock16 from authenticated stock17,so reproducing that probe does not silently weaken the runtime guard. Additional offline quota-restart hardening preserves prior study observations/rejection holds;it made no new remote model call. Future inference requires a newly frozen allowance.

## B — actual expansion/loading and full task

Control submitted canonical task bytes alone. Treatment submitted exactly ASCII `/distill-sol-pi:efficient-coding ` followed by those same bytes;both JSON-stdin payloads and prompt hashes were independently reconciled.

SDK replay alone showed a command envelope and was **not** accepted as body-loading proof. The CLI's native ROOT conversation JSONL stream,stored only in disposable tmpfs HOME and redacted/copied before actor stop,contained the **entire frontmatter-stripped frozen SKILL.md body and full task before the first assistant output** for each treatment. Controls contained the full task and no skill body. Native context hashes bind this evidence,not a model self-report or availability advertisement. The CLI trims outer newlines from treatment command arguments;all task content/line breaks remain,and the input suffix was byte-identical. That trimming is recorded rather than claiming byte-exact expanded trailing whitespace. No whole HOME/auth-state archive was copied.

## C — actual utilization and admission projections

| Native run | Seven-day actual before → after | Five-hour actual before → after | Highest scope admission projection |
|---|---|---|---:|
| Django ours |75% →76%|23% →0%|80%|
| Django none |76% →76%|0% →0%|81%|
| Matplotlib ours |76% →76%|0% →0%|81%|
| Matplotlib none |76% →76%|0% →0%|81%|

These are latest account-wide stream observations,not causal usage deltas attributable to a particular cell. The five-hour decrease was observed numerically in the native stream,not assumed from the reset clock. All reported scopes,including nested shorter-window records,were processed live;no additional model-specific scope was reported. Unreported scopes remain unobserved,not imputed to zero. Snapshots include observation age/origin and all outstanding reservations. At least5 percentage points per in-flight run were reserved per scope,adaptively increased for observed positive changes;maximum admission projection was **81% <90%**. External account use/coarse observations can race this projection;it is not a provider guarantee.

No5xx,429 or subscription rejection occurred. Resume cannot be authorized by elapsed reset time alone;new actual numeric headroom is required after a rejection/unknown hold. Study target remains150 even if budget forces an incomplete study.

## Integrity,cleanup and gate

- Native/expanded-context/prompt/model/usage/grade/plugin bindings reconciled for all4 cells.29 tests passed before the first cell and31 before the remaining three;post-smoke restart-hardening test increases the suite to32. No additional model/grader rerun for the metadata correction.
- Literal dedicated-token scan passed across120,841 retained explicit-attempt files;native/context redaction counts were0. No token value was printed/committed;no host `.credentials.json` or refresh session reused. This is a literal-value scan,not an arbitrary-encoding claim.
- Controllers,source preparers,actors,graders,proxy and network are absent. Exact model-stage image/base leases were reconciled with no force image removal/parent pruning. Private raw evidence and all prior charges remain;tools images retained for separately authorized work.
- **0 study calls. No study authorization,automatic promotion or inference restart. Await explicit supervisor go.**
