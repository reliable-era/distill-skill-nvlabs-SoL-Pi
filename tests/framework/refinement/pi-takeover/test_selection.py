import collections,json,pathlib,unittest
from select_subset import select,EXPOSED
R=pathlib.Path(__file__).resolve().parent
class Selection(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.actual=json.loads((R/'terminal-10pct-selection.json').read_text())
  cls.reproduced=select(pathlib.Path('/tmp/solpi-refinement-terminal-bench-2'))
 def test_exact_reproduction(self):self.assertEqual(self.actual,self.reproduced)
 def test_fraction_and_unique(self):
  p=self.actual;ids=[r['id'] for r in p['selected_tasks']]
  self.assertEqual(p['full_population'],89);self.assertEqual(p['selected_size'],9);self.assertEqual(len(set(ids)),9);self.assertTrue(.10<=p['fraction_of_full_population']<.12)
 def test_exposure_and_strata(self):
  p=self.actual;self.assertFalse(EXPOSED.intersection(r['id'] for r in p['selected_tasks']))
  self.assertEqual(dict(collections.Counter(r['difficulty'] for r in p['selected_tasks'])),p['stratum_quotas'])
  self.assertEqual(set(p['stratum_quotas']),{'easy','medium','hard'})
 def test_weights_cover_eligible_population(self):
  self.assertAlmostEqual(sum(r['design_weight'] for r in self.actual['selected_tasks']),87)
 def test_single_model_and_unlaunched(self):
  self.assertEqual(self.actual['model'],'Qwen3.8-27B-FP8');self.assertIn('metadata allocation only',self.actual['status'])
if __name__=='__main__':unittest.main()
