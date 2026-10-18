# G6 study — incomplete,paused at quota preflight

**Supervisor GO received;0/300 study cells admitted.** The fixed150-issue sample,arms,randomized paired order and explicit-invocation configuration from `9d95eb8` are unchanged. No study controller,Docker actor,credential read,API quota probe,model call or grader run was started. The stop is the supervisor's remaining-N quota guard,not model failure or missing credentials.

## Budget evidence and reason for pause

Supervisor estimate: **0.25 percentage points per native run**. For300 first-attempt cells alone,this forecasts **75 percentage points**. Retries/external account use could add demand. This is a forecast,not actual usage or imputed billing.

Latest retained actual seven-day utilization is **76%**,from the replacement-smoke stream. At preflight it was about22 minutes old,not a new live account query. The input hash,observation/evaluation epochs and age are in `study-budget-summary.json`. No new observation or automatic reset-to-zero was invented.

| Scenario | Forecast / ceiling | Result |
|---|---|---|
| All300 in current window |76% +75% =151% nominal demand;ceiling90%|does not fit|
| All300 in a hypothetical fresh week |75%;ceiling70%|does not fit,even starting at zero|
| Current window plus upcoming fresh week,keeping ALL existing guards |optimistic36 +260 =296 calls|still fewer than300|

The cross-reset calculation avoids imposing an unnecessary same-window-only assumption. The existing minimum **5-percentage-point in-flight reservation** remains:the new0.25pp cost forecast does not authorize reducing it. With utilization `u`,forecast rate0.0025 and cap `c`,the last of `n` serialized admissions requires:

```text
u + (n -1) *0.0025 +0.05 < c
```

- Current window: `u=0.76,c=0.90` permits at most36 calls;the37th admission reaches90%.
- Hypothetical new week: `u=0,c=0.70` permits at most260 calls;the261st reaches70%.
- Total296<300,even ignoring retries,other account usage,shorter/model-specific limits,parallel reservations/adaptive increases and preparation time before reset. Actual feasibility could be worse. This is not a claim that300 can never finish over an explicitly authorized longer multi-week schedule or with verified revised inputs.

The reset is epoch **1792353600**,2026-10-18 20:00UTC /2026-10-19 04:00+08. The cap changes from90% to70% at that boundary,but utilization can only decrease on actual numeric evidence,not the clock. The supervisor's new-week60% notification condition has not been observed;this preflight occurred before reset and made no new API query. The historical76% observation is not misreported as a new-week crossing.

## Execution/authorization state

| Quantity | State |
|---|---:|
| Preregistered issues |150,unchanged|
| Target study cells |300|
| Admitted study cells/attempts |0 /0|
| Complete study pairs |0|
| Unstarted cells |300;not failures|
| Study model tokens |0,exact because no study inference occurred|
| Study credential/API-probe accesses |0|
| New model/grader retries |0|

The intended ramp remains concurrency2 through20 cells,and4 only after20 with zero429/5xx/overloaded events across attempts. No cell was admitted,so the ramp was not reached or claimed tested in live study execution. Paired adjacency/order and record-and-rerun policies were not changed.

User GO is recorded as received in preregistration;admissions remain closed. The historical smoke-only allowance is not an executable study allowance,and the study budget guard now runs before credential/Docker work. No timed or unattended restart was scheduled. Raw preflight/hold evidence stays in the private G6 root;all prior traces/charges remain intact. No unrelated Docker/Git object was modified.

## Preregistered analysis at pause

There are **no study observations**. Do not reuse smoke results,impute300 failures,claim0% solve rate,or treat unstarted pairs as concordant.

| Planned analysis | Result |
|---|---|
| Control / explicit-skill solve rates |undefined;0 admitted per arm,not0%|
| Paired solve-rate difference |undefined/null|
|95% paired task-bootstrap CI |undefined;seed2026101704 preserved;20,000 draws planned,0 executed because no pairs|
| Exact McNemar p-value / discordant counts |undefined/null,not p=1|
| Paired all-attempt token-volume/solve ratio and CI |undefined/null|
| Cache-adjusted token-volume proxy ratio |undefined/null|

`study-results.json` encodes these null results and reasons. No efficacy,efficiency,promotion or contamination conclusion follows. Future completed analyses retain the same preregistered methods and eligible-cohort scope;contamination cannot be ruled out.

Prior natural smoke:314,731 reported tokens/3 native runs;replacement explicit smoke:497,638/4. Their **812,369 total reported tokens** remain separate cost bookkeeping,not study usage or pooled quality evidence. All smoke issues/cells remain excluded from scoring. The post-two-treatment-outcomes motivation for explicit activation and metadata-only stock guard correction remain disclosed in the original smoke/protocol records.

## Verification and next input

-42 unit tests pass,including exact strict-threshold capacity arithmetic,reset boundary,model-specific weekly caps,no reset-time imputation,conditional concurrency eligibility,old-versus-new-week60% notification,and preflight rejection before credential/Docker access.
- Frozen sample/order binding remains `9341ed43fb126642ba4dd8e9a6894be6e9692096537a243d9c1e61e0aa84c89a`.
- No study launch marker,study progress/native artifacts or active G6 controller was created. No credential value was read for this preflight,printed or persisted.

**Await supervisor direction.** A defensible continuation needs verified revised headroom/forecast inputs or explicit authorization for a longer cross-week allocation or reservation-policy change. Do not silently lower the5pp reservation,raise the70% cap,reduce N,or spend study calls to recalibrate a failed preflight. No push.
