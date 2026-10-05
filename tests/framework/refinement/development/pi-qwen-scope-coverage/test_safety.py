import unittest,tempfile,pathlib,json,unittest.mock as mock,subprocess
import run_screen as Q
S=Q.S
class Safety(unittest.TestCase):
 def topology(self):return {'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'}
 def test_empty_and_foreign_cutoffs_not_quality_safe(self):
  for req in [[],[{}],[{'provider_status':0}],[{'provider_status':503}],[{'provider_status':200,'error':'TimeoutError','local_deadline_fired':False}]]:
   self.assertFalse(Q.cutoff_diagnostic({'availability':'deadline_interrupted'},req))
 def test_session_actual600_and_busy_ambiguity_denied(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'ledger',self.topology())
   for load in [[],[{}],[{'num_reqs':1,'num_waiting_reqs':0}]]:
    with self.assertRaises(RuntimeError):s.begin('a',load)
   with mock.patch.object(S.time,'monotonic',return_value=100):s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}])
   self.assertEqual(s.deadline,700)
 def test_topology_and_cleanup_uncertainty_denied(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=self.topology();t['actor_gateway_empty']=False
   with self.assertRaises(RuntimeError):S.Session(pathlib.Path(tmp)/'bad',t)
   s=S.Session(pathlib.Path(tmp)/'ok',self.topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}])
   with self.assertRaises(RuntimeError):s.finish(False)
  with mock.patch.object(Q.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','daemon unavailable')):self.assertFalse(Q.absent('container','owned'))
 def test_source_mutation_and_caps_denied(self):
  p=json.loads((Q.R/'plan.json').read_text());p['seconds_per_actor']=180
  with self.assertRaisesRegex(RuntimeError,'caps'):Q.validate(p,'dummy')
  p=json.loads((Q.R/'plan.json').read_text());p['source_hashes']['run_screen.py']='0'*64
  with self.assertRaisesRegex(RuntimeError,'source mismatch'):Q.validate(p,'dummy')
 def test_generic_connect_timeout_not_local_timer(self):
  class Connection:
   sock=None
   def __init__(self,*a,**kw):pass
   def connect(self):raise TimeoutError('generic connection')
   def close(self):pass
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'ledger',self.topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}])
   with self.assertRaises(TimeoutError):s.forward('/v1/chat/completions',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda b:None,Connection)
   self.assertFalse(s.records[0]['local_deadline_fired'])
 def test_remaining_deadline_timer_records_actual_intervention(self):
  import threading,time
  event=threading.Event();timeouts=[]
  class Socket:
   def shutdown(self,*a):event.set()
  class Response:
   status=200
   def read1(self,n):
    if not event.wait(1):raise AssertionError('remaining deadline timer did not fire')
    raise ConnectionError('owned deadline closed socket')
  class Connection:
   sock=Socket()
   def __init__(self,*a,**kw):timeouts.append(kw['timeout'])
   def connect(self):pass
   def request(self,*a):pass
   def getresponse(self):return Response()
   def close(self):pass
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'ledger',self.topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.deadline=time.monotonic()+10.05
   with self.assertRaises(ConnectionError):s.forward('/v1/chat/completions',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda b:None,Connection)
   self.assertTrue(s.records[0]['local_deadline_fired']);self.assertGreater(timeouts[0],0);self.assertLess(timeouts[0],.06);self.assertTrue(Q.cutoff_diagnostic({},s.records))
if __name__=='__main__':unittest.main()
