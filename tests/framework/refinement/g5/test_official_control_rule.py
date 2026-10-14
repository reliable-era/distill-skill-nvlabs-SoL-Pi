import types,unittest
from control_worker import validate
class OfficialControlRule(unittest.TestCase):
 def test_absent_skipped_statuses_do_not_exclude_official_pair(self):
  spec=types.SimpleNamespace(FAIL_TO_PASS=['target'],PASS_TO_PASS=['preserved']);entry=dict(infra_failure=False,resolved=True,tests_status={k:dict(success=[],failure=[]) for k in ('FAIL_TO_PASS','PASS_TO_PASS')});resolve=lambda x,s:None
  coverage=validate(entry,spec,{},False,'gold',resolve,None);self.assertEqual(coverage['FAIL_TO_PASS']['expected'],1);entry['resolved']=False;validate(entry,spec,{},False,'nop',resolve,None)
 def test_official_noop_resolved_true_stays_excluded(self):
  spec=types.SimpleNamespace(FAIL_TO_PASS=[],PASS_TO_PASS=[]);entry=dict(infra_failure=False,resolved=True,tests_status={k:dict(success=[],failure=[]) for k in ('FAIL_TO_PASS','PASS_TO_PASS')})
  with self.assertRaises(RuntimeError):validate(entry,spec,{},False,'nop',lambda *a:None,None)
 def test_official_infrastructure_not_valid(self):
  spec=types.SimpleNamespace(FAIL_TO_PASS=[],PASS_TO_PASS=[])
  with self.assertRaises(RuntimeError):validate(dict(infra_failure=True),spec,{},False,'gold',lambda *a:None,None)
if __name__=='__main__':unittest.main()
