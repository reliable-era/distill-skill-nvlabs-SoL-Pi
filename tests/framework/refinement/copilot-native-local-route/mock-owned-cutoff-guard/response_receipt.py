"""Inspect bounded synthetic SSE receipt. Missing usage stays unavailable."""
import json
def inspect_response(body):
 if not isinstance(body,bytes) or len(body)>65536:raise ValueError('bounded bytes required')
 done=False;finishes=[];usages=[]
 for block in body.split(b'\n\n'):
  if not block:continue
  if done or not block.startswith(b'data: '):raise ValueError('framing/post-DONE')
  raw=block[6:]
  if raw==b'[DONE]':done=True;continue
  event=json.loads(raw)
  finishes.extend(c['finish_reason'] for c in event.get('choices',[]) if c.get('finish_reason'))
  if 'usage' in event:usages.append(event['usage'])
 return {'synthetic_ONLY':True,'done_seen':done,'terminal_count':len(finishes),'usage_event_count':len(usages),'usage':usages[0] if len(usages)==1 else None,'usage_complete':done and len(finishes)==1 and len(usages)==1,'real_model_tokens':None}
