import json,pathlib,shutil,subprocess,tarfile,tempfile,unittest
from capture_patch import capture
from common import sha
class LosslessCapture(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory(prefix='g5-capture-test-');self.addCleanup(t.cleanup);r=pathlib.Path(t.name);b=r/'baseline';w=b/'workspace';w.mkdir(parents=True);(w/'source.py').write_text('original\n');subprocess.run(['git','-C',str(w),'init','-q'],check=True,capture_output=True);subprocess.run(['git','-C',str(w),'add','.'],check=True,capture_output=True);subprocess.run(['git','-C',str(w),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','snapshot'],check=True,capture_output=True);head=subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip();(b/'manifest.json').write_text(json.dumps(dict(prepared=True,gold_in_actor=False,snapshot_commit=head,source_tree={'source.py':sha(w/'source.py')})));c=r/'candidate';shutil.copytree(w,c);out=r/'out';out.mkdir();return r,b,w,c,out
 def archive(self,r,c):
  p=r/'capture.tar'
  with tarfile.open(p,'w') as tar:tar.add(c,arcname='.')
  return p
 def test_empty_patch_valid_and_trusted_baseline_unchanged(self):
  r,b,w,c,out=self.fixture();original=sha(w/'source.py');proof=capture(self.archive(r,c),b,out);self.assertTrue(proof['complete_git_delta_replay_equal']);self.assertEqual((out/'model.patch').read_bytes(),b'');self.assertEqual(sha(w/'source.py'),original)
 def test_binary_utf8_lossless_and_source_mode(self):
  r,b,w,c,out=self.fixture();(c/'source.py').write_text('changed\n');(c/'source.py').chmod(0o755);(c/'artifact.pdf').write_bytes(b'\x00\xac\xffPDF\n');proof=capture(self.archive(r,c),b,out);(out/'model.patch').read_text();self.assertTrue(proof['utf8_readable']);self.assertTrue(proof['complete_git_delta_replay_equal']);self.assertEqual((out/'delta-replay/artifact.pdf').read_bytes(),b'\x00\xac\xffPDF\n');self.assertTrue((out/'delta-replay/source.py').stat().st_mode&0o111)
 def test_absolute_noneligible_link_rejected(self):
  r,b,w,c,out=self.fixture();(c/'evil').symlink_to('/etc/passwd')
  with self.assertRaises(ValueError):capture(self.archive(r,c),b,out)
if __name__=='__main__':unittest.main()
