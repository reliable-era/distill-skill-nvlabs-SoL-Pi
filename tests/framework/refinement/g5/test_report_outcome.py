import hashlib,json,pathlib,sys,tempfile,types,unittest
from unittest.mock import patch
from report_outcome import adjudicate_report
class OfficialReport(unittest.TestCase):
 def test_model_crash_report_without_tests_status_is_valid_unsolved(self):
  entry=dict(resolved=False,patch_successfully_applied=False,infra_failure=False,error="AttributeError: 'AutoField' object has no attribute 'output_field'")
  def coverage():return entry['tests_status']
  result=adjudicate_report(entry,coverage);self.assertIs(result['solved'],False);self.assertTrue(result['grade_valid']);self.assertEqual(result['diagnostic_errors'][0]['type'],'KeyError');self.assertEqual(result['classification'],'original_official_report')
 def test_diagnostic_parser_failure_cannot_override_resolved_true(self):
  def fail():raise RuntimeError('informational log parser unavailable')
  r=adjudicate_report(dict(resolved=True,infra_failure=False),fail);self.assertTrue(r['solved']);self.assertTrue(r['grade_valid'])
 def test_diagnostics_cannot_replace_official_outcome(self):
  r=adjudicate_report(dict(resolved=False,infra_failure=False),lambda:dict(solved=True,grade_valid=False));self.assertFalse(r['solved']);self.assertTrue(r['grade_valid'])
 def test_grader_adapter_keeps_official_failure_when_tests_status_missing(self):
  from grade_swe import grade
  with tempfile.TemporaryDirectory(prefix='g5-official-report-shape-') as tmp:
   root=pathlib.Path(tmp);dataset=root/'task.json';dataset.write_text(json.dumps([dict(instance_id='task',base_commit='base')]));model=root/'model.patch';model.write_text('nonempty source patch');entry=dict(resolved=False,infra_failure=False,patch_successfully_applied=False);calls=[]
   def run_instance(*args,**kw):calls.append(1);pathlib.Path('report.json').write_text(json.dumps({'task':entry}))
   client=types.SimpleNamespace(api=None,close=lambda:None);spec=types.SimpleNamespace(FAIL_TO_PASS=['test'],PASS_TO_PASS=[]);modules={n:types.ModuleType(n) for n in ('docker','swebench','swebench.harness','swebench.harness.utils','swebench.harness.run_evaluation','swebench.harness.grading')};modules['docker'].from_env=lambda **kw:client;modules['swebench.harness.utils'].make_test_spec=lambda task:spec;ev=modules['swebench.harness.run_evaluation'];ev.run_instance=run_instance;ev.LOG_INSTANCE='instance.log';ev.LOG_TEST_OUTPUT='test_output.txt';ev.APPLY_PATCH_FAIL='apply failed';gr=modules['swebench.harness.grading'];gr.get_logs_eval=lambda *a:({},True);gr._resolve_case=lambda *a:None;plan=dict(official_source_hashes={},wheel_sha256={},wheelhouse=str(root),private_dataset=str(dataset),private_dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),images={'task':'image'},official_source=str(root));oldpath=list(sys.path)
   try:
    with patch.dict(sys.modules,modules):result=grade(root/'grade','task',model,plan)
   finally:sys.path[:]=oldpath
   self.assertFalse(result['solved']);self.assertTrue(result['grade_valid']);self.assertEqual(result['errors'],[]);self.assertEqual(result['diagnostic_errors'][0]['type'],'KeyError');self.assertEqual(calls,[1])
 def test_boolean_official_outcome_required(self):
  for value in (None,0,1,'False'):
   with self.assertRaises(RuntimeError):adjudicate_report(dict(resolved=value))
if __name__=='__main__':unittest.main()
