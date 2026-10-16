import random,unittest
import numpy as np
from final_analysis import cost_partition,mcnemar,paired_statistics
class FinalAnalysis(unittest.TestCase):
 def test_exact_mcnemar(self):
  self.assertEqual(mcnemar([1]*10,[0]*10)['p_two_sided'],2/1024);self.assertEqual(mcnemar([1,0],[0,1])['p_two_sided'],1);self.assertEqual(mcnemar([1],[1])['p_two_sided'],1)
 def test_shared_original_rng_and_independent_arithmetic(self):
  solves=np.array([[1,0,1,1],[0,1,1,0],[1,1,0,1]]);tokens=np.array([[20,30,40,50],[60,70,80,90],[10,15,25,35]]);unknown=np.zeros_like(tokens);result,counts,raw=paired_statistics(solves,tokens,unknown,seed=7,draws=20);rng=random.Random(7)
  for i in range(20):
   sample=[rng.randrange(3) for _ in range(3)];self.assertEqual(counts[i].tolist(),[sample.count(j) for j in range(3)]);xsol=sum(solves[j,2] for j in sample);ysol=sum(solves[j,0] for j in sample);xtok=sum(tokens[j,2] for j in sample);ytok=sum(tokens[j,0] for j in sample);expected=float((xtok/xsol)/(ytok/ysol)) if xsol and ysol else None;self.assertAlmostEqual(raw['ours/none']['actual_all_cost_tokens_per_solve_ratio'][i],expected) if expected is not None else self.assertIsNone(raw['ours/none']['actual_all_cost_tokens_per_solve_ratio'][i]);self.assertAlmostEqual(raw['ours/none']['solve_rate_difference'][i],float((xsol-ysol)/3))
  self.assertEqual(result['ours/none']['tokens_per_solve_ratio']['point'],result['ours/none']['recorded_token_lower_bound_tps_quotient']['point'])
 def test_unknown_usage_preserves_undefined_true_ratios_not_proxy_bounds(self):
  solves=[[1]*4];tokens=[[10,20,30,40]];unknown=[[0,0,1,0]];r,_,_=paired_statistics(solves,tokens,unknown,seed=7,draws=20);c=r['ours/none'];self.assertIsNone(c['tokens_per_solve_ratio']['point']);self.assertEqual(c['tokens_per_solve_ratio']['undefined_draws'],20);self.assertEqual(c['recorded_token_lower_bound_tps_quotient']['point'],3);self.assertFalse(c['recorded_token_lower_bound_tps_quotient']['is_lower_bound_on_actual_ratio'])
 def test_disjoint_cost_partition_latest_quality_all_costs(self):
  def attempt(tokens,harness=False,complete=True):return dict(known_tokens_lower_bound=tokens,requests=1,harness_failure=harness,cost_complete=complete)
  rows=[dict(known_tokens_lower_bound=60,attempt_rows=[attempt(10,complete=False),attempt(20,harness=True),attempt(30)])];p=cost_partition(rows);self.assertEqual([p[k]['known_tokens_lower_bound'] for k in ('latest_scored','superseded_retry','superseded_harness')],[30,10,20]);self.assertIsNone(p['superseded_retry']['total_tokens']);self.assertEqual(p['latest_scored']['total_tokens'],30)
if __name__=='__main__':unittest.main()
