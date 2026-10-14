"""Read-only G5 closed-attempt receipt reconstruction from raw bytes.
No service/model calls. Does not infer unknown identities/costs from labels.
"""
import hashlib,json,pathlib
from common import save,sha
PEER='127.0.0.1:8000'

def valid_usage(u):return isinstance(u,dict) and all(type(u.get(k)) is int and u[k]>=0 for k in ('input_tokens','output_tokens','total_tokens')) and u['total_tokens']==u['input_tokens']+u['output_tokens']

def reconstruct(raw,record,error_body=None):
 events=[];malformed=False
 for line in raw.splitlines():
  if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
  try:events.append(json.loads(line[6:]))
  except ValueError:malformed=True
 terminal=[e for e in events if e.get('type') in ('response.completed','response.incomplete','response.failed')];u=terminal[-1].get('response',{}).get('usage') if terminal else None;models=list(dict.fromkeys(e['response']['model'] for e in events if isinstance(e.get('response'),dict) and isinstance(e['response'].get('model'),str)));lower=u['total_tokens'] if valid_usage(u) else 0;complete=bool(record['stream_eof'] and not malformed and len(terminal)==1 and valid_usage(u) and record['error'] is None and record['provider_status']==200)
 if error_body is not None:
  try:p=json.loads(error_body)
  except ValueError:p=None
  if isinstance(p,dict):
   response=p.get('response',p)
   if isinstance(response,dict):
    if isinstance(response.get('model'),str):models=[response['model']]
    if isinstance(response.get('usage'),dict):
     u=response['usage']
     if valid_usage(u):lower=u['total_tokens']
 zero=record.get('proven_zero_model_refusal',False)
 if zero:
  assert record['error']=='ConnectionRefusedError' and record['provider_status'] is None and not raw and error_body is None
  complete=True;lower=0
 return dict(usage=u,tokens_lower_bound=lower,cost_complete=complete,response_models=models,response_model=models[0] if len(models)==1 else None)

def audit(row):
 root=pathlib.Path(row['root']);transport=root/'transport';proof=dict(cell_id=row['cell_id'],attempt=row['attempt'],requests=row['requests'],raw_receipts_reconciled=False)
 if not row['native_started']:
  assert row['requests']==row['known_tokens_lower_bound']==0 and row['cost_complete'];assert not (transport/'ledger.json').exists() or json.loads((transport/'ledger.json').read_text())['provider_POST']==0;proof.update(raw_receipts_reconciled=True,zero_model_calls=True);return proof
 ledger=json.loads((transport/'ledger.json').read_text());assert ledger['backend']==PEER and ledger['parent_arm']==row['arm'] and ledger['request_role']=='primary';assert ledger['active_connections']==0;records=ledger['records'];assert len(records)==ledger['provider_POST']==row['requests']<=60;assert [r['request'] for r in records]==list(range(1,len(records)+1));identities={};unknown=0
 for r in records:
  n=r['request'];assert r['backend']==PEER and r['parent_arm']==row['arm'] and r['request_role']=='primary' and r['path']=='/v1/responses' and r['output_cap']==16384;original=transport/f'request-{n}.json';forwarded=transport/f'forwarded-request-{n}.json';assert sha(original)==r['original_sha256'] and sha(forwarded)==r['forwarded_sha256'];a=json.loads(original.read_bytes());b=json.loads(forwarded.read_bytes());assert a.get('stream') is True and a.get('model')==ledger['model'];a['max_output_tokens']=16384;assert a==b,'Forwarded prompt/body drift';response=transport/f'response-{n}.sse';raw=response.read_bytes() if response.exists() else b'';assert hashlib.sha256(raw).hexdigest()==r['response_sha256'] and len(raw)==r['response_bytes'];error=transport/f'provider-error-{n}.body';body=error.read_bytes() if error.exists() else None
  if body is not None:assert sha(error)==r['provider_error_sha256']
  derived=reconstruct(raw,r,body)
  for key,value in derived.items():assert r[key]==value,(n,key,'Receipt/raw reconstruction mismatch')
  if r['response_model'] is None:unknown+=1
  else:identities[r['response_model']]=identities.get(r['response_model'],0)+1
 assert row['known_tokens_lower_bound']==sum(r['tokens_lower_bound'] for r in records);assert row['cost_complete']==all(r['cost_complete'] for r in records);proof.update(raw_receipts_reconciled=True,ledger_sha256=sha(transport/'ledger.json'),known_tokens_lower_bound=row['known_tokens_lower_bound'],cost_complete=row['cost_complete'],response_identity_counts=identities,unknown_response_identity_requests=unknown,records=len(records));return proof
