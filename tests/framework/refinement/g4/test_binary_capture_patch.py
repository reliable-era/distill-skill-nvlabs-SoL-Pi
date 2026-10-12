import pathlib,tarfile,io,unittest
import test_recover_ignored_capture_links as fixtures
from recover_ignored_capture_links import project,sha
from binary_capture_patch import represent

class BinaryRepresentation(unittest.TestCase):
 setUp=fixtures.CaptureProjection.setUp
 archive=fixtures.CaptureProjection.archive
 def test_raw_pdf_nonutf8_is_losslessly_binary_represented(self):
  archive=self.archive();data=b'%PDF-1.4\n'+bytes([172,254])+b' exact bytes\n'
  with tarfile.open(archive,'a') as t:
   m=tarfile.TarInfo('result_images/raw.pdf');m.size=len(data);t.addfile(m,io.BytesIO(data))
  original=self.root/'projection';project(archive,self.base,original);before=sha(original/'model.patch')
  with self.assertRaises(UnicodeDecodeError):(original/'model.patch').read_text()
  binary=self.root/'binary';proof=represent(self.base,original,binary)
  self.assertEqual(sha(original/'model.patch'),before);self.assertTrue(proof['complete_git_delta_replay_equal']);self.assertTrue(proof['utf8_readable']);self.assertIn('GIT binary patch',(binary/'model.patch').read_text());self.assertEqual((binary/'applied/result_images/raw.pdf').read_bytes(),data);self.assertEqual((binary/'applied/code.py').read_text(),'after\n');self.assertEqual(proof['model_calls'],0)
 def test_text_capture_uses_same_uniform_binary_rule(self):
  original=self.root/'projection';project(self.archive(),self.base,original);proof=represent(self.base,original,self.root/'binary');self.assertTrue(proof['complete_git_delta_replay_equal']);self.assertTrue(proof['changed_path_byte_mode_proofs']);self.assertEqual((self.source/'code.py').read_text(),'before\n')

if __name__=='__main__':unittest.main()
