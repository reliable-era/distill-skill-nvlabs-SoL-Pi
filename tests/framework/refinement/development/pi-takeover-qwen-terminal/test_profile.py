import unittest,json,sys,pathlib,tempfile,copy
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'runtime'))
from output_policy import transform
from provider_cost import normalize_cost
from usage_normalization import normalize_request
from session import request_seconds,wait_idle
class Profile(unittest.TestCase):
 def terminal(self,status='completed',reason=None):
  r={'status':status,'usage':{'input_tokens':20,'output_tokens':5,'total_tokens':25}}
  if reason:r.update(incomplete_details={'reason':reason},max_output_tokens=8192)
  return [{'type':'response.completed','response':r}]
 def test_one_field(self):
  original={'model':'Qwen3.8-27B-FP8','input':[{'x':1}],'reasoning':{'summary':'auto'},'stream':True}
  forwarded,p=transform(json.dumps(original).encode());actual=json.loads(forwarded);self.assertEqual(actual.pop('max_output_tokens'),8192);self.assertEqual(actual,original);self.assertEqual(p['changed_fields'],['max_output_tokens'])
 def test_identity(self):
  b=b'{"max_output_tokens":8192}';self.assertEqual(transform(b)[0],b)
 def test_bad_caps(self):
  for v in [True,0,8191,8193,'8192',None,8192.0]:
   with self.subTest(v=v),self.assertRaises(ValueError):transform(json.dumps({'max_output_tokens':v}).encode())
 def test_length_terminal_cost_not_generation(self):
  e=self.terminal('incomplete','max_output_tokens');r=normalize_cost(e,True);self.assertTrue(r['provider_cost_complete']);self.assertFalse(r['generation_complete']);self.assertFalse(normalize_request(e,'responses',True)['gross_usage_complete'])
 def test_rejections(self):
  e=self.terminal('incomplete','max_output_tokens')
  for bad,eof in [(e,False),(e+e,True),(self.terminal('incomplete','context_length'),True),([{'type':'response.completed','response':{'status':'incomplete','max_output_tokens':8192,'incomplete_details':{'reason':'max_output_tokens'}}}],True)]:
   self.assertFalse(normalize_cost(bad,eof)['provider_cost_complete'])
 def test_zero_or_invalid_usage(self):
  for values in [(0,0,0),(20,5,24),(True,5,6)]:
   e=self.terminal('incomplete','max_output_tokens');e[0]['response']['usage']=dict(zip(['input_tokens','output_tokens','total_tokens'],values));self.assertFalse(normalize_cost(e,True)['provider_cost_complete'])
 def test_deadline(self):
  self.assertEqual(request_seconds(600,0),590);self.assertEqual(request_seconds(600,580),10)
  with self.assertRaises(RuntimeError):request_seconds(600,590)
 def test_idle_caps(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):wait_idle(pathlib.Path(d)/'x',seconds=60,max_gets=13)
   x=wait_idle(pathlib.Path(d)/'x',fetch=lambda deadline:{'status':200,'error':None,'load':[{'num_reqs':0,'num_waiting_reqs':0}]});self.assertEqual(x[0]['num_reqs'],0)
class OwnedBudget(unittest.TestCase):
 def session(self,root):
  from session import Session,IMAGE
  return Session(root,{'verified':True,'image_id':IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'})
 def test_seventeenth_receipt_no_forward_retains_sixteen(self):
  from session import LocalBudgetExhaustion
  with tempfile.TemporaryDirectory() as d:
   session=self.session(pathlib.Path(d)/'transport');session.begin('actor',[{'num_reqs':0,'num_waiting_reqs':0}]);calls=[]
   event={'type':'response.completed','response':{'status':'completed','usage':{'input_tokens':10,'output_tokens':2,'total_tokens':12}}}
   payload=b'data: '+json.dumps(event).encode()+b'\n\n'
   class Sock:
    def shutdown(self,*args):pass
   class Connection:
    sock=Sock()
    def connect(self):pass
    def close(self):pass
    def request(self,*args):calls.append(args)
    def getresponse(self):
     class Response:
      status=200;done=False
      def read1(self,n):
       if self.done:return b''
       self.done=True;return payload
     return Response()
   body=b'{"model":"Qwen3.8-27B-FP8","stream":true}'
   for _ in range(16):session.forward('/v1/responses',body,lambda data:None,connect=lambda *args,**kwargs:Connection())
   with self.assertRaises(LocalBudgetExhaustion) as raised:session.forward('/v1/responses',body,lambda data:None,connect=lambda *args,**kwargs:self.fail('seventeenth upstream called'))
   self.assertEqual(raised.exception.reason,'per_actor_POST_cap');self.assertEqual(len(calls),16);self.assertEqual(len(session.records),16);self.assertTrue(all(r['usage_complete'] for r in session.records));self.assertEqual(session.posts,16)
   ledger=json.loads((session.root/'ledger.json').read_text());receipt=ledger['local_budget_denials'][0];self.assertEqual(receipt['forward_count'],0);self.assertFalse(receipt['provider_forwarded']);self.assertEqual(receipt['actor_POST_count'],16);self.assertEqual(len(ledger['records']),16)
   session.finish(True);session.begin('next',[{'num_reqs':0,'num_waiting_reqs':0}])
 def test_global_cap_forbids_new_start(self):
  with tempfile.TemporaryDirectory() as d:
   session=self.session(pathlib.Path(d)/'transport');session.posts=64
   with self.assertRaises(RuntimeError):session.begin('next',[{'num_reqs':0,'num_waiting_reqs':0}])
   self.assertEqual(session.starts,0)
 def test_provider429_never_local_budget(self):
  with tempfile.TemporaryDirectory() as d:
   session=self.session(pathlib.Path(d)/'transport');session.begin('actor',[{'num_reqs':0,'num_waiting_reqs':0}])
   class Sock:
    def shutdown(self,*args):pass
   class Response:
    status=429
    def read(self,n):return b'provider limited'
   class Connection:
    sock=Sock()
    def connect(self):pass
    def close(self):pass
    def request(self,*args):pass
    def getresponse(self):return Response()
   with self.assertRaises(RuntimeError):session.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda data:None,connect=lambda *args,**kwargs:Connection())
   self.assertEqual(session.budget_denials,[]);self.assertEqual(session.records[0]['provider_status'],429);self.assertFalse(session.records[0]['actor_budget_exhaustion']);self.assertIsNotNone(session.records[0]['error'])
class Continuation(unittest.TestCase):
 def test_local_cap_captured_sixteen_may_continue_after_cleanup(self):
  import run_screen
  rows=[{'request':i,'error':None} for i in range(16)]
  self.assertIsNone(run_screen.actor_transport_error(rows,16,True,True))
  self.assertIsNotNone(run_screen.actor_transport_error(rows,16,False,True))
  self.assertIsNotNone(run_screen.actor_transport_error(rows,16,True,False))
  self.assertIsNotNone(run_screen.actor_transport_error(rows[:-1],16,True,True))
 def test_provider429_stops_even_after_owned_cap(self):
  import run_screen
  self.assertEqual(run_screen.actor_transport_error([{'request':1,'provider_status':429,'error':'RuntimeError','actor_budget_exhaustion':False}],1,True,True),'non-budget provider/transport error')
class ProtocolCost(unittest.TestCase):
 def events(self,output,status='completed'):
  r={'status':status,'usage':{'input_tokens':100,'output_tokens':output,'total_tokens':100+output}}
  if status=='incomplete':r.update(max_output_tokens=8192,incomplete_details={'reason':'max_output_tokens'})
  return [{'type':'response.completed','response':r}]
 def test_completed_overcap_cost_retained_violation(self):
  result=normalize_cost(self.events(9000),True);self.assertTrue(result['provider_cost_complete']);self.assertEqual(result['gross_tokens'],9100);self.assertFalse(result['protocol_valid']);self.assertEqual(result['protocol_violations'],['reported_output_tokens_exceed_8192'])
 def test_exact_cap_valid(self):
  for status in ['completed','incomplete']:
   result=normalize_cost(self.events(8192,status),True);self.assertTrue(result['protocol_valid']);self.assertEqual(result['protocol_violations'],[]);self.assertTrue(result['provider_cost_complete'])
 def test_invalid_totals_no_known_cost(self):
  event=self.events(9000);event[0]['response']['usage']['total_tokens']=9000;result=normalize_cost(event,True);self.assertFalse(result['provider_cost_complete']);self.assertIsNone(result['gross_tokens']);self.assertIsNone(result['protocol_valid'])
 def test_length_overcap_cost_retained_violation(self):
  result=normalize_cost(self.events(9000,'incomplete'),True);self.assertTrue(result['provider_cost_complete']);self.assertFalse(result['protocol_valid']);self.assertFalse(result['generation_complete']);self.assertEqual(result['gross_tokens'],9100)
if __name__=='__main__':unittest.main()
