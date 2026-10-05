import copy,json,pathlib,unittest
from prospective_output_budget import build,digest,R
D=R.parent/'development/pi-takeover-qwen-source-backed-verification/runtime'
HASHES=json.loads((R/'source-backed-doom-plan.json').read_text())['runtime_hashes']
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=build(D,HASHES,digest(R/'prospective_reasoning_adapter.py'),digest(R/'prospective_sse_bridge.py'));a=cls.m['adapter'];cls.provenance={**a.SOURCE_PINS,'model':a.MODEL,'output_streamer_sha256':a.SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'}
 def events(self,delta=0,status='incomplete',cap=16384,output=16382):return [{'type':'response.completed','response':{'model':self.m['adapter'].MODEL,'status':status,'incomplete_details':{'reason':'max_output_tokens'} if status=='incomplete' else None,'max_output_tokens':cap,'output':[{'type':'reasoning','status':'completed'}],'usage':{'input_tokens':100,'input_tokens_details':{'cached_tokens':80,'cache_write_tokens':0},'output_tokens':output,'output_tokens_details':{'reasoning_tokens':output+delta},'total_tokens':100+output}}}]
 def test_only_outputcap_changes(self):
  original={'model':self.m['adapter'].MODEL,'input':[{'role':'user','content':'test'}]};out,meta=self.m['policy'].transform(json.dumps(original).encode());parsed=json.loads(out);self.assertEqual(parsed.pop('max_output_tokens'),16384);self.assertEqual(parsed,original);self.assertEqual(meta['changed_fields'],['max_output_tokens']);self.assertFalse(meta['native_configuration_claim'])
 def test_matching_identity(self):
  raw=b'{"max_output_tokens":16384}';out,meta=self.m['policy'].transform(raw);self.assertEqual(out,raw);self.assertEqual(meta['changed_fields'],[])
 def test_conflicts_and_invalid_types(self):
  for cap in [8192,True,16384.0,'16384',None,-1]:
   with self.subTest(cap=cap):self.assertRaises(ValueError,self.m['policy'].transform,json.dumps({'max_output_tokens':cap}).encode())
 def test_source_hash_fail_closed(self):
  h={**HASHES,'output_policy.py':'0'*64};self.assertRaises(ValueError,build,D,h,digest(R/'prospective_reasoning_adapter.py'))
 def test_incomplete_is_cost_not_generation(self):
  v=self.m['cost'].normalize_cost(self.events(),True);self.assertTrue(v['provider_cost_complete']);self.assertTrue(v['protocol_valid']);self.assertFalse(v['generation_complete'])
 def test_completed(self):
  v=self.m['cost'].normalize_cost(self.events(status='completed',output=17),True);self.assertTrue(v['generation_complete']);self.assertEqual(v['gross_tokens'],117)
 def test_no_eof_no_cost(self):self.assertFalse(self.m['cost'].normalize_cost(self.events(),False)['provider_cost_complete'])
 def test_duplicate_terminal_no_cost(self):self.assertFalse(self.m['cost'].normalize_cost(self.events()*2,True)['provider_cost_complete'])
 def test_failed_without_usage_not_zero(self):
  v=self.m['cost'].normalize_cost([{'type':'response.failed','response':{'status':'failed'}}],True);self.assertFalse(v['provider_cost_complete']);self.assertIsNone(v['gross_tokens'])
 def test_other_cap_not_recognized(self):self.assertFalse(self.m['cost'].normalize_cost(self.events(cap=8192),True)['provider_cost_complete'])
 def test_excess_output_protocol_invalid(self):self.assertFalse(self.m['cost'].normalize_cost(self.events(status='completed',output=16385),True)['protocol_valid'])
 def test_every_proven_overshoot(self):
  for output in [16382,16383,16384]:
   for delta in range(1,8):
    e=self.events(delta=delta,output=output);original=copy.deepcopy(e);v=self.m['adapter'].derive(e,True,self.provenance);self.assertTrue(v['correction_applied']);self.assertEqual(e,original);expected=copy.deepcopy(e);expected[0]['response']['usage']['output_tokens_details']['reasoning_tokens']=output;self.assertEqual(v['derived_events'],expected);self.assertFalse(v['derived_cost']['generation_complete']);self.assertEqual(v['derived_cost']['gross_tokens'],100+output)
 def test_wrong_source_or_boundary_not_corrected(self):
  for events,provenance in [(self.events(delta=8),self.provenance),(self.events(delta=1,output=16000),self.provenance),(self.events(delta=1),{**self.provenance,'peer':'unknown'}),(self.events(delta=1,status='completed'),self.provenance)]:self.assertFalse(self.m['adapter'].derive(events,True,provenance)['correction_applied'])
 def test_bridge_preserves_status_output_content_gross(self):
  event=self.events(delta=5)[0];raw=b'data: '+json.dumps(event).encode()+b'\n\n';parts=[];b=self.m['bridge'].SSEBridge(parts.append);b.feed(raw[:19]);b.feed(raw[19:]);v=b.finish(True,self.provenance);self.assertEqual(v['raw_bytes'],raw);parsed=json.loads(b''.join(parts).splitlines()[0][6:]);expected=copy.deepcopy(event);expected['response']['usage']['output_tokens_details']['reasoning_tokens']=16382;self.assertEqual(parsed,expected);self.assertTrue(v['correction_applied']);self.assertTrue(v['framing_complete'])
 def test_malformed_frame_not_repaired(self):
  b=self.m['bridge'].SSEBridge(lambda _:None);b.feed(b'data: {bad}\n\n');v=b.finish(True,self.provenance);self.assertFalse(v['correction_applied']);self.assertFalse(v['framing_complete']);self.assertFalse(v['derived_cost']['provider_cost_complete'])
if __name__=='__main__':unittest.main()
