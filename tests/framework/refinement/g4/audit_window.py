"""Independent window receipt/artifact/cleanup reconciliation, no model calls.
Strict missing evidence remains unresolved; never fabricate cost/grade zero.
"""
import argparse,hashlib,json,pathlib,subprocess
from native import H,sha
from transport import usage_from_sse,waiting_zero,save

def audit(number):
 launch=json.loads((H/f'window-{number}-launch.json').read_text());root=pathlib.Path(launch['root']);window=json.loads((H/f'windows/{number}.json').read_text());rows=[];errors=[];pending=[];posts=0;known=0;unknown=0
 for cell in window['cells']:
  path=root/(cell+'-attempts.json')
  if not path.exists():pending.append(cell);continue
  attempts=json.loads(path.read_text())
  for row in attempts:
   attempt=pathlib.Path(row['root']);ledger=json.loads((attempt/'transport/ledger.json').read_text());records=ledger['records'];posts+=ledger['provider_POST'];known+=sum(r['tokens_lower_bound'] for r in records);unknown+=ledger['provider_POST']-sum(bool(r['cost_complete']) for r in records)
   if row['requests']!=ledger['provider_POST'] or len(records)!=ledger['provider_POST']:errors.append(cell+': POST/receipt disagreement')
   if ledger['active_connections'] or not row['owned_cleanup_verified']:errors.append(cell+': owned lifecycle unresolved')
   if row.get('native_started'):
    admission=json.loads((attempt/'admission.json').read_text())
    if not waiting_zero(admission['load']) or not 1<=admission['occupied_slots_after_admission']<=16:errors.append(cell+': admission invalid')
   for record in records:
    n=record['request'];original=attempt/f'transport/request-{n}.json';forwarded=attempt/f'transport/forwarded-request-{n}.json'
    if sha(original)!=record['original_sha256'] or sha(forwarded)!=record['forwarded_sha256']:errors.append(cell+': request hash mismatch')
    request=json.loads(forwarded.read_text())
    if request['max_output_tokens']!=16384 or record['backend']!='127.0.0.1:8000' or record['parent_arm']!=row['arm'] or record['request_role']!='primary':errors.append(cell+': route/cap/attribution mismatch')
    response=attempt/f'transport/response-{n}.sse'
    if response.exists():
     recomputed=usage_from_sse(response.read_bytes(),record['stream_eof'])
     for field in ('usage','response_model','response_models','cost_complete','tokens_lower_bound'):
      if record[field]!=recomputed[field]:errors.append(cell+': raw SSE '+field+' mismatch')
   if row.get('patch_sha256') and sha(attempt/'model.patch')!=row['patch_sha256']:errors.append(cell+': captured patch changed')
   if row.get('native_sha256') and sha(attempt/'native.jsonl')!=row['native_sha256']:errors.append(cell+': native output changed')
   check=subprocess.run(['docker','inspect',row['actor']],capture_output=True,text=True,timeout=20)
   if check.returncode==0 or 'No such' not in check.stderr:errors.append(cell+': actor absence unverified')
   rows.append(dict(cell_id=cell,attempt=row['attempt'],part=row['part'],arm=row['arm'],requests=row['requests'],solved=row['solved'],grade_valid=row['grade_valid'],cost_complete=row['cost_complete'],owned_cleanup_verified=row['owned_cleanup_verified'],attempt_sha256=sha(attempt/'attempt-result.json'),ledger_sha256=sha(attempt/'transport/ledger.json'),artifact_hashes={str(p.relative_to(attempt)):sha(p) for p in attempt.rglob('*') if p.is_file()}))
 live=subprocess.run(['ps','-p',str(launch['pid']),'-o','args='],capture_output=True,text=True).stdout.strip();result=dict(window=number,root=str(root),scheduler_live=bool(live),pending_cells=pending,rows=rows,provider_POSTs=posts,known_tokens_lower_bound=known,unknown_cost_requests=unknown,errors=errors,transport_artifact_cleanup_verified=not errors and not pending and not live,grade_reconciliation_pending=[r['cell_id'] for r in rows if not r['grade_valid']],not_a_completion_audit=True,model_calls_by_audit=0);save(H/f'window-{number}-audit.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print({k:v for k,v in r.items() if k!='rows'})
