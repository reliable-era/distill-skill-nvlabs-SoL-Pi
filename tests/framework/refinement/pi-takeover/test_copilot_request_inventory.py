import unittest,copy
from copilot_request_inventory import inventory
from copilot_native_usage_reconciliation import reconcile
class Tests(unittest.TestCase):
 def ledger(self):return {'all_POST_headers':4,'accepted_body_POST':1,'denied_connections':0,'records':[{'ordinal':i,'verb':'POST','path':'/v1/chat/completions','accepted':i==1,'status':200 if i==1 else 429,'synthetic_ONLY':True,'inference_calls':0} for i in range(1,5)]}
 def test_all_four_not_filtered(self):
  r=inventory(self.ledger());self.assertEqual(r['total_recorded_attempts'],4);self.assertEqual(r['accepted_ordinals'],[1]);self.assertEqual(r['denied_ordinals'],[2,3,4]);self.assertEqual(r['denied_POST_headers'],3)
 def test_native_empty_stays_incomplete(self):
  r=reconcile({'totalUserRequests':0,'modelMetrics':{},'agentMetrics':{}},self.ledger());self.assertEqual(r['status'],'INCOMPLETE_OR_UNCOVERED');self.assertEqual(r['observed_attempt_inventory']['all_POST_headers'],4);self.assertIsNone(r['observed_native_fixture_tokens']);self.assertFalse(r['real_scored_eligible'])
 def test_missing_duplicate_bool_ordinals_rejected(self):
  for mutate in [lambda l:l['records'].pop(),lambda l:l['records'][1].update(ordinal=1),lambda l:l['records'][0].update(ordinal=True),lambda l:l.update(accepted_body_POST=2),lambda l:l['records'][0].update(accepted=1)]:
   l=self.ledger();mutate(l)
   with self.assertRaises(ValueError):inventory(l)
 def test_denied_auxiliary_preserved(self):
  l=self.ledger();l['records'].append({'verb':'CONNECT','path':'unknown:443','status':403,'accepted':False});r=inventory(l);self.assertEqual(r['auxiliary_denied_records'],1);self.assertEqual(r['total_recorded_attempts'],5)
 def test_native_accepted_count_cannot_hide_denied(self):
  m={'Qwen3.8-27B-FP8':{'requests':{'count':1},'usage':{'inputTokens':0,'outputTokens':0,'cacheReadTokens':0,'cacheWriteTokens':0,'reasoningTokens':0}}};n={'totalUserRequests':1,'modelMetrics':m,'agentMetrics':{'main':{'modelMetrics':copy.deepcopy(m)}}};r=reconcile(n,self.ledger());self.assertIn('native_provider_request_count_mismatch',r['reasons']);self.assertEqual(r['observed_attempt_inventory']['denied_POST_headers'],3)
if __name__=='__main__':unittest.main()
