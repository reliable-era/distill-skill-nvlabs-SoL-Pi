import io,pathlib,tarfile,tempfile,unittest
from executable_capture import capture_executable
from artifact_capture import CaptureError
class ExecutableTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.out=pathlib.Path(self.tmp.name)/'binary'
 def tearDown(self):self.tmp.cleanup()
 def stream(self,mode):
  b=io.BytesIO()
  with tarfile.open(fileobj=b,mode='w') as t:
   m=tarfile.TarInfo('pmars');m.mode=mode;m.size=3;t.addfile(m,io.BytesIO(b'ELF'))
  b.seek(0);return b
 def test_exec(self):r=capture_executable(self.stream(0o755),self.out,'pmars',3);self.assertTrue(r['source_executable']);self.assertEqual(self.out.stat().st_mode&0o777,0o711)
 def test_nonexec_not_repaired(self):r=capture_executable(self.stream(0o644),self.out,'pmars',3);self.assertFalse(r['source_executable']);self.assertEqual(self.out.stat().st_mode&0o777,0o600)
 def test_setuid_stripped(self):r=capture_executable(self.stream(0o4755),self.out,'pmars',3);self.assertEqual(r['source_mode'],0o755);self.assertFalse(self.out.stat().st_mode&0o4000)
 def test_oversized_archive(self):
  with self.assertRaises(CaptureError):capture_executable(io.BytesIO(b'x'*65538),self.out,'pmars',1)
 def test_wrong_name(self):
  with self.assertRaises(CaptureError):capture_executable(self.stream(0o755),self.out,'other',3)
  self.assertFalse(self.out.exists())
if __name__=='__main__':unittest.main()
