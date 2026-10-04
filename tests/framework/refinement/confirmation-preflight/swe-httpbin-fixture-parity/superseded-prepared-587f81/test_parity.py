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
  with self.assertRaises(AssertionError):r.verify(C(),{'memory':512,'nano_cpus':1},[])
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
 def test_readonly_and_secret_gate(self):
  class C:
   attrs={'HostConfig':{'Memory':512,'NanoCpus':1,'PortBindings':{}},'Config':{'Env':['BUGSNAG_API_KEY=value']},'NetworkSettings':{'Networks':{'owned':{}}},'Mounts':[{'Destination':'/certs','RW':False}]}
   def reload(self):pass
  with self.assertRaises(AssertionError):r.verify(C(),{'memory':512,'nano_cpus':1},['/certs'])
  C.attrs['Config']['Env']=[];C.attrs['Mounts'][0]['RW']=True
  with self.assertRaises(AssertionError):r.verify(C(),{'memory':512,'nano_cpus':1},['/certs'])
if __name__=='__main__':unittest.main()
