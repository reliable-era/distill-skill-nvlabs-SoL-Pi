# G6 study — PAUSED:stale-baseline quota estimator defect

**3/300 native cells,3 valid official solves,1 complete pair;297 cells unstarted.** Controller3654442 drained/exited. This is a false-positive quota/estimator guard stop,**not actual90% budget exhaustion or a model failure**. No restart is scheduled;await supervisor decision.

## Guard diagnosis and pair exception

The running-quota amendment/57-test study-only allowance was committed as `671d86c` before inference. Python sources stayed byte-identical throughout these calls. Initial headroom used the latest retained smoke counters,which were about50 minutes old. The harness incorrectly also used those stale counters as learning anchors:

| Scope | Retained learning anchor | Earliest live study observation | Latest actual | Rate retained at pause |
|---|---:|---:|---:|---:|
| Seven-day |76%|79%|80%|4pp/cell|
| Five-hour |0%|19%|20%|10pp/cell (initial update19pp/cell)|

The gap before the first live study observation spans an unobserved pre-study interval and the initial request;it is not a measured study-only delta and cannot all be assigned to completed study cells for rate estimation. The cumulative weekly76%→80% increase was divided by one completed cell,creating a4pp forecast. With three still-reserved cells,the native-admission check projected **80% +3×4%=92%**,above90%,and rejected Django's promised second arm before credential/API admission. The actual weekly counter was only80%. Earliest live weekly was79%,not80%;the subsequent79%→80% step occurred within the study and must not be discarded in a correct replay. Account-wide steps still cannot be causally attributed to a particular run.

**This was my estimator-initialization implementation error.** Diagnosis was based on counter timestamps/anchors before study solve values were read;it was not an outcome/activation-driven exclusion. No source fix or inference rerun has been applied after observing results. The failed zero-call setup attempt is retained. Django has a half-pair because the reserved-arm live guard failed;this violates the intended normal-pause pair-completeness behavior and is explicitly disclosed,not recoded as a failed solution. The already-in-flight Matplotlib pair finished both arms during draining. No429,subscription rejection,5xx or overloaded event occurred;concurrency remained2,the20-cell ramp was not reached.

## Native-run ledger

| Issue | Arm | U / creation / read / output | Total tokens | Native wall | Official grade |
|---|---|---|---:|---:|---|
| django__django-13410 |none|8 /5,622 /59,653 /944|66,227|26.375s|solved|
| matplotlib__matplotlib-26342 |ours|16 /10,734 /150,422 /1,751|162,923|42.651s|solved|
| matplotlib__matplotlib-26342 |none|16 /9,338 /139,305 /1,612|150,271|40.536s|solved|

Every actual primary model was `claude-opus-5-5`,CLI2.1.302. Exact built-ins `cc-plugin-agents-md@builtin` and `cc-plugin-plugin-authoring@builtin`,path `builtin`,versions not separately reported/null;bound to the pinned CLI binary. Treatment additionally had only `distill-sol-pi@sol-pi-skills`1.0.0 at `/opt/g6/marketplace`,snapshot920c32eb69fff4227fe1e3991046b43a805ec61e. Exact input bytes/context hashes and full task evidence passed for all three;the one treatment's full frozen skill body appeared before assistant output. Controls had no skill body. No activation-based filtering.

All-attempt study total **379,421 =40 U +25,694 creation +349,380 read +4,307 output**,complete CLI-reported usage. Fixed5-minute cache proxy **71,402.5**,not dollars/TTL inference. Prior smoke812,369 tokens remain separate;combined cost bookkeeping1,191,790 tokens is not pooled quality evidence. The blocked Django treatment had0 model calls,not a missing/imputed token bill.

## Integrity and continuation gate

`study-pause-audit.json` reconciles prompt/native/context/patch/official-grade hashes,models,plugins,usage and all frozen source hashes. Controller,actors,graders,source preparers,proxy/network are absent;7 proven-owned stage image IDs are absent and the preexisting base is preserved,no force image removal/parent pruning. Dedicated-token literal scan passed across107,724 regular retained files;symlinks were not followed,native/context redactions0. No host refresh credential/HOME archive was used. Literal scanning does not prove absence of arbitrary encodings.

A proposed correction requires supervisor approval before new calls:use each scope's FIRST LIVE study observation as its learning baseline,retaining older observations only for initial headroom;then learn from subsequent actual steps and completed study cells. Preserve/replay all original observations,all379,421 charges and these three valid grades;complete the missing Django treatment next,skip completed cells,and continue the same frozen queue without changing N. Add a stale-seed/first-live/pair-completeness regression and re-freeze before inference. This correction has **not** been applied or executed.

## Preregistered interim analysis (one known complete pair only)

The mechanical one-pair bootstrap below is degenerate and uninformative about the fixed150-task population. Its point-mass CI must not be promoted as evidence of equality/efficiency. The unpaired Django solve/cost is retained in all-attempt bookkeeping but not silently turned into a second complete pair. Full-cohort effects/rates remain unknown;unstarted cells are not failures.

Fixed150 issues /300 cells;no smoke pooling. Sample/order unchanged.

Admitted cells:3/300;native attempts:3;known outcomes:3;complete pairs:1/150.
All-attempt reported token volume:379,421 (complete CLI-reported coverage).
Cache-adjusted5-minute token-volume proxy:71,402.50;not dollars or an inferred TTL.

| Arm | Admitted | Known grades | Solves among known | All-attempt tokens (lower bound if incomplete) |
|---|---:|---:|---:|---:|
| none |2|2|2|216,498|
| ours |1|1|1|162,923|

Analysis scope:INTERIM known complete-pair subset only;not full fixed-N inference. Unstarted/unknown cells are NOT failures. No imputation.
Paired solve difference:0.0;95% task-bootstrap CI:[0.0, 0.0];exact McNemar p:1.0;discordant counts:{'ours_only': 0, 'none_only': 0}.
Bootstrap seed2026101704;20,000 draws planned,20000 executed. Empty-pair analyses are undefined,not zero/p=1.
All-cost paired TPS ratio:1.0841945551703256;CI:[1.0841945551703256, 1.0841945551703256]. Cache proxy ratio:1.110010649627263;CI:[1.110010649627263, 1.110010649627263]. Cost ratios remain undefined with incomplete pair usage;undefined bootstrap draws are reported,not silently removed.

## Quota/status

```json
{
  "utc": "2026-10-18T19:28:34.807265+00:00",
  "state": "paused",
  "cells_done": 3,
  "target_cells": 300,
  "completed_pairs": 1,
  "quota": {
    "seven_day": {
      "utilization": 0.8,
      "rate": 0.040000000000000036,
      "unknown": false,
      "anchor_utilization": 0.76,
      "anchor_completed": 0,
      "last_step": 4,
      "reset": 1792353600,
      "observed_epoch": 1792351626.8396928,
      "origin": "matplotlib__matplotlib-26342/none/1",
      "observation_window_expired": false,
      "threshold": 0.9,
      "projected": 0.8,
      "inflight_native": 0,
      "reserved_cells": 0,
      "completed_study_cells": 3,
      "observation_age_seconds": 87.96772384643555
    },
    "five_hour": {
      "utilization": 0.2,
      "rate": 0.1,
      "unknown": false,
      "anchor_utilization": 0.0,
      "anchor_completed": 0,
      "last_step": 20,
      "reset": 1792365600,
      "observed_epoch": 1792351626.839566,
      "origin": "matplotlib__matplotlib-26342/none/1",
      "observation_window_expired": false,
      "threshold": 0.9,
      "projected": 0.2,
      "inflight_native": 0,
      "reserved_cells": 0,
      "completed_study_cells": 3,
      "observation_age_seconds": 87.96785616874695
    }
  },
  "adverse_api_event_seen": false,
  "issue_workers_limit": 2,
  "next_issue_index": 2,
  "pause_reason": "Issue quota/native/isolation/cleanup guard;supervisor input required",
  "hard_stop": false,
  "errors": [
    {
      "task": "django__django-13410",
      "type": "QuotaHold",
      "detail": "Sanitized per-attempt evidence retained;no credential exception text"
    }
  ]
}
```

Running rule supersedes preflight veto and5pp floor:initial0.25pp/run;update from actual1pp utilization steps over completed study cells. Reserve whole pairs;pending second arms count toward projected usage. No clock-based utilization reset. Unexpected external counter jumps/missing actual reset evidence can fail a reserved-arm guard;report any half-pair explicitly rather than overriding the quota guard. 429/subscription rejection stops admissions and drains;supervisor decision required at pause. Concurrency2 through20 clean cells,then4 only with no429/5xx/overloaded events. All retained attempts charged;ordinary outcomes not retried.

Per-attempt usage,time,model,exact plugins,expansion,quota and artifact hashes are in `study-results.json`;raw native/context/patch/grading evidence stays private. Prior natural/explicit smoke costs812,369 tokens remain separate;all smoke cells excluded. The explicit-invocation amendment was motivated after two natural treatment outcomes had been seen;no natural/explicit quality pooling. Contamination cannot be ruled out;descriptive results only/no promotion gate.

No automatic continuation after a pause;await supervisor reset/headroom decision. No push.
