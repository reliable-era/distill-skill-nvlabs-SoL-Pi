import unittest,json,pathlib,copy
import run_parity as r
class Guards(unittest.TestCase):
 def test_budget(self):
  p=json.loads((r.OUT/'plan.json').read_text());r.guard(p)
  for key in ['maximum_pulls','maximum_graders','maximum_retries']:
   q=copy.deepcopy(p);q[key]=1
   with self.assertRaises(AssertionError):r.guard(q)
 def test_source_contract(self):
  s=(r.OUT/'probe.py').read_text();self.assertIn('COUNT>12',s);self.assertIn("s.trust_env=False",s);self.assertIn('allow_redirects=False',s);self.assertNotIn('verify=False',s)
  l=(r.OUT/'listener.sh').read_text();self.assertIn('--bind 0.0.0.0:443',l);self.assertIn('--worker-class sync',l)
 def test_bad_caps(self):
  class C:
   attrs={'HostConfig':{'Memory':1,'NanoCpus':1},'Config':{'Env':[]},'NetworkSettings':{'Networks':{}}}
   def reload(self):pass
  with self.assertRaises(AssertionError):r.verify(C(),{'memory':512,'nano_cpus':1},{},'owned')
 def test_remote_and_budget_block_before_send(self):
  import importlib.util,requests
  spec=importlib.util.spec_from_file_location('parity_probe',r.OUT/'probe.py');m=importlib.util.module_from_spec(spec)
  original=requests.adapters.HTTPAdapter.send
  try:
   spec.loader.exec_module(m)
   req=requests.Request('GET','http://example.com/get').prepare()
   with self.assertRaises(RuntimeError):m.bounded_send(None,req)
   m.COUNT=12
   req=requests.Request('GET','https://httpbin.org/get').prepare()
   with self.assertRaises(RuntimeError):m.bounded_send(None,req)
  finally:requests.adapters.HTTPAdapter.send=original
 def fixture(self):
  class C:
   attrs={'HostConfig':{'Memory':512,'NanoCpus':1,'PortBindings':{}},'Config':{'Env':[]},'NetworkSettings':{'Networks':{'owned':{}}},'Mounts':[{'Source':'/private/ca.pem','Destination':'/certs/ca.pem','RW':False},{'Source':'/private/output','Destination':'/output','RW':True}]}
   def reload(self):pass
  return C()
 def test_exact_mount_source_mode_and_no_extra_keys(self):
  expected={'/private/ca.pem':('/certs/ca.pem',False),'/private/output':('/output',True)}
  r.verify(self.fixture(),{'memory':512,'nano_cpus':1},expected,'owned')
  for mutation in ['source','mode','extra_key']:
   c=self.fixture();c.attrs=copy.deepcopy(c.attrs)
   if mutation=='source':c.attrs['Mounts'][0]['Source']='/private/ca.key'
   elif mutation=='mode':c.attrs['Mounts'][0]['RW']=True
   else:c.attrs['Mounts'].append({'Source':'/private/ca.key','Destination':'/hidden.key','RW':False})
   with self.assertRaises(AssertionError):r.verify(c,{'memory':512,'nano_cpus':1},expected,'owned')
 def test_wrong_network_and_sensitive_env_rejected(self):
  expected={'/private/ca.pem':('/certs/ca.pem',False),'/private/output':('/output',True)}
  c=self.fixture();c.attrs=copy.deepcopy(c.attrs);c.attrs['NetworkSettings']['Networks']={'external':{}}
  with self.assertRaises(AssertionError):r.verify(c,{'memory':512,'nano_cpus':1},expected,'owned')
  c=self.fixture();c.attrs=copy.deepcopy(c.attrs);c.attrs['Config']['Env']=['BUGSNAG_API_KEY=value']
  with self.assertRaises(AssertionError):r.verify(c,{'memory':512,'nano_cpus':1},expected,'owned')
 def test_cleanup_requires_exact_kind_id(self):
  from types import SimpleNamespace
  ident='a'*64
  good=SimpleNamespace(returncode=1,stderr=('Error response from daemon: No such container: '+ident+'\n').encode())
  self.assertTrue(r.absence(good,'container',ident))
  for stderr in ['Error response from daemon: No such container: wrong','Error: No such object: '+ident,'daemon unavailable; No such container: '+ident]:
   self.assertFalse(r.absence(SimpleNamespace(returncode=1,stderr=stderr.encode()),'container',ident))
  self.assertFalse(r.absence(SimpleNamespace(returncode=0,stderr=good.stderr),'container',ident))
 def test_probe_mount_contains_output_only(self):
  service,probe=r.mount_sets({'source_mount':'/authentic','certificate_root':'/private'},pathlib.Path('/private'))
  self.assertNotIn('/private',probe);self.assertNotIn('/private/ca.key',probe);self.assertNotIn('/private/server.key',probe)
  self.assertEqual(probe['/private/output'],('/output',True));self.assertEqual(service['/private/server.key'],('/certs/server.key',False))
 def test_capture_timeout_is_error_and_bounded(self):
  import tempfile
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   work=pathlib.Path(d);(work/'service.json').write_text('{"id":"owned"}')
   with patch.object(r.subprocess,'run',side_effect=r.subprocess.TimeoutExpired('capture',5)) as call:
    self.assertEqual(r.capture_bounded(work),'capture_TimeoutExpired');self.assertEqual(call.call_args.kwargs['timeout'],5)
 def test_proven_entrypoint_uses_python3(self):
  s=(r.OUT/'listener.sh').read_text();self.assertIn('python3 -u -c',s);self.assertEqual(s.count("python3 -c 'from gunicorn.app.wsgiapp import run;run()'"),2);self.assertNotIn('python3 -m gunicorn',s)
 def network_attrs(self,members):
  return {'Id':'owned-network','Internal':True,'EnableIPv6':False,'Options':{'com.docker.network.bridge.gateway_mode_ipv4':'isolated'},'IPAM':{'Config':[{'Subnet':'private'}]},'Containers':{m:{} for m in members}}
 def test_lifecycle_waiting_probe_attached_before_release(self):
  import tempfile
  class Net:
   def reload(self):pass
  net=Net();net.attrs=self.network_attrs(['service'])
  with tempfile.TemporaryDirectory() as d:
   work=pathlib.Path(d);output=work/'output';output.mkdir()
   attrs=r.snapshot(net,work,'created-probe')
   with self.assertRaises(AssertionError):r.release_http(attrs,'service','probe',output,{'verified':True})
   self.assertFalse((output/'allow-http').exists())
   # Model Docker lifecycle: a started waiting process attaches, but HTTP is
   # still blocked until the host verifies/persists actual membership.
   net.attrs=self.network_attrs(['service','probe']);attrs=r.snapshot(net,work,'waiting-probe')
   self.assertFalse((output/'allow-http').exists());r.release_http(attrs,'service','probe',output,{'verified':True})
   self.assertEqual((output/'allow-http').read_text(),'network-proof-verified\n')
   self.assertTrue((work/'network-state-waiting-probe.json').exists())
   with self.assertRaises(FileExistsError):r.release_http(attrs,'service','probe',output,{'verified':True})
 def test_extra_member_never_releases_gate(self):
  import tempfile
  with tempfile.TemporaryDirectory() as d:
   output=pathlib.Path(d)/'output';output.mkdir()
   with self.assertRaises(AssertionError):r.release_http(self.network_attrs(['service','probe','foreign']),'service','probe',output,{})
   self.assertFalse((output/'allow-http').exists())
 def test_failed_inspect_persists_uncertainty(self):
  import tempfile
  class Net:
   attrs={'Containers':{'stale':{}}}
   def reload(self):raise RuntimeError('inspect unavailable')
  with tempfile.TemporaryDirectory() as d:
   work=pathlib.Path(d)
   with self.assertRaises(RuntimeError):r.snapshot(Net(),work,'failure')
   record=json.loads((work/'network-state-failure.json').read_text());self.assertEqual(record['inspection_error'],'RuntimeError')
if __name__=='__main__':unittest.main()
