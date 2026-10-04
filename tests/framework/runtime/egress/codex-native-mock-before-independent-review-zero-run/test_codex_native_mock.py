import importlib.util,pathlib,json,unittest
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('native',R/'codex_native_mock.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Safety(unittest.TestCase):
 def test_cap(self):
  p=json.loads((R/'codex-native-mock-plan.json').read_text());p['maximum_native_starts']=3
  with self.assertRaises(ValueError):m.validate(p)
 def test_no_real_provider(self):
  p=json.loads((R/'codex-native-mock-plan.json').read_text());p['provider_config']['model_providers.mock.base_url']='https://api.openai.com/v1'
  with self.assertRaises(ValueError):m.validate(p)
 def test_cleanup_guard(self):
  import subprocess
  with self.assertRaises(RuntimeError):m.cleanup_guard(subprocess.CompletedProcess([],1))
 def test_exact_receipts(self):
  self.assertFalse(m.receipt_ok(0,[{'method':'GET','path':'/v1/responses'}],''))
  self.assertTrue(m.receipt_ok(0,[{'method':'POST','path':'/v1/responses'}],''))
  self.assertFalse(m.receipt_ok(1,[],'configuration rejected'))
  self.assertTrue(m.receipt_ok(1,[],'HTTP403 destination denied'))
if __name__=='__main__':unittest.main()
