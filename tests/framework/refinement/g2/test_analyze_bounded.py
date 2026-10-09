"""Pure mathematical tests, not benchmark/provider evidence."""
import copy, unittest
import analyze as frozen
import analyze_bounded as bounded
class BoundTests(unittest.TestCase):
    def rows(self):
        rows=[dict(task=t,round=r,arm=a,grade_valid=True,cost_complete=True,provider_eof_valid=True,solved=True,tokens_lower_bound={'none':100,'K':90,'candidate':60,'Both':50}[a],native_wall_seconds=1) for t in (bounded.TASK,'b','c') for r in (1,2,3) for a in frozen.ARMS]
        target=next(x for x in rows if x['task']==bounded.TASK and x['round']==1 and x['arm']=='K');target['cell_id']=bounded.AUTHORIZED
        return rows
    def run_analysis(self,rows,rounds=(1,2,3)):
        return bounded.analyze([r for r in rows if r['round'] in rounds],[bounded.TASK,'b','c'],list(rounds),42,1000)
    def test_exact_inputs_preserve_frozen_results(self):
        rows=self.rows();v=self.run_analysis(rows);old=frozen.analyze(rows,[bounded.TASK,'b','c'],[1,2,3],42,1000)
        for pair in v['comparisons']:
            self.assertEqual(v['comparisons'][pair]['ratio'],old['comparisons'][pair]['ratio']);self.assertEqual(v['comparisons'][pair]['bootstrap_95'],old['comparisons'][pair]['bootstrap_95'])
    def test_authorized_gap_bounds_are_monotone_and_raw_unchanged(self):
        rows=self.rows();target=next(r for r in rows if r.get('cell_id')==bounded.AUTHORIZED);target.update(cost_complete=False,provider_eof_valid=False);before=copy.deepcopy(rows)
        upper=self.run_analysis(rows);self.assertEqual(rows,before);self.assertFalse(upper['raw_evidence_complete']);self.assertTrue(upper['family_accepted']);self.assertFalse(upper['aggregates']['K']['costs_complete']);self.assertIsNone(upper['aggregates']['K']['tokens_per_solve'])
        exact=copy.deepcopy(rows);t=next(r for r in exact if r.get('cell_id')==bounded.AUTHORIZED);t.update(cost_complete=True,provider_eof_valid=True,tokens_lower_bound=1090)
        true=self.run_analysis(exact)
        for pair in ('candidate/K','Both/K'):
            self.assertEqual(upper['comparisons'][pair]['true_ratio_relation_to_reported'],'<=');self.assertLessEqual(true['comparisons'][pair]['ratio'],upper['comparisons'][pair]['ratio'])
            for i in (0,1):self.assertLessEqual(true['comparisons'][pair]['bootstrap_95'][i],upper['comparisons'][pair]['bootstrap_95'][i])
        self.assertEqual(upper['comparisons']['candidate/none']['ratio'],true['comparisons']['candidate/none']['ratio']);self.assertEqual(upper['comparisons']['K/none']['true_ratio_relation_to_reported'],'>=')
    def test_other_unknown_cost_or_grade_blocks(self):
        for arm in frozen.ARMS:
            rows=self.rows();row=next(r for r in rows if r['arm']==arm and r['task']=='b');row['cost_complete']=False;self.assertFalse(self.run_analysis(rows)['family_accepted'])
        rows=self.rows();row=next(r for r in rows if r.get('cell_id')==bounded.AUTHORIZED);row.update(cost_complete=False,grade_valid=False);self.assertFalse(self.run_analysis(rows)['family_accepted'])
    def test_no_early_acceptance_and_exact_futility(self):
        rows=self.rows();row=next(r for r in rows if r.get('cell_id')==bounded.AUTHORIZED);row.update(cost_complete=False,provider_eof_valid=False)
        v=self.run_analysis(rows,(1,));self.assertFalse(v['family_accepted']);self.assertFalse(v['round_1_negative_stop'])
        for r in rows:
            if r['arm']=='candidate':r['solved']=False
        self.assertTrue(self.run_analysis(rows,(1,))['round_1_negative_stop'])
    def test_incomplete_roster_rejected(self):
        with self.assertRaises(ValueError):self.run_analysis(self.rows()[:-1])
if __name__=='__main__':unittest.main()
