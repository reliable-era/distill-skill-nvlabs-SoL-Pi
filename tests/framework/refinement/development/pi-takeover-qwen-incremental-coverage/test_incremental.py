"""Changed-scope tests only;no new real model or Docker calls."""
import json,pathlib,sys,unittest,difflib
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));import run_screen as Q
class Incremental(unittest.TestCase):
 def test_both_known_peers_and_no_unknown_or_missing_header(self):
  self.assertIsNone(Q.backend_error([{'provider_backend':'127.0.0.1:18001'},{'provider_backend':'127.0.0.1:18002'}]))
  for rows in [[],[{}],[{'provider_backend':'127.0.0.1:8000'}],[{'provider_backend':'remote.example:8000'}]]:self.assertIsNotNone(Q.backend_error(rows))
 def test_one_bullet_changed_from_scope_not_patch_first(self):
  old=(R.with_name('pi-takeover-qwen-terminal')/'frozen/candidate/SKILL.md').read_text().splitlines();new=(R/'frozen/candidate/SKILL.md').read_text().splitlines()
  changed=[op for op in difflib.SequenceMatcher(a=old,b=new).get_opcodes() if op[0]!='equal'];self.assertEqual(len(changed),1);tag,a,b,c,d=changed[0];self.assertEqual((tag,b-a,d-c),('replace',1,1));self.assertIn('complete inventory is not a prerequisite',new[c]);self.assertIn('do not silently exempt examples or data',new[c])
 def test_original_is_separate_not_used_in_both(self):
  self.assertEqual(Q.W.ARMS['original'],['original']);self.assertEqual(Q.W.ARMS['Both'],['karpathy','candidate']);self.assertTrue((R/'frozen/original/SKILL.md').exists())
if __name__=='__main__':unittest.main()
