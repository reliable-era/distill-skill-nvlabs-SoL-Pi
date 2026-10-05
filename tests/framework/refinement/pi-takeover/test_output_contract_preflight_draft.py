import unittest
from prepare_output_contract_preflight_draft import PARENT,CLAUSE,ANCHOR,draft
class DraftTests(unittest.TestCase):
 def test_only_one_clause_and_parent_recoverable(self):
  p=PARENT.read_text();d=draft(p);self.assertEqual(d.replace(CLAUSE+' ',''),p);self.assertEqual(d.count(CLAUSE),1);self.assertEqual(d.count('\n- '),p.count('\n- '))
 def test_conditional_disposable_no_answers(self):
  for token in ['expensive','unverified','disposable','output contract']:self.assertIn(token,CLAUSE)
  for token in ['fasttext','save_model','saveModel','OMP','thread','/app','epoch','lr=','600','150']:self.assertNotIn(token,CLAUSE)
 def test_safeguards_and_final_verification_unchanged(self):
  d=draft(PARENT.read_text());self.assertIn(CLAUSE+' '+ANCHOR,d);self.assertIn('retain source-backed checks needed to establish correctness.',d);self.assertIn('Finish once the requested behavior and required checks are satisfied.',d)
if __name__=='__main__':unittest.main()
