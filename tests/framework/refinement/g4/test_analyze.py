import unittest
from analyze import analyze_part,task_totals,SEEDS,DRAWS

def cell(task,arm,tokens,solved=True,round=1,extra=()):
 return dict(part='B',task=task,arm=arm,round=round,verified_solved=solved,attempts=[dict(exact_provider_tokens=tokens)]+list(extra))
class AnalysisTests(unittest.TestCase):
 def test_all_attempt_costs_and_final_solve_once(self):
  r=analyze_part('B',[cell('t','none',100,extra=[dict(exact_provider_tokens=50,native_timeout=True)]),cell('t','K',300)],draws=20)
  self.assertEqual(r['arms']['none']['all_attempt_provider_tokens'],150);self.assertEqual(r['arms']['none']['solves'],1);self.assertEqual(r['arms']['none']['native_timeouts'],1);self.assertEqual(r['comparisons']['K/none']['point'],2)
 def test_paired_task_cluster_preserves_rounds(self):
  rows=[cell(t,a,v,round=i) for t in ('a','b') for i in (1,2,3) for a,v in [('none',10),('K',20)]];r=analyze_part('B',rows,draws=100)
  self.assertEqual(r['arms']['none']['cells'],6);self.assertEqual(set(r['comparisons']['K/none']['draws']),{2.0})
 def test_unknown_cost_not_imputed(self):
  r=analyze_part('B',[cell('a','none',10),cell('a','K',None)],draws=20)
  self.assertIsNone(r['arms']['K']['all_attempt_provider_tokens']);self.assertIsNone(r['comparisons']['K/none']['point']);self.assertEqual(r['comparisons']['K/none']['draws'],[None]*20)
 def test_zero_solves_undefined_retained(self):
  r=analyze_part('B',[cell('a','none',10,False),cell('a','K',20)],draws=20)
  self.assertEqual(r['comparisons']['K/none']['undefined_draws'],20);self.assertEqual(r['comparisons']['K/none']['bootstrap95'],[None,None])
 def test_missing_arm_cluster_not_fabricated_zero(self):
  r=analyze_part('B',[cell('a','none',10),cell('a','K',20),cell('b','none',10)],draws=100)
  self.assertIsNone(r['comparisons']['K/none']['point']);self.assertGreater(r['comparisons']['K/none']['undefined_draws'],0);self.assertTrue(r['comparisons']['K/none']['interval_conditional_on_defined_draws'])
 def test_duplicate_cells_not_double_counted(self):
  with self.assertRaises(ValueError):task_totals([cell('a','K',10),cell('a','K',20)])
 def test_invalid_token_amount_rejected(self):
  for value in (True,-1,1.5):
   with self.assertRaises(ValueError):task_totals([cell('a','none',value)])
 def test_unattempted_unavailable_not_zero_cost(self):
  c=cell('a','none',10);c.update(attempts=[],verified_solved=None);r=analyze_part('B',[c],draws=20)
  self.assertEqual(r['arms']['none']['cells'],0);self.assertIsNone(r['arms']['none']['all_attempt_provider_tokens'])
 def test_seed_and_default20k_determinism(self):
  rows=[cell('a','none',10),cell('a','K',20)];a=analyze_part('B',rows);b=analyze_part('B',rows)
  self.assertEqual(a,b);self.assertEqual(a['seed'],SEEDS['B']);self.assertEqual(len(a['comparisons']['K/none']['draws']),DRAWS)
 def test_parts_not_pooled_and_A_cross_harness_labeled(self):
  rows=[dict(cell('a',arm,t),part='A') for arm,t in [('none',10),('K',20),('solpi',30)]];r=analyze_part('A',rows,draws=20)
  self.assertTrue(r['comparisons']['solpi/none']['cross_harness_informational_only'])
  with self.assertRaises(ValueError):analyze_part('C',rows,draws=20)
if __name__=='__main__':unittest.main()
