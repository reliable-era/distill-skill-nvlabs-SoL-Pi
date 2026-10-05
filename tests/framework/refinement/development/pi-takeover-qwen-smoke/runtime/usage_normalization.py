"""Request-scoped conservative normalization of parsed SGLang SSE data events.

Pass dictionaries in stream order and the literal '[DONE]' sentinel. This does
not certify native helper/compaction scope, cache billing components or dollars.
"""
def normalize_request(events,api,stream_eof):
 result={'gross_usage_complete':False,'gross_tokens':None,'input_tokens_inclusive':None,'output_tokens_inclusive':None,'cache_read_tokens_reported':None,'cache_write_tokens_reported':None,'reasoning_tokens_reported':None,'cache_components_complete':False,'error':None}
 def fail(reason):result['error']=reason;return result
 if stream_eof is not True:return fail('stream_not_eof')
 if not isinstance(events,(list,tuple)):return fail('events_not_sequence')
 if api=='responses':
  terminals=[(i,e) for i,e in enumerate(events) if isinstance(e,dict) and e.get('type')=='response.completed']
  if len(terminals)!=1:return fail('missing_or_duplicate_response_terminal')
  index,event=terminals[0];response=event.get('response')
  if not isinstance(response,dict) or response.get('status') not in (None,'completed'):return fail('invalid_terminal_response')
  usage=response.get('usage')
  if not isinstance(usage,dict):return fail('terminal_usage_missing')
  if any(isinstance(e,dict) and e.get('type') in ('response.failed','response.incomplete','error') for e in events):return fail('error_event')
  if index!=len(events)-1:return fail('events_after_terminal')
  fields=('input_tokens','output_tokens','total_tokens');input_details=usage.get('input_tokens_details');output_details=usage.get('output_tokens_details');reasoning=output_details.get('reasoning_tokens') if isinstance(output_details,dict) else None
 elif api=='chat':
  dones=[i for i,e in enumerate(events) if e=='[DONE]']
  terminals=[(i,e) for i,e in enumerate(events) if isinstance(e,dict) and e.get('choices')==[] and isinstance(e.get('usage'),dict)]
  if len(dones)!=1 or dones[0]!=len(events)-1:return fail('missing_or_duplicate_chat_done')
  if len(terminals)!=1 or terminals[0][0]!=dones[0]-1:return fail('missing_or_duplicate_final_chat_usage')
  if any(isinstance(e,dict) and e.get('error') for e in events):return fail('error_event')
  usage=terminals[0][1]['usage'];fields=('prompt_tokens','completion_tokens','total_tokens');input_details=usage.get('prompt_tokens_details');reasoning=usage.get('reasoning_tokens')
  if reasoning is None:
   details=usage.get('completion_tokens_details');reasoning=details.get('reasoning_tokens') if isinstance(details,dict) else None
 else:return fail('unsupported_api')
 values=[usage.get(k) for k in fields]
 if any(type(v) is not int or v<0 for v in values):return fail('missing_or_invalid_token_fields')
 inp,out,total=values
 if total<=0 or inp+out!=total:return fail('zero_or_inconsistent_total')
 cache=input_details.get('cached_tokens') if isinstance(input_details,dict) else None
 write=input_details.get('cache_write_tokens') if isinstance(input_details,dict) else None
 for name,value,bound in [('cache_read',cache,inp),('cache_write',write,inp),('reasoning',reasoning,out)]:
  if value is not None and (type(value) is not int or value<0 or value>bound):return fail('invalid_'+name+'_subset')
 if cache is not None and write is not None and cache+write>inp:return fail('cache_subsets_exceed_input')
 result.update(gross_usage_complete=True,gross_tokens=total,input_tokens_inclusive=inp,output_tokens_inclusive=out,cache_read_tokens_reported=cache,cache_write_tokens_reported=write,reasoning_tokens_reported=reasoning)
 return result
