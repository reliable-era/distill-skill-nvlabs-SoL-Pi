import hashlib,json,pathlib,tempfile,unittest
from audit_receipts import audit,reconstruct
from transport import usage_from_sse
class Receipts(unittest.TestCase):
 def fixture(self,raw,status=200,error=None,error_body=None):
  t=tempfile.TemporaryDirectory(prefix='solpi-g5-receipt-test-');self.addCleanup(t.cleanup);root=pathlib.Path(t.name);d=root/'transport';d.mkdir();a=dict(model='Qwen/Qwen3.8-27B',stream=True,input='fixture prompt');b=dict(a,max_output_tokens=16384);original=json.dumps(a).encode();forwarded=json.dumps(b).encode();(d/'request-1.json').write_bytes(original);(d/'forwarded-request-1.json').write_bytes(forwarded);(d/'response-1.sse').write_bytes(raw);r=dict(request=1,backend='127.0.0.1:8000',parent_arm='ours',request_role='primary',path='/v1/responses',output_cap=16384,original_sha256=hashlib.sha256(original).hexdigest(),forwarded_sha256=hashlib.sha256(forwarded).hexdigest(),response_sha256=hashlib.sha256(raw).hexdigest(),response_bytes=len(raw),stream_eof=status==200,error=error,provider_status=status,proven_zero_model_refusal=error=='ConnectionRefusedError');r.update(usage_from_sse(raw,r['stream_eof']));r['cost_complete']=r['cost_complete'] and error is None and status==200
  if error_body is not None:(d/'provider-error-1.body').write_bytes(error_body);r['provider_error_sha256']=hashlib.sha256(error_body).hexdigest();r.update(reconstruct(raw,r,error_body))
  if r['proven_zero_model_refusal']:r.update(cost_complete=True,tokens_lower_bound=0)
  (d/'ledger.json').write_text(json.dumps(dict(backend='127.0.0.1:8000',parent_arm='ours',request_role='primary',model=a['model'],active_connections=0,provider_POST=1,records=[r])));return dict(cell_id='fixture',arm='ours',attempt=1,root=str(root),native_started=True,requests=1,known_tokens_lower_bound=r['tokens_lower_bound'],cost_complete=r['cost_complete'])
 def completed(self):return b'data: {"type":"response.completed","response":{"model":"Qwen3.8-27B-FP8","usage":{"input_tokens":3,"output_tokens":2,"total_tokens":5}}}\n'
 def test_exact_provider_usage_and_identity(self):
  r=self.fixture(self.completed());p=audit(r);self.assertEqual(p['known_tokens_lower_bound'],5);self.assertTrue(p['cost_complete']);self.assertEqual(p['response_identity_counts'],{'Qwen3.8-27B-FP8':1})
 def test_missing_usage_not_imputed(self):
  r=self.fixture(b'data: {"type":"response.completed","response":{}}\n');p=audit(r);self.assertFalse(p['cost_complete']);self.assertEqual(p['unknown_response_identity_requests'],1)
 def test_5xx_valid_partial_usage_is_not_complete_cost(self):
  r=self.fixture(b'',503,error_body=b'{"model":"Qwen/Qwen3.8-27B","usage":{"input_tokens":3,"output_tokens":2,"total_tokens":5}}');p=audit(r);self.assertEqual(p['known_tokens_lower_bound'],5);self.assertFalse(p['cost_complete'])
 def test_refusal_proved_zero_not_generic_5xx_zero(self):
  self.assertTrue(audit(self.fixture(b'',None,'ConnectionRefusedError'))['cost_complete']);self.assertFalse(audit(self.fixture(b'',502,error_body=b'gateway error'))['cost_complete'])
 def test_prompt_mutation_detected(self):
  r=self.fixture(self.completed());d=pathlib.Path(r['root'])/'transport';p=d/'forwarded-request-1.json';v=json.loads(p.read_text());v['input']='changed';p.write_text(json.dumps(v));ledger=json.loads((d/'ledger.json').read_text());ledger['records'][0]['forwarded_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(d/'ledger.json').write_text(json.dumps(ledger))
  with self.assertRaises(AssertionError):audit(r)
 def test_raw_tampering_detected(self):
  r=self.fixture(self.completed());(pathlib.Path(r['root'])/'transport/response-1.sse').write_bytes(b'changed')
  with self.assertRaises(AssertionError):audit(r)
if __name__=='__main__':unittest.main()
