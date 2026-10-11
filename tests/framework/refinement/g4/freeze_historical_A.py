"""Reuse original canonical Claude measurements, never reconstruct/reprice costs.
132 pruned dev/heldout/real-SWE cells plus16 random-followup cells =148.
Keep both original campaigns and original cost/grade fields, including bounds.
Composite rows reproduce docs/evaluation.md scope; exclude old bundle/candidate.
"""
import csv,hashlib,json,pathlib
H=pathlib.Path(__file__).resolve().parent
REPO=H.parents[3]
WORKSPACE=REPO.parent
MAPPING={'baseline':'none','latest':'ours','karpathy':'K','karpathy_latest':'Both'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 output=H/'historical-A.json'
 if output.exists():raise RuntimeError('Existing historical freeze; verify, do not overwrite')
 sources=[WORKSPACE/'eval/pruned/audit/independent-final147-collection.v4.json',REPO/'tests/eval/random-followup/results/collection.json'];cells=[];stage_checks={}
 for index,path in enumerate(sources):
  source=json.loads(path.read_text());assert not source['source_errors']
  for c in source['cells']:
   if c['arm'] not in MAPPING or c['stage'] not in ('dev','heldout','real_swe'):continue
   assert type(c['total_tokens']) is int and type(c['resolved']) is bool and type(c['usage_complete']) is bool
   task='diagnostic/'+c['stage']+'/'+c['case'] if c['stage']!='real_swe' else 'swe/'+c['instance_id'];cells.append(dict(task=task,arm=MAPPING[c['arm']],round=c['round'],source_campaign='pruned' if index==0 else 'random-followup',original_row=c))
 csvpath=REPO/'tests/eval/pruned/results/comparison.csv'
 for row in csv.DictReader(csvpath.open()):
  arm={'No skill':'none','SoL-Pi':'ours','Karpathy':'K','Karpathy + SoL-Pi':'Both'}.get(row['configuration'])
  if row['stage'] not in ('dev','heldout','real_swe') or not arm:continue
  group=[x['original_row'] for x in cells if x['source_campaign']=='pruned' and x['arm']==arm and x['original_row']['stage']==row['stage']];assert len(group)==int(row['matched_attempts']) and sum(c['resolved'] for c in group)==int(row['solved']) and sum(c['total_tokens'] for c in group)==int(row['total_tokens']);stage_checks[row['stage']+'/'+arm]=True
 assert len(cells)==148 and len(stage_checks)==12
 tables={}
 for arm in MAPPING.values():
  tables[arm]={}
  for suite in ('diagnostic','swe'):
   group=[x['original_row'] for x in cells if x['arm']==arm and x['task'].startswith(suite+'/')];solves=sum(c['resolved'] for c in group);tokens=sum(c['total_tokens'] for c in group);incomplete=[c['run'] for c in group if not c['usage_complete']];assert len(group)==(25 if suite=='diagnostic' else 12)
   tables[arm][suite]=dict(attempts=len(group),verified_solves=solves,original_reported_tokens_or_lower_bound=tokens,original_reported_tokens_per_solve_or_lower_bound=tokens/solves,usage_complete=not incomplete,incomplete_original_records=incomplete,model_timeouts=sum(bool(c.get('timed_out')) for c in group),grade_timeouts=sum(bool(c.get('grade_timed_out')) for c in group))
 assert [tables[a]['diagnostic']['verified_solves'] for a in ('none','ours','K','Both')]==[21,23,19,22];assert [tables[a]['swe']['verified_solves'] for a in ('none','ours','K','Both')]==[9,11,11,8]
 result=dict(status='HISTORICAL_REUSE_ONLY_NO_NEW_MODEL_CALLS',agent='Claude Code2.1.286',reported_model='Qwen3.8-27B-FP8',logical_model='Qwen3.8-27B per user same-model decision',sources={str(p):sha(p) for p in sources+[csvpath,REPO/'docs/evaluation.md',REPO/'tests/report.md']},rows=tables,cells=cells,original_stage_csv_totals_checked=stage_checks,cost_semantics='Original CLI query-pipeline reported estimates, including auxiliary pipeline calls where CLI recorded them. Missing terminal totals remain original lower bounds; calls outside CLI query pipeline excluded. NOT reconstructed provider receipts or billed money.',cross_harness_ratios_informational_only=True,historical_costs_reestimated=False,old_bundle_and_rejected_candidate_excluded=True)
 output.write_text(json.dumps(result,indent=2)+'\n');print('148 original cells reused;12 original stage CSV totals match; original21/23/19/22 diagnostic and9/11/11/8 SWE solves reproduced')
if __name__=='__main__':main()
