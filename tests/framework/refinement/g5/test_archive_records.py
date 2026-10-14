import pathlib,tarfile,tempfile,unittest
from archive_records import compress
class ArchiveRecords(unittest.TestCase):
 def test_completed_bytes_modes_links_verified_before_owned_removal(self):
  with tempfile.TemporaryDirectory(prefix='solpi-g5-test-') as t:
   root=pathlib.Path(t);d=root/'completed';d.mkdir();(d/'file').write_bytes(b'\x00\xffraw trace');(d/'file').chmod(0o755);(d/'link').symlink_to('file');proof=compress(d,root/'archives',root);self.assertFalse(d.exists());self.assertTrue(proof['all_regular_bytes_modes_links_verified'])
   with tarfile.open(root/'archives'/proof['archive_name']) as tar:self.assertEqual(tar.extractfile('records/file').read(),b'\x00\xffraw trace');self.assertEqual(tar.getmember('records/link').linkname,'file')
 def test_unowned_path_rejected(self):
  with tempfile.TemporaryDirectory(prefix='solpi-g5-test-') as a,tempfile.TemporaryDirectory(prefix='unowned-') as b:
   with self.assertRaises(ValueError):compress(pathlib.Path(b),pathlib.Path(a)/'archives',pathlib.Path(a))
if __name__=='__main__':unittest.main()
