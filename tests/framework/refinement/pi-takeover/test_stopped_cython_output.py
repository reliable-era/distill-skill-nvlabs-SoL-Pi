import unittest
from stopped_cython_output import classify,PATHS
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def proof(self,*indices):return {p:i in indices for i,p in enumerate(PATHS)}
 def test_absent_source_only(self):
  r=classify('A /app/pyknotid\nA /app/pyknotid/setup.py',self.proof());self.assertEqual(r['output_state'],'absent');self.assertFalse(r['cost_eligibility']);self.assertTrue(r['source_transfer_pending'])
 def test_normal(self):self.assertEqual(classify('A '+PATHS[0]+'\nA '+PATHS[1],self.proof(0,1))['dynamic']['layout'],'normal')
 def test_editable(self):self.assertEqual(classify('\n'.join('A '+PATHS[i] for i in [0,2,3]),self.proof(0,2,3))['dynamic']['layout'],'editable')
 def test_unknown_version_not_absent(self):self.assertRaises(CaptureError,classify,'A '+PATHS[0].replace('0.5.3','0.5.4'),self.proof())
 def test_user_install_not_absent(self):self.assertRaises(CaptureError,classify,'A /root/.local/lib/python3.13/site-packages/pyknotid',self.proof())
 def test_ambiguous(self):self.assertRaises(CaptureError,classify,'\n'.join('A '+p for p in PATHS),self.proof(0,1,2,3))
 def test_contradiction(self):self.assertRaises(CaptureError,classify,'A '+PATHS[0]+'\nA '+PATHS[1],self.proof(0,1,2))
 def test_incomplete(self):self.assertRaises(CaptureError,classify,'',{})
 def test_malformed(self):self.assertRaises(CaptureError,classify,'invalid',self.proof())
if __name__=='__main__':unittest.main()
