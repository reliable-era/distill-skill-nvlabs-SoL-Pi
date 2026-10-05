# Read-only follow-up: allocation and resource symptoms

Evidence: `audit_scratch_request_allocation.py` / `scratch-request-allocation-audit.json`, and `audit_scratch_resource_errors.py` / `scratch-resource-error-audit.json`. Same completed scratch-capacity panel; 0 new provider POST, actors, classifier training, graders, fixtures or native probes. No canonical/runtime/service/budget changes. No new candidate or matrix prepared by this review.

## Allocation finding

| Arm | Emitted exec declarations | Emitted stdin declarations | Empty-poll requested yields (seconds) | Nonzero native completed commands |
|---|---:|---:|---|---:|
| Candidate | 14 | 3 | 30, 30, 20 | 3 |
| Both | 15 | 4 | 30, 30, 30, 30 | 4 |
| No skill | 13 | 3 | 120, 180, 240 | 3 |
| Karpathy | 13 | 4 | 20, 30, 30, 30 | 1 |

Actual tool schema permits exec yields through 30s and empty stdin polls through 300s. Candidate/Both/K chose shorter waits and exhausted their 16-POST allowances before the full actor wall limit; No skill already declared longer waits and still failed. **Do not infer polling dominated failures or that longer waits would solve them.** Emitted declarations include final responses not subsequently executed; tool calls need not equal provider requests. Requested yields are not measured waits or CPU time. No marginal causal polling cost is claimed.

## Stronger recurring symptom

Nonzero completed commands retain `pthread_create failed` / `Resource temporarily unavailable` in all four arms: candidate 2 commands, Both 3, No skill 1, K 1. Candidate's explicit PID-limit read occurs later; no matched explicit effective-limit read precedes the first resource symptom in any arm. Source pattern absence is not proof of no implicit knowledge; error text and exit status do not establish exact PID/CPU cause. Missing packages and invalid API methods are separate errors.

Initial symptom matching also counted a successful diagnostic command repeating the symptom text. Preserved `scratch-resource-error-audit-r1-unfiltered.json`; current filter restricts to nonzero completed commands, explicitly excluding successful diagnostics and masked pipeline failures. No actor/grader retry involved.

## Decision / next action

No polling-only successor justified by this evidence yet; longer-wait counterexample and non-dominant polling counts matter. Prioritize a bounded read-only review of how resource-error recovery changes settings versus diagnoses effective limits, before any single portable recovery rule is drafted. Do not convert error counts into savings, exact causality, hidden-quality predictions, or required task-specific settings. Do not rerun stopped actors, retrieve deleted models, enlarge budgets or modify shared inference services.

Terminal original panel remains 4/64/913671 COMPLETE provider tokens, 0/4 verified solves, rejected for promotion, owned cleanup verified. Other cohorts remain separate. Majority harness coverage, representative/family confirmation, three rounds, ALL3 95% paired intervals/5% tokens per verified solve/no-quality-loss, supported USD/exposure/promotion remain unverified. Goal active/incomplete.
