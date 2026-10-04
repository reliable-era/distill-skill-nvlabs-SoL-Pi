"""Collect completed Codex substage and keep pending Pi distinct; no model calls."""
import csv,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
records=json.loads((OUT/'codex-results.json').read_text())
assert len(records)==4 and all(r['solved'] is not None for r in records)
traces=[]
for r in records:
 dest=OUT/'codex'/r['arm'];events=[]
 for line in (dest/'stdout.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
 file_changes=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='file_change']
 trace={'arm':r['arm'],'command_executions':len(commands),'file_change_operations':len(file_changes),'command_output_characters':sum(len(i.get('aggregated_output','')) for i in commands),'command_errors':[{'command':i.get('command'),'exit_code':i.get('exit_code'),'output_characters':len(i.get('aggregated_output',''))} for i in commands if i.get('exit_code') not in (0,None)],'verification_commands':[i.get('command') for i in commands if 'pytest' in i.get('command','')]}
 traces.append(trace)
 for name,key in [('stdout.jsonl','transcript_sha256'),('model.patch','patch_sha256')]:assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==r[key]
 report=json.loads((OUT/r['official_report']).read_text())['pallets__flask-5014'];assert hashlib.sha256((OUT/r['official_report']).read_bytes()).hexdigest()==r['official_report_sha256'];assert report['resolved']==r['solved'] and not report['infra_failure']
 r['observed_model_label']=None;r['model_observation']='Configured gpt-6.1-sol; independently observed backend label TBD'
 (dest/'result.json').write_text(json.dumps(r,indent=2)+'\n')
(OUT/'codex-results.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'trace-audit-codex.json').write_text(json.dumps({'records':traces,'interpretation':'Descriptive one-round evidence; output characters are not tokens, and no causal attribution or general stable win follows.'},indent=2)+'\n')
labels={'none':'No skill','karpathy':'Karpathy','candidate':'Locate-first candidate','both':'Candidate + Karpathy (Both)'}
with (OUT/'summary-codex.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['harness','arm','solved','reported_total_tokens','elapsed_seconds']);writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in records)
byarm={r['arm']:r for r in records};candidate=byarm['candidate']['reported_total_tokens'];ratios={a:100*(candidate/byarm[a]['reported_total_tokens']-1) for a in ('none','karpathy','both')}
metadata={'stage_status':'Codex substage complete; Pi pending fresh human login','family':'SWE-bench Verified','task':'pallets__flask-5014','task_status':'previously exposed development fixture; not held-out confirmation','codex_actor_starts':4,'pi_actor_starts':0,'maximum_starts_total':8,'remaining_pi_slots':4,'verified_solves_codex':sum(r['solved'] for r in records),'timeouts':sum(r['timeout'] for r in records),'auth_errors':sum(r['execution_status']=='blocked_auth_or_quota' for r in records),'total_codex_actor_seconds':sum(r['elapsed_seconds'] for r in records),'configured_backend':'OpenAI ChatGPT OAuth, gpt-6.1-sol, native default effort','actual_independently_observed_backend':'TBD','billing_usd':'TBD','candidate_vs_control_reported_token_change_percent':ratios,'candidate_promoted':False,'confirmation_exposed':False,'model_sampling_seed':'TBD','order_seed':106}
(OUT/'stage-progress.json').write_text(json.dumps(metadata,indent=2)+'\n')
readme=(OUT/'README.md').read_text();tail=readme.split('Exact native image',1)[1];tail='Exact native image'+tail
head=['# Locate-first SWE development — Codex results','','Four Codex attempts completed and passed official grading. Pi has **zero starts** and awaits fresh login. This is one round on previously exposed SWE-bench Verified issue `pallets__flask-5014`; no candidate is promoted.','','| Skill | Solved | Reported tokens | Actor seconds |','|---|---:|---:|---:|']
for arm,label in labels.items():
 r=byarm[arm];head.append(f'| {label} | {int(r["solved"])}/1 | {r["reported_total_tokens"]:,} | {r["elapsed_seconds"]:.1f} |')
head+=['',f'Locate-first uses **{-ratios["none"]:.1f}% fewer** reported tokens than no skill, **{-ratios["karpathy"]:.1f}% fewer** than Karpathy and **{-ratios["both"]:.1f}% fewer** than Both in this Codex substage. Actual dollars, Pi results, repeated-round stability and cross-benchmark superiority remain **TBD**.','','The four starts had no cutoffs or auth errors. Each official report records one fail-to-pass and59 pass-to-pass successes, with no infrastructure failure. The no-op marker baseline was independently rejected before inference. The same frozen eight-start budget reserves four unspent Pi slots. Order seed106 controls order, not model randomness.','','Configured backend: ChatGPT OAuth `gpt-6.1-sol`, native default effort; a separately observed actual model label is **TBD**. Reported complete terminal counters include cached usage and are summed once. They are not invoice dollars.','','Saved traces show4 command executions and13,218 returned characters for candidate versus5 and22,790 for no skill. Karpathy runs the full source suite and encounters the three documented unrelated cookie-domain failures. This supports further testing of focused context; it does not establish causality. Other variability and instruction overhead remain possible contributors.','','Full records: [codex-results.json](codex-results.json), [summary-codex.csv](summary-codex.csv), [trace audit](trace-audit-codex.json), [stage progress](stage-progress.json), and [security/grading audit](audit.json).','','## Frozen setup and remaining Pi stage','']
text='\n'.join(head)+'\n'+tail
for a,b in [('and59','and 59'),('seed106','seed 106'),('show4','show 4'),('and13,218','and 13,218'),('versus5','versus 5'),('and22,790','and 22,790')]:text=text.replace(a,b)
text=text.replace('this folder is still prepared-only.','Codex is complete; Pi remains unstarted.').replace('This new phase remains prepared-only.','The Pi portion remains unstarted.').replace('before any explicit Pi launch','before any explicit Pi launch')
(OUT/'README.md').write_text(text)
print(json.dumps(metadata))
