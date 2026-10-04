"""Offline prepared/complete audit; never launches actors or graders."""
import hashlib,importlib.util,json,os,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((OUT/'plan.json').read_text());errors=[]
for relative,digest in plan['runtime_source_sha256'].items():
 if sha(OUT/relative)!=digest:errors.append('runtime hash: '+relative)
for arm,digest in plan['prompt_sha256'].items():
 if sha(OUT/(arm+'-prompt.txt'))!=digest:errors.append('prompt hash: '+arm)
for key,files in plan['skill_trees_sha256'].items():
 for relative,digest in files.items():
  if sha(OUT/'frozen'/key/relative)!=digest:errors.append('skill hash: '+key+'/'+relative)
records=[json.loads(p.read_text()) for p in sorted(OUT.glob('*/*/result.json'))]
if len(records)>8:errors.append('actor cap exceeded')
seen=set();official=[]
for r in records:
 pair=(r['harness'],r['arm'])
 if pair in seen:errors.append('duplicate actor '+str(pair))
 seen.add(pair);dest=OUT/r['harness']/r['arm']
 for name,key in [('stdout.jsonl','transcript_sha256'),('model.patch','patch_sha256')]:
  if sha(dest/name)!=r[key]:errors.append('artifact hash '+str(pair)+' '+name)
 if r.get('official_report'):
  p=OUT/r['official_report']; report=json.loads(p.read_text())['pallets__flask-5014']
  if sha(p)!=r['official_report_sha256']:errors.append('official report hash '+str(pair))
  if report['resolved']!=r['solved']:errors.append('score mismatch '+str(pair))
  official.append({'harness':r['harness'],'arm':r['arm'],'resolved':report['resolved'],'infra_failure':report['infra_failure'],'fail_to_pass_success':len(report['tests_status']['FAIL_TO_PASS']['success']),'pass_to_pass_success':len(report['tests_status']['PASS_TO_PASS']['success'])})
# Only compare private exact values; never print them.
secrets=[]
def walk(value):
 if isinstance(value,dict):
  for k,v in value.items():
   if isinstance(v,str) and len(v)>24 and any(t in k.lower() for t in ('token','key','secret','refresh','access')):secrets.append(v.encode())
   else:walk(v)
 elif isinstance(value,list):
  for v in value:walk(v)
credential_files=[Path.home()/'.pi/agent/auth.json',Path.home()/'.codex/auth.json']
if os.environ.get('SOLPI_PRIVATE_AUTH_CACHE'):
 cache=Path(os.environ['SOLPI_PRIVATE_AUTH_CACHE']).resolve()
 credential_files.extend([cache/'pi/.pi/agent/auth.json',cache/'codex/.codex/auth.json'])
for p in credential_files:
 if p.is_file():walk(json.loads(p.read_text()))
files=[p for p in OUT.rglob('*') if p.is_file()]
hits=[str(p.relative_to(OUT)) for p in files if any(v in p.read_bytes() for v in secrets)]
if hits:errors.append('credential content found: '+','.join(hits))
audit={'status':'prepared_only' if not records else 'complete' if len(records)==8 and len(official)==8 else 'partial','actor_starts_recorded':len(records),'model_calls_in_audit':0,'credential_values_checked':len(secrets),'credential_matching_files':hits,'official_reports':official,'errors':errors,'plan_sha256':sha(OUT/'plan.json'),'launch_manifest_present':(OUT/'launch-manifest.json').exists(),'source_snapshot_git_commit_count':int(subprocess.check_output(['git','-C','/tmp/solpi-refinement-flask-native-task-v2/workspace','rev-list','--count','HEAD'],text=True))}
(OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit));assert not errors
