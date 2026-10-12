import unittest
from BC_retry_scheduler import waiting_zero
class ActiveLoad(unittest.TestCase):
 def row(self,b,w=0):return dict(backend=b,num_reqs=0,num_waiting_reqs=w)
 def record(self,extra=()):return dict(body=[self.row('127.0.0.1:18001'),self.row('127.0.0.1:18002'),*extra])
 def test_active_zero_with_disabled_queue(self):self.assertTrue(waiting_zero(self.record([self.row('10.193.104.97:18001',100)])))
 def test_honey_if_advertised_must_zero(self):self.assertFalse(waiting_zero(self.record([self.row('127.0.0.1:9012',1)])))
 def test_local_queued(self):v=self.record();v['body'][0]['num_waiting_reqs']=1;self.assertFalse(waiting_zero(v))
 def test_unknown_backend_pauses(self):self.assertFalse(waiting_zero(self.record([self.row('unapproved:42')])))
 def test_missing_local_pauses(self):self.assertFalse(waiting_zero(dict(body=[self.row('127.0.0.1:18001')])))
 def test_malformed(self):
  for x in ({},dict(body=[]),dict(body=[None]),dict(body='bad')):self.assertFalse(waiting_zero(x))
 def test_bool_not_integer(self):v=self.record();v['body'][0]['num_waiting_reqs']=False;self.assertFalse(waiting_zero(v))
if __name__=='__main__':unittest.main()
