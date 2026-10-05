import http.client,json,pathlib,tempfile,threading,types,unittest
from prospective_body_capacity import proxy_factory,factory
from private_rejection_journal import RejectionJournal
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime';P=json.loads((R/'matched-cython-plan.json').read_text())
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'proxy-rejections.json';self.journal=RejectionJournal(self.path);m=proxy_factory(D/'stream_proxy.py',P['runtime_hashes']['stream_proxy.py'],self.journal);servermod=factory(D/'server.py',P['runtime_hashes']['server.py'],lambda r:None);h=type('PrivateProxy',(m.StreamingProxy,),{'authority':'provider.example:8000','broker_host':'127.0.0.1','broker_port':1});self.server=servermod.OwnedServer(('127.0.0.1',0),h);threading.Thread(target=self.server.serve_forever,daemon=True).start()
 def tearDown(self):self.server.cleanup();self.tmp.cleanup()
 def send(self,length,path='http://provider.example:8000/v1/responses'):
  c=http.client.HTTPConnection(*self.server.server_address,timeout=5)
  try:c.request('POST',path,b'',{'Content-Length':str(length)});r=c.getresponse();r.read();return r.status
  finally:c.close()
 def test_accepted_body_stream_unchanged(self):
  seen=[];servermod=factory(D/'server.py',P['runtime_hashes']['server.py'],lambda r:None)
  def forward(path,body,emit):seen.append(body);emit(b'data: {"synthetic":true}\n\n');return {}
  h=type('SyntheticBroker',(servermod.PostHandler,),{'session':types.SimpleNamespace(forward=forward)});backend=servermod.OwnedServer(('127.0.0.1',0),h);threading.Thread(target=backend.serve_forever,daemon=True).start();self.server.RequestHandlerClass.broker_port=backend.server_address[1];c=http.client.HTTPConnection(*self.server.server_address,timeout=5);body=b'x'*329291
  try:
   c.request('POST','http://provider.example:8000/v1/responses',body);r=c.getresponse();self.assertEqual(r.status,200);self.assertEqual(r.read(),b'data: {"synthetic":true}\n\n');self.assertEqual(seen,[body]);self.assertEqual(json.loads(self.path.read_text())['records'],[])
  finally:c.close();backend.cleanup()
 def test_overcap_durable_without_broker(self):
  self.assertEqual(self.send(8388609),413);x=json.loads(self.path.read_text())['records'];self.assertEqual(len(x),1);self.assertEqual(x[0]['declared_body_bytes'],8388609);self.assertFalse(x[0]['provider_forwarded']);self.assertEqual(x[0]['provider_POST'],0)
 def test_invalid_length(self):self.assertEqual(self.send('bad'),413);self.assertIsNone(json.loads(self.path.read_text())['records'][0]['declared_body_bytes'])
 def test_negative_length(self):self.assertEqual(self.send(-1),413);self.assertEqual(json.loads(self.path.read_text())['records'][0]['declared_body_bytes'],-1)
 def test_authority_still_denied(self):self.assertEqual(self.send(0,'http://other.example:8000/v1/responses'),403);self.assertEqual(json.loads(self.path.read_text())['records'],[])
if __name__=='__main__':unittest.main()
