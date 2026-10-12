import json,pathlib,tempfile,unittest
from analyze import analyze_part
from independent_analysis import check
from native import H,sha
from render_BC_reports import render
class ReportGuards(unittest.TestCase):
 def test_partial_window_not_a_final_report(self):
  with self.assertRaises(AssertionError):render(H/'window-01-canonical.json',H/'window-01-descriptive-analysis.json',H/'window-01-independent-analysis.json')
class CompleteSyntheticPanel(unittest.TestCase):
 """Synthetic local fixtures only; never publish these as experiment results."""
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(prefix='g4-report-test-');root=pathlib.Path(cls.temp.name);cls.source=root/'synthetic.json';cls.analysis=root/'analysis.json';cls.independent=root/'independent.json';cells=[]
  for part,tasks,rounds in [('B',9,3),('C',18,1)]:
   for task in range(tasks):
    for round in range(1,rounds+1):
     for arm in ('none','K','ours','Both'):
      attempt=dict(exact_provider_tokens=None if arm=='K' else 100,known_tokens_lower_bound=50 if arm=='K' else 100,native_timeout=arm=='Both',grader_timeout=arm=='Both');attempts=[attempt]
      if arm=='ours' and task==0 and round==1:attempts=[dict(exact_provider_tokens=10,known_tokens_lower_bound=10,native_timeout=False,grader_timeout=False),attempt]
      cells.append(dict(part=part,task=str(task),round=round,arm=arm,eligibility='control_valid',attempts=attempts,verified_solved=None if arm=='K' else arm!='Both'))
  cls.source.write_text(json.dumps(dict(cells=cells)));cls.analysis.write_text(json.dumps(dict(input_sha256=sha(cls.source),analysis_source_sha256=sha(H/'analyze.py'),parts={p:analyze_part(p,[c for c in cells if c['part']==p]) for p in ('B','C')})));assert check(cls.source,cls.analysis,cls.independent)==[]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_complete_panel_actual_analyzer_schema_renders(self):
  reports=render(self.source,self.analysis,self.independent);self.assertEqual(set(reports),{'B','C'})
  for p,text in reports.items():
   self.assertIn('Unavailable',text);self.assertIn('20000',text);self.assertIn('Undefined draws stay null',text);self.assertIn('all costs retained',text) if p=='C' else self.assertIn('original verifier',text)
   self.assertIn('Unknown grades',text);self.assertIn('these tables alone are not completion',text)
  self.assertIn('|ours|27|28|27|0|0|2710|',reports['B']);self.assertIn('|ours|18|19|18|0|0|1810|',reports['C'])
 def test_changed_canonical_rejected(self):
  path=pathlib.Path(self.temp.name)/'changed.json';data=json.loads(self.source.read_text());data['cells'][0]['verified_solved']=False;path.write_text(json.dumps(data))
  with self.assertRaises(AssertionError):render(path,self.analysis,self.independent)
if __name__=='__main__':unittest.main()
