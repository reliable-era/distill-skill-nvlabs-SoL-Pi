import os,pathlib,tarfile,tempfile,unittest
from source_archive import archive_source
class SourceArchiveTests(unittest.TestCase):
 def test_uid0_preserves_bytes_modes_and_links(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);source=root/'work';source.mkdir();file=source/'executable';file.write_bytes(b'unchanged source\x00\n');file.chmod(0o751);(source/'link').symlink_to('executable');archive_source(source,root/'source.tar')
   with tarfile.open(root/'source.tar') as tar:
    members=tar.getmembers();self.assertTrue(all(m.uid==m.gid==0 for m in members));self.assertEqual(tar.extractfile('testbed/executable').read(),file.read_bytes());self.assertEqual(tar.getmember('testbed/executable').mode,0o751);self.assertEqual(tar.getmember('testbed/link').linkname,'executable')
   self.assertEqual(file.stat().st_mode&0o777,0o751)
if __name__=='__main__':unittest.main()
