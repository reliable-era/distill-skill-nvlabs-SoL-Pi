#!/usr/bin/env python3
"""Offline original-output and split token counters; never prints credential bytes."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
PRIVATE=Path('/tmp/solpi-unpublished-raw-audit/acceptance-first-screen')
def main():
 records=json.loads((OUT/'results.json').read_text());metrics=[]
 for record in records:
  path=PRIVATE/record['family']/'codex'/record['arm']/'stdout.jsonl'
  if not path.exists():
   metrics.append({'family':record['family'],'arm':record['arm'],'observed':False,'availability_status':record['execution_status']});continue
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==record['transcript_sha256']
  events=[]
  for n,line in enumerate(raw.decode(errors='replace').splitlines(),1):
   try:value=json.loads(line)
   except ValueError:continue
   if isinstance(value,dict):events.append((n,value))
  commands=[(n,e['item']) for n,e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
  usages=[e.get('usage') for n,e in events if e.get('type')=='turn.completed']
  usage=usages[0] if len(usages)==1 and isinstance(usages[0],dict) else {}
  inp,cached,out=[usage.get(k) for k in ('input_tokens','cached_input_tokens','output_tokens')]
  uncached=inp-cached if isinstance(inp,int) and isinstance(cached,int) and inp>=cached else None
  if record['reported_total_tokens'] is not None:assert inp+out==record['reported_total_tokens']
  metrics.append({'family':record['family'],'arm':record['arm'],'observed':True,'original_transcript_sha256':record['transcript_sha256'],'published_transcript_sha256':hashlib.sha256((OUT/record['family']/'codex'/record['arm']/'stdout.jsonl').read_bytes()).hexdigest(),'reported_total_tokens':record['reported_total_tokens'],'input_tokens_including_cache':inp,'uncached_input_tokens':uncached,'cached_input_tokens':cached,'output_tokens':out,'cache_write_input_tokens':usage.get('cache_write_input_tokens'),'reasoning_output_tokens_included_in_output':usage.get('reasoning_output_tokens'),'billing_usd':None,'elapsed_seconds':record['elapsed_seconds'],'command_calls':len(commands),'original_returned_output_chars':sum(len(item.get('aggregated_output','')) for n,item in commands),'nonzero_shell_exit_lines':[n for n,item in commands if item.get('exit_code') not in (0,None)],'terminal_usage_observations':usages,'commands':[{'original_jsonl_line':n,'returned_chars':len(item.get('aggregated_output','')),'returned_lines':len(item.get('aggregated_output','').splitlines()),'exit_code':item.get('exit_code')} for n,item in commands]})
 (OUT/'trace-metrics.json').write_text(json.dumps({'scope':'Original private unredacted command aggregated_output characters counted once; not tokens or proof of exact model-visible payload. Original SHA256 checked. Native terminal cache/output split; reasoning not added again. All dollar costs TBD.','records':metrics},indent=2)+'\n')
 print(json.dumps({'measured_records':len(metrics),'original_hashes_verified':True}))
if __name__=='__main__':main()
