import importlib.util,pathlib,tempfile,unittest,json
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('session',R/'session.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
TOPO={'verified':True,'image_id':m.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'}
class Socket:
 def shutdown(self,*a):pass
class Response:
 status=200
 def __init__(self):self.chunks=iter([b'data: {"usa',b'ge":{"prompt_tokens":3}}\n\n',b'data: [DONE]\n\n',b''])
 def read1(self,n):return next(self.chunks)
class Connection:
 def __init__(self,*a,**k):self.sock=Socket()
 def connect(self):pass
 def request(self,*a):pass
 def getresponse(self):return Response()
 def close(self):pass
class Controls(unittest.TestCase):
 def test_idle_strict(self):
  self.assertTrue(m.idle([{'num_reqs':0,'num_waiting_reqs':0}]))
  for x in [[],{},[{'num_reqs':False,'num_waiting_reqs':0}],[{'num_reqs':0}], [{'num_reqs':0,'num_waiting_reqs':1}]]:self.assertFalse(m.idle(x))
 def test_stream_split_usage_and_caps(self):
  with tempfile.TemporaryDirectory() as t:
   q=m.Session(pathlib.Path(t)/'private',TOPO);q.begin('pi',[{'num_reqs':0,'num_waiting_reqs':0}]);out=[]
   body=json.dumps({'model':'Qwen3.8-27B-FP8','stream':True}).encode()
   for _ in range(4):q.forward('/v1/responses',body,out.append,Connection)
   self.assertTrue(q.records[0]['stream_eof']);self.assertTrue(q.records[0]['usage_observed']);self.assertIsNone(q.records[0]['usage_complete'])
   self.assertEqual(json.loads((q.root/'usage-1.json').read_text())[0]['prompt_tokens'],3)
   with self.assertRaises(RuntimeError):q.forward('/v1/responses',body,out.append,Connection)
   self.assertEqual(q.posts,4)
   with self.assertRaises(RuntimeError):q.finish(True,['compaction'])
 def test_provider_error_private_bounded(self):
  class ErrorResponse:
   status=400
   def read(self,n):return b'x'*n
  class ErrorConnection(Connection):
   def getresponse(self):return ErrorResponse()
  with tempfile.TemporaryDirectory() as tmp:
   q=m.Session(pathlib.Path(tmp)/'private',TOPO);q.begin('pi',[{'num_reqs':0,'num_waiting_reqs':0}])
   with self.assertRaisesRegex(RuntimeError,'status=400'):q.forward('/v1/chat/completions',json.dumps({'model':'Qwen3.8-27B-FP8','stream':True}).encode(),lambda b:None,ErrorConnection)
   self.assertEqual(q.records[0]['provider_status'],400);self.assertTrue(q.records[0]['error_body_truncated']);self.assertEqual((q.root/'provider-error-1.body').stat().st_size,65536)
 def test_usage_no_defaults(self):
  self.assertIsNone(m.usage_audit([{'input_tokens':2}],True,True));self.assertIsNone(m.usage_audit([{'input_tokens':2,'output_tokens':3,'total_tokens':5}],False,True));self.assertEqual(m.usage_audit([{'input_tokens':2,'output_tokens':3,'total_tokens':5}],True,True)['total'],5)
 def test_lock_inode_and_release(self):
  import os
  with tempfile.TemporaryDirectory() as t:
   pins=[]
   for n in ['a','b']:
    f=pathlib.Path(t)/n;f.touch();st=f.stat();pins.append({'path':str(f),'device':st.st_dev,'inode':st.st_ino})
   with m.inference_locks(pins):pass
   pins[1]['inode']+=1
   with self.assertRaises(RuntimeError):
    with m.inference_locks(pins):pass
if __name__=='__main__':unittest.main()
