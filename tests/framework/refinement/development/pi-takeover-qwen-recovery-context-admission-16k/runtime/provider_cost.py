from usage_normalization import normalize_request
"""Prospective SGLang-specific length-cap cost rule; original normalizer unchanged."""
import copy

def protocol_check(result):
 result['protocol_valid']=None
 result['protocol_violations']=[]
 if result['provider_cost_complete']:
  if result['output_tokens_inclusive']>16384:
   result['protocol_valid']=False
   result['protocol_violations']=['reported_output_tokens_exceed_16384']
  else:result['protocol_valid']=True
 return result

def normalize_cost(events,stream_eof):
 strict=normalize_request(events,'responses',stream_eof)
 strict['generation_complete']=strict['gross_usage_complete']
 strict['provider_cost_complete']=strict['gross_usage_complete']
 if strict['gross_usage_complete']:return protocol_check(strict)
 if stream_eof is not True or not isinstance(events,(list,tuple)):return protocol_check(strict)
 terminals=[e for e in events if isinstance(e,dict) and e.get('type')=='response.completed']
 if len(terminals)!=1:return protocol_check(strict)
 response=terminals[0].get('response',{})
 if response.get('status')!='incomplete' or response.get('incomplete_details')!={'reason':'max_output_tokens'} or type(response.get('max_output_tokens')) is not int or response['max_output_tokens']!=16384:return protocol_check(strict)
 usage=response.get('usage',{})
 if type(usage.get('output_tokens')) is not int:return protocol_check(strict)
 adapted=copy.deepcopy(events)
 next(e for e in adapted if isinstance(e,dict) and e.get('type')=='response.completed')['response']['status']='completed'
 result=normalize_request(adapted,'responses',stream_eof)
 result['generation_complete']=False
 result['provider_cost_complete']=result['gross_usage_complete']
 result['normalization_scope']='Pinned SGLang unique response.completed length-capped terminal; final usage+EOF; provider traffic only'
 return protocol_check(result)
