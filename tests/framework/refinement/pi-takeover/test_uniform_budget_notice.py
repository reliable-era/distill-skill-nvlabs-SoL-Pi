import unittest
from uniform_budget_notice import NOTICE,add_notice
class Tests(unittest.TestCase):
 def test_uniform(self):
  outputs=[add_notice('task','public',s) for s in [[],['candidate'],['original','karpathy'],['karpathy']]]
  for out in outputs:self.assertEqual(out.count(NOTICE),1);self.assertTrue(out.startswith('task\n\n'+NOTICE+'\npublic'))
 def test_only_notice_added(self):
  old='task\n\npublic\n\nUse supplied skills in /skills. No subagents,compaction,web retrieval or external solutions. Work in /app.\n\ncandidate'
  self.assertEqual(add_notice('task','public',['candidate']).replace(NOTICE+'\n',''),old)
 def test_limits_unchanged(self):
  for phrase in ['16 forwarded model requests','600 seconds','Every forwarded request','rejected locally','no actor retry','do not change the task requirements']:self.assertIn(phrase,NOTICE)
 def test_reject_non_text(self):self.assertRaises(TypeError,add_notice,{},'public')
if __name__=='__main__':unittest.main()
