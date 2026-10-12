"""Independent retry receipt/hash/route/cap/active-admission/actual-absence audit.
Only B/C-owned original/retry names/artifacts; no A access/model calls.
"""
import json,pathlib,subprocess
from native import H,sha
from transport import usage_from_sse,save

def admission_valid(a):
 rows=a.get('load',{}).get('body');local={'127.0.0.1:18001','127.0.0.1:18002'};active=local|{'127.0.0.1:9012'};disabled={'10.193.104.97:18001','10.193.104.97:18002'}
 if not isinstance(rows,list) or any(not isinstance(r,dict) or r.get('backend') not in active|disabled for r in rows):return False
 selected=[r for r in rows if r['backend'] in active]
 return local<={r['backend'] for r in selected} and all(type(r.get('num_waiting_reqs')) is int and r['num_waiting_reqs']==0 and type(r.get('num_reqs')) is int and r['num_reqs']>=0 for r in selected) and 1<=a.get('occupied_slots_after_admission',0)<=8 and a.get('BC_reserved_slots')==8 and a.get('supervisor_A_reserved_slots')==8 and a.get('attempt')==2

def audit():
 launch=json.loads((H/'BC-retry-launch.json').read_text());root=pathlib.Path(launch['root']);manifest=json.loads((H/'BC-retry-manifest.json').read_text());proofs=[];pending=[];errors=[];posts=known=unknown=0;samples=json.loads((root/'admission-observations.json').read_text()) if (root/'admission-observations.json').exists() else []
 for m in manifest['rows']:
  cell=m['cell_id'];old=pathlib.Path(m['original_root']);assert sha(old/'attempt-result.json')==m['original_attempt_sha256'] and sha(old/'transport/ledger.json')==m['original_ledger_sha256'];p=root/(cell+'-attempts.json')
  if not p.exists():pending.append(cell);continue
  rows=json.loads(p.read_text());assert len(rows)==1 and rows[0]['attempt']==2;row=rows[0];d=pathlib.Path(row['root']);ledger=json.loads((d/'transport/ledger.json').read_text());records=ledger['records'];bad=[];posts+=len(records);known+=sum(r['tokens_lower_bound'] for r in records);unknown+=sum(not r['cost_complete'] for r in records)
  if row['cell_id']!=cell or row['part']!=m['part'] or row['task']!=m['task'] or row['arm']!=m['arm']:bad.append('frozen identity/arm')
  if ledger['provider_POST']!=row['requests'] or ledger['provider_POST']!=len(records) or not 0<=row['requests']<=60:bad.append('counts/60 request bound')
  if row.get('wall_seconds') is not None and not 0<=row['wall_seconds']<=7200:bad.append('7200 native wall bound')
  if ledger['active_connections'] or not row['owned_cleanup_verified']:bad.append('broker/cleanup unresolved')
  if row.get('native_started'):
   a=json.loads((d/'admission.json').read_text())
   if not admission_valid(a) or a['cell_id']!=cell or a['load'] not in samples:bad.append('raw matched active-only/reserved8 admission')
  for r in records:
   n=r['request'];original=d/f'transport/request-{n}.json';forwarded=d/f'transport/forwarded-request-{n}.json'
   if sha(original)!=r['original_sha256'] or sha(forwarded)!=r['forwarded_sha256']:bad.append('request hash')
   req=json.loads(forwarded.read_text())
   if req.get('max_output_tokens')!=16384 or r['backend']!='127.0.0.1:8000' or r['request_role']!='primary' or r['parent_arm']!=m['arm']:bad.append('output/route/attribution')
   response=d/f'transport/response-{n}.sse'
   if response.exists():
    v=usage_from_sse(response.read_bytes(),r['stream_eof'])
    if any(r[k]!=v[k] for k in ('usage','response_model','response_models','cost_complete','tokens_lower_bound')):bad.append('raw SSE reconciliation')
   elif r.get('provider_error_sha256') and sha(d/f'transport/provider-error-{n}.body')!=r['provider_error_sha256']:bad.append('error body hash')
  if any(x.get('forwarded') is not False or x.get('reason') not in ('request_cap','wall_cap') for x in ledger['budget_denials']):bad.append('unforwarded denial')
  if any(x['reason']=='request_cap' for x in ledger['budget_denials']) and len(records)!=60:bad.append('cap/denial disagreement')
  for f,k in [('model.patch','patch_sha256'),('native.jsonl','native_sha256')]:
   if row.get(k) and sha(d/f)!=row[k]:bad.append('captured/native hash')
  ps=subprocess.run(['docker','inspect',row['actor']],capture_output=True,text=True,timeout=20)
  if ps.returncode==0 or 'No such' not in ps.stderr:bad.append('actual owned actor absence')
  if bad:errors.append(dict(cell_id=cell,checks=bad))
  proofs.append(dict(cell_id=cell,attempt=2,requests=len(records),grade_valid=row['grade_valid'],solved=row['solved'],attempt_sha256=sha(d/'attempt-result.json'),ledger_sha256=sha(d/'transport/ledger.json'),all_checks_passed=not bad,artifact_hashes={str(f.relative_to(d)):sha(f) for f in d.rglob('*') if f.is_file()}))
 live=bool(subprocess.run(['ps','-p',str(launch['pid']),'-o','args='],capture_output=True,text=True).stdout.strip());result=dict(rows=proofs,pending_cells=pending,errors=errors,scheduler_live=live,provider_POSTs=posts,known_tokens_lower_bound=known,unknown_cost_requests=unknown,transport_artifact_cleanup_verified=not pending and not errors and not live,original_records_retained=True,attempt3_authorized=False,not_a_goal_completion_audit=True,model_calls=0,auditor_sha256=sha(__file__),load_coverage='Only advertised routed entries; honey absent if metadata omits it, not imputed zero');save(H/'BC-retry-transport-audit.json',result);return result
if __name__=='__main__':
 r=audit();print({k:v for k,v in r.items() if k!='rows'})
