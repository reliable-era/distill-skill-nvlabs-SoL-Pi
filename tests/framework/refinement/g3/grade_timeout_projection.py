"""Named exact-artifact unsuccessful-test timeout projections, raw grade retained.
Only diagnosed zero-step loops proved to hang an original accepted test. This is
not a solve rescue, task exclusion, model-cell retry, or timeout budget increase.
"""
import json,pathlib,re
from run_cell import H,sha,tree

def apply(value):
 file=H/'grade-timeout-repair.json'
 if not file.exists():return value
 sidecar=json.loads(file.read_text());replay=json.loads((H/'grade-timeout-replay-result.json').read_text());assert sha(H/'grade-timeout-replay-result.json')==sidecar['replay_result_sha256'];assert replay['model_calls']==0 and replay['all_owned_grader_containers_absent'];gold=next(r for r in replay['rows'] if r['cell_id']=='gold');assert gold['exit']==0 and sha(gold['log'])==gold['log_sha256']
 repairs=[]
 for row in value['rows']:
  evidence=sidecar['cells'].get(row['cell_id'])
  if not evidence:continue
  assert row['solved'] is None and not row['grade_valid'];d=pathlib.Path(evidence['root']);raw=json.loads((d/'attempt-result.json').read_text());assert sha(d/'attempt-result.json')==evidence['raw_attempt_result_sha256'];assert raw['verifier_exit']==2 and not raw['grade_valid'] and raw['solved'] is None;assert sha(d/'verifier.log')==raw['verifier_sha256'];assert (d/'verifier.log').read_text().strip()=='TimeoutExpired';assert tree(d/'final-work')==raw['final_work_hashes'];assert sha(d/'final-work/sum-of-multiples.js')==evidence['solution_sha256'];assert sha(d/'grader/tests/sum-of-multiples.spec.js')==evidence['original_test_sha256']
  rr=next(r for r in replay['rows'] if r['cell_id']==row['cell_id']);assert rr['exit']==2 and 180<=rr['seconds']<300 and sha(rr['log'])==rr['log_sha256'];assert pathlib.Path(rr['log']).read_text().strip()=='TimeoutExpired';assert rr['captured_work_hashes']==raw['final_work_hashes']
  # Inspect only exact captured source and original test witness. Both loops
  # initialize/advance by the supplied factor; factor0 never changes the index.
  source=(d/'final-work/sum-of-multiples.js').read_text();test=(d/'grader/tests/sum-of-multiples.spec.js').read_text();assert 'sum([0], 1)' in test
  if evidence['loop_variable']=='multiple':assert 'let multiple = factor; multiple < limit; multiple += factor' in source
  else:assert 'let value = multiple; value < limit; value += multiple' in source
  row.update(solved=False,grade_valid=True,native_timeout=row['timeout'],grader_timeout=True,timeout=True,grade_repair='Exact original-test180s timeout verified as captured zero-step nontermination; unsuccessful original test outcome, raw exit2/null grade preserved')
  repairs.append(dict(cell_id=row['cell_id'],sidecar_sha256=sha(file),model_requests_added=0,original_verifier_exit=2,original_grade_unknown=True,projected_solved=False,original_grader_budget_unchanged_seconds=180))
 value['grade_timeout_repairs']=repairs;return value
