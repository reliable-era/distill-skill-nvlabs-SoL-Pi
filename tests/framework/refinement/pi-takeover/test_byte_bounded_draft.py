import pathlib,json,hashlib,unittest
from prepare_byte_bounded_observations_draft import OLD,NEW
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Tests(unittest.TestCase):
 def test_exact_single_mechanism_and_hashes(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'byte-bounded-observations/efficient-coding/SKILL.md';m=json.loads((q.parent.parent/'draft-manifest.json').read_text());s=q.read_text();self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(s.count(NEW),1);self.assertEqual(sha(q),m['candidate_sha256']);self.assertEqual(sha(p),m['parent_sha256']);self.assertFalse(m['known_quality_or_token_economy_win']);self.assertEqual(len(s.split())-len(p.read_text().split()),27)
 def test_safeguards_and_scope_preserved(self):
  s=(C/'byte-bounded-observations/efficient-coding/SKILL.md').read_text()
  for text in ['actual command status','relevant failure context','saved-log path','Before accepting a result','original sources','required checks','do not weaken final acceptance','byte-bounded']:self.assertIn(text,s)
  for text in ['fasttext','model.bin','thread=','167772160','16384','Qwen','600s','private_test','18001']:self.assertNotIn(text,s)
 def test_readonly_observation_audit_is_historical_not_savings(self):
  p=json.loads((R/'fasttext-tool-observation-audit.json').read_text());self.assertEqual(p['real_model_POST_added'],0);self.assertEqual(p['unknown_cost_requests'],[31]);self.assertEqual(p['by_arm']['candidate']['large_observations'][0]['provider_visible_bytes'],10215);self.assertEqual(p['by_arm']['candidate']['large_observations'][0]['requests'],[13,14,15,16]);self.assertEqual(p['native']['candidate']['max_native_output_bytes'],222943);self.assertFalse(p['goal_complete'])
if __name__=='__main__':unittest.main()
