import importlib.util,pathlib,subprocess,unittest
spec=importlib.util.spec_from_file_location('gate',pathlib.Path(__file__).with_name('run_gate.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Actor:
 def __init__(self):self.live=True
 def wait(self,timeout):
  if self.live:raise subprocess.TimeoutExpired('mock docker actor',timeout)
  return 143
 def poll(self):return None if self.live else 143
class Cutoff(unittest.TestCase):
 def test_actual_cutoff_adapter(self):
  actor=Actor();calls=[]
  def run(cmd,**kwargs):
   calls.append(cmd)
   if cmd[1]=='stop':actor.live=False
   return subprocess.CompletedProcess(cmd,0)
  r=m.docker_cutoff(actor,'owned-mock',0.01,run)
  self.assertEqual(calls,[['docker','stop','-t','5','owned-mock'],['docker','rm','-f','owned-mock']]);self.assertTrue(r['interrupted']);self.assertEqual(r['cleanup_errors'],[])
 def test_failed_cleanup_preserved(self):
  r=m.docker_cutoff(Actor(),'owned-mock',0.01,lambda *a,**k:subprocess.CompletedProcess(a,1))
  self.assertTrue(r['cleanup_errors']);self.assertIsNone(r['exit_code'])
if __name__=='__main__':unittest.main()
