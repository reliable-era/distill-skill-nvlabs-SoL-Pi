import io,pathlib,tarfile,tempfile,unittest
from directory_capture import capture_directory
from artifact_capture import CaptureError

def archive(items):
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode='w') as t:
  for name,kind,data in items:
   m=tarfile.TarInfo(name);m.type=kind;m.linkname='/etc/passwd';m.size=len(data) if kind==tarfile.REGTYPE else 0;t.addfile(m,io.BytesIO(data) if kind==tarfile.REGTYPE else None)
 b.seek(0);return b
D=tarfile.DIRTYPE;F=tarfile.REGTYPE
class DirectoryTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.out=pathlib.Path(self.tmp.name)/'capture'
 def tearDown(self):self.tmp.cleanup()
 def test_nested(self):x=capture_directory(archive([('documents',D,b''),('documents/sub/a',F,b'abc')]),self.out,'documents');self.assertEqual(x['bytes'],3);self.assertEqual((self.out/'sub/a').read_bytes(),b'abc')
 def test_empty_directory(self):self.assertEqual(capture_directory(archive([('./documents/',D,b'')]),self.out,'documents')['files'],{})
 def test_unsafe(self):
  for name,kind in [('documents/../outside',F),('/documents/a',F),('other/a',F),('documents/link',tarfile.SYMTYPE),('documents/link',tarfile.LNKTYPE),('documents/device',tarfile.CHRTYPE)]:
   with self.subTest(name=name),self.assertRaises(CaptureError):capture_directory(archive([('documents',D,b''),(name,kind,b'x')]),self.out,'documents')
   self.assertFalse(self.out.exists())
 def test_duplicate(self):
  with self.assertRaises(CaptureError):capture_directory(archive([('documents',D,b''),('documents/a',F,b'x'),('documents/a',F,b'y')]),self.out,'documents')
  self.assertFalse(self.out.exists())
 def test_bounds(self):
  with self.assertRaises(CaptureError):capture_directory(archive([('documents',D,b''),('documents/a',F,b'123')]),self.out,'documents',max_bytes=2)
  self.assertFalse(self.out.exists())
 def test_entries(self):
  with self.assertRaises(CaptureError):capture_directory(archive([('documents',D,b''),('documents/a',F,b'x')]),self.out,'documents',max_entries=1)
 def test_missing_root(self):
  with self.assertRaises(CaptureError):capture_directory(archive([('documents/a',F,b'x')]),self.out,'documents')
 def test_truncated_rollback(self):
  b=archive([('documents',D,b''),('documents/a',F,b'abc')]).getvalue()[:1026]
  with self.assertRaises(tarfile.ReadError):capture_directory(io.BytesIO(b),self.out,'documents')
  self.assertFalse(self.out.exists())
 def test_existing_preserved(self):
  self.out.mkdir();(self.out/'keep').write_text('keep')
  with self.assertRaises(CaptureError):capture_directory(archive([]),self.out,'documents')
  self.assertEqual((self.out/'keep').read_text(),'keep')
if __name__=='__main__':unittest.main()
