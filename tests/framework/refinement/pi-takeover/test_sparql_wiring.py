import unittest,ast,pathlib,json,hashlib,types
import run_behavior_first_sparql_screen as runner
from sparql_output_presence import stopped_output_present
from artifact_capture import CaptureError
import test_regex_output_presence as presence_fixtures
R=pathlib.Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_compile(self):ast.parse(runner.code)
 def test_fixed_task_and_candidate_runtime(self):self.assertIn("['selected_tasks'][7]['id']",runner.code);self.assertIn('pi-takeover-qwen-behavior-first-admission-16k',runner.code);self.assertNotIn('pi-takeover-qwen-source-backed-16k',runner.code)
 def test_explicit_tested_admission_notold_factory(self):self.assertIn('capacity_server=admission_factory(',runner.code);self.assertNotIn('capacity_server=factory(',runner.code);self.assertIn('AdmissionJournal(root/',runner.code);self.assertIn('admission_mark',runner.code)
 def test_original_tests_and_data(self):self.assertIn('if len(events)!=3',runner.code);self.assertIn("grade,'--network','none'",runner.code);self.assertIn("row['trusted_original_graph_verified']=True",runner.code);self.assertIn('original-graph.ttl',runner.code)
 def test_correct_output(self):self.assertIn('/app/solution.sparql',runner.code);self.assertNotIn('/app/regex.txt',runner.code);self.assertNotIn('capture_before(',runner.code)
 def test_uniform_resources_skills_budget(self):self.assertIn('from sparql_public_inputs import recipe',runner.code);self.assertIn("'provider_POST_cap':64",runner.code);self.assertIn('configured_output_cap=16384',runner.code);self.assertIn("comparator_Both_definition']=='currentcandidate+frozenKarpathy'",runner.code)
 def test_ready_not_score(self):
  x=json.loads((R/'sparql-readiness-probe.json').read_text());self.assertTrue(x['passed'] and x['cleanup_verified']);self.assertEqual(x['official_test_runs'],0);self.assertEqual(x['model_POST'],0);self.assertEqual(len(x['collected_original_tests']),3)
 def test_presence_exactpath(self):c,requests=presence_fixtures.Tests().fake();self.assertTrue(stopped_output_present('owned','image',c));self.assertIn('solution.sparql',requests[1][1]);self.assertNotIn('regex.txt',requests[1][1])
 def test_absence_verified(self):self.assertFalse(stopped_output_present('owned','image',presence_fixtures.Tests().fake(404)[0]))
 def test_race_not_quality_failure(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',presence_fixtures.Tests().fake(404,identity='changed')[0])
 def test_forbidden_mount(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',presence_fixtures.Tests().fake(mounts=[{'Destination':'/tests'}])[0])
 def test_new_helper_same_native_gate_bytes(self):
  helper=R.parent/'development/pi-takeover-qwen-behavior-first-admission-16k/runtime/broker_admission.py';plan=json.loads((R/'admission-native-probe-plan.json').read_text());self.assertEqual(hashlib.sha256(helper.read_bytes()).hexdigest(),plan['prospective_module_sha256'])
if __name__=='__main__':unittest.main()
