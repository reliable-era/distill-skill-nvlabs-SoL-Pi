"""Local Unix-socket fixture integration ONLY, never native/provider inference."""
import pathlib,sys,tempfile,threading,time,socket,http.client,json,unittest,contextlib
from unittest.mock import patch
D=pathlib.Path(__file__).resolve().parent.parent/'copilot-native-local-route/mock-successful-stream-prepared'
sys.path.insert(0,str(D))
import run_mock as prepared
from provider_fixture import inspect_fixture,MODEL
class UnixClient(http.client.HTTPConnection):
 def __init__(self,path):super().__init__('provider.example',8000,timeout=2);self.path=path
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(2);self.sock.connect(self.path)
class Integration(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cps-fixture-');self.root=pathlib.Path(self.temp.name);self.server=prepared.Broker(str(self.root/'b.sock'),self.root);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join(2);end=time.monotonic()+2
  while self.server.workers and time.monotonic()<end:time.sleep(.01)
  self.assertFalse(self.thread.is_alive());self.assertEqual(self.server.workers,0);self.temp.cleanup()
 def payload(self):return {'model':MODEL,'stream':True,'messages':[{'role':'user','content':'fixture'}],'tools':[{'type':'function','function':{'name':'report_intent','parameters':{'required':['intent'],'properties':{'intent':{'type':'string'}}}}}]}
 def request(self,obj,path='/v1/chat/completions'):
  c=UnixClient(str(self.root/'b.sock'))
  try:c.request('POST',path,json.dumps(obj).encode(),{'Content-Type':'application/json'});r=c.getresponse();return r.status,r.getheader('Content-Type'),r.read()
  finally:c.close()
 def test_full_two_phase_sse_and_budget(self):
  with contextlib.ExitStack() as stack:
   blocked=[stack.enter_context(patch(k,side_effect=AssertionError('external execution forbidden'))) for k in ['subprocess.run','subprocess.Popen','socket.create_connection']]
   q=self.payload();status,kind,body=self.request(q);self.assertEqual(status,200);self.assertEqual(kind,'text/event-stream');self.assertEqual(inspect_fixture(body)['finish'],'tool_calls')
   q['messages'].append({'role':'tool','tool_call_id':'synthetic-call-1','content':'intent reported'})
   status,_,body=self.request(q);self.assertEqual(status,200);self.assertEqual(inspect_fixture(body)['finish'],'stop')
   status,_,_=self.request(q);self.assertEqual(status,429);self.assertEqual(self.server.posts,2);self.assertTrue(self.server.fixture.tool_result_seen);self.assertTrue(all(x['inference_calls']==0 for x in self.server.records));self.assertTrue(all(x.call_count==0 for x in blocked))
 def test_unrecognized_schema_fail_closed(self):
  q=self.payload();q['tools'][0]['function']['name']='bash';status,_,_=self.request(q);self.assertEqual(status,422);self.assertEqual(self.server.fixture.phase,0)
 def test_missing_followup_not_success(self):
  q=self.payload();self.assertEqual(self.request(q)[0],200);self.assertEqual(self.request(q)[0],422);self.assertFalse(self.server.fixture.tool_result_seen)
 def test_wrong_endpoint_not_forwarded(self):
  self.assertEqual(self.request(self.payload(),'/v1/other')[0],429);self.assertEqual(self.server.posts,0)
if __name__=='__main__':unittest.main()
