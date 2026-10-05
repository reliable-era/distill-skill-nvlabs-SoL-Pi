# Copilot native saved-usage reconciliation — offline, deliberately ineligible

CURRENT MISSING-USAGE NEGATIVE nativeCopilot gate: plan0c05b5c833343ec7c2b258905b87b939ab3e6fa31349acde137097a9229282ba/root/tmp/solpi-cpmu-0c05b5c833343ec7;1native1syntheticPOST200/exit0/actualACK/0realinference/0retry/sourcecapscleanupverified. Retained bounded370byte responsehash/writecompleted370: stop+DONE butNOusageevent. Native1modelrequest/1userturn reportsALLusagezeros; providerusageUNAVAILABLE_NOT_ZERO. routing_passONLYprotocol NOTaccounting. Actualsavedreconciliation INCOMPLETE_OR_UNCOVERED;10regressiontestsPASS including nativezero+missingproviderusage;3receiptfixturetestsPASS. Read ../copilot-native-local-route/mock-missing-final-usage/README.md/execution-audit.json. No oldpositivegate rerun/priorresultchange/realcostinference; appwritealoneNOTallbyteconsumptionproof. Remainingactualmidstreamcutoff/auxiliaryprovideraccounting/actualQwen/delivery/gradedperformance unverified. Canonicalunchanged/candidateunstarted/schedulerwait0/noactiveworker/goalINCOMPLETE.


Added copilot_native_usage_reconciliation.py, test_copilot_native_usage_reconciliation.py (9 tests PASS), audit_copilot_saved_usage_reconciliation.py. Actual saved pinned1.0.91 native schemas/ledgers audited without any new native start, providerPOST, network, process or model call. Plan/source/private artifacts checked against original execution audits; stages not pooled or altered.

| Independent saved stage | Accounting classification |
| --- | --- |
| unsupported intent stream,1POST422 | INCOMPLETE_OR_UNCOVERED; empty native model metrics, tokenusage unavailable |
| guard diagnostic,1POST422 | INCOMPLETE_OR_UNCOVERED; empty native model metrics, tokenusage unavailable |
| final stream,1POST200 | MATCHED_FIXTURE_ONLY; input12+output6=18synthetic |
| declared view tool loop,2POST200 | MATCHED_FIXTURE_ONLY; input24+output12=36synthetic |

For failed receipts, native userturn count0 does not establish providerrequest0 or tokens0. Missing nativeusage yields None, not zero. Per-model call counts must equal acceptedPOST inventory; totalUserRequests counts turns and is NOT a provider-cost counter. Agent/main mirrors are not added; lastCall fields are not aggregate usage. Cache/reasoning subsets not added. Unknown/missing fields, booleans-as-integers, negative counts, subset violations, unexpectedmodels, unmatchedagentbreakdowns, failedresponses, auxiliary headers, duplicate/missingordinals and membership mismatch cannot pass the narrowed reconciliation. Unsupported real-inference receipts are rejected, not relabeled fake.

Fixture expectations derived by AST literal parsing of unchanged pinned provider_fixture.py FAKE_USAGE, not executing source or inventing provider observations. Successful native totals equal those fixture expectations; **raw provider response usage was NOT retained by these mock gates**. Thus provider_usage_receipts_complete=false and real_scored_eligible=false EVEN on MATCHED_FIXTURE_ONLY. real_model_tokens/USD remain unavailable. No mock token count enters benchmark accounting. This reconciler is explicitly saved-synthetic-schema-only, NOT a production real-Qwen accounting adapter.

The tests cover manufactured malformed/missing cases and observed schema behavior. They DO NOT prove native behavior after actual transport cutoff, complete auxiliary detection, fresh native receipts, actual Qwen behavior, candidate delivery or original grading/quality/economy. Passing offline tests or saved happy paths cannot qualify primaryharness confirmation.

## Next concrete gap

Any prospective native gate should retain bounded response status/hash/usage/terminal events and independently reconcile accepted+denied+auxiliary request inventory, completion/drain and native accounting. A separately frozen missing-final-usage/cutoff fixture is changed-behavior evidence; do not rerun unchanged successful controls. No real model inference, scoring-wait renewal or server change is authorized by this offline work. Scored output-contract stage remains entirelyunstarted/schedulerwait0; canonical unchanged, noactiveworker, goal incomplete.
