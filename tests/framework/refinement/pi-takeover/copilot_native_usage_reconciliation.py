"""Offline reconciliation of the observed Copilot1.0.91 mock schema ONLY.
No I/O/inference. Fixture expectations are pinned-source expectations, NOT saved
raw provider usage. This cannot qualify real-model accounting or benchmark wins.
"""
from copilot_request_inventory import inventory
MODEL='Qwen3.8-27B-FP8'
FIELDS=('inputTokens','outputTokens','cacheReadTokens','cacheWriteTokens','reasoningTokens')
def count(x):
 if type(x) is not int or x<0:raise ValueError('nonnegative integer required')
 return x
def reconcile(native,ledger,fixture_per_call=None):
 """Return unknown/incomplete explicitly; do not pool stages or add breakdowns."""
 reasons=[];tokens=None;requests=None;turns=None;expected=None
 records=ledger.get('records',[])
 if not isinstance(records,list):raise ValueError('ledger records required')
 observed=inventory(ledger);accepted=observed['accepted_body_POST']
 if observed['denied_POST_headers'] or observed['auxiliary_denied_records'] or observed['denied_connection_count']:reasons.append('denied_or_auxiliary_attempts_retained_not_eligible')
 if not accepted:reasons.append('zero_POST_not_execution_or_solve_proof')
 for r in records:
  receipt=r.get('response_receipt')
  if receipt is None:
   if fixture_per_call is None:reasons.append('provider_response_usage_unavailable')
  else:
   inspection=receipt.get('inspection')
   if receipt.get('write_completed') is not True:reasons.append('response_delivery_unconfirmed')
   if not isinstance(inspection,dict) or inspection.get('usage_complete') is not True or inspection.get('usage') is None:reasons.append('provider_response_usage_missing_or_incomplete')
 if any(type(r.get('status')) is not int or r['status']!=200 for r in records):reasons.append('failed_or_unavailable_response')
 # Exact mock scope: unknown inference counts/unspecified receipt types reject.
 if any(r.get('synthetic_ONLY') is not True or type(r.get('inference_calls')) is not int or r['inference_calls']!=0 for r in records):raise ValueError('only saved zero-inference fixtures supported')
 if native is None:reasons.append('native_usage_file_unavailable')
 else:
  try:
   turns=count(native['totalUserRequests']);metrics=native['modelMetrics']
   if not isinstance(metrics,dict) or set(metrics)!={MODEL}:raise ValueError('missing_or_unsupported_model_metrics')
   m=metrics[MODEL];requests=count(m['requests']['count']);u=m['usage']
   if set(u)!=set(FIELDS):raise ValueError('missing_or_uncovered_usage_fields')
   values={k:count(u[k]) for k in FIELDS}
   if values['cacheReadTokens']>values['inputTokens'] or values['cacheWriteTokens']>values['inputTokens'] or values['reasoningTokens']>values['outputTokens']:raise ValueError('subset_bounds')
   agents=native.get('agentMetrics')
   if not isinstance(agents,dict) or set(agents)!={'main'} or not isinstance(agents['main'],dict) or agents['main'].get('modelMetrics')!=metrics:reasons.append('agent_breakdown_uncovered_or_mismatched')
   if requests!=observed['all_POST_headers']:reasons.append('native_provider_request_count_mismatch')
   tokens=values|{'inclusive_gross':values['inputTokens']+values['outputTokens']}
  except (KeyError,TypeError,ValueError):
   reasons.append('native_usage_schema_missing_or_invalid');tokens=None
 if fixture_per_call is not None:
  if len(fixture_per_call)!=accepted:raise ValueError('fixture expectation membership mismatch')
  sums={k:0 for k in FIELDS}
  for u in fixture_per_call:
   if set(u)!=set(FIELDS):raise ValueError('fixture expectation fields')
   for k in FIELDS:sums[k]+=count(u[k])
  expected=sums|{'inclusive_gross':sums['inputTokens']+sums['outputTokens']}
  if tokens!=expected:reasons.append('native_fixture_expected_usage_mismatch')
 return {'scope':'COPILOT_1.0.91_SAVED_SYNTHETIC_ONLY','status':'MATCHED_FIXTURE_ONLY' if not reasons else 'INCOMPLETE_OR_UNCOVERED',
         'reasons':list(dict.fromkeys(reasons)),'observed_attempt_inventory':observed,'accepted_provider_POST':accepted,'native_model_request_count':requests,'native_user_turn_count':turns,
         'observed_native_fixture_tokens':tokens,'pinned_source_fixture_expectation_NOT_raw_provider_usage':expected,
         'provider_usage_receipts_complete':False,'real_model_tokens':None,'USD':None,'native_agent_model_metrics_not_additive':True,
         'lastCall_counters_not_run_total':True,'real_scored_eligible':False}
