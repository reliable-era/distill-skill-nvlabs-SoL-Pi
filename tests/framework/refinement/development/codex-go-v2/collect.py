#!/usr/bin/env python3
"""Collect the five frozen development attempts; no model calls."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'tests/framework/refinement'))
from audit import calls,events
sys.path.insert(0,str(ROOT/'tests/framework'))
from accounting import terminal_usage
plan=json.loads((HERE/'plan.json').read_text()); rows=[]
regrades={a['result']:a for a in json.loads((HERE/'regrade.json').read_text())['attempts']}
for p in sorted((HERE/'results').glob('*/result.json')):
 r=json.loads(p.read_text()); transcript=p.with_name('agent.log');es=list(events(transcript));u=terminal_usage(es,'codex')
 config=r['config']; accepted=regrades[str(p.relative_to(ROOT))]
 rows.append({'result':str(p.relative_to(ROOT)),'result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'transcript_sha256':hashlib.sha256(transcript.read_bytes()).hexdigest(),'configuration':config,'solved':accepted['solved'],'original_grader_interpretation':'infrastructure error; ungraded','accepted_grader_exit_code':accepted['grader_exit_code'],'status':r.get('status'),'elapsed_seconds':r.get('elapsed_seconds'),'observed_tool_calls':len(list(calls(transcript,'codex'))),'usage':u,'observed_backend':'TBD','nonzero_tool_exit_events':[{'item_id':e.get('item',{}).get('id'),'type':e.get('item',{}).get('type'),'exit_code':e.get('item',{}).get('exit_code')} for e in es if e.get('type')=='item.completed' and (e.get('item',{}).get('exit_code') not in (None,0) or e.get('item',{}).get('status')=='failed')]} )
(HERE/'collection.json').write_text(json.dumps({'stage':'development only; public task exposed to candidate selection; not confirmation','configured_backend':'OpenAI ChatGPT OAuth gpt-6.1-sol; native default effort','seed':'schedule only; model random seed uncontrolled','attempts':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
