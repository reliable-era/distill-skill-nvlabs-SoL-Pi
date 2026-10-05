import copy,json,pathlib,tempfile,unittest,hashlib
from audit_16k_regex import validate_response
import test_prospective_output_budget as fixtures
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixtures.Tests.setUpClass();cls.fixture=fixtures.Tests()
 def build(self,delta=0):
  e=self.fixture.events(delta=delta);derived=self.fixture.m['adapter'].derive(e,True,self.fixture.provenance);corrected=derived.get('derived_events',e);raw=b'data: '+json.dumps(e[0]).encode()+b'\n\n';out=b'data: '+json.dumps(corrected[0]).encode()+b'\n\n';av={**derived,'framing_complete':True};view={'accounting_view':av,'raw_sha256':hashlib.sha256(raw).hexdigest(),'derived_sha256':hashlib.sha256(out).hexdigest(),'provenance':self.fixture.provenance};request={'provider_status':200,'error':None,'stream_eof':True,'provider_backend':'127.0.0.1:18001','payload_policy':{'output_cap':16384}};return raw,out,request,view
 def call(self,values):
  raw,out,req,view=values
  with tempfile.TemporaryDirectory() as folder:
   p=pathlib.Path(folder);(p/'raw').write_bytes(raw);(p/'derived').write_bytes(out);return validate_response(p/'raw',p/'derived',req,view,self.fixture.m['adapter'].derive)
 def test_clean(self):cost,tr=self.call(self.build());self.assertEqual(cost['gross_tokens'],16482);self.assertEqual(tr['status'],'incomplete')
 def test_proven_overshoot(self):cost,tr=self.call(self.build(3));self.assertEqual(cost['reasoning_tokens_reported'],16382);self.assertFalse(cost['generation_complete'])
 def test_forged_cost_green_not_accepted(self):
  v=self.build();v[3]['accounting_view']['derived_cost']['gross_tokens']=1;self.assertRaises(AssertionError,self.call,v)
 def test_wrong_peer(self):v=self.build();v[2]['provider_backend']='127.0.0.1:18002';self.assertRaises(AssertionError,self.call,v)
 def test_missing_eof(self):v=self.build();v[2]['stream_eof']=False;self.assertRaises(AssertionError,self.call,v)
 def test_wrong_cap(self):v=self.build();v[2]['payload_policy']['output_cap']=8192;self.assertRaises(AssertionError,self.call,v)
 def test_modified_status_or_content(self):
  v=list(self.build(1));event=json.loads(v[1][6:].strip());event['response']['status']='completed';v[1]=b'data: '+json.dumps(event).encode()+b'\n\n';v[3]['derived_sha256']=hashlib.sha256(v[1]).hexdigest();self.assertRaises(AssertionError,self.call,v)
if __name__=='__main__':unittest.main()
