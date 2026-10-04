"""Offline native agy preparation/result audit. Never calls a model."""
import hashlib,json,re,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];CACHE=Path('/tmp/solpi-refinement-auth-cache')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((OUT/'plan.json').read_text());global_file=ROOT/'tests/framework/refinement/development-budget-agy-flask-locate-first.json';budget=json.loads(global_file.read_text());errors=[]
if budget['local_plan_sha256']!=sha(OUT/'plan.json') or budget['max_actor_attempts']!=4:errors.append('global/local budget binding')
for relative,digest in plan['runtime_source_sha256'].items():
 if sha(OUT/relative)!=digest:errors.append('runtime hash '+relative)
for a,d in plan['prompt_sha256'].items():
 if sha(OUT/(a+'-prompt.txt'))!=d:errors.append('prompt hash '+a)
for key,source in plan['skill_trees_sha256'].items():
 for relative,digest in source.items():
  if sha(OUT/'frozen'/key/relative)!=digest:errors.append('skill hash '+key+'/'+relative)
if sha(plan['native_binary'])!=plan['native_binary_sha256']:errors.append('native ELF hash mismatch')
if sha('/tmp/solpi-refinement-swe-data.json')!=plan['task_manifest']['private_dataset_sha256']:errors.append('private dataset hash mismatch')
starts=[json.loads(p.read_text()) for p in OUT.glob('agy/*/actor-start.json')];records=[json.loads(p.read_text()) for p in OUT.glob('agy/*/result.json')]
if len(starts)>4:errors.append('four-start cap exceeded')
seen=set();traces=[];official=[]
for r in records:
 a=r['arm'];dest=OUT/'agy'/a
 if a in seen:errors.append('duplicate arm '+a)
 seen.add(a)
 for name,key in [('stdout.jsonl','transcript_sha256'),('model.patch','patch_sha256')]:
  if sha(dest/name)!=r[key]:errors.append('artifact hash '+a+' '+name)
 events=[]
 for line in (dest/'stdout.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 terminals=[e.get('result',{}) for e in events if e.get('event')=='result'];success=len(terminals)==1 and terminals[0].get('status')=='SUCCESS'
 if not success and r['reported_total_tokens'] is not None:errors.append('error/missing terminal usage treated complete '+a)
 tool_steps={}
 for e in events:
  step=e.get('step_update',{})
  if step.get('step_type')=='tool':tool_steps[step.get('step_index')]=step
 tool_events=list(tool_steps.values())
 candidates=[e for e in events if re.search(r'https?://|curl\b|wget\b|git\s+clone|web_search|search_web|fetch|test_blueprints\.py|test_empty_name_not_allowed',json.dumps(e),re.I)]
 # Candidate text may be source/test reads or local regressions, not proof of remote fetch.
 traces.append({'arm':a,'terminal_statuses':[x.get('status') for x in terminals],'unique_tool_steps':len(tool_events),'tool_names':[x.get('tool_name') for x in tool_events],'tool_parameters':[{'step_index':x.get('step_index'),'tool_name':x.get('tool_name'),'parameters':x.get('tool_info',{}).get('parameters')} for x in tool_events],'external_or_test_access_candidate_events':candidates,'limit':'Includes local source/tests mentions; inspect actual payloads for remote evidence. Native cloud-search gate and invisible network calls remain TBD.'})
 if r.get('official_report'):
  p=OUT/r['official_report'];d=json.loads(p.read_text())['pallets__flask-5014']
  if sha(p)!=r['official_report_sha256'] or d['resolved']!=r['official_patch_resolved']:errors.append('official score/hash '+a)
  official.append({'arm':a,'patch_resolved':d['resolved'],'comparative_solved':r['solved'],'infra_failure':d['infra_failure'],'fail_to_pass_success':len(d['tests_status']['FAIL_TO_PASS']['success']),'pass_to_pass_success':len(d['tests_status']['PASS_TO_PASS']['success'])})
secrets=[]
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if isinstance(v,str) and len(v)>24 and any(y in k.lower() for y in ('token','key','secret','refresh','access')):secrets.append(v.encode())
   else:walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
for p in (Path.home()/'.gemini/antigravity-cli/antigravity-oauth-token',CACHE/'agy/.gemini/antigravity-cli/antigravity-oauth-token'):
 if p.is_file():walk(json.loads(p.read_text()))
files=[p for p in OUT.rglob('*') if p.is_file()];hits=[str(p.relative_to(OUT)) for p in files if any(s in p.read_bytes() for s in secrets)]
if hits:errors.append('credential values in '+','.join(hits))
report={'stage_status':'prepared_only' if not starts else 'complete' if len(official)==4 else 'partial','actor_starts':len(starts),'result_records':len(records),'model_calls_in_audit':0,'plan_sha256':sha(OUT/'plan.json'),'global_budget_sha256':sha(global_file),'native_elf_sha256':sha(plan['native_binary']),'native_offline_version_probe':(OUT/'native-version-probe.txt').read_text().strip(),'credential_values_checked':len(secrets),'credential_matching_files':hits,'private_auth_seed_present':(CACHE/'agy/.gemini/antigravity-cli/antigravity-oauth-token').is_file(),'credential_validity':'Four native attempts authenticated successfully; future expiry TBD' if len(records)==4 and all(r['execution_status']=='completed' for r in records) else 'TBD: no verified successful model attempt','native_cloud_search_gate':'TBD','official_reports':official,'errors':errors}
(OUT/'external-access-audit.json').write_text(json.dumps({'scope':'Saved raw native events only; no clean held-out claim or complete network telemetry','records':traces},indent=2)+'\n')
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not errors
