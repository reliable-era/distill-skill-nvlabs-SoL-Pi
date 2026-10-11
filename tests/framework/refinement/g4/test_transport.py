"""Offline broker tests; no real HTTP connections or provider calls."""
import json,pathlib,tempfile,time,unittest
from unittest.mock import patch
import transport
class TransportTests(unittest.TestCase):
 def sse(self,model='Qwen3.8-27B-FP8',usage=None):
  response={'usage':usage or dict(input_tokens=7,output_tokens=3,total_tokens=10)}
  if model is not None:response['model']=model
  return b'data: '+json.dumps(dict(type='response.completed',response=response)).encode()+b'\n\n'
 def test_response_model_and_usage_retained(self):
  r=transport.usage_from_sse(self.sse(),True);self.assertEqual(r['response_model'],'Qwen3.8-27B-FP8');self.assertEqual(r['usage']['total_tokens'],10);self.assertTrue(r['cost_complete'])
 def test_model_missing_explicit_unknown(self):
  r=transport.usage_from_sse(self.sse(model=None),True);self.assertIsNone(r['response_model']);self.assertEqual(r['response_model_unknown_reason'],'missing_in_response');self.assertTrue(r['cost_complete'])
 def test_incomplete_stream_not_imputed(self):self.assertFalse(transport.usage_from_sse(self.sse(),False)['cost_complete'])
 def test_parent_arm_required(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):transport.Broker(pathlib.Path(d)/'b',time.monotonic()+100,None)
 def test_logical_model_aliases_no_variant_shares(self):
  for ids in ([transport.MODEL],['Qwen3.8-27B-FP8'],[transport.MODEL,'Qwen3.8-27B-FP8']):
   with patch.object(transport,'metadata',return_value={'body':{'data':[{'id':x} for x in ids]}}):transport.check_model()
 def test_unexpected_model_not_accepted(self):
  with patch.object(transport,'metadata',return_value={'body':{'data':[{'id':'unapproved'}]}}):
   with self.assertRaises(RuntimeError):transport.check_model()
 def test_zero_wait_requires_every_backend(self):
  self.assertTrue(transport.waiting_zero({'body':[dict(num_waiting_reqs=0,num_reqs=2)]}));self.assertFalse(transport.waiting_zero({'body':[dict(num_waiting_reqs=0,num_reqs=2),dict(num_waiting_reqs=1,num_reqs=0)]}));self.assertFalse(transport.waiting_zero({'body':[]}))
 def test_refusal_only_route8000_and_charged_zero_with_proof(self):
  class Client:
   def send_error(self,*a):pass
  class Refused:
   def __init__(self,host,port,**kw):self.host=host;self.port=port;self.outer.assertEqual((host,port),('127.0.0.1',8000))
   def connect(self):raise ConnectionRefusedError('offline mock')
   def close(self):pass
  Refused.outer=self
  with tempfile.TemporaryDirectory() as d,patch.object(transport,'metadata',return_value={'body':[]}):
   broker=transport.Broker(pathlib.Path(d)/'b',time.monotonic()+100,'K');broker.forward('/v1/responses',json.dumps(dict(model=transport.MODEL,stream=True)).encode(),Client(),connect=Refused);r=broker.records[0];self.assertEqual(r['parent_arm'],'K');self.assertEqual(r['request_role'],'primary');self.assertTrue(r['proven_zero_model_refusal']);self.assertTrue(r['cost_complete']);self.assertEqual(r['tokens_lower_bound'],0);self.assertIsNone(r['response_model'])
if __name__=='__main__':unittest.main()
