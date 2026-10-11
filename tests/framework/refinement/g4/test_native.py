"""Native argument/authorization checks only; never start actors or call models."""
import pathlib,tempfile,unittest
from native import argv,create_args,authorized
class NativeTests(unittest.TestCase):
 def test_incomplete_prereg_cannot_infer(self):
  with self.assertRaises(RuntimeError):authorized({'cell_id':'x','part':'C'},{'full_preregistration':False},{'cells':['x']})
 def test_no_window_cell_cannot_infer(self):
  with self.assertRaises(RuntimeError):authorized({'cell_id':'x','part':'C'},{'full_preregistration':True},{'cells':[]})
 def test_codex_flags_and_local_unix_relay_endpoint(self):
  args=argv('task');self.assertIn('--ignore-user-config',args);self.assertIn('--ephemeral',args);self.assertIn('--json',args);self.assertTrue(any('base_url="http://127.0.0.1:8080/v1"' in s for s in args));self.assertTrue(any('request_max_retries=0' in s for s in args));self.assertTrue(any('multi_agent=false' in s for s in args))
 def test_C_same_readonly_offline_cache_and_no_gold_mount(self):
  args=create_args('solpi-g4-test','sha256:fake','/private/cell','C',8192,'/testbed','/private/public-wheels');text=' '.join(args);self.assertIn('--network none',text);self.assertIn('8192m',text);self.assertIn('/private/public-wheels:/wheelhouse:ro',text);self.assertIn('PIP_NO_INDEX=1',text);self.assertNotIn('/solution',text);self.assertNotIn('/tests:',text);self.assertNotIn('docker.sock',text)
 def test_C_without_matching_cache_rejected(self):
  with self.assertRaises(ValueError):create_args('x','image','root','C',8192,'/testbed')
 def test_no_direct_backend_or_gpu_in_actor_args(self):
  text=' '.join(create_args('solpi-g4-test','image','root','B',2048,'/app'));self.assertNotIn('9012',text);self.assertNotIn('--gpus',text);self.assertNotIn('--privileged',text);self.assertNotIn('--network host',text)
if __name__=='__main__':unittest.main()
