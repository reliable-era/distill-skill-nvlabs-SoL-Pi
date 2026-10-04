import importlib.util,pathlib,json,unittest
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('native',R/'codex_native_mock.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Safety(unittest.TestCase):
 def test_home_directory_created_before_exec(self):
  import tempfile,subprocess,os
  with tempfile.TemporaryDirectory() as tmp:
   home=pathlib.Path(tmp)/'home'/'.codex'
   result=subprocess.run(m.home_exec(['/bin/sh','-c','test -d "$CODEX_HOME" && printf ready']),env={'CODEX_HOME':str(home),'PATH':'/usr/bin:/bin'},capture_output=True,text=True,timeout=3)
   self.assertEqual(result.returncode,0);self.assertEqual(result.stdout,'ready');self.assertTrue(home.is_dir());self.assertEqual(list(home.iterdir()),[])
 def test_cap(self):
  p=json.loads((R/'codex-native-mock-plan.json').read_text());p['maximum_native_starts']=3
  with self.assertRaises(ValueError):m.validate(p)
 def test_no_real_provider(self):
  p=json.loads((R/'codex-native-mock-plan.json').read_text());p['provider_config']['model_providers.mock.base_url']='https://api.openai.com/v1'
  with self.assertRaises(ValueError):m.validate(p)
 def test_cleanup_guard(self):
  import subprocess
  with self.assertRaises(RuntimeError):m.cleanup_guard(subprocess.CompletedProcess([],1))
 def test_exact_receipts(self):
  self.assertFalse(m.receipt_ok(0,[{'method':'GET','path':'/v1/responses'}],''))
  self.assertTrue(m.receipt_ok(0,[{'method':'POST','path':'/v1/responses'}],''))
  self.assertFalse(m.receipt_ok(1,[],'configuration rejected'))
  self.assertTrue(m.receipt_ok(1,[],'HTTP403 destination denied'))
 def test_explicit_container_absence(self):
  import subprocess
  self.assertTrue(m.absence_verified(subprocess.CompletedProcess([],1,stderr=b'Error: No such object: owned-fixture'),'owned-fixture'))
  self.assertFalse(m.absence_verified(subprocess.CompletedProcess([],1,stderr=b'Cannot connect to Docker daemon'),'owned-fixture'))
  self.assertFalse(m.absence_verified(subprocess.CompletedProcess([],0,stderr=b''),'owned-fixture'))
 def test_network_absence_variants(self):
  import subprocess
  self.assertTrue(m.network_absence_verified(subprocess.CompletedProcess([],1,stderr='Error response from daemon: network owned-fixture not found'),'owned-fixture'))
  self.assertTrue(m.network_absence_verified(subprocess.CompletedProcess([],1,stderr='Error: No such network: owned-fixture'),'owned-fixture'))
  self.assertFalse(m.network_absence_verified(subprocess.CompletedProcess([],1,stderr='Cannot connect to Docker daemon'),'owned-fixture'))
 def test_topology(self):
  import copy
  actor={'Internal':True,'EnableIPv6':False,'Options':{'com.docker.network.bridge.gateway_mode_ipv4':'isolated'},'IPAM':{'Config':[{'Subnet':'192.0.2.0/24'}]}}
  provider={'Internal':True,'EnableIPv6':False}
  self.assertTrue(m.topology_ok(actor,provider))
  bad=copy.deepcopy(actor);bad['IPAM']['Config'][0]['Gateway']='192.0.2.1';self.assertFalse(m.topology_ok(bad,provider))
  bad=copy.deepcopy(actor);bad['EnableIPv6']=True;self.assertFalse(m.topology_ok(bad,provider))
  bad=copy.deepcopy(provider);bad['Internal']=False;self.assertFalse(m.topology_ok(actor,bad))
 def test_bypass_failures_not_certified(self):
  self.assertTrue(m.probe_ok({'direct_ip_blocked':True,'nonallowed_denied':True,'connect_denied':True}))
  self.assertFalse(m.probe_ok({'direct_ip_blocked':False,'nonallowed_denied':True,'connect_denied':True}))
  self.assertFalse(m.probe_ok({'direct_ip_blocked':True,'nonallowed_denied':False,'connect_denied':True}))
 def test_denied_receipt_requires_denial_body(self):
  self.assertFalse(m.receipt_ok(1,[],'unrelated code403'))
 def test_deadline_exhaustion(self):
  from unittest.mock import patch
  with patch.object(m.time,'monotonic',return_value=31):
   with self.assertRaises(TimeoutError):m.remaining(30,15)
  with patch.object(m.time,'monotonic',return_value=29):self.assertEqual(m.remaining(30,15),1)
 def test_unsafe_control_route(self):
  p=json.loads((R/'codex-native-mock-plan.json').read_text());p['controls'][1]['base_url']='https://api.openai.com/v1'
  with self.assertRaises(ValueError):m.validate(p)
 def test_primary_preflight_error_persisted(self):
  from unittest.mock import patch
  import sys,uuid,shutil
  token='offline-unit-'+uuid.uuid4().hex;private=pathlib.Path('/tmp')/('solpi-codexmock-'+token)
  try:
   with patch.object(sys,'argv',['fixture','--execute-mock-only','--plan-sha256',token]),patch.object(m,'sha',return_value=token),patch.object(m,'validate'),patch.object(m.subprocess,'check_output',side_effect=RuntimeError('offline metadata failure')):
    with self.assertRaisesRegex(RuntimeError,'durable private errors'):m.main()
   evidence=json.loads((private/'final-evidence.json').read_text());self.assertEqual(evidence['native_starts'],0);self.assertEqual(evidence['errors'][0]['phase'],'primary');self.assertEqual(evidence['errors'][0]['message'],'offline metadata failure')
  finally:shutil.rmtree(private,ignore_errors=True)
if __name__=='__main__':unittest.main()
