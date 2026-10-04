import importlib.util,pathlib,tempfile,unittest,json
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('wrapper',R/'wrapper.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Offline(unittest.TestCase):
 def test_private_home_and_grader(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=m.prepare(pathlib.Path(tmp)/'fixture',1234);self.assertTrue((root/'home/.codex').is_dir());self.assertEqual((root.stat().st_mode & 0o777),0o700)
   models=json.loads((root/'home/.pi/agent/models.json').read_text());self.assertEqual(models['providers']['local-readiness']['baseUrl'],'http://provider.example:1234/v1')
   from unittest.mock import patch
   import subprocess
   def fake(args,**kwargs):
    if args[1]=='inspect':return subprocess.CompletedProcess(args,1,stderr='No such object: '+args[2])
    return subprocess.CompletedProcess(args,0,stderr='')
   with patch.object(m.subprocess,'run',side_effect=fake) as run:
    self.assertTrue(m.grade(root/'work',True)['solved']);self.assertEqual(run.call_args_list[0].kwargs['timeout'],10);self.assertIn('preexec_fn',run.call_args_list[0].kwargs)
    launch=run.call_args_list[0].args[0];self.assertIn('none',launch);self.assertIn('512m',launch);self.assertIn('--read-only',launch)

 def test_grader_output_bound(self):
  from unittest.mock import patch
  import subprocess,sys
  original=subprocess.run
  def fake(args,**kw):
   if args[1]=='run':return original([sys.executable,'-c','import os;os.write(1,b"x"*70000)'],**kw)
   if args[1]=='inspect':return subprocess.CompletedProcess(args,1,stderr='No such object: '+args[2])
   return subprocess.CompletedProcess(args,0,stderr='')
  with tempfile.TemporaryDirectory() as tmp:
   root=m.prepare(pathlib.Path(tmp)/'fixture',1234)
   with patch.object(m.subprocess,'run',side_effect=fake):result=m.grade(root/'work',None)
   self.assertLessEqual(result['grader_metadata']['streams']['stdout']['bytes'],65536);self.assertFalse(result['solved']);self.assertIsNone(result['usage'])
 def test_argv_budget_and_unknown(self):
  self.assertIn('--no-extensions',m.argv('pi',1234));self.assertIn('web_search="disabled"',m.argv('codex',1234))
  with self.assertRaises(ValueError):m.argv('other',1234)
  with self.assertRaises(ValueError):m.argv('codex',0)
if __name__=='__main__':unittest.main()
