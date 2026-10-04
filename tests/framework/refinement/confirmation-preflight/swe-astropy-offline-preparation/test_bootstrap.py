import pathlib,importlib.util,unittest,tempfile
from unittest.mock import patch
from types import SimpleNamespace
p=pathlib.Path(__file__).with_name('run_bootstrap.py');spec=importlib.util.spec_from_file_location('bootstrap',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_partial_output_survives_failure(self):
  with tempfile.TemporaryDirectory() as d:
   log=pathlib.Path(d)/'partial.log';prefix=pathlib.Path(d)/'prefix.sh';prefix.write_text('echo partial; exit 7\n');command=m.bootstrap_command('true','true')[2].replace('/official-bootstrap-prefix.sh',str(prefix)).replace('/output/private-bootstrap.log',str(log))
   import subprocess
   r=subprocess.run(['bash','-c',command],capture_output=True)
   self.assertEqual(r.returncode,7);self.assertEqual(log.read_text(),'partial\n')
 def test_status_requires_all_gates(self):
  base={'worker-result':{'exit_code':0},'numpy-before':{'numpy':'1.25.2'},'numpy-after':{'numpy':'1.25.2'},'cleanup':{'absence_verified':True}}
  self.assertEqual(m.readiness_status(base),'validated_bootstrap_success')
  base['worker-result']['exit_code']=1;self.assertEqual(m.readiness_status(base),'bootstrap_exit_failure')
  base['worker-result']['exit_code']=0;base['numpy-after']['numpy']='other';self.assertEqual(m.readiness_status(base),'runtime_numpy_changed_or_missing')
 def test_no_auth_no_execution(self):
  with patch.object(m,'load',side_effect=[{}, {'authorized':False}]):
   with self.assertRaises(AssertionError):m.guards()
 def test_cleanup_absence_required(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0),SimpleNamespace(returncode=1,stderr=b'daemon error')]):
   with self.assertRaises(RuntimeError):m.clean('fake',pathlib.Path(d))
if __name__=='__main__':unittest.main()
