import unittest,ast,pathlib,json,hashlib
import run_coalesced_fasttext_screen as runner
R=pathlib.Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_compile(self):ast.parse(runner.code)
 def test_fixed_task_candidate_resources(self):
  self.assertIn("['selected_tasks'][8]['id']",runner.code);self.assertIn('pi-takeover-qwen-coalesced-verification-admission-16k',runner.code);self.assertIn("memory_mb=public['memory_mb']",runner.code)
 def test_target_only(self):
  self.assertIn('/app/model.bin',runner.code);self.assertNotIn('/app/solution.sparql',runner.code);self.assertNotIn('original_graph',runner.code);self.assertIn('if len(events)!=2',runner.code)
 def test_explicit_private_factory(self):
  self.assertIn('capacity_server=admission_factory(',runner.code);self.assertNotIn('capacity_server=factory(',runner.code);self.assertIn('admission_mark',runner.code)
 def test_uniform_limits(self):
  for x in ["'native_starts_cap':4","'provider_POST_cap':64","'per_actor_POST_cap':16","'actor_seconds':600",'configured_output_cap=16384','setup_seconds_cap=90']:self.assertIn(x,runner.code)
 def test_private_writable_trusted_only(self):
  self.assertIn("str(trusted_tests)+':/tests:rw'",runner.code);self.assertNotIn("str(SOURCE/'tests')+':/tests:ro'",runner.code);self.assertIn("row['original_test_files_unchanged_after_grading']=True",runner.code)
 def test_replay_neverstart_api(self):
  self.assertIn('if present:row[\'replay\']=replay_capture(SOURCE.name,captured,grade,image,actor_image_id=actor_image)',runner.code);x=json.loads((R/'fasttext-readiness-probe-r3.json').read_text());self.assertTrue(x['passed'] and x['cleanup_verified'] and x['never_started_replay_api_respected']);self.assertEqual(x['official_test_runs'],0);self.assertEqual(x['models_trained'],0)
 def test_candidate_only_runtime_freeze(self):
  d=R.parent/'development/pi-takeover-qwen-coalesced-verification-admission-16k';m=json.loads((d/'freeze-manifest.json').read_text());self.assertEqual(m['candidate_sha256'],'cff132600efdd10e64ec47283e164be66c0992ce1d610ce442f6715a705aad87');self.assertEqual(m['runtime_delta'],'NONE/allruntimefilesbyteidenticalincludingtestedadmissionhelper');self.assertTrue(all(hashlib.sha256((d/'runtime'/n).read_bytes()).hexdigest()==h for n,h in m['runtime_hashes'].items()))
if __name__=='__main__':unittest.main()
