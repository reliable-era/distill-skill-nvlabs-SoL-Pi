import unittest,tempfile,pathlib,json
from unittest.mock import patch
import run_diagnostic as r
class Evidence(unittest.TestCase):
 def test_log_cap_and_state(self):
  class C:
   id='owned';attrs={'State':{'Status':'exited','Running':False,'ExitCode':1,'OOMKilled':False,'Error':'boot error'}}
   def reload(self):pass
   def logs(self,**kwargs):return iter([b'a'*40000,b'b'*40000,b'never'])
  with tempfile.TemporaryDirectory() as d:
   result=r.capture(C(),pathlib.Path(d));self.assertEqual(result['log_bytes'],65536);self.assertEqual(result['state']['ExitCode'],1);self.assertTrue(result['truncated_or_at_cap']);self.assertEqual((pathlib.Path(d)/'private-listener.log').stat().st_size,65536)
 def test_log_failure_retains_state_not_success(self):
  class C:
   id='owned';attrs={'State':{'ExitCode':2,'OOMKilled':True,'Error':'failure'}}
   def reload(self):pass
   def logs(self,**kwargs):raise RuntimeError('unavailable')
  with tempfile.TemporaryDirectory() as d:
   result=r.capture(C(),pathlib.Path(d));self.assertEqual(result['status'],'capture_failed');self.assertEqual(result['state']['ExitCode'],2);self.assertTrue(result['state']['OOMKilled'])
 def test_cleanup_ambiguous_absence_rejected(self):
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory() as d,patch.object(r.subprocess,'run',side_effect=[SimpleNamespace(returncode=0),SimpleNamespace(returncode=1,stderr=b'No such object; daemon unavailable')]):
   with self.assertRaises(AssertionError):r.cleanup('owned',pathlib.Path(d))
   self.assertFalse(json.loads((pathlib.Path(d)/'cleanup.json').read_text())['absence_verified'])
 def test_listener_source_logged_before_gunicorn(self):
  s=(r.OUT/'listener.sh').read_text();self.assertLess(s.index('authentic_import'),s.index('gunicorn --workers'));self.assertIn('source_path',s);self.assertIn('core_sha256',s)
if __name__=='__main__':unittest.main()
