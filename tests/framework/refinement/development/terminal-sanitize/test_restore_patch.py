"""Test publication marker reconstruction without literal credential strings."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('terminal_audit',Path(__file__).with_name('audit_replay.py'))
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class RestorePatchTests(unittest.TestCase):
 def test_digest_restores_original_patch_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   # Synthetic prefix is assembled; no real credential or literal token stored.
   token=b'h'+b'f_'+b'A'*24
   (root/'fixture.txt').write_bytes(b'key='+token+b'\n')
   digest=hashlib.sha256(token).hexdigest().encode()
   original=b'-key='+token+b'\n+key=<placeholder>\n'
   published=original.replace(token,b'[REDACTED_HF_TOKEN_'+digest+b']')
   restored=audit.restore_patch(published,root)
   self.assertEqual(restored,original)
   self.assertEqual(hashlib.sha256(restored).digest(),hashlib.sha256(original).digest())
 def test_unknown_digest_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   marker=b'[REDACTED_HF_TOKEN_'+b'0'*64+b']'
   with self.assertRaisesRegex(ValueError,'absent from pinned'):
    audit.restore_patch(marker,Path(td))

if __name__=='__main__':unittest.main()
