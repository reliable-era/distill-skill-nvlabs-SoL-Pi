import importlib.util,pathlib,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
p=pathlib.Path(__file__).with_name('run_controls.py');s=importlib.util.spec_from_file_location('controls',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_caps_before_return_and_cleanup(self):
  calls=[];removed=[];c=SimpleNamespace(id='mock',attrs={'HostConfig':{'Memory':m.MEM,'NanoCpus':4_000_000_000,'NetworkMode':'none'}},reload=lambda:None,remove=lambda **k:removed.append(k))
  def create(**kw):calls.append(kw);return c
  with tempfile.TemporaryDirectory() as d, patch.object(m,'verified_cleanup',side_effect=lambda cid,rec:removed.append(cid)):
   g=m.ContainerGuard(SimpleNamespace(create=create),pathlib.Path(d)/'limits.json');g.create(image='digest');self.assertEqual(calls[0]['mem_limit'],m.MEM);self.assertEqual(calls[0]['nano_cpus'],4_000_000_000);self.assertTrue(calls[0]['network_disabled']);g.cleanup();self.assertEqual(len(removed),1)
   with self.assertRaises(RuntimeError):g.create(image='digest')
 def test_authorization_requires_true(self):
  with patch.object(m,'load',return_value={'authorized':False,'plan_sha256':'hash'}),patch.object(m,'sha',return_value='hash'):
   with self.assertRaises(RuntimeError):m.authorized({})
 def test_budget_duplicate_rejected(self):
  plan=m.load(p.with_name('execution-plan.json'));plan['controls'][1]=plan['controls'][0].copy()
  with self.assertRaises(RuntimeError):m.validate_plan(plan)
 def test_changed_timeout_rejected(self):
  plan=m.load(p.with_name('execution-plan.json'));plan['limits']['outer_seconds']=901
  with self.assertRaises(RuntimeError):m.validate_plan(plan)
 def test_worker_replay_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   f=pathlib.Path(d)/'start.json';m.claim_worker(f,0,'hash')
   with self.assertRaises(FileExistsError):m.claim_worker(f,0,'hash')
 def test_cleanup_failure_propagates(self):
  c=SimpleNamespace(id='mock')
  g=m.ContainerGuard(None,'unused');g.created=[c]
  with patch.object(m,'verified_cleanup',side_effect=RuntimeError('unverified')):
   with self.assertRaises(RuntimeError):g.cleanup()
 def test_cleanup_requires_confirmed_absence(self):
  with tempfile.TemporaryDirectory() as d, patch.object(m.subprocess,'run',side_effect=[SimpleNamespace(returncode=0),SimpleNamespace(returncode=1,stderr=b'daemon unavailable')]):
   with self.assertRaises(RuntimeError):m.verified_cleanup('mock',pathlib.Path(d)/'cleanup.json')
 def test_api_build_pull_blocked(self):
  api=m.APIGuard(SimpleNamespace(inspect_image=lambda x:'inspected'))
  for method in ['build','pull','import_image','load_image','commit']:
   with self.assertRaises(RuntimeError):getattr(api,method)
  self.assertEqual(api.inspect_image('digest'),'inspected')
 def test_client_api_is_guarded(self):
  client=m.ClientGuard(SimpleNamespace(api=SimpleNamespace(build=lambda:None),images=None,containers=None),'unused')
  with self.assertRaises(RuntimeError):client.api.build()
  with self.assertRaises(RuntimeError):client.images.build()
 def test_checks_both_actual_filesystems(self):
  seen=[]
  with patch.object(m,'image_bytes',return_value=0),patch.object(m.shutil,'disk_usage',side_effect=lambda path:seen.append(path) or SimpleNamespace(free=m.FREE)):
   m.disk_checks({'docker_root_dir':'/image-store','artifact_filesystem_path':'/private-store'},0)
  self.assertEqual(seen,['/image-store','/private-store'])
 def test_no_implicit_pull(self):
  with self.assertRaises(RuntimeError):m.ImageGuard(None).pull('image')
 def test_disk_stop(self):
  for initial,current,free in [(0,m.GROWTH+1,m.FREE),(0,0,m.FREE-1)]:
   with self.assertRaises(RuntimeError):m.disk_guard(initial,current,free)
 def test_failed_limits_cleanup(self):
  removed=[];c=SimpleNamespace(id='mock',attrs={'HostConfig':{'Memory':1,'NanoCpus':4_000_000_000,'NetworkMode':'none'}},reload=lambda:None,remove=lambda **k:removed.append(k))
  with tempfile.TemporaryDirectory() as d, patch.object(m,'verified_cleanup',side_effect=lambda cid,rec:removed.append(cid)):
   g=m.ContainerGuard(SimpleNamespace(create=lambda **kw:c),pathlib.Path(d)/'limits.json')
   with self.assertRaises(RuntimeError):g.create(image='digest')
   self.assertEqual(len(removed),1)
if __name__=='__main__':unittest.main()
