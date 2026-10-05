import unittest,pathlib,importlib.util,json,tempfile,ast
R=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('screen',R/'run_screen.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
class Protocol(unittest.TestCase):
 def test_budget_intervention_not_generic_provider_error(self):
  self.assertTrue(q.cutoff_diagnostic({},[{'error':'IncompleteRead','provider_status':200,'local_deadline_fired':True}]))
  self.assertFalse(q.cutoff_diagnostic({},[{'error':'IncompleteRead','provider_status':200,'local_deadline_fired':False}]))
  self.assertFalse(q.cutoff_diagnostic({'availability':'deadline_interrupted'},[{'provider_status':503}]))
 def test_actual_pi_config_and_new_candidate(self):
  task={'baseline':None,'prompt':None}
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);(r/'base').mkdir();(r/'prompt').write_text('fixture');task.update(baseline=str(r/'base'),prompt=str(r/'prompt'));p=q.W.prepare(r/'actor',8000,task,'candidate');settings=json.loads((p/'home/.pi/agent/settings.json').read_text());self.assertEqual(settings['retry']['provider']['timeoutMs'],600000);self.assertEqual(q.sha(p/'skills/candidate/SKILL.md'),'603e81e6eba2c34de42ea3d0f4b8c039e01b2aa64ac962ef4a407a5caa9e715b')
 def test_original_grade_function_unchanged(self):
  p=json.loads((R/'plan.json').read_text());source=(R/'runtime/wrapper.py').read_text();f=ast.get_source_segment(source,next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='grade'));import hashlib;self.assertEqual(hashlib.sha256(f.encode()).hexdigest(),p['reused_grading_control']['adapter_grade_function_sha256'])
 def test_caps_and_schedule(self):
  p=json.loads((R/'plan.json').read_text());self.assertEqual(p['seconds_per_actor'],600);self.assertEqual(p['order_seed'],131);self.assertEqual(len(p['schedule']),12)
  for family in p['tasks']:self.assertEqual(sorted(x['arm'] for x in p['schedule'] if x['family']==family),['Both','K','candidate','none'])
if __name__=='__main__':unittest.main()
