"""Exercise unchanged owned Session with fake upstream;no real model/network calls."""
import json,pathlib,tempfile,time,unittest
from unittest import mock
from prospective_broker_session import ProspectiveSession
from test_prospective_sse_bridge import END,P,DELTA,frame
import session as S
class Tests(unittest.TestCase):
 def exchange(self,disconnect=False,unknown_peer=False,broken=False):
  raw=DELTA+frame(END);calls=[];client=[]
  class Sock:
   def shutdown(self,*a):pass
  class Response:
   status=200;position=0
   def getheader(self,name):return 'unknown' if unknown_peer else P['peer']
   def read1(self,n):
    if self.position>=len(raw):
     if broken:raise ConnectionResetError('synthetic EOF failure')
     return b''
    x=raw[self.position:self.position+11];self.position+=len(x);return x
  class Connection:
   sock=Sock()
   def connect(self):pass
   def request(self,*a):calls.append(a)
   def getresponse(self):return Response()
   def close(self):pass
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);base=S.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'synthetic-offline'})
   base.begin('synthetic',[{'num_reqs':0,'num_waiting_reqs':0}]);wrapped=ProspectiveSession(base,{P['peer']:P})
   def emit(chunk):
    if disconnect:raise BrokenPipeError()
    client.append(chunk)
   if broken:
    with self.assertRaises(ConnectionResetError):wrapped.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',emit,connect=lambda *a,**kw:Connection())
   else:wrapped.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',emit,connect=lambda *a,**kw:Connection())
   self.assertEqual(len(calls),1);self.assertEqual(base.posts,1);self.assertEqual((base.root/'response-1.sse').read_bytes(),raw);self.assertFalse(base.records[0]['usage_audit']['protocol_valid']);self.assertFalse(base.records[0]['usage_complete'])
   view=wrapped.prospective_records[0]['accounting_view'];self.assertEqual(view['correction_applied'],not(unknown_peer or broken));self.assertEqual(view['consumer_detached'],disconnect);self.assertFalse(view['derived_cost']['generation_complete']);self.assertEqual(view['derived_cost']['gross_tokens'],16257 if not(unknown_peer or broken) else None)
   disk=json.loads((base.root/'ledger.json').read_text());self.assertFalse(disk['records'][0]['usage_complete']);self.assertTrue((base.root/'prospective-ledger.json').is_file());self.assertFalse(wrapped.prospective_records[0]['derived_bytes_are_consumption_evidence']);base.finish(True)
 def test_regular(self):self.exchange()
 def test_detached(self):self.exchange(disconnect=True)
 def test_unknown_route(self):self.exchange(unknown_peer=True)
 def test_missing_eof(self):self.exchange(broken=True)
 def test_budget_denial_no_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   base=S.Session(pathlib.Path(d)/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'synthetic-offline'});base.begin('synthetic',[{'num_reqs':0,'num_waiting_reqs':0}]);base.deadline=time.monotonic()-1;wrapped=ProspectiveSession(base,{P['peer']:P})
   with self.assertRaises(S.LocalBudgetExhaustion):wrapped.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda _:None,connect=lambda *a,**kw:self.fail('forbidden post'))
   self.assertEqual(base.posts,0);self.assertEqual(wrapped.prospective_records,[])
if __name__=='__main__':unittest.main()
