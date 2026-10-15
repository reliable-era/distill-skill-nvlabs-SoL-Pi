import json,pathlib,random,tempfile,unittest
from analyze import ARMS,aggregate,bootstrap,panel,percentile,ratios

def cell(task,arm,tokens=100,solved=True,complete=True):
 a=dict(task=task,arm=arm,attempt=1,requests=1,known_tokens_lower_bound=tokens,cost_complete=complete,solved=solved,grade_valid=solved is not None,timeout=False,grader_timeout=False)
 return dict(task=task,arm=arm,scored_attempt=1,solved=solved,requests=1,known_tokens_lower_bound=tokens,cost_complete=complete,attempt_rows=[a])
class Analysis(unittest.TestCase):
 def test_all_attempt_cost_last_quality(self):
  rows=[cell('a',a) for a in ARMS];r=rows[2];a=dict(r['attempt_rows'][0],solved=False,known_tokens_lower_bound=30);b=dict(r['attempt_rows'][0],attempt=2,known_tokens_lower_bound=70);r.update(scored_attempt=2,requests=2,attempt_rows=[a,b]);tasks,by=panel(rows,['a']);s=aggregate(tasks,by);self.assertEqual(s['ours']['total_tokens'],100);self.assertEqual(s['ours']['attempts'],2);self.assertEqual(s['ours']['solves'],1)
 def test_unknown_cost_ratios_unavailable_not_bound_ratios(self):
  rows=[cell('a',a,complete=a!='ours') for a in ARMS];r=bootstrap(rows,['a'],draws=20);c=r['comparisons']['ours/none'];self.assertIsNone(c['point']['total_tokens']);self.assertEqual(c['tokens_per_verified_solve_ratio']['undefined_draws'],20)
 def test_unknown_grade_not_false(self):
  rows=[cell('a',a,solved=None if a=='ours' else True) for a in ARMS];r=bootstrap(rows,['a'],draws=20);self.assertEqual(r['arms']['ours']['unavailable_grades'],1);self.assertIsNone(r['comparisons']['ours/none']['point']['tokens_per_verified_solve']);self.assertEqual(r['comparisons']['ours/none']['point']['total_tokens'],1)
 def test_full_panel_required(self):
  with self.assertRaises(AssertionError):panel([cell('a','none')],['a'])
 def test_zero_solves_nulls_retained(self):
  rows=[cell(t,a,solved=t=='b') for t in ('a','b') for a in ARMS];r=bootstrap(rows,['a','b'],draws=20000);c=r['comparisons']['ours/none'];self.assertGreater(c['tokens_per_verified_solve_ratio']['undefined_draws'],0);self.assertEqual(c['tokens_per_verified_solve_ratio']['coverage'],'conditional_on_defined_draws');self.assertEqual(c['tokens_per_verified_solve_ratio']['percentile_95'],[1,1]);self.assertEqual(r['bootstrap']['draws'],20000)
 def test_shared_paired_draws_independent_arithmetic(self):
  rows=[cell(t,a,tokens=(10 if t=='a' else 40)*(2 if a=='ours' else 1),solved=t=='b' or a=='none') for t in ('a','b') for a in ARMS]
  with tempfile.TemporaryDirectory(prefix='g5-analysis-test-') as t:
   p=pathlib.Path(t)/'draws.jsonl';r=bootstrap(rows,['a','b'],seed=7,draws=25,private_draw_file=p);rng=random.Random(7)
   for d in map(json.loads,p.read_text().splitlines()):
    sample=[('a','b')[rng.randrange(2)] for _ in range(2)];self.assertEqual(d['task_multiplicities'],{x:sample.count(x) for x in set(sample)});ours=sum((10 if x=='a' else 40)*2 for x in sample);none=sum(10 if x=='a' else 40 for x in sample);os=sum(x=='b' for x in sample);ns=len(sample);expected=(ours/os)/(none/ns) if os else None;self.assertEqual(d['ratios']['ours/none']['tokens_per_verified_solve'],expected)
 def test_five_attempt_infra_exhausted_retained_and_all_costs(self):
  rows=[cell('a',a) for a in ARMS];r=rows[2];attempts=[dict(r['attempt_rows'][0],attempt=i,known_tokens_lower_bound=i*10,solved=None,grade_valid=False,connection_infra_failure=True) for i in range(1,6)];r.update(attempt_rows=attempts,requests=5,known_tokens_lower_bound=150,scored_attempt=5,solved=False,status='infra-exhausted');tasks,by=panel(rows,['a']);s=aggregate(tasks,by);self.assertEqual(s['ours']['cells'],1);self.assertEqual(s['ours']['solves'],0);self.assertEqual(s['ours']['infra_exhausted'],1);self.assertEqual(s['ours']['total_tokens'],150);self.assertEqual(s['ours']['retry_overhead_tokens_lower_bound'],140)
 def test_harness_attempt_preserves_cost_above_five_ordinals(self):
  rows=[cell('a',a) for a in ARMS];r=rows[2];attempts=[dict(r['attempt_rows'][0],attempt=i,known_tokens_lower_bound=10,solved=None,grade_valid=False,connection_infra_failure=True,harness_failure=i==3) for i in range(1,7)];r.update(attempt_rows=attempts,requests=6,known_tokens_lower_bound=60,scored_attempt=6,solved=False,status='infra-exhausted');tasks,by=panel(rows,['a']);s=aggregate(tasks,by);self.assertEqual(s['ours']['infra_exhausted'],1);self.assertEqual(s['ours']['total_tokens'],60)
 def test_percentile_linear(self):self.assertEqual(percentile([0,100],.025),2.5)
if __name__=='__main__':unittest.main()
