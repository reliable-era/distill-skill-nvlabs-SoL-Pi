import copy,unittest
from prospective_reasoning_adapter import derive,SOURCE,MODEL,SOURCE_PINS
class AdapterTests(unittest.TestCase):
 def setUp(self):
  self.events=[{'type':'response.completed','response':{'model':MODEL,'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},'max_output_tokens':8192,'usage':{'input_tokens':8067,'output_tokens':8190,'total_tokens':16257,'output_tokens_details':{'reasoning_tokens':8193}}}}]
  self.provenance={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'}
 def run_adapter(self):return derive(self.events,True,self.provenance)
 def test_recognized_bug(self):
  original=copy.deepcopy(self.events);r=self.run_adapter();self.assertTrue(r['correction_applied']);self.assertEqual(r['raw_cost']['error'],'invalid_reasoning_subset');self.assertFalse(r['raw_provider_protocol_valid']);self.assertEqual(r['derived_cost']['gross_tokens'],16257);self.assertEqual(r['derived_cost']['reasoning_tokens_reported'],8190);self.assertFalse(r['derived_cost']['generation_complete']);self.assertFalse(r['deployment_approved']);self.assertEqual(self.events,original)
 def test_other_peer(self):self.provenance['peer']='127.0.0.1:18002';self.assertTrue(self.run_adapter()['correction_applied'])
 def test_unknown_source(self):self.provenance['output_streamer_sha256']='0'*64;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_unknown_peer(self):self.provenance['peer']='other';self.assertFalse(self.run_adapter()['correction_applied'])
 def test_no_eof(self):self.assertFalse(derive(self.events,False,self.provenance)['correction_applied'])
 def test_inconsistent_total(self):self.events[0]['response']['usage']['total_tokens']=1;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_negative_reasoning(self):self.events[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=-1;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_large_overshoot(self):self.events[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=9000;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_maximum_seven_overshoot(self):self.events[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=8197;self.assertTrue(self.run_adapter()['correction_applied'])
 def test_impossible_eight_overshoot(self):self.events[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=8198;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_changed_worker_source(self):self.provenance['dflash_worker_sha256']='0'*64;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_other_budget(self):self.events[0]['response']['max_output_tokens']=9000;self.assertFalse(self.run_adapter()['correction_applied'])
 def test_bad_cache(self):self.events[0]['response']['usage']['input_tokens_details']={'cached_tokens':999999};self.assertFalse(self.run_adapter()['correction_applied'])
 def test_duplicate_terminal(self):self.events.append(copy.deepcopy(self.events[0]));self.assertFalse(self.run_adapter()['correction_applied'])
 def test_valid_receipt_untouched(self):self.events[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=100;r=self.run_adapter();self.assertFalse(r['correction_applied']);self.assertTrue(r['raw_cost']['provider_cost_complete'])
if __name__=='__main__':unittest.main()
