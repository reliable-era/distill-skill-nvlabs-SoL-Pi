import hashlib,http.client,json,pathlib,threading,types,unittest
from prospective_body_capacity import factory,BODY_CAP,expanded_component
R=pathlib.Path(__file__).resolve().parent;SOURCE=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime/server.py';PLAN=json.loads((R/'matched-cython-plan.json').read_text())
class Tests(unittest.TestCase):
 def test_changed_source_rejects(self):self.assertRaises(ValueError,factory,SOURCE,'0'*64,lambda r:None)
 def test_proxy_guard_only(self):
  p=SOURCE.parent/'stream_proxy.py';old=p.read_text();derived=expanded_component(p,PLAN['runtime_hashes']['stream_proxy.py'],'proxy');self.assertEqual(derived,old.replace('if not 0<=n<=262144:self.send_error(413);return','if not 0<=n<=8388608:self.send_error(413);return'))
 def test_session_guard_only(self):
  p=SOURCE.parent/'session.py';old=p.read_text();derived=expanded_component(p,PLAN['runtime_hashes']['session.py'],'session');self.assertEqual(derived,old.replace('or len(body)>262144:','or len(body)>8388608:'))
 def test_component_source_pin(self):self.assertRaises(ValueError,expanded_component,SOURCE.parent/'session.py','0'*64,'session')
 def test_unknown_component(self):self.assertRaises(ValueError,expanded_component,SOURCE,PLAN['runtime_hashes']['server.py'],'unknown')
 def setUp(self):
  self.denials=[];self.calls=[];self.before=SOURCE.read_bytes();self.module=factory(SOURCE,PLAN['runtime_hashes']['server.py'],self.denials.append)
  def forward(path,body,emit):self.calls.append((path,body));emit(b'data: {"synthetic":true}\n\n');return {}
  handler=type('H',(self.module.PostHandler,),{'session':types.SimpleNamespace(forward=forward)});self.server=self.module.OwnedServer(('127.0.0.1',0),handler);threading.Thread(target=self.server.serve_forever,daemon=True).start()
 def tearDown(self):self.server.cleanup();self.assertEqual(self.before,SOURCE.read_bytes())
 def request(self,body=b'{}',length=None,path='/v1/responses',method='POST',headers=None):
  c=http.client.HTTPConnection(*self.server.server_address,timeout=5)
  try:
   h={'Content-Length':str(len(body) if length is None else length),**(headers or {})};c.request(method,path,body,h);r=c.getresponse();content=r.read();return r.status,content
  finally:c.close()
 def test_cross_old_cap_unchanged_bytes(self):
  body=b'{"text":"'+b'a'*262145+b'"}';status,data=self.request(body);self.assertEqual(status,200);self.assertEqual(self.calls,[('/v1/responses',body)]);self.assertEqual(self.denials,[])
 def test_at_new_cap(self):body=b'x'*BODY_CAP;self.assertEqual(self.request(body)[0],200);self.assertEqual(self.calls[0][1],body)
 def test_above_cap_not_forwarded(self):self.assertEqual(self.request(length=BODY_CAP+1)[0],413);self.assertEqual(self.calls,[]);self.assertEqual(self.denials[0]['provider_POST'],0)
 def test_negative_length(self):self.assertEqual(self.request(length=-1)[0],413);self.assertEqual(self.calls,[])
 def test_malformed_length(self):self.assertEqual(self.request(length='bad')[0],413);self.assertIsNone(self.denials[0]['declared_body_bytes'])
 def test_get_forbidden(self):self.assertEqual(self.request(method='GET')[0],403);self.assertEqual(self.calls,[])
 def test_other_post_path(self):self.assertEqual(self.request(path='/other')[0],403);self.assertEqual(self.calls,[])
 def test_chunked_forbidden(self):self.assertEqual(self.request(headers={'Transfer-Encoding':'chunked'})[0],403);self.assertEqual(self.calls,[])
if __name__=='__main__':unittest.main()
