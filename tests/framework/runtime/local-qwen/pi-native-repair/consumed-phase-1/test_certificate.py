import importlib.util,pathlib,json,copy,unittest
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('runner',R/'run_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Certificate(unittest.TestCase):
 def setUp(self):
  self.cert=json.loads((R/'plan.json').read_text())['routing_certificate'];self.report=json.loads(pathlib.Path(self.cert['path']).read_text())
 def test_exact_bound_audit(self):self.assertTrue(m.certificate_ok(self.report,self.cert))
 def test_forged_or_malformed(self):
  for mutate in [lambda x:x.update(status='PASS'),lambda x:x.update(plan_sha256='forged'),lambda x:x['evidence'].update(POST=1),lambda x:x['evidence'].update(errors=['failed']),lambda x:x['evidence'].update(broker_socket_absent=False),lambda x:x['actual_container_inspect'][1].update(mounts=[{'destination':'/broker'}]),lambda x:x['actual_network_inspect'][0].update(gateway_present=True),lambda x:x['actual_container_inspect'][0]['mounts'][1].update(RW=True),lambda x:x['independent_remaining_owned'].update(containers=['live'])]:
   report=copy.deepcopy(self.report);mutate(report);self.assertFalse(m.certificate_ok(report,self.cert))
if __name__=='__main__':unittest.main()
