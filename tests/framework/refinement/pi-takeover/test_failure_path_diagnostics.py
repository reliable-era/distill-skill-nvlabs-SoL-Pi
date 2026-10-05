import unittest,threading,types,tarfile,math
from prospective_completion_drain import drain
from prospective_capture_rejection import classify
class Tests(unittest.TestCase):
 def raw(self):return types.SimpleNamespace(active='owned',deadline=100.,posts=1,lock=threading.Lock(),connections={1:True})
 def test_pending_drains_withoutdeadline_orPOSTchange(self):
  r=self.raw();initial=r.deadline;t=[90.];result=drain(r,now=lambda:t[0],sleep=lambda dt:(t.__setitem__(0,t[0]+dt),r.connections.clear()));self.assertTrue(result['drained']);self.assertEqual(r.deadline,initial);self.assertEqual(r.posts,1)
 def test_expired_is_unknown_notzero(self):
  r=self.raw();v=drain(r,now=lambda:331.);self.assertFalse(v['drained']);self.assertTrue(v['usage_remains_unavailable']);self.assertEqual(v['completion_limit'],330.)
 def test_epochchange_reject(self):
  r=self.raw();self.assertRaises(RuntimeError,drain,r,now=lambda:90.,sleep=lambda dt:setattr(r,'active','other'))
 def test_newforward_reject(self):
  r=self.raw();self.assertRaises(RuntimeError,drain,r,now=lambda:90.,sleep=lambda dt:setattr(r,'posts',2))
 def test_nonfinite_deadline_reject(self):
  r=self.raw();r.deadline=math.nan;self.assertRaises(ValueError,drain,r)
 def test_writer_not_finished_evenconnections_empty(self):
  r=self.raw();r.connections.clear();lock=threading.Lock();lock.acquire();s=types.SimpleNamespace(raw_session=r,forward_lock=lock);v=drain(s,now=lambda:331.);self.assertFalse(v['drained']);self.assertTrue(lock.locked());lock.release()
 def test_capture_exactvalidboundary(self):
  m=tarfile.TarInfo('model.bin');m.size=160;self.assertIsNone(classify(m,1,'model.bin',160));m.name='./model.bin';self.assertIsNone(classify(m,1,'model.bin',160))
 def test_capture_distinctreasons_withoutpayload(self):
  m=tarfile.TarInfo('model.bin');m.size=161;self.assertEqual(classify(m,1,'model.bin',160)['reason'],'size_cap');m.type=tarfile.SYMTYPE;self.assertEqual(classify(m,1,'model.bin',160)['reason'],'member_type');m.name='unknown';self.assertEqual(classify(m,1,'model.bin',160)['reason'],'member_name');self.assertEqual(classify(m,2,'model.bin',160)['reason'],'member_count');self.assertFalse(classify(m,2,'model.bin',160)['payload_read'])
if __name__=='__main__':unittest.main()
