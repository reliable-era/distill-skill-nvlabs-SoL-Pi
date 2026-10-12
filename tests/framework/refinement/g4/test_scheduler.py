"""Offline policy tests, no metadata HTTP/actors/model calls."""
import json,pathlib,tempfile,unittest
from unittest.mock import patch
from scheduler import retry_eligible,Queue
class SchedulerTests(unittest.TestCase):
 def row(self,root,requests=0,**kw):return dict(root=str(root),requests=requests,owned_cleanup_verified=True,native_started=True,timeout=False,grader_timeout=False,**kw)
 def ledger(self,root,records):
  (root/'transport').mkdir();(root/'transport/ledger.json').write_text(json.dumps(dict(provider_POST=len(records),records=records)))
 def test_proven_zero_posts_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);self.ledger(p,[]);self.assertTrue(retry_eligible(self.row(p)))
 def test_refused_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);self.ledger(p,[dict(request=1,provider_status=None,proven_zero_model_refusal=True,connection_infra_failure=True)]);self.assertTrue(retry_eligible(self.row(p,1)))
 def test_model_error_and_cap_never_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);self.ledger(p,[dict(request=1,provider_status=400)]);self.assertFalse(retry_eligible(self.row(p,1)))
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);r=self.row(p,60);self.assertFalse(retry_eligible(r));r=self.row(p);r['timeout']=True;self.assertFalse(retry_eligible(r))
 def test_failed_terminal_even_after_reset_never_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);self.ledger(p,[dict(request=1,provider_status=200,connection_infra_failure=True)]);(p/'transport/response-1.sse').write_text('data: {"type":"response.failed"}\n');self.assertFalse(retry_eligible(self.row(p,1)))
 def test_cleanup_uncertain_never_retry(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.row(pathlib.Path(d));r['owned_cleanup_verified']=False;self.assertFalse(retry_eligible(r))
 def test_admission_requires_reserved_slot(self):
  with tempfile.TemporaryDirectory() as d:
   q=Queue({}, {},d)
   with self.assertRaises(RuntimeError):q.start_callback({'cell_id':'x'},1)
 def test_admission_returns_fresh_all_zero_proof(self):
  with tempfile.TemporaryDirectory() as d:
   q=Queue({}, {},d);q.active={'x':{}}
   with patch.object(q,'observation',return_value={'body':[dict(num_waiting_reqs=0,num_reqs=3)]}):r=q.start_callback({'cell_id':'x'},1)
   self.assertEqual(r['occupied_slots_after_admission'],1);self.assertEqual(r['load']['body'][0]['num_waiting_reqs'],0)
if __name__=='__main__':unittest.main()
