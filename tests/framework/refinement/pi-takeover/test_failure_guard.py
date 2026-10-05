import unittest,types,threading
from prospective_failure_guard import guard
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def raw(self):return types.SimpleNamespace(active='owned',deadline=100.,posts=1,lock=threading.Lock(),connections={1:True})
 def test_actual_captureexception_preserved_before_teardown(self):
  r=self.raw();history=[];epoch=(r.active,r.deadline,r.posts);error=CaptureError('synthetic header rejection')
  def stop():history.append('stop');return True
  def sleep(dt):history.append('receipt_finished');r.connections.clear()
  def record(result):self.assertTrue(result['drained']);history.append('drain_recorded')
  try:
   with self.assertRaises(CaptureError) as raised:
    with guard(r,stop,record,now=lambda:90.,sleep=sleep):raise error
   self.assertIs(raised.exception,error)
  finally:history.append('teardown')
  self.assertEqual(history,['stop','receipt_finished','drain_recorded','teardown']);self.assertEqual((r.active,r.deadline,r.posts),epoch)
 def test_expired_actual_exception_still_preserved_unknown(self):
  r=self.raw();records=[]
  with self.assertRaises(CaptureError):
   with guard(r,lambda:True,records.append,now=lambda:331.):raise CaptureError('synthetic')
  self.assertFalse(records[0]['drained']);self.assertTrue(records[0]['usage_remains_unavailable']);self.assertEqual(r.posts,1)
 def test_unverified_stop_failsclosed_no_drain(self):
  r=self.raw();records=[]
  with self.assertRaises(RuntimeError):
   with guard(r,lambda:False,records.append):pass
  self.assertEqual(records,[]);self.assertEqual(r.deadline,100.)
if __name__=='__main__':unittest.main()
