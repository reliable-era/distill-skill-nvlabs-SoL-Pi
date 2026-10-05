"""Bounded raw chat-completions receipt via existing SSEBridge collector.
Offline collector only: caller owns stop/admission, deadlines, source pinning,
passive drain and file persistence. No provider/native launch or normalization.
"""
from prospective_sse_bridge import SSEBridge

def nonnegative(value):
 if type(value) is not int or value<0:raise ValueError('nonnegative integer count required')
 return value
class ChatReceipt:
 def __init__(self,emit,model,max_bytes=2097152):
  if not isinstance(model,str) or not model:raise ValueError('fixed model required')
  if type(max_bytes) is not int or max_bytes<=0:raise ValueError('positive byte cap required')
  self.bridge=SSEBridge(emit,max_bytes=max_bytes);self.model=model;self.finished=False;self.feed_error=None
 def feed(self,chunk):
  if self.finished:raise ValueError('receipt already finalized')
  try:self.bridge.feed(chunk)
  except Exception as e:self.feed_error=type(e).__name__;raise
 def finish(self,stream_eof):
  if self.finished:raise ValueError('receipt already finalized')
  self.finished=True;self.bridge.finished=True
  reasons=[];usage=None;done=False;terminal=[];usages=[];ids=set()
  if self.feed_error is not None:reasons.append('collector_feed_error')
  if stream_eof is not True:reasons.append('upstream_EOF_unverified')
  if self.bridge.pending or self.bridge.malformed_data:reasons.append('incomplete_or_malformed_SSE_framing')
  for event in self.bridge.events:
   if done:reasons.append('event_after_DONE')
   if event=='[DONE]':done=True;continue
   if not isinstance(event,dict):reasons.append('unsupported_event');continue
   identity=event.get('id')
   if not isinstance(identity,str) or not identity:reasons.append('response_identity_missing')
   else:ids.add(identity)
   if event.get('model')!=self.model:reasons.append('model_mismatch_or_missing')
   if event.get('object')!='chat.completion.chunk':reasons.append('unsupported_wire_event')
   choices=event.get('choices')
   if not isinstance(choices,list):reasons.append('choices_unavailable');continue
   for choice in choices:
    if not isinstance(choice,dict) or type(choice.get('index')) is not int or choice.get('index')!=0:reasons.append('unsupported_choice');continue
    if choice.get('finish_reason') is not None:terminal.append(choice['finish_reason'])
   if 'usage' in event:usages.append(event['usage'])
  if len(ids)!=1:reasons.append('response_identity_ambiguous')
  if not done:reasons.append('DONE_missing')
  if len(terminal)!=1 or terminal[0] not in ['stop','tool_calls']:reasons.append('terminal_missing_duplicate_or_unsupported')
  if len(usages)!=1:reasons.append('usage_missing_or_duplicate')
  else:
   try:
    raw=usages[0];i=nonnegative(raw['prompt_tokens']);o=nonnegative(raw['completion_tokens']);total=nonnegative(raw['total_tokens'])
    if total!=i+o:raise ValueError('inclusive_total_mismatch')
    # Optional detail absence is unknown, never manufactured zero.
    cached=raw.get('prompt_tokens_details',{}).get('cached_tokens');reasoning=raw.get('completion_tokens_details',{}).get('reasoning_tokens')
    if cached is not None and nonnegative(cached)>i:raise ValueError('cache_subset_invalid')
    if reasoning is not None and nonnegative(reasoning)>o:raise ValueError('reasoning_subset_invalid')
    usage={'input_tokens':i,'output_tokens':o,'inclusive_gross_tokens':total,'cache_read_tokens':cached,'reasoning_tokens':reasoning}
   except (KeyError,TypeError,AttributeError,ValueError):reasons.append('usage_invalid');usage=None
  complete=not reasons
  return {'receipt_complete':complete,'reasons':list(dict.fromkeys(reasons)),'observed_usage':usage,'eligible_usage':usage if complete else None,'raw_bytes':bytes(self.bridge.raw),'consumer_detached':self.bridge.detached,'DONE_seen':done,'terminal_count':len(terminal),'usage_event_count':len(usages),'cache_reasoning_not_added':True,'provider_source_identity_checked':False,'native_usage_completeness_NOT_proven':True,'real_scoring_eligibility_NOT_established':True}
