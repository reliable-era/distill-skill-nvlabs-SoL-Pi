"""G5 once-only infrastructure classifier; never retries model/cap/timeouts.
Raw bodies remain private; missing usage remains unknown, never fabricated.
"""
import json,pathlib

def model_answered(raw):
 for line in raw.splitlines():
  if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
  try:e=json.loads(line[6:])
  except ValueError:continue
  if e.get('type') in ('response.output_text.delta','response.function_call_arguments.delta') and e.get('delta'):return True
  if e.get('type')=='response.output_item.done' and e.get('item',{}).get('type') in ('function_call','message'):return True
 return False

def classify(row):
 if row.get('attempt',1)>=2:return dict(retry=False,reason='once-only retry exhausted')
 if not row.get('owned_cleanup_verified'):return dict(retry=False,reason='owned cleanup unverified',stop=True)
 if row.get('timeout') or row.get('grader_timeout') or row.get('requests',0)>=60:return dict(retry=False,reason='timeout or request cap')
 if not row.get('native_started'):
  error=row.get('error') or {}
  allowed=error.get('category') in ('image_failure','container_failure_before_native')
  return dict(retry=allowed,reason=error.get('category','unclassified pre-native failure'),stop=not allowed)
 d=pathlib.Path(row['root'])/'transport';ledger=json.loads((d/'ledger.json').read_text())
 if ledger['budget_denials']:return dict(retry=False,reason='request/wall cap denial')
 infrastructure=False;reasons=[]
 for r in ledger['records']:
  raw=(d/f"response-{r['request']}.sse").read_bytes() if (d/f"response-{r['request']}.sse").exists() else b''
  for line in raw.splitlines():
   if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
   try:e=json.loads(line[6:])
   except ValueError:continue
   if e.get('type') in ('response.failed','response.incomplete'):return dict(retry=False,reason='recorded model error/output cap')
  status=r.get('provider_status')
  if isinstance(status,int) and 500<=status<600:infrastructure=True;reasons.append('HTTP5xx')
  if r.get('connection_infra_failure'):infrastructure=True;reasons.append('connection refused/reset')
  if (r.get('client_disconnected') or r.get('error') in ('TimeoutError','RemoteDisconnected','BrokenPipeError')) and not model_answered(raw):infrastructure=True;reasons.append('client disconnected before model answer')
 return dict(retry=infrastructure,reason=','.join(sorted(set(reasons))) if reasons else 'no permitted infrastructure evidence')
