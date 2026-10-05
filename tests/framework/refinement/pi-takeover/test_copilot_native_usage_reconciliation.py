import unittest,copy
from copilot_native_usage_reconciliation import reconcile,MODEL
U={'inputTokens':24,'outputTokens':12,'cacheReadTokens':8,'cacheWriteTokens':0,'reasoningTokens':4}
def native():
 m={MODEL:{'requests':{'count':2},'usage':dict(U)}}
 return {'totalUserRequests':1,'modelMetrics':m,'agentMetrics':{'main':{'modelMetrics':copy.deepcopy(m)}},'lastCallInputTokens':12,'lastCallOutputTokens':6}
def ledger():return {'accepted_body_POST':2,'all_POST_headers':2,'records':[{'ordinal':i,'verb':'POST','path':'/v1/chat/completions','accepted':True,'status':200,'synthetic_ONLY':True,'inference_calls':0} for i in (1,2)]}
class Tests(unittest.TestCase):
 def test_two_calls_one_turn_no_double_count(self):
  r=reconcile(native(),ledger(),[{k:v//2 for k,v in U.items()}]*2);self.assertEqual(r['status'],'MATCHED_FIXTURE_ONLY');self.assertEqual(r['observed_native_fixture_tokens']['inclusive_gross'],36);self.assertEqual(r['native_user_turn_count'],1);self.assertFalse(r['real_scored_eligible']);self.assertIsNone(r['real_model_tokens'])
 def test_missing_native_unknown_not_zero(self):
  r=reconcile(None,ledger());self.assertIsNone(r['observed_native_fixture_tokens']);self.assertIn('native_usage_file_unavailable',r['reasons'])
 def test_failed_empty_metrics_not_free(self):
  n=native();n['modelMetrics']={};l=ledger();l['records'][0]['status']=422;r=reconcile(n,l);self.assertEqual(r['status'],'INCOMPLETE_OR_UNCOVERED');self.assertIsNone(r['observed_native_fixture_tokens']);self.assertFalse(r['provider_usage_receipts_complete'])
 def test_last_call_as_aggregate_rejected(self):
  n=native();n['modelMetrics'][MODEL]['requests']['count']=1;r=reconcile(n,ledger());self.assertIn('native_provider_request_count_mismatch',r['reasons'])
 def test_duplicate_ordinal_rejected(self):
  l=ledger();l['records'][1]['ordinal']=1
  with self.assertRaises(ValueError):reconcile(native(),l)
 def test_bool_negative_missing_and_uncovered_fields(self):
  for change in [lambda u:u.update(inputTokens=True),lambda u:u.update(outputTokens=-1),lambda u:u.pop('reasoningTokens'),lambda u:u.update(hiddenTokens=4),lambda u:u.update(cacheReadTokens=25)]:
   n=native();change(n['modelMetrics'][MODEL]['usage']);r=reconcile(n,ledger());self.assertIsNone(r['observed_native_fixture_tokens'])
 def test_auxiliary_and_mismatched_agent_flagged(self):
  n=native();n['agentMetrics']['subagent']={};l=ledger();l['records'].append({'verb':'GET','path':'/unsupported','accepted':False,'status':403,'synthetic_ONLY':True,'inference_calls':0});r=reconcile(n,l);self.assertIn('agent_breakdown_uncovered_or_mismatched',r['reasons']);self.assertIn('denied_or_auxiliary_attempts_retained_not_eligible',r['reasons'])
 def test_real_receipts_outside_scope(self):
  l=ledger();l['records'][0]['inference_calls']=1
  with self.assertRaises(ValueError):reconcile(native(),l)
 def test_terminal_zero_native_usage_without_provider_usage_incomplete(self):
  n=native();n['modelMetrics'][MODEL]['usage']={k:0 for k in U};n['agentMetrics']['main']['modelMetrics']=copy.deepcopy(n['modelMetrics']);l=ledger()
  for r in l['records']:r['response_receipt']={'write_completed':True,'inspection':{'usage_complete':False,'usage':None}}
  r=reconcile(n,l);self.assertEqual(r['status'],'INCOMPLETE_OR_UNCOVERED');self.assertIn('provider_response_usage_missing_or_incomplete',r['reasons']);self.assertIsNone(r['real_model_tokens'])
 def test_expected_usage_mismatch(self):
  r=reconcile(native(),ledger(),[{k:0 for k in U}]*2);self.assertIn('native_fixture_expected_usage_mismatch',r['reasons'])
if __name__=='__main__':unittest.main()
