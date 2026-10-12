import copy,unittest
from audit_admissions import zero
class RawAdmission(unittest.TestCase):
 def load(self):return dict(backend='127.0.0.1:8000',path='/get_load',status=200,body=[dict(num_waiting_reqs=0),dict(num_waiting_reqs=0)])
 def test_all_advertised_backends_required(self):
  self.assertTrue(zero(self.load()));v=self.load();v['body'][-1]['num_waiting_reqs']=1;self.assertFalse(zero(v))
 def test_empty_missing_noninteger_waiting_rejected(self):
  for rows in ([],[{}],[dict(num_waiting_reqs=False)],[dict(num_waiting_reqs='0')],[dict(num_waiting_reqs=0.0)]):
   with self.subTest(rows=rows):v=self.load();v['body']=rows;self.assertFalse(zero(v))
 def test_direct_backend_outage_wrong_path_rejected(self):
  for k,v in (('backend','127.0.0.1:18002'),('status',503),('path','/v1/responses')):
   with self.subTest(k=k):r=self.load();r[k]=v;self.assertFalse(zero(r))
if __name__=='__main__':unittest.main()
