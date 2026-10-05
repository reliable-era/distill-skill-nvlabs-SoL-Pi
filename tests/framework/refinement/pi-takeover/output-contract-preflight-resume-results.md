# Guarded zero-start resumption — bounded admission still blocked

## What changed and was verified

A single guarded resumption of ALL4 UNSTARTED cells, NOT a retry of an actor. Original frozen plan/result remain byte-for-byte unchanged; original failed admission remains published. No frozen skill/runtime/model/resource/budget change. The execution link is `output-contract-preflight-resume-contract.json`, with original/generated/resume/script hashes. New pre-actor behavior: validate zero activity/only original source-pin file, prevent duplicate activation with stage lock, regenerate and compare the exact frozen plan without writing it, preserve original source snapshot and write separate resumed source/result/progress files only if admitted. Actor code region remains identical except declared progress-journal renaming. Existing model locks/source/idleness/ownership gates remain in force.

Three new guard tests passed zero-only/fail-closed cases, immutable plan/separate output, exact actor region and unchanged caps. R1 failed because test included the deliberately renamed progress journal; retained in output-contract-preflight-resume-test-r1-failure.json; only declared filename normalized for corrected comparison. Tests cover guard structure, not live actor success, grading or economics. Resume terminal auditor prepared but NOT run: no actor/transport exists to audit.

## Actual outcome

Worker1526809 terminated after the existing300-second scheduler ceiling. Measured elapsed300.0007701087743s includes timer/scheduling overhead, not a budget increase. 30 bounded metadata-only GET observations, no observed idle admission; final counts[{num_reqs:0,num_waiting_reqs:0},{num_reqs:1,num_waiting_reqs:0}]. These sampled counts do not prove continuous workload, ownership, stalled-provider causality or recover the first admission's exact response.

**0 native starts/0 actor model POST. ALL4 unstarted, no grades or actual skill delivery.** Root still only original live-source-pins.json, no transport/broker/actor state. Independent `output-contract-preflight-resume-blocked-audit.json` checks original plan/result and resume source hashes, wait result, stopped PID and OC16 containers/networks absent. No unknown work cancelled, provider patched/restarted, route switched, resource/budget raised or model fallback used. One local Qwen and frozen9/89/two-source scope unchanged.

## Decision and blocker

Blocked/inconclusive, not failed candidate/zero quality/token economy. Remaining native starts4/POST64 unused, but remaining scheduler wait0. No further waiting or automatic attempt under exhausted ceiling. Next input needed: verified reserved both-replica idle availability, with explicit remaining-budget-safe activation contract preserving all zero-start records, source/locks/plan/limits. Do not blindly rerun or overwrite plan/result, relax busy guard, retry actors, pool cohorts, change easier tasks or silently renew wait budget. If service availability cannot be established, stop scored execution with the evidence rather than manufacturing progress.

Canonical unchanged; diff checks pass. No active worker; candidate frozen but untested. Final majority3of5/families/full representative/3round/ALL3paired95%/5%complete tokens-per-verified-solve/noqualityloss/USD/exposure/promotion requirements remain unverified. Goal active/incomplete, no completion update.
