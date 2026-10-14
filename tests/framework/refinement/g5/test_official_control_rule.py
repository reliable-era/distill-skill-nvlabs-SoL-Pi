import json,pathlib,tempfile,types,unittest
from official_control_rule import pair
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
 def test_collect_log_text_and_infra_flags_do_not_override_resolved(self):
  with tempfile.TemporaryDirectory(prefix='g5-official-rule-') as t:
   roots={}
   for kind,resolved in (('gold',True),('nop',False)):
    d=pathlib.Path(t)/kind;d.mkdir();(d/'report.json').write_text(json.dumps({'django__django-15098':dict(resolved=resolved,infra_failure=True,infra_failure_reason='collect')}));(d/'test_output.txt').write_text('collecting tests; collected100 items; test collection');roots[kind]=str(d)
   r=pair(roots,'django__django-15098',t);self.assertTrue(r['valid_pair']);self.assertEqual(r['category'],'eligible')
if __name__=='__main__':unittest.main()
