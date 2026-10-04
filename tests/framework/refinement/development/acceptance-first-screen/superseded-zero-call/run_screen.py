#!/usr/bin/env python3
"""Matched, single-attempt reused-development screen; separate root launch gate."""
import argparse,fcntl,hashlib,importlib.util,json,os,random,re,shutil,subprocess,tarfile,tempfile,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
REF=ROOT/'tests/framework/refinement';CACHE=Path('/tmp/solpi-refinement-auth-cache')
PRIVATE=Path('/tmp/solpi-unpublished-raw-audit/acceptance-first-screen')
ARMS={'none':[],'karpathy':['karpathy'],'candidate':['candidate'],'both':['karpathy','candidate']}
SOURCES={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','candidate':REF/'candidates/acceptance-first/efficient-coding'}
FAMILIES={
 'terminal':{'adapter':REF/'development/terminal-bounded-search/run_screen.py','workspace':Path('/tmp/solpi-terminal-bounded-search-baseline'),'prompt':Path('/tmp/solpi-refinement-terminal-bench-2/sanitize-git-repo/instruction.md'),'image':'sha256:575d33f0522d38aa9978013294f4b03629fea2bd11ea82a32306197968b8e8ac','mount':'/app/dclm','task':'terminal-bench-2/sanitize-git-repo'},
 'go':{'adapter':REF/'development/go-locate-first/run_screen.py','workspace':Path('/tmp/solpi-polyglot-go-smoke-v2/workspace'),'prompt':Path('/tmp/solpi-polyglot-go-smoke-v2/prompt.txt'),'image':'sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118','mount':'/workspace','task':'go/exercises/practice/food-chain'},
 'flask':{'adapter':REF/'development/swe-flask-locate-first/run_screen.py','workspace':Path('/tmp/solpi-refinement-flask-native-task-v2/workspace'),'prompt':Path('/tmp/solpi-refinement-flask-native-task-v2/prompt.txt'),'image':'sha256:10a67635ce037886b760a72f6eef8459beb6a0c6e070c0748a037839135acc45','mount':'/workspace','task':'pallets__flask-5014'}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(p):return {str(q.relative_to(p)):sha(q) for q in sorted(p.rglob('*')) if q.is_file()}
def write(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def publish(p,data):
 raw=PRIVATE/p.relative_to(OUT);raw.parent.mkdir(parents=True,exist_ok=True,mode=0o700);raw.write_bytes(data);os.chmod(raw,0o600)
 public=re.sub(rb'hf_[A-Za-z0-9]{20,}',lambda m:b'[REDACTED_HF_TOKEN_'+hashlib.sha256(m.group()).hexdigest().encode()+b']',data)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(public)
 return {'path':str(p.relative_to(OUT)),'original_sha256':hashlib.sha256(data).hexdigest(),'published_sha256':sha(p)}

def prepare():
 if (OUT/'plan.json').exists():raise RuntimeError('Frozen plan exists')
 order=list(ARMS);random.Random(110).shuffle(order)
 refs={}
 for f,c in FAMILIES.items():
  assert subprocess.check_output(['docker','image','inspect',c['image'],'--format','{{.Id}}'],text=True).strip()==c['image']
  adapter=c['adapter'];refs[str(adapter.relative_to(ROOT))]=sha(adapter)
  old=adapter.parent
  for p in sorted((old/'frozen/runtime').glob('*.py')):refs[str(p.relative_to(ROOT))]=sha(p)
  if f=='go':
   for p in sorted((old/'frozen/grader').rglob('*')):
    if p.is_file():refs[str(p.relative_to(ROOT))]=sha(p)
  for p in [old/'plan.json']:
   refs[str(p.relative_to(ROOT))]=sha(p)
  if f=='terminal':
   for p in Path('/tmp/solpi-refinement-terminal-bench-2/sanitize-git-repo/tests').rglob('*'):
    if p.is_file():refs[str(p)]=sha(p)
  if f=='flask':refs['/tmp/solpi-refinement-swe-data.json']=sha('/tmp/solpi-refinement-swe-data.json')
  write(OUT/f/'baseline-files.json',files(c['workspace']))
  for arm,keys in ARMS.items():
   prompt=c['prompt'].read_text()
   for key in keys:prompt+='\n\nApply supplied skill instructions (complete resources at /skills/'+key+'):\n\n'+(SOURCES[key]/'SKILL.md').read_text()
   (OUT/f/(arm+'-prompt.txt')).write_text(prompt)
 budget={'purpose':'Separate acceptance-first matched reused development allocation, not confirmation','maximum_actor_starts':12,'per_family_maximum':4,'actor_timeout_seconds':180,'maximum_actor_wall_seconds':2160,'automatic_retries':0,'family_order':list(FAMILIES),'order_seed':110,'arm_order':order,'harness':'codex','stop_rule':'Finish the four matched arms within a family, then stop all later families if official candidate solved is not True. Auth/quota/infrastructure ambiguity stops immediately. Record all unused starts; no replacement tasks or retries.'}
 write(OUT/'global-budget.json',budget)
 plan={'purpose':budget['purpose'],'status_at_freeze':'Prepared only; zero actors','candidate':'acceptance-first','candidate_manifest_sha256':sha(REF/'candidate-acceptance-first-manifest.json'),'harness':'codex','requested_model':'gpt-6.1-sol','resolved_server_model':'TBD','effort':'native defaults','model_sampling_seed':'TBD','budget_sha256':sha(OUT/'global-budget.json'),'family_order':list(FAMILIES),'order':order,'maximum_actor_starts':12,'actor_timeout_seconds':180,'automatic_retries':0,'runner_sha256':sha(Path(__file__)),'reused_source_files_sha256':refs,'skills':{k:{'path':str(p.relative_to(ROOT)),'files_sha256':files(p)} for k,p in SOURCES.items()},'families':{f:{**{k:str(v) for k,v in c.items()},'baseline_manifest_sha256':sha(OUT/f/'baseline-files.json'),'prompt_sha256':{a:sha(OUT/f/(a+'-prompt.txt')) for a in ARMS}} for f,c in FAMILIES.items()},'auth':'Only persistent private /tmp/solpi-refinement-auth-cache/codex HOME mounted writable; shared fcntl codex.lock; host seed never written','resources':'Full selected skill trees readonly /skills, inline SKILL instructions uniform','capture':'Complete Git plus working/untracked content delta before cleanup/verifier from first actor; trusted baseline patch, all outcomes and partial usage retained','publication':'Private originals outside Git, digest-redacted HF text, binary archive publication refused if it contains HF-shaped plaintext','source_policy':'Existing frozen adapters/runtime/grader files reused by hash without copies; no selected sealed tasks touched','gate':'Root execution-authorization.json must match exact plan and budget hashes; exclusive launch refuses repeat','billing_usd':'TBD'}
 write(OUT/'plan.json',plan);print(json.dumps({'plan_sha256':sha(OUT/'plan.json'),'budget_sha256':sha(OUT/'global-budget.json'),'order':order,'zero_actors':True}),flush=True)

def verify():
 p=json.loads((OUT/'plan.json').read_text());assert sha(Path(__file__))==p['runner_sha256'];assert sha(OUT/'global-budget.json')==p['budget_sha256']
 for rel,d in p['reused_source_files_sha256'].items():assert sha(Path(rel) if rel.startswith('/') else ROOT/rel)==d,rel
 assert sha(REF/'candidate-acceptance-first-manifest.json')==p['candidate_manifest_sha256']
 for k,s in p['skills'].items():assert files(ROOT/s['path'])==s['files_sha256']
 for f,c in FAMILIES.items():
  assert files(c['workspace'])==json.loads((OUT/f/'baseline-files.json').read_text())
  assert sha(OUT/f/'baseline-files.json')==p['families'][f]['baseline_manifest_sha256']
  for a in ARMS:assert sha(OUT/f/(a+'-prompt.txt'))==p['families'][f]['prompt_sha256'][a]
 return p

def grade(f,work,dest,patch,tag):
 c=FAMILIES[f];m=load('grade_'+f,c['adapter'])
 if f=='terminal':
  m.OUT=OUT;m.PRIVATE=PRIVATE;code,audit=m.grade(work,dest/'verifier');return code,code==0 if code in (0,1) else None,{'publication':audit}
 if f=='go':
  code=m.grade(work,dest/'grade.txt');return code,code==0 if code in (0,1) else None,{'grader':'original frozen restored-tests adapter'}
 m.OUT=OUT/'flask';code,reports=m.official([{'instance_id':c['task'],'model_name_or_path':'acceptance-first-'+tag,'model_patch':patch}], 'solpi-acceptance-first-'+tag+'-110')
 if not reports:return code,None,{'infrastructure':'No official report; no inferred empty-patch grade'}
 report=json.loads(reports[0].read_text());leaf=report.get(c['task'],report);solved=leaf.get('resolved') if not leaf.get('infra_failure') else None
 return code,solved,{'official_report':str(reports[0].relative_to(OUT)),'official_report_sha256':sha(reports[0])}

def execute():
 if (OUT/'launch.json').exists():raise RuntimeError('Already launched: no retry/resume')
 auth=OUT/'execution-authorization.json'
 if not auth.exists():raise RuntimeError('Root execution authorization missing; zero actors')
 a=json.loads(auth.read_text());p=verify()
 if a.get('authorized') is not True or a.get('plan_sha256')!=sha(OUT/'plan.json') or a.get('global_budget_sha256')!=sha(OUT/'global-budget.json') or a.get('max_actor_attempts')!=12:raise RuntimeError('Root authorization mismatch')
 home=CACHE/'codex';assert (home/'.codex/auth.json').is_file()
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 with (OUT/'launch.json').open('x') as h:json.dump({'plan_sha256':sha(OUT/'plan.json'),'authorization_sha256':sha(auth),'maximum_actor_starts':12},h)
 collect=load('acceptance_collect',FAMILIES['terminal']['adapter'].parent/'frozen/runtime/collect.py')
 patcher=load('acceptance_patcher',FAMILIES['go']['adapter'].parent/'frozen/runtime/swe_patch.py')
 results=[];publications=[];stop=None
 for f,c in FAMILIES.items():
  if stop:break
  # Independent no-op control; no credentials/test content mounted in any actor.
  if f=='flask':
   control_patch='diff --git a/.solpi_noop_marker b/.solpi_noop_marker\nnew file mode 100644\n--- /dev/null\n+++ b/.solpi_noop_marker\n@@ -0,0 +1 @@\n+Grader sanity only.\n'
  else:control_patch=''
  code,solved,detail=grade(f,c['workspace'],OUT/f/'control',control_patch,'noop-'+f)
  write(OUT/f/'control.json',{'exit_code':code,'solved':solved,**detail})
  if solved is not False:stop='grader_control_infrastructure';break
  family_results=[]
  for arm in p['order']:
   dest=OUT/f/'codex'/arm;dest.mkdir(parents=True)
   with (CACHE/'codex.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    if len(list(OUT.glob('*/codex/*/actor-start.json')))>=12:raise RuntimeError('Shared 12-start cap exhausted')
    if len(list((OUT/f).glob('codex/*/actor-start.json')))>=4:raise RuntimeError('Family four-start cap exhausted')
    with tempfile.TemporaryDirectory(prefix='solpi-acceptance-'+f+'-') as td:
     tmp=Path(td);work=tmp/'workspace';shutil.copytree(c['workspace'],work);resources=tmp/'skills';resources.mkdir()
     for k in ARMS[arm]:shutil.copytree(SOURCES[k],resources/k)
     name='solpi-acceptance-'+f+'-'+arm
     cmd=['docker','run','--rm','--name',name,'--user','0:0','--entrypoint','/bin/bash','-e','HOME=/eval-home','--mount',f'type=bind,src={home},dst=/eval-home','--mount',f'type=bind,src={work},dst={c["mount"]}','--mount',f'type=bind,src={resources},dst=/skills,readonly','-w',c['mount'],c['image'],'-c','exec "$@"','actor','codex','exec','--json','--ignore-user-config','--ephemeral','--dangerously-bypass-approvals-and-sandbox','--model','gpt-6.1-sol']
     if f=='go':cmd+=['--skip-git-repo-check']
     cmd+=[(OUT/f/(arm+'-prompt.txt')).read_text()]
     with (dest/'actor-start.json').open('x') as h:json.dump({'family':f,'arm':arm,'timeout_seconds':180,'plan_sha256':sha(OUT/'plan.json'),'full_resources':True},h)
     start=time.monotonic();timeout=False
     try:r=subprocess.run(cmd,capture_output=True,timeout=180);stdout,stderr,exit_code=r.stdout,r.stderr,r.returncode
     except subprocess.TimeoutExpired as e:stdout,stderr,exit_code=e.stdout or b'',e.stderr or b'',None;timeout=True;subprocess.run(['docker','rm','-f',name],capture_output=True)
     elapsed=time.monotonic()-start;publications += [publish(dest/'stdout.jsonl',stdout),publish(dest/'stderr.txt',stderr)]
     baseline=json.loads((OUT/f/'baseline-files.json').read_text());final=files(work);changed=[q for q,h in final.items() if baseline.get(q)!=h];deleted=sorted(set(baseline)-set(final))
     raw_delta=PRIVATE/dest.relative_to(OUT)/'final-state-delta.tar.gz';raw_delta.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
     with tarfile.open(raw_delta,'w:gz') as tar:
      for q in changed:tar.add(work/q,arcname=q,recursive=False)
     os.chmod(raw_delta,0o600)
     with tarfile.open(raw_delta,'r:gz') as tar:archive_safe=not any(re.search(rb'hf_[A-Za-z0-9]{20,}',tar.extractfile(member).read()) for member in tar.getmembers() if member.isfile())
     if archive_safe:shutil.copy2(raw_delta,dest/'final-state-delta.tar.gz')
     write(dest/'final-state-manifest.json',{'files_sha256':final,'changed_or_added_files':changed,'deleted_files':deleted,'delta_sha256':sha(raw_delta),'public_delta_available':archive_safe,'capture':'Full Git/working/untracked before grader and cleanup'})
     if f=='terminal':patch=subprocess.check_output(['git','-c',f'safe.directory={work}','-C',str(work),'diff','--binary','d6987af002b122fef54bc0be402062c76488a4d9'])
     else:patch=patcher.snapshot_patch(c['workspace'],work).encode()
     publications.append(publish(dest/'workspace.patch',patch))
     code,solved,detail=grade(f,work,dest,patch.decode(),'codex-'+f+'-'+arm)
     total,basis=collect.token_total('codex',collect.events(dest/'stdout.jsonl'))
     text=(stdout+stderr).decode(errors='replace').lower();blocked=any(s in text for s in ['invalid_grant','authentication failed','failed to refresh oauth','insufficient_quota','quota exceeded','usage limit','login required','unauthorized'])
     record={'family':f,'harness':'codex','arm':arm,'task':c['task'],'solved':None if blocked else solved,'execution_status':'blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if exit_code==0 else 'agent_error','elapsed_seconds':elapsed,'exit_code':exit_code,'grade_exit_code':code,'reported_total_tokens':total,'token_basis':basis,'billing_cost_usd':None,'transcript_sha256':hashlib.sha256(stdout).hexdigest(),'patch_sha256':hashlib.sha256(patch).hexdigest(),**detail}
     subprocess.run(['docker','run','--rm','--network','none','--user','0:0','--entrypoint','chown','--mount',f'type=bind,src={tmp},dst=/cleanup','--mount',f'type=bind,src={home},dst=/private-auth',c['image'],'-R',f'{os.getuid()}:{os.getgid()}','/cleanup','/private-auth'],capture_output=True,check=True)
   write(dest/'result.json',record);results.append(record);family_results.append(record);write(OUT/'results.json',results);write(OUT/'publication-redaction-audit.json',publications);print(json.dumps(record),flush=True)
   if blocked or solved is None:stop='auth_quota_or_grader_infrastructure';break
  candidate=[r for r in family_results if r['arm']=='candidate']
  if not stop and (not candidate or candidate[0]['solved'] is not True):stop='official_candidate_failure_'+f
 starts=len(list(OUT.glob('*/codex/*/actor-start.json')))
 write(OUT/'completion.json',{'starts':starts,'unused_starts':12-starts,'stop_reason':stop,'replacement_tasks':0,'retries':0,'completed_families':[f for f in FAMILIES if len([r for r in results if r['family']==f])==4]})
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','verify','execute']);args=ap.parse_args()
 if args.action=='prepare':prepare()
 elif args.action=='verify':verify();print('Frozen inputs verified; zero actors')
 else:execute()
