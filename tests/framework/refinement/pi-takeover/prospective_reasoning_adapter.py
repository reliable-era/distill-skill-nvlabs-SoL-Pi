"""Offline prospective metadata derivation;raw validation/receipts remain untouched.
Not installed in any broker. Not permission to reprice historical cohorts.
"""
import copy,pathlib,sys
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime'))
from provider_cost import normalize_cost
SOURCE='4f069fbba82a77360fec29330edf5f6cf3740960984c5e1d01ef4e385c90ecaa'
MODEL='Qwen3.8-27B-FP8'
SOURCE_PINS={'dflash_worker_sha256':'5fd1e3f16c5725e4d56ac327515b56cfd06de52f94b069332d43faad7d771482','dflash_utils_sha256':'61feff7656e2e4c157e472a1140ea9525200f5003f9bf0de639b50424e776018','schedule_batch_sha256':'348cd231d705a618c3d4a80a356470f92a430a941c97b429a8b5d16336fd035c','dflash_kernel_sha256':'21f11619531f493bbe9f71d465912ca707f2d722991832e446ff65aecb40528c'}

def derive(events,stream_eof,provenance):
 raw=normalize_cost(events,stream_eof)
 result={'raw_cost':raw,'raw_provider_protocol_valid':raw.get('protocol_valid'),'correction_applied':False,'derived_cost':raw,'deployment_approved':False}
 if raw.get('error')!='invalid_reasoning_subset':return result
 expected={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8}
 if not isinstance(provenance,dict) or type(provenance.get('speculative_num_draft_tokens')) is not int or any(provenance.get(k)!=v for k,v in expected.items()) or provenance.get('peer') not in ['127.0.0.1:18001','127.0.0.1:18002']:return result
 if stream_eof is not True or not isinstance(events,(list,tuple)):return result
 terminals=[e for e in events if isinstance(e,dict) and e.get('type')=='response.completed']
 if len(terminals)!=1:return result
 response=terminals[0].get('response',{})
 if response.get('model')!=MODEL or response.get('status')!='incomplete' or response.get('incomplete_details')!={'reason':'max_output_tokens'} or type(response.get('max_output_tokens')) is not int or response['max_output_tokens']!=8192:return result
 usage=response.get('usage',{});details=usage.get('output_tokens_details',{})
 if not isinstance(details,dict):return result
 output=usage.get('output_tokens');reasoning=details.get('reasoning_tokens')
 if type(output) is not int or type(reasoning) is not int or not 8190<=output<=8192 or not 1<=reasoning-output<=7:return result
 adapted=copy.deepcopy(events)
 next(e for e in adapted if isinstance(e,dict) and e.get('type')=='response.completed')['response']['usage']['output_tokens_details']['reasoning_tokens']=output
 normalized=normalize_cost(adapted,stream_eof)
 if not normalized.get('provider_cost_complete') or normalized.get('error'):return result
 # Only a subtype field changes;gross counters and completion status are identical.
 result.update(correction_applied=True,derived_events=adapted,derived_cost=normalized,raw_provider_protocol_valid=False,correction={'field':'output_tokens_details.reasoning_tokens','raw':reasoning,'derived':output,'rule':'min(raw_reasoning,emitted_output);recognized source/length boundary only'},scope='Prospective derived receipt view only;raw receipt remains invalid;no generation,effort,budget,gross usage or historical eligibility changes')
 return result
