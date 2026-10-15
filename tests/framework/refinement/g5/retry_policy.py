"""G5 infrastructure classifier;terminal5xx max5 per user2026-10-16.
Other infrastructure remains once-only;no ordinary model/cap/timeout reruns.
Raw bodies remain private; missing usage remains unknown, never fabricated.
"""
import json,pathlib,re

def model_answered(raw):
 for line in raw.splitlines():
  if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
  try:e=json.loads(line[6:])
  except ValueError:continue
  if e.get('type') in ('response.output_text.delta','response.function_call_arguments.delta') and e.get('delta'):return True
  if e.get('type')=='response.output_item.done' and e.get('item',{}).get('type') in ('function_call','message'):return True
 return False

def native_http5xx(raw):
 """Only native error/turn.failed events, never tool output or task text."""
 codes=set();types=set();final_5xx=False;events=[]
 for index,line in enumerate(raw.splitlines(),1):
  try:e=json.loads(line)
  except (ValueError,UnicodeDecodeError):continue
  if not isinstance(e,dict):continue
  if e.get('type')=='turn.completed':final_5xx=False
  if e.get('type') not in ('error','turn.failed'):continue
  event_codes=set();error=e.get('error') or {};messages=[e.get('message')]
  if isinstance(error,dict):
   messages.append(error.get('message'))
   for key in ('status','status_code','http_status'):
    if type(error.get(key)) is int and 500<=error[key]<600:event_codes.add(error[key])
  for message in messages:
   if not isinstance(message,str):continue
   found=re.findall(r'(?i)\b(?:unexpected\s+status|HTTP(?:/\d(?:\.\d)?)?(?:\s+(?:status|error))?(?:\s+code)?|status(?:\s+code)?)\s*[:=]?\s*(5\d{2})\b',message)
   if found:event_codes.update(map(int,found))
  final_5xx=bool(event_codes)
  if event_codes:
   codes.update(event_codes);types.add(e['type']);events.append(dict(line=index,event_type=e['type'],status_codes=sorted(event_codes),event_time=e.get('timestamp') or e.get('time')))
 return dict(connection_infra_failure=final_5xx,native_http5xx_status_codes=sorted(codes),native_http5xx_event_types=sorted(types),native_http5xx_events=events)

def classify(row):
 f=pathlib.Path(row['root'])/'native.jsonl' if row.get('root') else None
 native=native_http5xx(f.read_bytes() if f and f.exists() else b'')
 def decision(**kw):return dict(**kw,**native)
 if not row.get('owned_cleanup_verified'):return decision(retry=False,reason='owned cleanup unverified',stop=True)
 if row.get('timeout') or row.get('grader_timeout'):return decision(retry=False,reason='timeout')
 if native['connection_infra_failure']:return decision(retry=row.get('budget_attempt',row.get('attempt',1))<5,reason='terminal native HTTP5xx',infra_exhausted=row.get('budget_attempt',row.get('attempt',1))>=5)
 if row.get('attempt',1)>=2:return decision(retry=False,reason='once-only other-infrastructure retry exhausted')
 if row.get('requests',0)>=60:return decision(retry=False,reason='request cap')
 if not row.get('native_started'):
  error=row.get('error') or {}
  allowed=error.get('category') in ('image_failure','container_failure_before_native')
  return decision(retry=allowed,reason=error.get('category','unclassified pre-native failure'),stop=not allowed)
 d=pathlib.Path(row['root'])/'transport';ledger=json.loads((d/'ledger.json').read_text())
 if ledger['budget_denials']:return decision(retry=False,reason='request/wall cap denial')
 infrastructure=native['connection_infra_failure'];reasons=['native HTTP5xx'] if infrastructure else []
 for r in ledger['records']:
  raw=(d/f"response-{r['request']}.sse").read_bytes() if (d/f"response-{r['request']}.sse").exists() else b''
  for line in raw.splitlines():
   if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
   try:e=json.loads(line[6:])
   except ValueError:continue
   response=e.get('response') or {}
   if e.get('type') in ('response.failed','response.incomplete','error') or (isinstance(response,dict) and (response.get('status') in ('failed','incomplete') or response.get('error'))):return decision(retry=False,reason='recorded model error/output cap')
  status=r.get('provider_status')
  if isinstance(status,int) and 500<=status<600:infrastructure=True;reasons.append('HTTP5xx')
  if r.get('connection_infra_failure'):infrastructure=True;reasons.append('connection refused/reset')
  if (r.get('client_disconnected') or r.get('error') in ('TimeoutError','RemoteDisconnected','BrokenPipeError')) and not model_answered(raw):infrastructure=True;reasons.append('client disconnected before model answer')
 return decision(retry=infrastructure,reason=','.join(sorted(set(reasons))) if reasons else 'no permitted infrastructure evidence')
