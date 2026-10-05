"""Offline safety tests for the small takeover delta."""
import http.client,json,pathlib,sys,tempfile,unittest
from unittest import mock
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'runtime'));sys.path.insert(0,str(R))
import session as S,run_screen as Q
class Takeover(unittest.TestCase):
 def session(self,root):
  return S.Session(root,{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'})
 def test_actual_80_global_cap(self):
  with tempfile.TemporaryDirectory() as d:
   s=self.session(pathlib.Path(d)/'transport');s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.posts=80
   with self.assertRaises(S.LocalBudgetExhaustion):s.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda _:None,connect=lambda *a,**kw:self.fail('forwarded past cap'))
   self.assertEqual(s.budget_denials[-1]['maximum_global_POST'],80)
 def deadline_case(self,elapsed):
  with tempfile.TemporaryDirectory() as d:
   s=self.session(pathlib.Path(d)/'transport');s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.deadline=600;t=[100]
   class Sock:
    def shutdown(self,*a):pass
   class Connection:
    sock=Sock()
    def connect(self):pass
    def request(self,*a):pass
    def getresponse(self):t[0]=elapsed;raise http.client.RemoteDisconnected('offline deadline')
    def close(self):pass
   with mock.patch.object(S.time,'monotonic',side_effect=lambda:t[0]),mock.patch.object(S.threading,'Timer'):
    with self.assertRaises(http.client.RemoteDisconnected):s.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda _:None,connect=lambda *a,**kw:Connection())
   return s.records[0]
 def test_deadline_before_headers_can_grade_not_claim_zero(self):
  r=self.deadline_case(830)
  self.assertIsNone(r['provider_status']);self.assertTrue(r['actor_budget_exhaustion']);self.assertFalse(r['usage_complete'])
  self.assertIsNone(Q.actor_transport_error([r],1,True,True))
 def test_early_disconnect_stops(self):
  r=self.deadline_case(110)
  self.assertFalse(r['actor_budget_exhaustion']);self.assertIsNotNone(Q.actor_transport_error([r],1,True,True))
 def test_one_model_five_cells(self):
  p=json.loads((R/'plan.json').read_text())
  self.assertEqual(p['scope_constraints']['model'],'Qwen3.8-27B-FP8');self.assertFalse(p['scope_constraints']['model_fallback'])
  self.assertEqual(len(p['schedule']),5);self.assertEqual(set(x['arm'] for x in p['schedule']),{'none','K','candidate','Both','original'})
  self.assertEqual(p['maximum_provider_POST_total'],80)
if __name__=='__main__':unittest.main()
