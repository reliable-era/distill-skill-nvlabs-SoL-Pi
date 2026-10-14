"""Offline-only G5 protocol checks; no model, container or network calls."""
import pathlib,unittest
from common import H,image_tag
from native import CONFIG,argv
from transport import usage_from_sse
from images import FLOOR,RESERVE
class Protocol(unittest.TestCase):
 def test_idle_timeout_and_no_hidden_retries(self):
  self.assertEqual(CONFIG['model_providers.local.stream_idle_timeout_ms'],1800000);self.assertEqual(CONFIG['model_providers.local.stream_max_retries'],0);self.assertEqual(CONFIG['model_providers.local.request_max_retries'],0);self.assertIn('--ignore-user-config',argv('fixture'))
 def test_plain_client_source(self):
  for name in ('run_swe_cell.py','transport.py','native.py'):
   text=(H/name).read_text();self.assertNotIn('metadata(',text);self.assertNotIn('waiting_zero(',text);self.assertNotIn('/get_load',text);self.assertNotIn('/v1/models',text)
 def test_official_image_tag(self):self.assertEqual(image_tag('django__django-123'),'swebench/sweb.eval.x86_64.django_1776_django-123:latest')
 def test_storage_floor(self):self.assertEqual(FLOOR,300_000_000_000);self.assertGreater(RESERVE,0)
 def test_missing_usage_stays_unknown(self):
  r=usage_from_sse(b'',False);self.assertFalse(r['cost_complete']);self.assertIsNone(r['usage']);self.assertIsNone(r['response_model']);self.assertEqual(r['tokens_lower_bound'],0)
 def test_data_filter_and_caps_kept(self):
  text=(H/'run_swe_cell.py').read_text();self.assertIn("filter='data'",text);self.assertIn('16384 output tokens',text);self.assertIn('started+7200',text)
if __name__=='__main__':unittest.main()
