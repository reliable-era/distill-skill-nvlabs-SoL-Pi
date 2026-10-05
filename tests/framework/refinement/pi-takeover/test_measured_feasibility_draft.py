import unittest,pathlib,json,hashlib
from prepare_measured_feasibility_draft import OLD,NEW
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Tests(unittest.TestCase):
 def test_one_mechanism_and_full_parent_recovery(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'measured-feasibility/efficient-coding/SKILL.md';m=json.loads((q.parent.parent/'draft-manifest.json').read_text());s=q.read_text();self.assertEqual(s.count(NEW),1);self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(sha(q),m['candidate_sha256']);self.assertEqual(sha(p),m['parent_sha256']);self.assertEqual(len(s.split())-len(p.read_text().split()),41)
 def test_no_taskanswers_or_hypothesis_bundle(self):
  s=(C/'measured-feasibility/efficient-coding/SKILL.md').read_text();self.assertIn('If a cheap measurement',s);self.assertIn('reuse trustworthy existing evidence',s);self.assertIn(OLD[2:],s)
  for x in ['fasttext','vocab','bucket=','model.bin','150MB','0.62','thread=','byte-bounded','12.8424','300.8948']:self.assertNotIn(x,s)
 def test_observed_constraints_not_private_grade(self):
  p=json.loads((R/'byte-bounded-feasibility-audit.json').read_text());s=p['sequence_evidence'];self.assertTrue(s['public_size_and_private_accuracy_constraints_known_before_training']);self.assertTrue(s['first_full_training_before_cheap_driver_measurement']);self.assertEqual(s['private_original_grade'],'UNAVAILABLE_NOT_INFERRED_FROM_PUBLIC_ACCURACY');self.assertEqual(s['saved_file_declared_bytes'],180281405);self.assertEqual(p['real_model_POST_added'],0);self.assertFalse(p['goal_complete'])
if __name__=='__main__':unittest.main()
