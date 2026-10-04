import copy
import unittest
from collect_qwen_development import summarize


class Accounting(unittest.TestCase):
    def setUp(self):
        self.plan = {'schedule': [dict(id=str(i), family='swe', arm='candidate') for i in range(2)]}
        self.rows = [dict(id=str(i), family='swe', arm='candidate', usage_complete=True,
                          observed_gross_tokens_lower_bound=100, grade={'solved': i == 0}) for i in range(2)]

    def collect(self, rows):
        return summarize(self.plan, {'actors': rows, 'errors': []})['arms'][2]

    def test_failure_cost_included(self):
        self.assertEqual(self.collect(self.rows)['complete_tokens_per_solve'], 200)

    def test_prior_cohort_is_disclosed_without_pooling(self):
        self.plan.update(cohort='repaired', order_seed=127,
                         prior_consumed_attempts={'native_starts': 2, 'provider_POST': 17})
        result = summarize(self.plan, {'actors': self.rows})
        self.assertEqual(result['cohort'], 'repaired')
        self.assertEqual(result['order_seed'], 127)
        self.assertEqual(result['prior_consumed_attempts']['native_starts'], 2)
        self.assertFalse(result['prior_attempts_included_in_arm_metrics'])
        self.assertEqual(result['arms'][2]['recorded_attempts'], 2)
        self.assertEqual(result['arms'][2]['complete_tokens_per_solve'], 200)

    def test_partial_usage_cannot_certify_savings(self):
        rows = copy.deepcopy(self.rows)
        rows[1]['usage_complete'] = None
        self.assertIsNone(self.collect(rows)['complete_tokens_per_solve'])
        self.assertEqual(self.collect(rows)['observed_gross_tokens_lower_bound'], 200)

    def test_missing_attempt_prevents_complete_comparison(self):
        result = self.collect(self.rows[:1])
        self.assertEqual(result['missing_attempts'], 1)
        self.assertIsNone(result['complete_tokens_per_solve'])

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            self.collect([self.rows[0], self.rows[0]])

    def test_infrastructure_failure_cannot_be_verified_solve(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['grade']['infrastructure_error'] = 'permission denied'
        result = self.collect(rows)
        self.assertEqual(result['solved'], 0)
        self.assertEqual(result['ungraded'], 1)
        self.assertIsNone(result['complete_tokens_per_solve'])

    def test_unknown_grade_not_counted_as_solve(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['grade'] = {}
        result = self.collect(rows)
        self.assertEqual(result['solved'], 0)
        self.assertEqual(result['ungraded'], 1)
        self.assertIsNone(result['complete_tokens_per_solve'])


if __name__ == '__main__':
    unittest.main()
