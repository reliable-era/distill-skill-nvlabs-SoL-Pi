import pathlib,json,unittest,hashlib
from prepare_scratch_capacity_draft import OLD,NEW
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates'
class Tests(unittest.TestCase):
 def test_exact_parent_recovery_and_hash(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'scratch-capacity/efficient-coding/SKILL.md';m=json.loads((q.parent.parent/'draft-manifest.json').read_text());s=q.read_text();self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(s.count(NEW),1);self.assertEqual(hashlib.sha256(q.read_bytes()).hexdigest(),m['candidate_sha256']);self.assertEqual(len(s.split())-len(p.read_text().split()),26);self.assertFalse(m['frozen']);self.assertFalse(m['scored'])
 def test_conditional_scope_no_answers_no_bundling(self):
  self.assertTrue(NEW.endswith(OLD[2:]));self.assertIn('For large writes or intermediate data',NEW);s=(C/'scratch-capacity/efficient-coding/SKILL.md').read_text()
  for x in ['fasttext','model.bin','/tmp','/app','128','4096','1 CPU','thread=','lr=','600','documented idiomatic baseline','cheap measurement']:self.assertNotIn(x,s)
 def test_evidence_limits_and_no_calls(self):
  m=json.loads((R/'declared-scratch-capacity-audit.json').read_text());rows={x['arm']:x for x in m['rows']};self.assertTrue(rows['candidate']['model_save_to_tmp_declared']);self.assertTrue(rows['candidate']['df_app_but_no_matched_df_tmp']);self.assertTrue(rows['none']['literal_no_space_error_retained']);self.assertTrue(rows['K']['literal_no_space_error_retained']);self.assertFalse(rows['candidate']['literal_no_space_error_retained']);self.assertEqual(m['new_model_POST'],0);self.assertFalse(m['goal_complete']);p=json.loads((R/'provider-visible-skill-priority-audit.json').read_text());self.assertTrue(p['full_prompt_and_skills_persisted_each_request']);self.assertEqual(p['POST'],63)
if __name__=='__main__':unittest.main()
