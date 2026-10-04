import copy,importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('terminal_control_tests',OUT/'run_controls.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
class GuardTests(unittest.TestCase):
 def setUp(self):self.plan=json.loads((OUT/'plan.json').read_text())
 def test_exact_budget_permitted(self):runner.cap_check(self.plan,8,4,0)
 def test_ninth_control_refused(self):
  with self.assertRaises(AssertionError):runner.cap_check(self.plan,9,4,0)
 def test_fifth_pull_refused(self):
  with self.assertRaises(AssertionError):runner.cap_check(self.plan,0,5,0)
 def test_build_refused(self):
  with self.assertRaises(AssertionError):runner.cap_check(self.plan,0,0,1)
 def test_model_agent_refused(self):
  p=copy.deepcopy(self.plan);p['controls'][0]['agent']='codex'
  with self.assertRaises(AssertionError):runner.cap_check(p,0,0,0)
 def test_retry_refused(self):
  p=copy.deepcopy(self.plan);p['automatic_retries']=1
  with self.assertRaises(AssertionError):runner.cap_check(p,0,0,0)
 def test_disk_growth_and_minimum(self):
  before={1:{'free':100}};self.assertEqual(runner.disk_ok(before,{1:{'free':80}},20,50),(True,20));self.assertFalse(runner.disk_ok(before,{1:{'free':79}},20,50)[0]);self.assertFalse(runner.disk_ok(before,{1:{'free':40}},100,50)[0])
 def test_cleanup_confirmed(self):
  with patch.object(runner,'owned_containers',side_effect=[['mock'],[]]),patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):self.assertTrue(runner.cleanup('fixture'))
 def test_cleanup_timeout_refused(self):
  with patch.object(runner,'owned_containers',return_value=['mock']),patch.object(runner.subprocess,'run',side_effect=subprocess.TimeoutExpired('docker',15)):self.assertFalse(runner.cleanup('fixture'))
 def test_cleanup_remaining_refused(self):
  with patch.object(runner,'owned_containers',return_value=['mock']),patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):self.assertFalse(runner.cleanup('fixture'))
 def test_missing_auth_blocks_before_pull(self):
  with patch.object(runner.OUT.__class__,'exists',return_value=False):
   with self.assertRaisesRegex(RuntimeError,'authorization missing'):runner.check_authorization(self.plan)
 def test_resource_mismatch_refused(self):
  inspected={'HostConfig':{'NanoCpus':0,'Memory':2147483648},'Mounts':[],'Config':{'Env':[]}}
  with patch.object(runner,'owned_containers',return_value=['fixture']),patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps([inspected]))):
   with self.assertRaisesRegex(RuntimeError,'enforcement mismatch'):runner.runtime_container_checks('fixture',set(),Path('/tmp/private-fixture'))
 def test_external_auth_mount_refused(self):
  inspected={'HostConfig':{'NanoCpus':1000000000,'Memory':2147483648},'Mounts':[{'Type':'bind','Source':'/tmp/external-auth-fixture'}],'Config':{'Env':[]}}
  with patch.object(runner,'owned_containers',return_value=['fixture']),patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps([inspected]))):
   with self.assertRaisesRegex(RuntimeError,'external bind mount'):runner.runtime_container_checks('fixture',set(),Path('/tmp/private-fixture'))
 def test_time_cap_cancels_process(self):
  process=MagicMock();process.poll.return_value=None;process.wait.return_value=-15
  with tempfile.TemporaryDirectory() as td:
   context={'private':Path(td),'start':0,'plan':self.plan}
   with patch.object(runner.subprocess,'Popen',return_value=process),patch.object(runner.time,'monotonic',side_effect=[0,2,2]),patch.object(runner,'kill_process') as kill:
    r=runner.guarded_process(['fixture'],Path(td)/'log',1,context)
    self.assertEqual(r['stop_reason'],'time_cap');kill.assert_called_once_with(process)
 def test_order_change_refused(self):
  p=copy.deepcopy(self.plan);p['controls'].reverse()
  with self.assertRaises(AssertionError):runner.cap_check(p,0,0,0)
if __name__=='__main__':unittest.main()
