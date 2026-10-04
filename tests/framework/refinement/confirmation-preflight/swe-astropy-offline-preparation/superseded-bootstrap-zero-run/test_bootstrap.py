import pathlib,importlib.util,unittest,tempfile
from unittest.mock import patch
from types import SimpleNamespace
p=pathlib.Path(__file__).with_name('run_bootstrap.py');spec=importlib.util.spec_from_file_location('bootstrap',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_no_auth_no_execution(self):
  with patch.object(m,'load',side_effect=[{}, {'authorized':False}]):
   with self.assertRaises(AssertionError):m.guards()
 def test_cleanup_absence_required(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0),SimpleNamespace(returncode=1,stderr=b'daemon error')]):
   with self.assertRaises(RuntimeError):m.clean('fake',pathlib.Path(d))
if __name__=='__main__':unittest.main()
