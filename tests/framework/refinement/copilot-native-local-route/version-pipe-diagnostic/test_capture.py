import unittest,tempfile,pathlib,io,hashlib
from worker import capture
class Capture(unittest.TestCase):
 def test_capture_drains_and_hashes_after_limit(self):
  data=b'x'*200000
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'stream';r=capture(io.BytesIO(data),p)
   self.assertEqual(p.stat().st_size,65536);self.assertEqual(r['total_bytes'],200000);self.assertEqual(r['sha256_full_stream'],hashlib.sha256(data).hexdigest())
 def test_no_global_file_limit(self):
  s=(pathlib.Path(__file__).parent/'worker.py').read_text();self.assertNotIn('setrlimit',s);self.assertIn('start_new_session=True',s);self.assertIn('p.wait(timeout=5)',s)
if __name__=='__main__':unittest.main()
