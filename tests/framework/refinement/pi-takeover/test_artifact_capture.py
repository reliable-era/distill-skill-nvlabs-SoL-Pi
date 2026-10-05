import io,pathlib,tarfile,tempfile,unittest
from artifact_capture import capture_file,CaptureError

def stream(entries):
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode='w') as t:
  for name,data,kind in entries:
   m=tarfile.TarInfo(name);m.type=kind;m.size=len(data) if kind==tarfile.REGTYPE else 0;m.linkname='/etc/passwd';t.addfile(m,io.BytesIO(data) if kind==tarfile.REGTYPE else None)
 b.seek(0);return b
class CaptureTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.out=pathlib.Path(self.tmp.name)/'payload'
 def tearDown(self):self.tmp.cleanup()
 def test_valid(self):self.assertEqual(capture_file(stream([('./regex.txt',b'abc',tarfile.REGTYPE)]),self.out,'regex.txt',3)['bytes'],3);self.assertEqual(self.out.read_bytes(),b'abc')
 def test_empty_file(self):self.assertEqual(capture_file(stream([('regex.txt',b'',tarfile.REGTYPE)]),self.out,'regex.txt',0)['bytes'],0)
 def test_unsafe_members(self):
  for name,kind in [('../regex.txt',tarfile.REGTYPE),('/regex.txt',tarfile.REGTYPE),('regex.txt',tarfile.SYMTYPE),('regex.txt',tarfile.LNKTYPE),('regex.txt',tarfile.DIRTYPE),('regex.txt',tarfile.CHRTYPE)]:
   with self.subTest(name=name,kind=kind),self.assertRaises(CaptureError):capture_file(stream([(name,b'x',kind)]),self.out,'regex.txt',10)
   self.assertFalse(self.out.exists())
 def test_multiple_members_rollback(self):
  with self.assertRaises(CaptureError):capture_file(stream([('regex.txt',b'a',tarfile.REGTYPE),('other',b'b',tarfile.REGTYPE)]),self.out,'regex.txt',10)
  self.assertFalse(self.out.exists())
 def test_oversize(self):
  with self.assertRaises(CaptureError):capture_file(stream([('regex.txt',b'1234',tarfile.REGTYPE)]),self.out,'regex.txt',3)
  self.assertFalse(self.out.exists())
 def test_existing_preserved(self):
  self.out.write_bytes(b'original')
  with self.assertRaises(CaptureError):capture_file(stream([]),self.out,'regex.txt',10)
  self.assertEqual(self.out.read_bytes(),b'original')
 def test_missing(self):
  with self.assertRaises(CaptureError):capture_file(stream([]),self.out,'regex.txt',10)
 def test_truncated_payload_rollback(self):
  b=stream([('regex.txt',b'abc',tarfile.REGTYPE)]).getvalue()[:514]
  with self.assertRaises(tarfile.ReadError):capture_file(io.BytesIO(b),self.out,'regex.txt',10)
  self.assertFalse(self.out.exists())
 def test_bad_contract(self):
  with self.assertRaises(CaptureError):capture_file(stream([]),self.out,'../regex.txt',10)
if __name__=='__main__':unittest.main()
