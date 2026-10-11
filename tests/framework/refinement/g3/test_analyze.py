import copy,unittest
from analyze import analyze,ARMS
class AnalysisTests(unittest.TestCase):
 def rows(self,rounds=(1,2,3)):
  return [dict(task=t,round=n,arm=a,solved=True,grade_valid=True,tokens_lower_bound=50 if a in ('candidate','Both') else 100,cost_complete=True,attempts=1) for t in ('a','b','c') for n in rounds for a in ARMS]
 def go(self,rows,rounds=(1,2,3)):
  return analyze(rows,['a','b','c'],list(rounds),77,repetitions=200)
 def test_all_gates(self):self.assertTrue(self.go(self.rows())['family_accepted'])
 def test_futility_no_early_success(self):
  v=self.go(self.rows((1,)),(1,));self.assertTrue(v['round1_survived']);self.assertFalse(v['family_accepted'])
 def test_karpathy_futility(self):
  rows=self.rows((1,))
  for r in rows:
   if r['arm']=='K':r['tokens_lower_bound']=40
  self.assertTrue(self.go(rows,(1,))['round1_negative_stop'])
 def test_quality_stop(self):
  rows=self.rows((1,));next(r for r in rows if r['arm']=='candidate')['solved']=False
  self.assertTrue(self.go(rows,(1,))['round1_negative_stop'])
 def test_missing_and_duplicate(self):
  for rows in (self.rows()[:-1],self.rows()+self.rows()[:1]):
   with self.assertRaises(ValueError):self.go(rows)
 def test_unknown_denominator(self):
  rows=self.rows();next(r for r in rows if r['arm']=='K')['cost_complete']=False;before=copy.deepcopy(rows);v=self.go(rows);self.assertTrue(v['family_accepted']);self.assertFalse(v['raw_costs_complete']);self.assertEqual(v['comparisons']['candidate/K']['true_ratio_relation'],'<=');self.assertEqual(rows,before)
 def test_unknown_numerator_blocks(self):
  rows=self.rows();next(r for r in rows if r['arm']=='candidate')['cost_complete']=False;v=self.go(rows);self.assertFalse(v['family_accepted']);self.assertFalse(v['comparisons']['candidate/K']['conservative_upper_eligible'])
 def test_failure_costs_retained(self):
  rows=self.rows();r=rows[0];r['solved']=False;r['tokens_lower_bound']=1234;r['attempts']=2;v=self.go(rows);self.assertEqual(v['aggregates']['none']['tokens_lower_bound'],2034);self.assertEqual(v['aggregates']['none']['attempts'],10)
 def test_undefined_not_dropped(self):
  rows=self.rows()
  for r in rows:
   if r['arm']=='none':r['solved']=False
  v=self.go(rows);c=v['comparisons']['candidate/none'];self.assertEqual(c['undefined_replicates'],200);self.assertIsNone(c['surrogate_bootstrap_95'][1]);self.assertFalse(v['family_accepted'])
 def test_invalid_grade_blocks(self):
  rows=self.rows();rows[0]['grade_valid']=False;self.assertFalse(self.go(rows)['family_accepted'])
if __name__=='__main__':unittest.main()
