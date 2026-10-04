import importlib.util,pathlib,unittest,json
from unittest.mock import Mock
r=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('broker',r/'broker.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
s=importlib.util.spec_from_file_location('route',r/'route.py');route=importlib.util.module_from_spec(s);s.loader.exec_module(route)
class Safety(unittest.TestCase):
 def test_post_denied(self):
  x=object.__new__(m.Broker);x.send_error=Mock();m.Broker.posts=0;x.do_POST();x.send_error.assert_called_once_with(403);self.assertEqual(m.Broker.posts,1)
 def test_invalid_path_denied_before_upstream(self):
  x=object.__new__(m.Broker);x.connection=Mock();x.path='/solution';x.headers={};x.send_error=Mock();x.do_GET();x.send_error.assert_called_once_with(403)
 def test_zero_model_guard(self):
  p=json.loads((r/'plan.json').read_text());p['model_starts']=1
  with self.assertRaises(RuntimeError):route.validate(p)
 def test_absence_requires_evidence(self):
  self.assertFalse(route.absence(1,'permission denied','container','owned'));self.assertFalse(route.absence(0,'','container','owned'));self.assertTrue(route.absence(1,'Error response from daemon: No such container: owned','container','owned'))
 def test_absence_rejects_other_object(self):
  self.assertFalse(route.absence(1,'Error response from daemon: No such container: foreign','container','owned'))
  self.assertFalse(route.absence(1,'Error: No such network: owned','container','owned'))
  self.assertTrue(route.absence(1,'Error: No such network: owned','network','owned'))
 def test_actual_helper_resource_guard(self):
  self.assertTrue(route.resources_ok({'HostConfig':{'NanoCpus':1000000000,'Memory':536870912}}))
  self.assertFalse(route.resources_ok({'HostConfig':{'NanoCpus':1000000000,'Memory':0}}))
 def test_absolute_read_cutoff_installed_and_joined(self):
  from unittest.mock import patch
  x=object.__new__(m.Broker);x.connection=Mock();x.path='/v1/models';x.headers={};x.send_response=Mock();x.send_header=Mock();x.end_headers=Mock();x.wfile=Mock()
  conn=Mock();conn.getresponse.return_value.read.return_value=b'{}';conn.getresponse.return_value.status=200
  timer=Mock();m.Broker.get_count=0
  with patch.object(m.http.client,'HTTPConnection',return_value=conn),patch.object(m.threading,'Timer',return_value=timer) as factory:
   x.do_GET();self.assertEqual(factory.call_args.args[0],5);factory.call_args.args[1]();conn.sock.shutdown.assert_called_once();timer.start.assert_called_once();timer.cancel.assert_called_once();timer.join.assert_called_once();self.assertEqual(m.Broker.active,0)
 def test_failed_command_stderr_is_durable(self):
  import tempfile,sys
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)
   with self.assertRaisesRegex(RuntimeError,'command_failure'):
    route.bounded_command([sys.executable,'-c','import sys;print("mock stdout");print("retained mock failure",file=sys.stderr);sys.exit(7)'],p,1,2)
   self.assertIn('retained mock failure',(p/'command-1.stderr').read_text());self.assertEqual(json.loads((p/'command-1.json').read_text())['exit_code'],7)
 def test_capture_is_bounded(self):
  import tempfile,sys
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)
   try:route.bounded_command([sys.executable,'-c','import os;os.write(1,b"x"*65536)'],p,1,2)
   except RuntimeError:pass
   self.assertLessEqual((p/'command-1.stdout').stat().st_size,32768)
if __name__=='__main__':unittest.main()
