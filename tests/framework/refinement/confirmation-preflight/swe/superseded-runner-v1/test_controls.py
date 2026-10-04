import importlib.util,pathlib,tempfile,unittest
from types import SimpleNamespace
p=pathlib.Path(__file__).with_name('run_controls.py');s=importlib.util.spec_from_file_location('controls',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_caps_before_return_and_cleanup(self):
  calls=[];removed=[];c=SimpleNamespace(id='mock',attrs={'HostConfig':{'Memory':m.MEM,'NanoCpus':4_000_000_000,'NetworkMode':'none'}},reload=lambda:None,remove=lambda **k:removed.append(k))
  def create(**kw):calls.append(kw);return c
  with tempfile.TemporaryDirectory() as d:
   g=m.ContainerGuard(SimpleNamespace(create=create),pathlib.Path(d)/'limits.json');g.create(image='digest');self.assertEqual(calls[0]['mem_limit'],m.MEM);self.assertEqual(calls[0]['nano_cpus'],4_000_000_000);self.assertTrue(calls[0]['network_disabled']);g.cleanup();self.assertEqual(len(removed),1)
   with self.assertRaises(RuntimeError):g.create(image='digest')
 def test_no_implicit_pull(self):
  with self.assertRaises(RuntimeError):m.ImageGuard(None).pull('image')
 def test_disk_stop(self):
  for initial,current,free in [(0,m.GROWTH+1,m.FREE),(0,0,m.FREE-1)]:
   with self.assertRaises(RuntimeError):m.disk_guard(initial,current,free)
 def test_failed_limits_cleanup(self):
  removed=[];c=SimpleNamespace(id='mock',attrs={'HostConfig':{'Memory':1,'NanoCpus':4_000_000_000,'NetworkMode':'none'}},reload=lambda:None,remove=lambda **k:removed.append(k))
  with tempfile.TemporaryDirectory() as d:
   g=m.ContainerGuard(SimpleNamespace(create=lambda **kw:c),pathlib.Path(d)/'limits.json')
   with self.assertRaises(RuntimeError):g.create(image='digest')
   self.assertEqual(len(removed),1)
if __name__=='__main__':unittest.main()
