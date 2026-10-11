import pathlib,tempfile,time,unittest
from unittest.mock import patch
from scheduler import Queue,next_attempt
class Tests(unittest.TestCase):
 def cell(self):return dict(cell_id='cell',task='task',round=1,arm='none')
 def row(self,n=1,retry=False):return dict(cell_id='cell',attempt=n,infra_retry_eligible=retry,cleanup_errors=[])
 def test_once_uniform_retry(self):
  c=self.cell();self.assertEqual(next_attempt(c,[]),1);self.assertEqual(next_attempt(c,[self.row(retry=True)]),2);self.assertIsNone(next_attempt(c,[self.row(retry=True),self.row(2,True)]));self.assertIsNone(next_attempt(c,[self.row()]))
 def test_cleanup_blocks(self):
  r=self.row();r['cleanup_errors']=['owned']
  with self.assertRaises(RuntimeError):next_attempt(self.cell(),[r])
 def test_queue_retry_retains_both(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);q=Queue({},[self.cell()],[],p,p,time.time()+30)
   def fake(c,n,root,plan,admission,cb):return self.row(n,n==1)
   with patch('scheduler.attempt',side_effect=fake):q.run(0,self.cell(),1)
   self.assertEqual([r['attempt'] for r in q.rows],[1,2]);self.assertEqual(q.active,0);self.assertEqual(q.max_active,1)
 def test_cap_model_failure_no_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);q=Queue({},[self.cell()],[],p,p,time.time()+30)
   with patch('scheduler.attempt',return_value=self.row()):q.run(0,self.cell(),1)
   self.assertEqual(len(q.rows),1)
 def test_waiting_zero_admission(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);q=Queue({},[],[],p,p,time.time()+30);q.active=18;v={'body':[{'num_reqs':22,'num_waiting_reqs':0}]}
   with patch('scheduler.metadata',return_value=v):self.assertEqual(q.admit(0,True,'cell-a1',None),v)
   self.assertEqual(q.sequence,1);self.assertEqual(q.events[0]['slots'],18)
 def test_outage_stops(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);q=Queue({},[],[],p,p,time.time()+30)
   with patch('scheduler.metadata',side_effect=ConnectionRefusedError('mock')):
    with self.assertRaises(ConnectionRefusedError):q.admit(0,True,'cell-a1',None)
   self.assertIn('9012 metadata outage',q.stop)
 def test_expired_window_no_attempt(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);q=Queue({},[],[],p,p,time.time()-1)
   with patch('scheduler.attempt') as f:q.run(0,self.cell(),1);f.assert_not_called()
if __name__=='__main__':unittest.main()
