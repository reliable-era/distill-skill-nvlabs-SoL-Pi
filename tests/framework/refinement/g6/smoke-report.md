# G6 partial smoke — BLOCKED,study not ready

**Three of four native smoke cells ran. Admissions stopped at the control isolation guard. No study calls,automatic restart or gate relaxation.** The controller drained and exited;owned actors,graders,proxy and network are absent. Raw evidence remains private.

## Preparation and provenance

- Contract/sample commit `d1fe82a`:444 eligible cohort,150 outcome-blind Hamilton repository-stratified study issues,two seeded held-out smoke issues;sample unchanged.
- Pinned runner/image and four real no-model Docker fixtures: `a7eb0bf`. Final stdin-transport verification and19 passing unit tests/smoke-only allowance: `591d9dfcd7ba5022cf856e22acbe2bc6793d9cb0`.
- Plugin snapshot: `920c32eb69fff4227fe1e3991046b43a805ec61e`;normal local marketplace installation,not a dirty-worktree or inline-skill treatment.
- CLI **2.1.302**;requested and provider-reported primary model **`claude-opus-5-5`** for every native run. No fallback observed.60 Claude turns/7200-second native wall cap,not G5 request equivalence.
- All runner source hashes remain frozen at first inference. The initial setup-only hold/transport repair had zero native starts or streams;its evidence is retained separately. No treatment results were available then.

## Per-run results

Tokens are complete **CLI-reported** counts for these three native runs,including the rejected control. U/C/R/O=uncached input/cache creation/cache read/output. Wall time is the headless CLI interval,not image preparation or grading.

| Issue | Arm | Token volume | U / C / R / O | Native wall | Model ID | Skill advertised / explicitly invoked | Official quality |
|---|---|---:|---|---:|---|---|---|
| django__django-12663 | ours |70,574|8 /7,559 /61,476 /1,531|27.67s|claude-opus-5-5|yes / no|valid,solved|
| django__django-12663 | none |82,931|8 /20,919 /60,860 /1,144|32.18s|claude-opus-5-5|no / no|**unknown: guard stopped before capture/grading**|
| matplotlib__matplotlib-25311 | ours |161,226|18 /7,442 /151,858 /1,908|88.88s|claude-opus-5-5|yes / no|valid,solved|
| matplotlib__matplotlib-25311 | none |—|—|—|not run|not run|not run|

Matplotlib treatment was already in flight when the Django control guard fired. It finished and was graded;the second Matplotlib arm was never admitted. No failed control quality was invented,and no post-hoc source reconstruction/regrade was attempted after its actor was removed.

**All native charges retained:**314,731 reported tokens =34 U +35,920 C +274,194 R +4,583 O. Fixed5-minute cache-adjusted token-volume proxy **76,936.4**,not dollars or a billing/TTL estimate. Per-model counts and native/attempt evidence hashes are in `smoke-summary.json` and `smoke-audit.json`. There is no paired solve/TPS inference from this incomplete smoke,and none of these issues enters study scoring.

## Why the guard stopped

The fresh control's installed-plugin inventory was empty and its advertised skill list was empty under `--disable-slash-commands`. Nevertheless,native stream init advertised two **CLI-bundled** plugins:

- `cc-plugin-agents-md` (`path: builtin`)
- `cc-plugin-plugin-authoring` (`path: builtin`)

They also appeared in treatment,which additionally advertised `distill-sol-pi`. This is bundled CLI behavior,**not evidence of a host settings/credential mount**. It conflicts with the runner's literal no-control-plugins guard,so admissions stopped before control patch capture/official grading. The offline installed-plugin check alone did not expose native bundled declarations. The guard has not been relaxed after observing results.

**Activation caveat:**the frozen parser's `ours_loaded` field means availability in init `skills`,not independently proven loading of the full `SKILL.md` body. Neither treatment emitted an explicit `Skill` invocation or an explicit `Read` of that file. Full-body loading is therefore not independently established;no activation-based filtering or efficacy claim is made. Treatment also advertised stock built-in skills,which must be addressed explicitly when finalizing the intended isolation baseline.

## Limits,credentials and cleanup

- No terminal5xx,429 or subscription rejection. Four native rate events across the three runs were `allowed_warning`,reporting seven-day utilization0.75 and reset epoch1792353600. This account-level warning is not an attributed smoke usage delta. The admission stop was isolation-related,not a quota reset pause.
- Runtime token was passed only via tmpfs env files to Docker exec;not via command-line values,image or container-create environment. No host `.credentials.json` was read/copied and no refresh flow was reused. Literal token scanning passed across60,411 retained attempt files;native redaction counts were0. This is a literal-value scan,not a claim about arbitrary encodings.
- All three actors and their owned graders are absent;owned proxy/network and controller are absent. Exact image leases/intermediate ownership were reconciled with no force image removal or parent pruning. Tools image is retained for offline investigation/future separately authorized work. Root free at summary generation:1,821,918,355,456 bytes.

## Required next input

**Do not authorize the300-run study from this report.** First resolve the bundled-plugin/skill baseline offline:verify a way to suppress unintended built-ins,or explicitly approve which immutable CLI built-ins count as baseline. Then freeze the clarification and request a new allowance for a replacement2x2 smoke,retaining all existing charges/evidence. No additional inference is authorized by the current stopped launch. Await supervisor direction.
