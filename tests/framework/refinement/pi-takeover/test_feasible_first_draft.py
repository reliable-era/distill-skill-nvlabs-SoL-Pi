import unittest,pathlib,json,hashlib
from prepare_feasible_first_draft import OLD,NEW
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Tests(unittest.TestCase):
 def test_single_bullet_parent_recovery(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'feasible-first/efficient-coding/SKILL.md';m=json.loads((q.parent.parent/'draft-manifest.json').read_text());s=q.read_text();self.assertEqual(s.count(NEW),1);self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(sha(q),m['candidate_sha256']);self.assertEqual(sha(p),m['parent_sha256']);self.assertEqual(len(s.split())-len(p.read_text().split()),20)
 def test_safeguards_exception_and_no_taskanswers(self):
  s=(C/'feasible-first/efficient-coding/SKILL.md').read_text()
  for x in ['unless that intermediate and its conversion are necessary and checked','small reversible change','do not weaken final acceptance or verification','Before accepting a result','original sources','required checks']:self.assertIn(x,s)
  for x in ['fasttext','model.bin','150MB','0.62','bucket=','thread=','byte-bounded','cheap measurement','600']:self.assertNotIn(x,s)
 def test_evidence_no_causal_or_quality_claim(self):
  m=json.loads((R/'feasible-first-choice-audit.json').read_text());self.assertTrue(m['explicit_strategy_evidence']['candidate_knew_hard_limit_and_intentionally_selected_nonconforming_baseline_then_conversion']);self.assertTrue(m['explicit_strategy_evidence']['Both_selected_fitting_baseline_then_improve_if_needed']);self.assertEqual(m['separate_official_grades'],{'candidate':0,'Both':1});self.assertEqual(m['model_calls_added'],0);self.assertFalse(m['promotion']);self.assertFalse(m['goal_complete'])
if __name__=='__main__':unittest.main()
