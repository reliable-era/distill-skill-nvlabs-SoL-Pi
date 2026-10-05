import unittest,json,types
from copilot_owned_issuance_guard import IssuanceGuard,relay_response
from prospective_owned_epoch import stop
class Response:
 def __init__(self,length,chunks):self.length=length;self.chunks=list(chunks)
 def read1(self,n):
  b=self.chunks.pop(0) if self.chunks else b'';self.length-=len(b);return b
class Tests(unittest.TestCase):
 def test_verified_stop_before_eof_teardown(self):
  order=[];g=IssuanceGuard(1,lambda:order.append('stop') or True,lambda r:order.append('receipt'))
  self.assertTrue(g.admit())
  try:
   with self.assertRaises(EOFError):relay_response(Response(8,[b'ACK']),lambda b:order.append('content'),g)
  finally:order.append('teardown')
  self.assertEqual(order,['content','stop','receipt','teardown']);self.assertFalse(g.admit());self.assertEqual(g.headers,2);self.assertEqual(g.denied,1)
 def test_complete_http_no_stop_no_usage_claim(self):
  g=IssuanceGuard(1,lambda:(_ for _ in ()).throw(AssertionError()),lambda r:None)
  self.assertEqual(relay_response(Response(3,[b'ACK']),lambda b:None,g),3);self.assertIsNone(g.abort_result)
 def test_unknown_length_stop_fail_closed(self):
  g=IssuanceGuard(1,lambda:True,lambda r:None)
  with self.assertRaises(ValueError):relay_response(Response(None,[]),lambda b:None,g)
  self.assertTrue(g.closed)
 def test_unverified_stop_sticky_and_not_repeated(self):
  calls=[];g=IssuanceGuard(1,lambda:calls.append(1) or False,lambda r:None)
  with self.assertRaises(RuntimeError):relay_response(Response(8,[]),lambda b:None,g)
  g.abort('again');self.assertEqual(calls,[1]);self.assertFalse(g.abort_result['owned_stop_verified']);self.assertFalse(g.admit())
 def test_cap_without_relaunch(self):
  g=IssuanceGuard(1,lambda:True,lambda r:None);self.assertTrue(g.admit());self.assertFalse(g.admit());self.assertEqual(g.accepted,1);self.assertEqual(g.headers,2)
 def epoch(self,changed=False):
  session=types.SimpleNamespace(active='candidate',deadline=123)
  ctx={'arm':'candidate','deadline':123,'container_id':'exact-id','name':'owned-name','image':'pinned-image'};calls=[]
  def docker(*args):
   calls.append(args)
   return json.dumps([{'Id':'different' if changed else 'exact-id','Image':'pinned-image','State':{'Running':len(calls)==1,'Paused':False}}])
  return session,ctx,docker,calls
 def test_reuse_actual_owned_epoch_stop_identity_checks(self):
  s,c,d,calls=self.epoch();g=IssuanceGuard(1,lambda:stop(s,c,d,{'owned-name'}),lambda r:None)
  with self.assertRaises(EOFError):relay_response(Response(2,[]),lambda b:None,g)
  self.assertEqual([x[0] for x in calls],['inspect','stop','inspect']);self.assertTrue(g.abort_result['owned_stop_verified'])
 def test_reused_stop_rejects_wrong_container_no_stop(self):
  s,c,d,calls=self.epoch(True);g=IssuanceGuard(1,lambda:stop(s,c,d,{'owned-name'}),lambda r:None)
  with self.assertRaises(RuntimeError):relay_response(Response(2,[]),lambda b:None,g)
  self.assertEqual([x[0] for x in calls],['inspect']);self.assertFalse(g.abort_result['owned_stop_verified'])
if __name__=='__main__':unittest.main()
