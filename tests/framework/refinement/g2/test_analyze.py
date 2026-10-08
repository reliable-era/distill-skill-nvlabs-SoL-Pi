"""Mathematical analysis tests only; not benchmark/provider mock evidence."""
import unittest
from analyze import analyze

class AnalysisTests(unittest.TestCase):
    def rows(self):
        return [dict(task=t,round=r,arm=a,grade_valid=True,cost_complete=True,solved=True,
                     tokens_lower_bound={'none':100,'K':90,'candidate':60,'Both':50}[a],native_wall_seconds=1)
                for t in ('a','b','c') for r in (1,2,3) for a in ('none','K','candidate','Both')]
    def test_all_required_comparisons_not_candidate_both(self):
        v=analyze(self.rows(),['a','b','c'],[1,2,3],42,1000)
        self.assertTrue(v['family_accepted']);self.assertGreater(v['comparisons']['candidate/Both']['ratio'],1)
        self.assertFalse(v['comparisons']['candidate/Both']['gate'])
    def test_no_early_win(self):
        v=analyze([r for r in self.rows() if r['round']==1],['a','b','c'],[1],42,100)
        self.assertFalse(v['round_1_negative_stop']);self.assertFalse(v['family_accepted'])
    def test_quality_loss_futility(self):
        rows=[r for r in self.rows() if r['round']==1];rows[2]['solved']=False
        self.assertTrue(analyze(rows,['a','b','c'],[1],42,100)['round_1_negative_stop'])
    def test_zero_solve_is_not_a_win(self):
        rows=self.rows()
        for r in rows:
            if r['arm']=='candidate':r['solved']=False
        v=analyze(rows,['a','b','c'],[1,2,3],42,100)
        self.assertFalse(v['family_accepted']);self.assertIsNone(v['comparisons']['candidate/none']['bootstrap_95'][1])
    def test_unknown_cost_blocks_acceptance(self):
        rows=self.rows();rows[0]['cost_complete']=False
        self.assertFalse(analyze(rows,['a','b','c'],[1,2,3],42,100)['family_accepted'])
    def test_duplicate_and_incomplete_rosters_rejected(self):
        rows=self.rows()
        with self.assertRaises(ValueError):analyze(rows+[rows[0]],['a','b','c'],[1,2,3],42,100)
        with self.assertRaises(ValueError):analyze(rows[:-1],['a','b','c'],[1,2,3],42,100)

if __name__=='__main__':unittest.main()
