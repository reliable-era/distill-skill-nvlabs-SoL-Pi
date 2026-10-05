import unittest,pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_exact_one_bullet(self):
  folder=R.parent/'candidates/coalesced-verification';m=json.loads((folder/'draft-manifest.json').read_text());text=(folder/'efficient-coding/SKILL.md').read_text();parent=(R.parent/'candidates/behavior-first-progress/efficient-coding/SKILL.md').read_text();self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),m['candidate_sha256']);self.assertEqual(text.count(m['new_bullet']),1);self.assertEqual(text.replace(m['new_bullet'],m['old_bullet']),parent);self.assertEqual(len(text.split()),436)
 def test_safeguards_byte_preserved(self):
  text=(R.parent/'candidates/coalesced-verification/efficient-coding/SKILL.md').read_text();self.assertIn('For irreversible actions, check the required safeguards first; do not weaken final acceptance or verification.',text);self.assertIn('do not validate a generated artifact only against the assumptions used to create it',text);self.assertIn('retain source-backed checks needed to establish correctness',text);self.assertIn('keep labeled results and each exit status',text)
 def test_wheel_metadata_toplevel_only(self):
  names=['setuptools-80.9.0.dist-info/METADATA','setuptools/_vendor/packaging-24.2.dist-info/METADATA'];chosen=[n for n in names if n.endswith('.dist-info/METADATA') and len(pathlib.PurePosixPath(n).parts)==2];self.assertEqual(chosen,[names[0]])
 def test_software_proof_not_model_win(self):
  x=json.loads((R/'fasttext-cached-software-probe-r2.json').read_text());self.assertTrue(x['passed'] and x['cleanup_verified']);self.assertEqual(len(x['collected_original_tests']),2)
  for k in ['model_POST','models_trained','gold_runs','official_test_runs','scored_actor_starts']:self.assertEqual(x[k],0)
if __name__=='__main__':unittest.main()
