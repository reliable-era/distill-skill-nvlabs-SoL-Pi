import unittest
from analyze import analyze_part
from independent_analysis import independent
class IndependentTests(unittest.TestCase):
 def test_rounds_retries_unknown_and_missing_pair_draws(self):
  cells=[]
  for task in ('x','y'):
   for arm in ('none','K','ours','Both'):
    for r in (1,2):
     if task=='y' and arm=='Both':continue
     attempts=[dict(exact_provider_tokens=10,known_tokens_lower_bound=10,native_timeout=False,grader_timeout=False),dict(exact_provider_tokens=None if task=='x' and arm=='K' else 5,known_tokens_lower_bound=5,native_timeout=False,grader_timeout=False)]
     cells.append(dict(part='B',task=task,arm=arm,round=r,attempts=attempts,verified_solved=r==1))
  primary=analyze_part('B',cells);metrics,draws=independent('B',cells)
  for arm,row in metrics.items():
   for field,value in row.items():self.assertEqual(primary['arms'][arm][field],value)
  for name,values in draws.items():self.assertEqual(primary['comparisons'][name]['draws'],values)
  self.assertEqual(len(draws['ours/none']),20000);self.assertIn(None,draws['Both/none']);self.assertIn(None,draws['ours/K'])
if __name__=='__main__':unittest.main()
