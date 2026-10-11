import io,json,pathlib,tempfile,time,unittest
from unittest.mock import patch
from transport import Broker,MODEL,usage_from_sse,waiting_zero
RAW=b'data: '+json.dumps({'type':'response.completed','response':{'usage':{'input_tokens':100,'output_tokens':12,'total_tokens':112}}}).encode()+b'\n\n'
class Client:
 def __init__(self):self.wfile=io.BytesIO();self.errors=[]
 def send_response(self,*a):pass
 def send_header(self,*a):pass
 def end_headers(self):pass
 def send_error(self,n):self.errors.append(n)
class Sock:
 def shutdown(self,*a):pass
class Response:
 status=200
 def __init__(self):self.once=False
 def read1(self,n):
  if self.once:return b''
  self.once=True;return RAW
class Connection:
 def __init__(self,host,port,timeout):assert (host,port)==('127.0.0.1',9012);self.sock=Sock()
 def connect(self):pass
 def request(self,method,path,body,headers):
  assert method=='POST' and path=='/v1/responses';v=json.loads(body);assert v['model']==MODEL and v['max_output_tokens']==16384
 def getresponse(self):return Response()
 def close(self):pass
class Refused(Connection):
 def connect(self):raise ConnectionRefusedError('test-only refused')
class Tests(unittest.TestCase):
 def test_standard_usage(self):self.assertEqual(usage_from_sse(RAW,True)['tokens_lower_bound'],112);self.assertTrue(usage_from_sse(RAW,True)['cost_complete'])
 def test_terminal_incomplete_usage_exact(self):
  raw=RAW.replace(b'response.completed',b'response.incomplete');self.assertTrue(usage_from_sse(raw,True)['cost_complete']);self.assertEqual(usage_from_sse(raw,True)['tokens_lower_bound'],112)
 def test_missing_terminal_unknown(self):self.assertFalse(usage_from_sse(b'data: {}\n',True)['cost_complete'])
 def test_eof_required(self):self.assertFalse(usage_from_sse(RAW,False)['cost_complete'])
 def test_malformed_or_inconsistent(self):
  self.assertFalse(usage_from_sse(RAW+b'data: bad\n',True)['cost_complete']);self.assertFalse(usage_from_sse(RAW.replace(b'112',b'113'),True)['cost_complete'])
 def test_waiting_all_ranks(self):
  self.assertTrue(waiting_zero({'body':[{'num_reqs':12,'num_waiting_reqs':0}]}));self.assertFalse(waiting_zero({'body':[{'num_reqs':0,'num_waiting_reqs':1}]}));self.assertFalse(waiting_zero({'body':[]}))
 def test_direct_forward_and_refused(self):
  for connection,complete in ((Connection,True),(Refused,False)):
   with tempfile.TemporaryDirectory() as d:
    b=Broker(pathlib.Path(d)/'transport',time.monotonic()+7200);client=Client()
    with patch('transport.metadata',return_value={'body':[]}):b.forward('/v1/responses',json.dumps({'model':MODEL,'stream':True}).encode(),client,connect=connection)
    self.assertEqual(b.posts,1);self.assertTrue(b.records[0]['cost_complete']);self.assertEqual(b.records[0]['backend'],'127.0.0.1:9012')
    if not complete:self.assertTrue(b.records[0]['connection_infra_failure']);self.assertTrue(b.records[0]['proven_zero_model_refusal']);self.assertEqual(b.records[0]['tokens_lower_bound'],0)
 def test_caps_before_forward(self):
  with tempfile.TemporaryDirectory() as d:
   b=Broker(pathlib.Path(d)/'t',time.monotonic()+7200);b.posts=60;c=Client();b.forward('/v1/responses',json.dumps({'model':MODEL,'stream':True}).encode(),c,connect=Connection);self.assertEqual(c.errors,[429]);self.assertEqual(b.posts,60);self.assertFalse(b.denials[0]['forwarded'])
 def test_model_and_output_identity(self):
  with tempfile.TemporaryDirectory() as d:
   b=Broker(pathlib.Path(d)/'t',time.monotonic()+7200)
   for v in ({'model':'wrong','stream':True},{'model':MODEL,'stream':True,'max_output_tokens':10}):
    with self.assertRaises(ValueError):b.forward('/v1/responses',json.dumps(v).encode(),Client())
   self.assertEqual(b.posts,0)
if __name__=='__main__':unittest.main()
