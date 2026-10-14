import json,pathlib,tempfile,unittest
from retry_policy import classify,model_answered
class RetryPolicy(unittest.TestCase):
 def fixture(self,record,events=b'',**overrides):
  temp=tempfile.TemporaryDirectory(prefix='g5-retry-test-');self.addCleanup(temp.cleanup);root=pathlib.Path(temp.name);d=root/'transport';d.mkdir();(d/'ledger.json').write_text(json.dumps(dict(records=[dict(request=1,**record)],budget_denials=[])));(d/'response-1.sse').write_bytes(events);return dict(attempt=1,root=str(root),native_started=True,owned_cleanup_verified=True,requests=1,timeout=False,grader_timeout=False,**overrides)
 def test_5xx_uniform_retry(self):self.assertTrue(classify(self.fixture(dict(provider_status=503)))['retry'])
 def test_caps_never_retry(self):
  r=self.fixture(dict(provider_status=502));r['requests']=60;self.assertFalse(classify(r)['retry'])
 def test_timeout_never_retry(self):
  r=self.fixture(dict(provider_status=502));r['timeout']=True;self.assertFalse(classify(r)['retry'])
 def test_model_error_wins_over_5xx(self):self.assertFalse(classify(self.fixture(dict(provider_status=502),b'data: {"type":"response.incomplete"}\n'))['retry'])
 def test_disconnect_before_not_after_answer(self):
  r=dict(provider_status=200,client_disconnected=True);self.assertTrue(classify(self.fixture(r))['retry']);self.assertFalse(classify(self.fixture(r,b'data: {"type":"response.output_text.delta","delta":"hello"}\n'))['retry'])
 def test_no_attempt3(self):
  r=self.fixture(dict(provider_status=502));r['attempt']=2;self.assertFalse(classify(r)['retry'])
 def test_pre_native_only_proved_category(self):
  r=dict(attempt=1,native_started=False,owned_cleanup_verified=True,requests=0,error=dict(category='image_failure'));self.assertTrue(classify(r)['retry']);r['error']={};self.assertTrue(classify(r)['stop'])
 def test_cleanup_uncertainty_stops(self):
  r=self.fixture(dict(provider_status=503));r['owned_cleanup_verified']=False;self.assertTrue(classify(r)['stop'])
 def test_created_metadata_is_not_model_answer(self):self.assertFalse(model_answered(b'data: {"type":"response.created"}\n'))
if __name__=='__main__':unittest.main()
