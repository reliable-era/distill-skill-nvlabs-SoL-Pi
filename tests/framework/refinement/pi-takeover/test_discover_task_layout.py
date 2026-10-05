import unittest
from discover_task_layout import discover_from_diff
from task_artifacts import SITE
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def test_pmars(self):self.assertEqual(discover_from_diff('build-pmars','A /app/pmars-0.9.4\nA /app/pmars-0.9.4/src'),{'source_directory':'/app/pmars-0.9.4'})
 def test_ambiguous_pmars(self):self.assertRaises(CaptureError,discover_from_diff,'build-pmars','A /app/pmars-0.9.4\nA /app/pmars-0.9.5')
 def test_deleted_pmars(self):self.assertRaises(CaptureError,discover_from_diff,'build-pmars','D /app/pmars-0.9.4')
 def test_normal(self):self.assertEqual(discover_from_diff('build-cython-ext','A '+SITE+'/pyknotid-0.5.3.dist-info\nA '+SITE+'/pyknotid')['layout'],'normal')
 def test_editable(self):
  x=discover_from_diff('build-cython-ext','\n'.join('A '+SITE+'/'+p for p in ['pyknotid-0.5.3.dist-info','__editable__.pyknotid-0.5.3.pth','__editable___pyknotid_0_5_3_finder.py']));self.assertEqual(x['layout'],'editable');self.assertEqual(len(x['sidecars']),2)
 def test_missing_linkage(self):self.assertRaises(CaptureError,discover_from_diff,'build-cython-ext','A '+SITE+'/pyknotid-0.5.3.dist-info')
 def test_wrong_distribution(self):self.assertRaises(CaptureError,discover_from_diff,'build-cython-ext','A '+SITE+'/pyknotid-1.0.dist-info')
 def test_ambiguous_layout(self):self.assertRaises(CaptureError,discover_from_diff,'build-cython-ext','\n'.join('A '+SITE+'/'+p for p in ['pyknotid-0.5.3.dist-info','pyknotid','__editable__.pyknotid-0.5.3.pth']))
 def test_malformed(self):self.assertRaises(CaptureError,discover_from_diff,'build-pmars','nonsense')
 def test_fixed_task(self):self.assertEqual(discover_from_diff('regex-log',''),{})
if __name__=='__main__':unittest.main()
