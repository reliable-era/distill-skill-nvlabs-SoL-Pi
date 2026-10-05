import unittest
from resume_output_contract_preflight_zero_start import transformed,original_code,validate_zero
class ResumeTests(unittest.TestCase):
 def test_zero_only_fail_closed(self):
  validate_zero({'starts':0,'POST':0,'rows':[]},['live-source-pins.json'])
  for x in [{'starts':1,'POST':0,'rows':[]},{'starts':0,'POST':1,'rows':[]},{'starts':False,'POST':0,'rows':[]},{'starts':0,'POST':0,'rows':[{}]}]:
   with self.assertRaises(RuntimeError):validate_zero(x,['live-source-pins.json'])
  with self.assertRaises(RuntimeError):validate_zero({'starts':0,'POST':0,'rows':[]},['live-source-pins.json','transport'])
 def test_same_plan_and_separate_result(self):
  s=transformed();self.assertIn('assert_frozen_plan(plan)',s);self.assertIn('assert_zero_root(root)',s);self.assertIn('scheduler_wait_seconds=resume_wait_seconds',s);self.assertIn('output-contract-preflight-fasttext-resume-result.json',s);self.assertNotIn("(R/'output-contract-preflight-fasttext-result.json').write_text",s)
 def test_actor_body_and_cleanup_unchanged(self):
  s=transformed().replace('output-contract-preflight-fasttext-resume-progress.json','output-contract-preflight-fasttext-progress.json')
  # Only declared progress-journal renaming is normalized; actor region is exact.
  marker=next(l for l in original_code.splitlines(True) if 'for arm in arms:' in l)
  end='   except Exception as e:'
  a=original_code.index(marker);b=s.index(marker)
  self.assertEqual(original_code[a:original_code.index(end,a)],s[b:s.index(end,b)])
  for text in ['with S.inference_locks', 'verify_live_sources()',"'native_starts_cap':4,'provider_POST_cap':64","per_actor_POST_cap':16","actor_seconds':600","completion_grace_seconds':240"]:self.assertIn(text,s)
if __name__=='__main__':unittest.main()
