import unittest,pathlib,json,hashlib
from prepare_documented_baseline_draft import OLD,NEW
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates'
class Tests(unittest.TestCase):
 def test_exact_recovery_hash_words(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'documented-baseline/efficient-coding/SKILL.md';s=q.read_text();m=json.loads((q.parent.parent/'draft-manifest.json').read_text());self.assertEqual(s.count(NEW),1);self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(hashlib.sha256(q.read_bytes()).hexdigest(),m['candidate_sha256']);self.assertEqual(len(s.split())-len(p.read_text().split()),23);self.assertFalse(m['frozen']);self.assertFalse(m['scored'])
 def test_requirement_override_and_original_safeguards(self):
  self.assertIn('override defaults only to meet requirements or respond to observed evidence',NEW);self.assertTrue(NEW.endswith(OLD[2:]));s=(C/'documented-baseline/efficient-coding/SKILL.md').read_text()
  for x in ['fasttext','model.bin','lr=','dim=','thread=','150MB','0.62','600','byte-bounded','cheap measurement']:self.assertNotIn(x,s)
 def test_evidence_preserves_failed_counterexample_and_limits(self):
  m=json.loads((R/'existing-api-defaults-audit.json').read_text());rows=m['rows'];good=next(x for x in rows if x['stage']=='measured-feasibility' and x['arm']=='Both');counter=next(x for x in rows if x['stage']=='feasible-first' and x['arm']=='K');self.assertEqual(good['original_grade'],1);self.assertTrue(good['training_source_numeric_learning_rate_declaration_metadata'][0]['all_match_public_api_default']);self.assertEqual(counter['original_grade'],0);self.assertTrue(counter['training_source_numeric_learning_rate_declaration_metadata'][0]['any_match_public_api_default']);self.assertEqual(m['new_model_POST'],0);self.assertFalse(m['numeric_training_values_exported']);self.assertFalse(m['goal_complete']);self.assertTrue(m['limitations'])
if __name__=='__main__':unittest.main()
