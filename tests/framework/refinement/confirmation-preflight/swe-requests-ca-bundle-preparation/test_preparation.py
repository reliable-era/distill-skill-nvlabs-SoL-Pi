import unittest,json,pathlib,hashlib,copy
import run_preparation as r
class MetadataScope(unittest.TestCase):
 def test_zero_HTTP_and_no_tests_or_packages(self):
  root=pathlib.Path(__file__).resolve().parent;source=(root/'probe.py').read_text()
  self.assertNotIn('requests.get(',source);self.assertNotIn('Session(',source);self.assertNotIn('pip ',source);self.assertNotIn('pytest',source);self.assertIn('DEFAULT_CA_BUNDLE_PATH',source);self.assertIn('total>1048576',source)
 def test_frozen_consumed_phase(self):
  p=json.loads((pathlib.Path(__file__).resolve().parent/'plan.json').read_text())
  for f,h in p['preserved_consumed_phase'].items():self.assertEqual(hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),h)
 def test_caps_scope(self):
  p=json.loads((pathlib.Path(__file__).resolve().parent/'plan.json').read_text());self.assertTrue(p['caps']['read_only']);self.assertEqual(p['caps']['network_mode'],'none');self.assertEqual(p['probe_seconds'],10);self.assertEqual(p['future_control_plan_required']['combined_cap'],14)
 def test_actual_trust_facts_all_required(self):
  metadata={'requests_version':'2.3.0','extracted_bytes':100,'facts':{'send_defaults_to_self_verify':True,'send_merges_CA_environment':False,'request_merges_CA_environment':True,'adapter_uses_default_CA':True},'records':{key:{'path':'/actual/'+key,'sha256':'a'*64,'bytes':25} for key in ['sessions','adapters','certs','default_CA']}}
  metadata['records']['default_CA']['PEM_certificate_count']=1;r.metadata_gate(metadata)
  for key in metadata['facts']:
   wrong=copy.deepcopy(metadata);wrong['facts'][key]=not wrong['facts'][key]
   with self.assertRaises(RuntimeError):r.metadata_gate(wrong)
  wrong=copy.deepcopy(metadata);wrong['extracted_bytes']=1048577
  with self.assertRaises(RuntimeError):r.metadata_gate(wrong)
if __name__=='__main__':unittest.main()
