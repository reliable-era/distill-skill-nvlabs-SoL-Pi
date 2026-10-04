import unittest
from compare import compare


def records():
    return [dict(harness='pi', benchmark=f'b{t}', task=f't{t}', round=r,
                 arm=a, solved=True, tokens=80 if a == 'ours' else 100,
                 usage_complete=True)
            for t in range(3) for r in range(3)
            for a in ('none', 'karpathy', 'ours', 'both')]


class ComparisonTests(unittest.TestCase):
    def test_unknown_is_not_a_win(self):
        rows = records(); rows[0]['usage_complete'] = False
        self.assertFalse(compare(rows, bootstrap=100)['pi']['win'])

    def test_unmatched_and_duplicate_rejected(self):
        rows = records()
        self.assertFalse(compare(rows[1:], bootstrap=100)['pi']['win'])
        with self.assertRaises(ValueError):
            compare(rows + [rows[0]], bootstrap=100)

    def test_failed_attempts_cost_and_quality_count(self):
        rows = records()
        self.assertTrue(compare(rows, bootstrap=100)['pi']['win'])
        for r in rows:
            if r['arm'] == 'ours' and r['round'] == 0:
                r['solved'] = False
        result = compare(rows, bootstrap=100)['pi']
        self.assertFalse(result['win'])
        self.assertAlmostEqual(result['comparisons']['none']['cost_ratio'], 1.2)
