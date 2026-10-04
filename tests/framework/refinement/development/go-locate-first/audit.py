"""Offline ledger, transcript, external-fetch, grader and exact secret audit."""
import hashlib,json,os,re,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((OUT/'plan.json').read_text());budget=json.loads((OUT/'budget.json').read_text());errors=[]
assert budget['local_plan_sha256']==sha(OUT/'plan.json')
for relative,digest in plan['runtime_source_sha256'].items():
 if sha(OUT/relative)!=digest:errors.append('runtime hash: '+relative)
for arm,digest in plan['prompt_sha256'].items():
 if sha(OUT/(arm+'-prompt.txt'))!=digest:errors.append('prompt hash: '+arm)
for key,files in plan['skill_trees_sha256'].items():
 for relative,digest in files.items():
  if sha(OUT/'frozen'/key/relative)!=digest:errors.append('skill hash: '+key+'/'+relative)
for relative,digest in plan['grader_files_sha256'].items():
 if sha(OUT/'frozen/grader'/relative)!=digest:errors.append('grader hash: '+relative)
starts=[json.loads(p.read_text()) for p in OUT.glob('*/*/actor-start.json')]
records=[json.loads(p.read_text()) for p in OUT.glob('*/*/result.json')]
if len(starts)>8:errors.append('total start cap exceeded')
for h in ('pi','codex'):
 if sum(r['harness']==h for r in starts)>4:errors.append('per-harness cap exceeded')
seen=set();grade_counts=[];trace=[]
for r in records:
 pair=(r['harness'],r['arm']);dest=OUT/r['harness']/r['arm']
 if pair in seen:errors.append('duplicate attempt '+str(pair))
 seen.add(pair)
 for name,key in [('stdout.jsonl','transcript_sha256'),('model.patch','patch_sha256')]:
  if sha(dest/name)!=r[key]:errors.append('artifact hash '+str(pair)+' '+name)
 events=[]
 for line in (dest/'stdout.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
 external=[{'command':i.get('command'),'exit_code':i.get('exit_code'),'output_characters':len(i.get('aggregated_output',''))} for i in commands if re.search(r'https?://|\bcurl\b|\bwget\b|git\s+clone|urllib|requests\.(get|post)|food_chain_test\.go|example\.go',i.get('command',''),re.I)]
 native_web=[{'type':e.get('item',{}).get('type'),'event_type':e.get('type')} for e in events if 'web' in e.get('item',{}).get('type','').lower()]
 trace.append({'harness':r['harness'],'arm':r['arm'],'command_executions':len(commands),'command_output_characters':sum(len(i.get('aggregated_output','')) for i in commands),'external_or_official_test_access_candidates':external,'native_web_events':native_web,'scan_limit':'Saved trace evidence only; absence of these markers is not proof of no external access or pretraining exposure'})
 if 'grade_sha256' in r:
  log=dest/'grade.txt'
  if sha(log)!=r['grade_sha256']:errors.append('grade hash '+str(pair))
  counts=[int(x) for x in re.findall(r'Executed accepted tests:\s*(\d+)',log.read_text())]
  passes=sum(1 for line in log.read_text().splitlines() if line.startswith('{') and json.loads(line).get('Action')=='pass' and json.loads(line).get('Test'))
  skipped=sum(1 for line in log.read_text().splitlines() if line.startswith('{') and json.loads(line).get('Action')=='skip' and json.loads(line).get('Test'))
  if r['solved'] and skipped:errors.append('official tests skipped '+str(pair))
  if r['solved'] and (not counts or counts[-1]!=passes or passes==0):errors.append('executed test count mismatch '+str(pair))
  grade_counts.append({'harness':r['harness'],'arm':r['arm'],'solved':r['solved'],'executed_accepted_tests':counts[-1] if counts else None,'json_pass_test_events':passes,'json_skipped_test_events':skipped,'network':'none','grader_credentials_mounted':False})
secrets=[]
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and len(x)>24 and any(t in k.lower() for t in ('token','key','secret','refresh','access')):secrets.append(x.encode())
   else:walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
paths=[Path.home()/'.pi/agent/auth.json',Path.home()/'.codex/auth.json']
if os.environ.get('SOLPI_PRIVATE_AUTH_CACHE'):
 cache=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']);paths.extend([cache/'pi/.pi/agent/auth.json',cache/'codex/.codex/auth.json'])
for p in paths:
 if p.is_file():walk(json.loads(p.read_text()))
files=[p for p in OUT.rglob('*') if p.is_file()];hits=[str(p.relative_to(OUT)) for p in files if any(s in p.read_bytes() for s in secrets)]
if hits:errors.append('credential content found: '+','.join(hits))
report={'stage_status':'Codex complete; Pi unstarted' if len(grade_counts)==4 and len(starts)==4 else 'partial','actor_starts':len(starts),'pi_actor_starts':sum(r['harness']=='pi' for r in starts),'records':len(records),'model_calls_in_audit':0,'plan_sha256':sha(OUT/'plan.json'),'credential_values_checked':len(secrets),'credential_matching_files':hits,'grader_records':grade_counts,'exposure':'Reused public development task; prior external test accesses exist. No clean held-out claims. New trace audit is descriptive, not complete network telemetry.','errors':errors}
(OUT/'external-fetch-audit.json').write_text(json.dumps({'records':trace,'scope':'Saved native traces; actual external accesses require inspecting candidate command outputs. Prior exposures retained elsewhere; no clean held-out claim.'},indent=2)+'\n')
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not errors
