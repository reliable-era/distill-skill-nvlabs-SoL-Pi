# G6 study — running-quota amendment,start authorized

Pre-launch snapshot:0/300 study cells. Supervisor clarification supersedes the full-N preflight veto and5pp reservation. The historical pause report/empty analysis remain in `study-preflight-report.md` and `study-preflight-results.json` (and commit16aab94). They are not active vetoes.

Fixed150 issues x{control,explicit skill};sample/order/model/CLI/plugin/task and all smoke exclusions unchanged. Reserve both frozen-order arms before starting an issue. Project actual observed utilization +(active native +pending promised +candidate cells)*running rate. Initial rate0.25pp/cell;after actual1pp steps update cumulative utilization delta /completed study cells since observed-window anchor. No5pp floor,no remaining-N veto,no clock-based reset to zero. Seven-day ceiling90% before1792353600,70% afterward;all reported shorter/model-specific scopes remain guarded.

Normal quota pause stops NEW pairs and drains reserved pairs,then writes cells/utilization/rate and reports for supervisor decision. Any429/subscription rejection stops ALL admissions immediately and drains;retain charges and record-and-rerun only after explicit reset/headroom and supervisor continuation. Unexpected account counter jumps/expired reset evidence can fail a promised-arm live guard;report any incomplete pair rather than bypass quota/auth/isolation. Cross-week continuation is allowed,but no unattended restart after a reported pause.

Concurrency2 through20 completed clean cells,then4 only with no429/5xx/overloaded event. All attempts charged,ordinary model outcomes not retried,terminal5xx retain the five-attempt/backoff/circuit rule. Report actual new-week weekly utilization>=60%,every pause,and completion. No inference occurred before recording this clarification/freeze.

Runtime status/evidence stays private under the existing G6 root: `study-status.json`,`study-admission-events.jsonl`,`study/*/*/attempt-result.json`. At pause/completion,`study_analysis.py` replaces this snapshot with the actual report and `study-results.json`:20,000 paired task bootstrap (seed2026101704),exact McNemar,all-attempt TPS/cache-proxy ratios when coverage permits. Unknown outcomes/usage and unstarted cells are not imputed;interim complete-pair subset is labelled,not the full150-task estimand. Smoke costs812,369 tokens stay separate. No natural/explicit quality pooling;post-two-treatment-outcomes activation motivation remains disclosed. Contamination cannot be ruled out;descriptive/no promotion gate.

No push.
