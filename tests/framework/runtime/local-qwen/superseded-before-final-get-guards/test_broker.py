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
  self.assertFalse(route.absence(1,'permission denied'));self.assertFalse(route.absence(0,''));self.assertTrue(route.absence(1,'No such container'))
if __name__=='__main__':unittest.main()
