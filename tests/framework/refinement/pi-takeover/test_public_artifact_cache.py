import hashlib,pathlib,tempfile,unittest
from public_artifact_cache import verify_artifact_directory
class Tests(unittest.TestCase):
 def fixture(self,r):
  (r/'source.tar').write_bytes(b'original');return {'source.tar':{'bytes':8,'sha256':hashlib.sha256(b'original').hexdigest()}}
 def test_valid(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);self.assertEqual(verify_artifact_directory(r,m)['files'],1)
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);(r/'source.tar').write_bytes(b'changed');self.assertRaises(ValueError,verify_artifact_directory,r,m)
 def test_unmanifested(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);(r/'target.deb').write_bytes(b'notallowed');self.assertRaises(ValueError,verify_artifact_directory,r,m)
 def test_missing(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);(r/'source.tar').unlink();self.assertRaises(ValueError,verify_artifact_directory,r,m)
 def test_link(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);(r/'source.tar').unlink();(r/'source.tar').symlink_to('/etc/passwd');self.assertRaises(ValueError,verify_artifact_directory,r,m)
 def test_apt_bookkeeping(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);m=self.fixture(r);(r/'lock').touch();(r/'partial').mkdir();self.assertTrue(verify_artifact_directory(r,m,True)['verified']);(r/'partial/missing.deb').write_bytes(b'bad');self.assertRaises(ValueError,verify_artifact_directory,r,m,True)
 def test_path_injection(self):
  with tempfile.TemporaryDirectory() as d:self.assertRaises(ValueError,verify_artifact_directory,d,{'../x':{}})
if __name__=='__main__':unittest.main()
