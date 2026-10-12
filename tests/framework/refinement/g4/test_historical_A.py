import json,random,unittest
from native import H
class HistoricalEvidenceTests(unittest.TestCase):
 def test_original_table_amounts_not_reestimated(self):
  original=json.loads((H/'historical-A.json').read_text());self.assertEqual(len(original['cells']),148)
  for arm,groups in original['rows'].items():
   for kind,row in groups.items():
    cells=[c for c in original['cells'] if c['arm']==arm and c['task'].startswith('diagnostic/')==(kind=='diagnostic')];self.assertEqual(sum(c['original_row']['total_tokens'] for c in cells),row['original_reported_tokens_or_lower_bound']);self.assertEqual(sum(c['original_row']['resolved'] is True for c in cells),row['verified_solves'])
 def test_all_draws_and_undefined_blocked_rows_retained(self):
  analysis=json.loads((H/'analysis-A-historical.json').read_text());self.assertEqual(analysis['seed'],2026101211);self.assertEqual(analysis['task_clusters'],16)
  for name,row in analysis['comparisons'].items():
   self.assertEqual(len(row['draws']),20000);self.assertEqual(sum(v is None for v in row['draws']),row['undefined_draws']);self.assertEqual(sum(v is not None for v in row['draws']),row['defined_draws'])
   if name.startswith('solpi'):self.assertEqual(row['defined_draws'],0);self.assertEqual(row['bootstrap95'],[None,None])
if __name__=='__main__':unittest.main()
