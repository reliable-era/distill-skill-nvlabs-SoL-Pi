import unittest,tempfile,pathlib,json,copy
from unittest.mock import patch
import run_controls as r
class Guards(unittest.TestCase):
 def test_fixed_two_controls_and_no_pulls(self):
  p=r.load(r.OUT/'execution-plan.json');r.validate_plan(p)
  for key in ['maximum_controls','maximum_pulls','maximum_builds']:
   q=copy.deepcopy(p);q[key]+=1
   with self.assertRaises(RuntimeError):r.validate_plan(q)
 def test_exact_cleanup_error(self):
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory() as d,patch.object(r.subprocess,'run',side_effect=[SimpleNamespace(returncode=0),SimpleNamespace(returncode=1,stderr=b'No such object; daemon unavailable')]):
   with self.assertRaises(RuntimeError):r.verified_cleanup('owned',pathlib.Path(d)/'cleanup.json')
 def test_started_membership_verified_before_test(self):
  import docker
  class Inner:
   id='grader'
   def start(self):self.started=True
  class Net:
   attrs={'Id':'network','Internal':True,'EnableIPv6':False,'Options':{'com.docker.network.bridge.gateway_mode_ipv4':'isolated'},'IPAM':{'Config':[]},'Containers':{'service':{},'grader':{}}}
   def reload(self):pass
  class Client:
   class Networks:
    def get(self,ident):return Net()
   networks=Networks()
   class Containers:
    def get(self,ident):
     class Service:
      attrs={'State':{'Running':True}};status='running'
      def reload(self):pass
     return Service()
   containers=Containers()
   def close(self):pass
  with tempfile.TemporaryDirectory() as d,patch.object(r,'PRIVATE',pathlib.Path(d)),patch.object(docker,'from_env',return_value=Client()):
   r.dump(pathlib.Path(d)/'fixture.json',{'service_id':'service','network_id':'network'});record=pathlib.Path(d)/'limits.json';r.dump(record,{'verified_before_test':False});inner=Inner();r.TrustedContainer(inner,record).start();self.assertTrue(r.load(record)['verified_before_test']);self.assertTrue((pathlib.Path(d)/'network-state-before-test.json').exists())
   Net.attrs=copy.deepcopy(Net.attrs);Net.attrs['Containers']['foreign']={};r.dump(record,{'verified_before_test':False})
   with self.assertRaises(AssertionError):r.TrustedContainer(Inner(),record).start()
   self.assertFalse(r.load(record)['verified_before_test']);self.assertIn('foreign',r.load(pathlib.Path(d)/'network-state-before-test.json')['Containers'])
 def test_incomplete_negative_not_accepted(self):
  row={'patch_is_None':False,'patch_exists':True,'patch_successfully_applied':True,'resolved':False,'infra_failure':False,'tests_status':{'FAIL_TO_PASS':{'success':[],'failure':['f']},'PASS_TO_PASS':{'success':['p'],'failure':[]}}}
  resolve=lambda x,m:x if x in m else None
  r.control_grade_gate({'task':row},'task','unchanged',{'f':'FAILED','p':'PASSED'},['f'],['p'],resolve,None)
  row['infra_failure']=True
  with self.assertRaises(RuntimeError):r.control_grade_gate({'task':row},'task','unchanged',{'f':'FAILED','p':'PASSED'},['f'],['p'],resolve,None)
 def test_no_build_api(self):
  for name in ['build','pull','load_image','commit']:
   with self.assertRaises(RuntimeError):getattr(r.APIGuard(object()),name)
 def test_ca_mount_mismatch_rejected_before_start(self):
  class Container:
   id='grader'
   def reload(self):pass
  class Inner:
   def __init__(self,source,rw):self.source=source;self.rw=rw
   def create(self,*a,**kw):
    c=Container();c.attrs={'HostConfig':{'Memory':r.MEM,'NanoCpus':4000000000,'NetworkMode':'owned','PortBindings':{}},'Config':{'NetworkDisabled':False,'Env':['REQUESTS_CA_BUNDLE=/certs/ca.pem']},'Mounts':[{'Source':self.source,'Destination':'/certs/ca.pem','RW':self.rw}]};return c
  plan=r.load(r.OUT/'execution-plan.json');ca=str(pathlib.Path(plan['fixture']['certificate_root'])/'ca.pem')
  with tempfile.TemporaryDirectory() as d,patch.object(r,'PRIVATE',pathlib.Path(d)):
   r.dump(pathlib.Path(d)/'fixture.json',{'network_name':'owned'})
   for source,rw in [(ca.replace('ca.pem','ca.key'),False),(ca,True)]:
    guard=r.ContainerGuard(Inner(source,rw),pathlib.Path(d)/'record.json')
    with self.assertRaises(AssertionError):guard.create(image=plan['images'][0])
 def test_combined_attempt_cap_cannot_expand(self):
  plan=r.load(r.OUT/'execution-plan.json');plan['combined_budget']['combined_maximum_control_attempts']=15
  with self.assertRaises(RuntimeError):r.validate_plan(plan)
 def test_timeout_records_owned_session_before_group_drain(self):
  from unittest.mock import MagicMock
  fake=MagicMock();fake.pid=444999;fake.wait.side_effect=[r.subprocess.TimeoutExpired('worker',1),0]
  with tempfile.TemporaryDirectory() as d,patch.object(r.subprocess,'Popen',return_value=fake) as spawn,patch.object(r,'process_start',return_value='birth'):
   record=pathlib.Path(d)/'worker-process.json'
   def drain(path):self.assertEqual(r.load(path)['pgid'],444999);self.assertEqual(r.load(path)['starttime'],'birth')
   with patch.object(r,'bounded_terminal',side_effect=drain) as stop:
    with self.assertRaises(r.subprocess.TimeoutExpired):r.owned_run(['fixed-worker'],pathlib.Path(d)/'private.log',1,record)
    self.assertTrue(spawn.call_args.kwargs['start_new_session']);stop.assert_called_once()
 def test_live_group_terminated_before_terminal_proof(self):
  ident=444999;row={'pid':ident,'pgid':ident,'sid':ident,'state':'S'};record={'pid':ident,'pgid':ident,'sid':ident,'starttime':'birth'}
  with tempfile.TemporaryDirectory() as d,patch.object(r,'process_start',return_value='birth'),patch.object(r,'group_members',side_effect=[[row],[],[],[]]),patch.object(r.os,'killpg') as kill:
   proof=pathlib.Path(d)/'proof.json';r.terminal_group(record,proof);self.assertTrue(r.load(proof)['terminal']);kill.assert_called_once_with(ident,r.signal.SIGTERM)
 def test_reused_pid_not_signaled(self):
  ident=444999;record={'pid':ident,'pgid':ident,'sid':ident,'starttime':'original'}
  with tempfile.TemporaryDirectory() as d,patch.object(r,'process_start',return_value='different'),patch.object(r.os,'killpg') as kill:
   proof=pathlib.Path(d)/'proof.json'
   with self.assertRaises(RuntimeError):r.terminal_group(record,proof)
   self.assertFalse(r.load(proof)['terminal']);kill.assert_not_called()
 def test_original_CA_prefix_preserved_and_only_public_CA_added(self):
  plan=r.load(r.OUT/'execution-plan.json');r.verify_merged_CA(plan)
  original=pathlib.Path(plan['merged_CA_bundle']['original_source_path']).read_bytes();merged=pathlib.Path(plan['merged_CA_bundle']['private_path']).read_bytes()
  self.assertTrue(merged.startswith(original));self.assertEqual(merged.count(b'-----BEGIN CERTIFICATE-----'),150)
  wrong=copy.deepcopy(plan);wrong['merged_CA_bundle']['readonly_grader_destination']='/wrong/ca.pem'
  with self.assertRaises(RuntimeError):r.verify_merged_CA(wrong)
 def test_valid_grader_gets_exact_two_RO_CA_mounts(self):
  class C:
   id='grader'
   def reload(self):pass
  class Inner:
   def create(self,*a,**kw):
    c=C();c.attrs={'HostConfig':{'Memory':r.MEM,'NanoCpus':4000000000,'NetworkMode':'owned','PortBindings':{}},'Config':{'NetworkDisabled':False,'Env':['REQUESTS_CA_BUNDLE=/certs/ca.pem']},'Mounts':[{'Source':src,'Destination':v['bind'],'RW':v['mode']=='rw'} for src,v in kw['volumes'].items()]};return c
  plan=r.load(r.OUT/'execution-plan.json')
  with tempfile.TemporaryDirectory() as d,patch.object(r,'PRIVATE',pathlib.Path(d)):
   r.dump(pathlib.Path(d)/'fixture.json',{'network_name':'owned'});record=pathlib.Path(d)/'record.json'
   c=r.ContainerGuard(Inner(),record).create(image=plan['images'][0]);self.assertEqual(len(c.attrs['Mounts']),2);self.assertTrue(all(not m['RW'] for m in c.attrs['Mounts']));self.assertTrue(r.load(record)['readonly_merged_default_CA_verified'])
if __name__=='__main__':unittest.main()
