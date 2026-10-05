import unittest,ast
import run_16k_regex_screen as runner
class Tests(unittest.TestCase):
 def test_code_compiles(self):ast.parse(runner.code)
 def test_task_order(self):self.assertIn("['selected_tasks'][6]['id']",runner.code);self.assertIn('/regex-log',runner.code)
 def test_no_tex_or_html_output_semantics(self):
  for text in ['capture_before(',"'/app/out.html'",'protected_inputs_original=','row[\'protected_before\']']:self.assertNotIn(text,runner.code)
 def test_original_grade(self):self.assertIn("if len(events)!=1",runner.code);self.assertIn("grade,'--network','none'",runner.code);self.assertIn('cached_grader_setup import prepare',runner.code)
 def test_uniform_software(self):self.assertIn('from regex_actor_inputs import recipe',runner.code);self.assertNotIn('from actor_public_inputs import recipe,',runner.code);self.assertIn('public_python_binding_sha256',runner.code)
 def test_absence_not_quality_inference(self):self.assertIn('output_absent_verified',runner.code);self.assertIn('test ! -e /app/regex.txt',runner.code);self.assertIn('row[\'reward\']=reward.read_text()',runner.code)
 def test_fixed_budget_and_both(self):self.assertIn("'native_starts_cap':4",runner.code);self.assertIn("'provider_POST_cap':64",runner.code);self.assertIn('configured_output_cap=16384',runner.code);self.assertIn("comparator_Both_definition']=='currentcandidate+frozenKarpathy'",runner.code)
if __name__=='__main__':unittest.main()
