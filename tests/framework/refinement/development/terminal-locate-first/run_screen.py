#!/usr/bin/env python3
"""Four new bounded Codex starts; no retries and publication-safe task evidence."""
import argparse,fcntl,hashlib,importlib.util,json,os,random,re,shutil,subprocess,tarfile,tempfile,time,uuid
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
TASK=Path('/tmp/solpi-refinement-terminal-bench-2/sanitize-git-repo')
IMAGE='sha256:575d33f0522d38aa9978013294f4b03629fea2bd11ea82a32306197968b8e8ac'
BASE=Path('/tmp/solpi-terminal-locate-first-baseline')
CACHE=Path('/tmp/solpi-refinement-auth-cache');PRIVATE=Path('/tmp/solpi-unpublished-raw-audit/terminal-locate-first')
ARMS={'none':[],'karpathy':['karpathy'],'candidate':['candidate'],'both':['karpathy','candidate']}
SOURCES={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','candidate':ROOT/'tests/framework/refinement/candidates/locate-first/efficient-coding'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(root):return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
def call(args,**kw):return subprocess.run(args,capture_output=True,**kw)
def write(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def import_module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def publish(dest,data):
 """Keep original bytes privately; no token values printed or stored in source."""
 relative=dest.relative_to(OUT);raw=PRIVATE/relative;raw.parent.mkdir(parents=True,exist_ok=True,mode=0o700);raw.write_bytes(data);os.chmod(raw,0o600)
 count=0
 def marker(match):
  nonlocal count
  count+=1;return b'[REDACTED_HF_TOKEN_'+hashlib.sha256(match.group()).hexdigest().encode()+b']'
 public=re.sub(rb'hf_[A-Za-z0-9]{20,}',marker,data);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(public)
 return {'path':str(relative),'original_sha256':hashlib.sha256(data).hexdigest(),'published_sha256':sha(dest),'redaction_count':count}

def fresh_baseline(path):
 path.mkdir(parents=True)
 name='terminal-locate-source-'+uuid.uuid4().hex[:12]
 r=call(['docker','create','--name',name,IMAGE]);assert r.returncode==0
 try:r=call(['docker','cp',name+':/app/dclm/.',str(path)]);assert r.returncode==0
 finally:call(['docker','rm',name])

def grade(work,dest):
 dest.mkdir(parents=True,exist_ok=True)
 r=call(['docker','run','--rm','--network','none','-e','GIT_OPTIONAL_LOCKS=0','--mount',f'type=bind,src={work},dst=/app/dclm','--mount',f'type=bind,src={TASK}/tests,dst=/tests,readonly','--mount',f'type=bind,src={dest},dst=/logs/verifier',IMAGE,'python','-m','pytest','--ctrf','/logs/verifier/ctrf.json','/tests/test_outputs.py','-rA'],timeout=180)
 publication=publish(dest/'grade.txt',r.stdout+r.stderr)
 return r.returncode,publication

def prepare():
 if (OUT/'plan.json').exists():raise SystemExit('Frozen plan exists; no overwrite')
 assert call(['docker','image','inspect',IMAGE,'--format','{{.Id}}']).stdout.decode().strip()==IMAGE
 frozen=OUT/'frozen';frozen.mkdir()
 for k,p in SOURCES.items():shutil.copytree(p,frozen/k)
 runtime=frozen/'runtime';runtime.mkdir();shutil.copy2(ROOT/'tests/framework/trials/collect.py',runtime/'collect.py');shutil.copy2(ROOT/'tests/framework/accounting.py',frozen/'accounting.py')
 if BASE.exists():raise RuntimeError('Fresh stage baseline path exists; do not silently reuse')
 fresh_baseline(BASE);write(OUT/'baseline-files.json',files(BASE))
 order=list(ARMS);random.Random(107).shuffle(order)
 prompt_hashes={}
 for arm,names in ARMS.items():
  prompt=(TASK/'instruction.md').read_text()
  for name in names:prompt+='\n\nApply supplied skill instructions (complete resources at /skills/'+name+'):\n\n'+(frozen/name/'SKILL.md').read_text()
  (OUT/(arm+'-prompt.txt')).write_text(prompt);prompt_hashes[arm]=sha(OUT/(arm+'-prompt.txt'))
 plan={'purpose':'New bounded development stage on reused sanitize task; not confirmation','harness':'codex','candidate':'locate-first','requested_model':'gpt-6.1-sol','resolved_server_model':'TBD','reasoning':'native defaults','maximum_actor_starts':4,'actor_timeout_seconds':180,'maximum_actor_wall_seconds':720,'automatic_retries':0,'rounds':1,'order_seed':107,'order':order,'model_sampling_seed':'TBD','arms':ARMS,'image_id':IMAGE,'source_commit':call(['git','-C',str(TASK.parent),'rev-parse','HEAD']).stdout.decode().strip(),'task_sha256':files(TASK),'skill_delivery':'uniform inline SKILL.md plus FULL readonly /skills resources; only selected bundles mounted','skill_files_sha256':{k:files(frozen/k) for k in SOURCES},'prompt_sha256':prompt_hashes,'runtime_sha256':files(frozen/'runtime'),'accounting_sha256':sha(frozen/'accounting.py'),'runner_sha256':sha(Path(__file__)),'baseline_manifest_sha256':sha(OUT/'baseline-files.json'),'auth':'persistent private cache /tmp/solpi-refinement-auth-cache/codex mounted writable; shared fcntl codex.lock serializes refresh; host original never written','stop_rule':'Auth/quota failure stops later starts; no retries or substitution','billing_usd':'TBD','publication':'HF-shaped tokens digest-redacted; raw originals private outside Git; full filesystem delta captured before original grader from first actor'}
 write(OUT/'plan.json',plan);print(json.dumps({'frozen_plan_sha256':sha(OUT/'plan.json'),'order':order,'maximum_actor_starts':4}),flush=True)

def execute():
 if (OUT/'launch.json').exists():raise SystemExit('Stage already launched; no automatic resume/retry')
 plan=json.loads((OUT/'plan.json').read_text());assert sha(Path(__file__))==plan['runner_sha256'];assert files(BASE)==json.loads((OUT/'baseline-files.json').read_text())
 assert sha(ROOT/plan['global_budget_path'])==plan['global_budget_sha256']
 for k in SOURCES:assert files(OUT/'frozen'/k)==plan['skill_files_sha256'][k]
 for arm in ARMS:assert sha(OUT/(arm+'-prompt.txt'))==plan['prompt_sha256'][arm]
 assert sha(OUT/'frozen/accounting.py')==plan['accounting_sha256'];assert files(OUT/'frozen/runtime')==plan['runtime_sha256']
 PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
 home=CACHE/'codex';assert (home/'.codex/auth.json').is_file(),'Persistent private auth seed unavailable'
 write(OUT/'launch.json',{'plan_sha256':sha(OUT/'plan.json'),'maximum_actor_starts':4,'actor_timeout_seconds':180,'automatic_retries':0})
 changes=[]
 # Validate current official tests before models; immutable pristine baseline retained.
 for tag in ('baseline','oracle'):
  with tempfile.TemporaryDirectory(prefix='terminal-locate-control-') as td:
   work=Path(td)/'workspace';shutil.copytree(BASE,work)
   if tag=='oracle':
    r=call(['docker','run','--rm','--network','none','--mount',f'type=bind,src={work},dst=/app/dclm','--mount',f'type=bind,src={TASK}/solution,dst=/solution,readonly',IMAGE,'bash','/solution/solve.sh'],timeout=180);assert r.returncode==0;changes.append(publish(OUT/'sanity-oracle-execution.txt',r.stdout+r.stderr))
   g,publication=grade(work,OUT/('sanity-'+tag));changes.append(publication);assert g==(1 if tag=='baseline' else 0)
 collect=import_module('terminal_frozen_collect',OUT/'frozen/runtime/collect.py');results=[];blocked=False
 for arm in plan['order']:
  dest=OUT/'codex'/arm;dest.mkdir(parents=True)
  record={'harness':'codex','arm':arm,'task':'terminal-bench-2/sanitize-git-repo','round':1,'requested_model':'gpt-6.1-sol','resolved_server_model':'TBD','billing_cost_usd':None}
  if blocked:record.update(execution_status='not_attempted_auth_or_quota',solved=None,reported_total_tokens=None)
  else:
   with (CACHE/'codex.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    with tempfile.TemporaryDirectory(prefix='terminal-locate-actor-') as td:
     tmp=Path(td);work=tmp/'workspace';shutil.copytree(BASE,work);resources=tmp/'skills';resources.mkdir()
     for key in ARMS[arm]:shutil.copytree(OUT/'frozen'/key,resources/key)
     name='solpi-terminal-locate-first-'+arm
     command=['docker','run','--rm','--name',name,'--user','0:0','--entrypoint','/bin/bash','-e','HOME=/eval-home','--mount',f'type=bind,src={home},dst=/eval-home','--mount',f'type=bind,src={work},dst=/app/dclm','--mount',f'type=bind,src={resources},dst=/skills,readonly','-w','/app/dclm',IMAGE,'-c','exec "$@"','actor','codex','exec','--json','--ignore-user-config','--ephemeral','--dangerously-bypass-approvals-and-sandbox','--model','gpt-6.1-sol',(OUT/(arm+'-prompt.txt')).read_text()]
     if len(list(OUT.glob('codex/*/actor-start.json')))>=4:raise RuntimeError('Four-start budget exhausted')
     with (dest/'actor-start.json').open('x') as f:json.dump({'arm':arm,'timeout_seconds':180,'plan_sha256':sha(OUT/'plan.json'),'full_resource_mount':True},f,indent=2)
     start=time.monotonic();timeout=False
     try:r=call(command,timeout=180);stdout,stderr,code=r.stdout,r.stderr,r.returncode
     except subprocess.TimeoutExpired as e:stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True;call(['docker','rm','-f',name])
     elapsed=time.monotonic()-start
     changes.append(publish(dest/'stdout.jsonl',stdout));changes.append(publish(dest/'stderr.txt',stderr))
     # Snapshot complete filesystem including Git/untracked before verifier touches it.
     final=files(work);base=json.loads((OUT/'baseline-files.json').read_text());changed=[p for p,v in final.items() if base.get(p)!=v];deleted=sorted(set(base)-set(final))
     with tarfile.open(dest/'final-state-delta.tar.gz','w:gz') as tar:
      for p in changed:tar.add(work/p,arcname=p,recursive=False)
     write(dest/'final-state-manifest.json',{'files_sha256':final,'changed_or_added_files':changed,'deleted_files':deleted,'delta_sha256':sha(dest/'final-state-delta.tar.gz'),'capture':'Complete Git and working/untracked files after actor exit, before verifier','baseline_image_id':IMAGE})
     # Trusted baseline commit comparison captures staged/unstaged/committed edits.
     diff=call(['git','-c',f'safe.directory={work}','-C',str(work),'diff','--binary','d6987af002b122fef54bc0be402062c76488a4d9']);changes.append(publish(dest/'workspace.patch',diff.stdout))
     changes.append(publish(dest/'workspace-status.txt',call(['git','-c',f'safe.directory={work}','-C',str(work),'status','--porcelain']).stdout))
     g,publication=grade(work,dest/'verifier');changes.append(publication)
     total,basis=collect.token_total('codex',collect.events(dest/'stdout.jsonl'))
     text=(stdout+stderr).decode(errors='replace').lower();blocked=any(s in text for s in ['invalid_grant','authentication failed','failed to refresh oauth','insufficient_quota','quota exceeded','usage limit','login required','unauthorized'])
     record.update(execution_status='blocked_auth_or_quota' if blocked else 'timeout' if timeout else 'completed' if code==0 else 'agent_error',timeout=timeout,elapsed_seconds=elapsed,exit_code=code,grade_exit_code=g,solved=None if blocked or g not in (0,1) else g==0,reported_total_tokens=total,token_basis=basis,transcript_sha256=hashlib.sha256(stdout).hexdigest(),published_transcript_sha256=sha(dest/'stdout.jsonl'),patch_sha256=hashlib.sha256(diff.stdout).hexdigest(),published_patch_sha256=sha(dest/'workspace.patch'))
     call(['docker','run','--rm','--network','none','--mount',f'type=bind,src={tmp},dst=/cleanup','--mount',f'type=bind,src={home},dst=/private-auth',IMAGE,'chown','-R',f'{os.getuid()}:{os.getgid()}','/cleanup','/private-auth'])
  write(dest/'result.json',record);results.append(record);write(OUT/'results.json',results);write(OUT/'publication-redaction-audit.json',{'originals':'Private outside Git under restrictive permissions','changes':changes});print(json.dumps(record),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','execute']);args=parser.parse_args();prepare() if args.action=='prepare' else execute()
