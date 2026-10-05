"""Offline cross-layer broker tests; fake upstream, no Docker or real inference."""
import http.client,json,pathlib,socket,sys,tempfile,threading,time,unittest
from unittest import mock
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'runtime'));sys.path.insert(0,str(R))
import session as S,server as B,run_screen as Q
class Harvest(unittest.TestCase):
 def topology(self):return {'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'offline'}
 def exchange(self,late_headers):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);release=threading.Event();started=threading.Event();calls=[]
   terminal=b'data: '+json.dumps({'type':'response.completed','response':{'status':'completed','usage':{'input_tokens':20,'output_tokens':5,'total_tokens':25}}}).encode()+b'\n\n'
   first=b'data: {"type":"response.output_text.delta","delta":"partial"}\n\n'
   class Sock:
    def shutdown(self,*a):pass
   class Response:
    status=200;index=0
    def read1(self,n):
     self.index+=1
     if self.index==1:return first
     if self.index==2:
      if not release.wait(3):raise TimeoutError('offline test release missing')
      return terminal
     return b''
   class Connection:
    sock=Sock()
    def connect(self):started.set()
    def close(self):pass
    def request(self,*a):calls.append(a)
    def getresponse(self):
     if late_headers and not release.wait(3):raise TimeoutError('offline late headers release missing')
     return Response()
   class TestSession(S.Session):
    def forward(self,path,body,emit):return super().forward(path,body,emit,connect=lambda *a,**kw:Connection())
   session=TestSession(root/'transport',self.topology());session.begin('stopped-actor',[{'num_reqs':0,'num_waiting_reqs':0}])
   handler=type('OfflinePost',(B.PostHandler,),{'session':session});path=str(root/'broker.sock');server=B.OwnedUnixServer(path,handler)
   worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
   class UnixConnection(http.client.HTTPConnection):
    def connect(self):self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(3);self.sock.connect(path)
   client=UnixConnection('offline',timeout=3)
   try:
    client.request('POST','/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',{'Content-Type':'application/json'})
    self.assertTrue(started.wait(3))
    if not late_headers:
     response=client.getresponse();self.assertEqual(response.status,200);self.assertEqual(response.read1(len(first)),first)
    # Represents a removed actor/frontend. Close only this offline client;
    # provider remains live until the separately released final usage.
    client.close()
    with server.guard:fronts=list(server.sockets)
    for front in fronts:
     try:front.shutdown(socket.SHUT_RDWR)
     except OSError:pass
    release.set();deadline=time.monotonic()+3
    while server.workers and time.monotonic()<deadline:time.sleep(.01)
    self.assertEqual(server.workers,0);self.assertEqual(len(calls),1);self.assertEqual(session.posts,1)
    self.assertEqual(len(session.records),1);record=session.records[0]
    self.assertTrue(record['client_disconnected']);self.assertTrue(record['usage_complete']);self.assertTrue(record['stream_eof']);self.assertIsNone(record['error']);self.assertEqual(record['usage_audit']['gross_tokens'],25)
   finally:
    release.set();client.close();server.cleanup();worker.join(2)
 def test_disconnect_midstream_preserves_final_cost(self):self.exchange(False)
 def test_late_headers_after_disconnect_preserve_final_cost(self):self.exchange(True)
 def test_grace_deadline_and_actor_gate_remain_distinct(self):
  self.assertEqual(S.request_seconds(600,100),490);self.assertEqual(S.provider_seconds(600,100),730)
  self.assertEqual(S.provider_seconds(600,590),240)
  with self.assertRaises(RuntimeError):S.provider_seconds(600,830)
  with tempfile.TemporaryDirectory() as d:
   session=S.Session(pathlib.Path(d)/'transport',self.topology());session.begin('actor',[{'num_reqs':0,'num_waiting_reqs':0}]);session.deadline=600
   with mock.patch.object(S.time,'monotonic',return_value=590),self.assertRaises(S.LocalBudgetExhaustion):session.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda _:None,connect=lambda *a,**kw:self.fail('new model call after actor cutoff'))
   self.assertEqual(session.posts,0);self.assertFalse(session.budget_denials[0]['provider_forwarded'])
 def test_busy_grace_abort_only_owned_connections(self):
  clock=[0];server=type('Server',(),{'workers':1})();session=mock.Mock()
  def abort():server.workers=0;return 1
  session.abort_owned_connections.side_effect=abort
  report=Q.harvest_owned(session,server,clock=lambda:clock[0],sleep=lambda x:clock.__setitem__(0,clock[0]+x))
  self.assertTrue(report['parent_wait_expired']);self.assertLessEqual(report['waited_seconds'],243);session.abort_owned_connections.assert_called_once_with()
 def test_uncertain_cleanup_stops(self):
  clock=[0];server=type('Server',(),{'workers':1})();session=mock.Mock();session.abort_owned_connections.return_value=0
  with self.assertRaises(RuntimeError):Q.harvest_owned(session,server,clock=lambda:clock[0],sleep=lambda x:clock.__setitem__(0,clock[0]+x))
  self.assertLessEqual(clock[0],243)
 def test_idle_harvest_has_no_extra_model_calls(self):
  session=mock.Mock();server=type('Server',(),{'workers':0})();report=Q.harvest_owned(session,server)
  self.assertFalse(report['parent_wait_expired']);session.abort_owned_connections.assert_not_called()
if __name__=='__main__':unittest.main()
