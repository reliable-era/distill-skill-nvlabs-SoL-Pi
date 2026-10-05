import ast,json,pathlib,hashlib,unittest
from run_scratch_capacity_fasttext_screen import code
R=pathlib.Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_frozen_runtime_only_candidate_changed(self):
  d=R.parent/'development/pi-takeover-qwen-scratch-capacity-admission-16k';old=R.parent/'development/pi-takeover-qwen-coalesced-verification-admission-16k';m=json.loads((d/'freeze-manifest.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();self.assertTrue(all(h(d/'runtime'/n)==v==h(old/'runtime'/n) for n,v in m['runtime_hashes'].items()));p=json.loads((old/'freeze-manifest.json').read_text());self.assertEqual([n for n,v in m['frozen_manifest'].items() if p['frozen_manifest'][n]!=v],['candidate/SKILL.md']);self.assertEqual(m['comparator_Both_definition'],'currentcandidate+frozenKarpathy')
 def test_one_new_fourarm_candidate_phase(self):
  ast.parse(code)
  for text in ["arms=['none','K','candidate','Both']","'native_starts_cap':4,'provider_POST_cap':64","per_actor_POST_cap':16","actor_seconds':600","completion_grace_seconds':240","configured_output_cap=16384","historical_stage_not_replayed=True","old_cohort_pooling=False","transport_skill_causal_claim=False"]:self.assertIn(text,code)
  self.assertNotIn("raise SystemExit('prepared-only",code);self.assertIn("scratch-capacity-fasttext-plan.json",code);self.assertIn("pi-takeover-qwen-scratch-capacity-admission-16k",code)
 def test_failure_callback_and_grader_safety(self):
  for text in ['actor_context=None;row=None;name=None',"actor_context['container_id']=inspect['Id']",'stop_epoch(session,actor_context,docker,owned)','run_cell(session,row',"finish_failure(session,actor_context",":/tests:rw","str(trusted_tests)","CAP",'CAP_DROP']:
   if text not in ['CAP','CAP_DROP']:self.assertIn(text,code)
  self.assertIn("'--cap-drop','ALL'",code);self.assertIn("'--network','none'",code);self.assertIn("if row['output_present']:",code);self.assertIn("replay_capture(SOURCE.name,d/'captured'",code);self.assertIn("row['test_events']!=2",code)
if __name__=='__main__':unittest.main()
