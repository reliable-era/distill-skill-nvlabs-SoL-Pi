import pathlib,json,importlib.util,unittest,copy
p=pathlib.Path(__file__).with_name('run_readiness.py');s=importlib.util.spec_from_file_location('ready',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_hard_budget(self):
  plan=json.loads(p.with_name('plan.json').read_text());m.budget_guard(plan);plan['maximum_pulls']=2
  with self.assertRaises(AssertionError):m.budget_guard(plan)
 def test_source_contract_has_no_listener(self):
  plan=json.loads(p.with_name('plan.json').read_text());code=plan['metadata_entrypoint'][2];compile(code,'metadata','exec');self.assertNotIn('app.run(',code);self.assertIn('core_sha256',code);self.assertIn("gunicorn.__version__=='19.9.0'",code)
 def test_result_gate_rejects_failed_observations(self):
  plan=json.loads(p.with_name('plan.json').read_text());app={'stage':'app','python':'3.6.9','gunicorn':'19.9.0','app_source':'/fixture/httpbin/core.py','core_sha256':plan['core_source_sha256'],'ssl_settings_present':True};record={'worker-result':{'exit_code':0},'caps':plan['caps'],'cleanup':{'absence_verified':True},'mount-environment':{k:True for k in ['readonly_source_verified','pythonpath_verified','sensitive_env_keys_absent','verified_before_execution']},'metadata':[app]};m.result_gate(record,plan)
  for key,value in [('worker-result',{'exit_code':1}),('caps',{}),('cleanup',{'absence_verified':False}),('metadata',[])]:
   bad=copy.deepcopy(record);bad[key]=value
   with self.assertRaises(RuntimeError):m.result_gate(bad,plan)
  for field in ['app_source','core_sha256']:
   bad=copy.deepcopy(record);bad['metadata'][0][field]='wrong'
   with self.assertRaises(RuntimeError):m.result_gate(bad,plan)
  bad=copy.deepcopy(record);bad['mount-environment']['sensitive_env_keys_absent']=False
  with self.assertRaises(RuntimeError):m.result_gate(bad,plan)
if __name__=='__main__':unittest.main()
