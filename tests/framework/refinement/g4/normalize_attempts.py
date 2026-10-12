"""Canonical separate-part cells from reconciled windows, all attempts charged.
Original grades never overwritten: explicit captured-only repair projections.
Unattempted/excluded/blocked cells aren't zero costs or model failures.
"""
import argparse,json,pathlib
from native import H,sha
from transport import save

def normalize(windows):
 plan=json.loads((H/'preregistration.json').read_text());order=json.loads((H/'queue-order.json').read_text());lookup={c['cell_id']:dict(c,attempts=[],verified_solved=None,eligibility=('A blocked; not a failed-control exclusion' if c['part']=='A' else 'control_valid' if c['task'] in plan['eligible_tasks'][c['part']] else 'failed_original_control_exclusion')) for rows in order['parts'].values() for c in rows};seen=set();provenance=[]
 for window in windows:
  audited=json.loads((H/f'window-{window}-audit.json').read_text())
  if not audited['transport_artifact_cleanup_verified']:raise RuntimeError('Require final independent window audit')
  launch=json.loads((H/f'window-{window}-launch.json').read_text());root=pathlib.Path(launch['root']);cells=json.loads((H/f'windows/{window}.json').read_text())['cells'];projection=H/f'window-{window}-C-grade-projection.json';repairs={r['cell_id']:r for r in json.loads(projection.read_text())['rows']} if projection.exists() else {}
  for cell in cells:
   if cell in seen:raise RuntimeError('Cell appears in multiple inference windows')
   seen.add(cell);canonical=lookup[cell];raw=json.loads((root/(cell+'-attempts.json')).read_text());assert 1<=len(raw)<=2
   for row in raw:
    attempt=pathlib.Path(row['root']);ledger=json.loads((attempt/'transport/ledger.json').read_text());records=ledger['records'];complete=len(records)==ledger['provider_POST'] and all(r['cost_complete'] for r in records);known=sum(r['tokens_lower_bound'] for r in records);assert row['requests']==ledger['provider_POST'];receipt=dict(attempt=row['attempt'],exact_provider_tokens=known if complete else None,known_tokens_lower_bound=known,requests=ledger['provider_POST'],native_timeout=row['timeout'],grader_timeout=row['grader_timeout'],native_wall_seconds=row.get('wall_seconds'),original_error=row['error'],original_grade_valid=row['grade_valid'],original_solved=row['solved'],original_attempt_sha256=sha(attempt/'attempt-result.json'),ledger_sha256=sha(attempt/'transport/ledger.json'),receipt_root=str(attempt/'transport'),response_model_usage=[dict(request=r['request'],parent_arm=r['parent_arm'],request_role=r['request_role'],response_model=r['response_model'],response_models=r['response_models'],response_model_unknown_reason=r['response_model_unknown_reason'],usage=r['usage'],cost_complete=r['cost_complete']) for r in records]);canonical['attempts'].append(receipt)
   last=raw[-1];canonical['verified_solved']=last['solved'] if last['grade_valid'] else None
   if cell in repairs:
    repair=repairs[cell];assert repair['attempt']==last['attempt'] and repair['original_attempt_sha256']==sha(pathlib.Path(last['root'])/'attempt-result.json');result=pathlib.Path(repair['authoritative_grade_root'])/'grade-result.json';assert sha(result)==repair['authoritative_grade_sha256'];grade=json.loads(result.read_text());assert grade['owned_containers_absent'];canonical['verified_solved']=grade['solved'] if grade['grade_valid'] else None;canonical['grade_reconciliation']=repair
  provenance.append(dict(window=window,audit_sha256=sha(H/f'window-{window}-audit.json'),launch_sha256=sha(H/f'window-{window}-launch.json'),grade_projection_sha256=sha(projection) if projection.exists() else None))
 return dict(cells=list(lookup.values()),provenance=provenance,normalizer_sha256=sha(__file__),attempted_cells=len(seen),all_attempts_charged=True,blocked_A_not_imputed=True,historical_A_not_in_this_fresh_cell_input=True,model_calls=0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=pathlib.Path);p.add_argument('windows',nargs='+');a=p.parse_args();save(a.output,normalize(a.windows))
