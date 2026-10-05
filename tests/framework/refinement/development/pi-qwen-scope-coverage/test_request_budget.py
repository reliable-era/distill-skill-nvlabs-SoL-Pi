import unittest,tempfile,pathlib,json
import run_screen as Q
S=Q.S
class Budget(unittest.TestCase):
 def test_seventeenth_denied_before_forward_preserves_all16(self):
  calls=[]
  class Socket:
   def shutdown(self,*a):pass
  class Response:
   status=200
   def __init__(self):self.parts=iter([b'data: {"choices":[],"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}}\n\ndata: [DONE]\n\n',b''])
   def read1(self,n):return next(self.parts)
  class Connection:
   sock=Socket()
   def __init__(self,*a,**kw):calls.append(1)
   def connect(self):pass
   def request(self,*a):pass
   def getresponse(self):return Response()
   def close(self):pass
  topology={'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'}
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',topology);s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);body=b'{"model":"Qwen3.8-27B-FP8","stream":true}'
   for i in range(16):s.forward('/v1/chat/completions',body,lambda b:None,Connection)
   prior=list(s.records)
   with self.assertRaisesRegex(RuntimeError,'local request budget exhausted'):s.forward('/v1/chat/completions',body,lambda b:None,Connection)
   self.assertEqual(len(calls),16);self.assertEqual(s.records,prior);self.assertEqual(s.posts,16)
   saved=json.loads((s.root/'ledger.json').read_text());self.assertEqual(len(saved['records']),16);denial=saved['local_budget_denials'][0];self.assertEqual(denial['actor'],'a');self.assertEqual(denial['forwarded'],0);self.assertTrue(denial['before_forward']);self.assertTrue(Q.cutoff_diagnostic({'id':'a'},s.records,saved['local_budget_denials']))
 def test_generic429_and_ambiguous_denial_stop(self):
  denied={'actor':'a','reason':'local_request_budget_exhausted','before_forward':True,'forwarded':0,'actor_POST':16,'total_POST':16}
  complete=[{'provider_status':200,'stream_eof':True,'usage_complete':True,'error':None}]*16
  self.assertFalse(Q.cutoff_diagnostic({'id':'a'},[{'provider_status':429,'error':'providerHTTP'}],[]))
  self.assertFalse(Q.cutoff_diagnostic({'id':'a'},complete,[dict(denied,forwarded=1)]))
  self.assertFalse(Q.cutoff_diagnostic({'id':'a'},complete,[dict(denied,actor='foreign')]))
  self.assertFalse(Q.cutoff_diagnostic({'id':'a'},complete[:-1],[denied]))
  self.assertFalse(Q.cutoff_diagnostic({'id':'a'},[dict(z,usage_complete=False) for z in complete],[denied]))
if __name__=='__main__':unittest.main()
