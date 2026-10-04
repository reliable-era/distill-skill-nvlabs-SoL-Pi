#!/usr/bin/env python3
"""Bounded native development screen; official Terminal-Bench pytest verifier."""
import hashlib,json,os,random,shutil,subprocess,tempfile,time,importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
TASK=Path('/tmp/solpi-refinement-terminal-bench-2/sanitize-git-repo')
IMAGE='sol-pi-terminal-native:2026-10-04'
def call(args,**kw):return subprocess.run(args,capture_output=True,**kw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def grade(work,dest):
 dest.mkdir(parents=True,exist_ok=True)
 r=call(['docker','run','--rm','--network','none','--mount',f'type=bind,src={work},dst=/app/dclm','--mount',f'type=bind,src={TASK}/tests,dst=/tests,readonly','--mount',f'type=bind,src={dest},dst=/logs/verifier',IMAGE,'python','-m','pytest','--ctrf','/logs/verifier/ctrf.json','/tests/test_outputs.py','-rA'],timeout=180)
 (dest/'grade.txt').write_bytes(r.stdout+r.stderr)
 return r.returncode

def main():
 if (OUT/'plan.json').exists():raise SystemExit('Existing plan: no automatic retries')
 frozen=OUT/'frozen';frozen.mkdir(exist_ok=True)
 sources={'karpathy':ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines','shipped':ROOT/'skills/efficient-coding','lean-parent':ROOT/'tests/framework/refinement/candidates/lean-tools/efficient-coding','no-reread':ROOT/'tests/framework/refinement/candidates/lean-tools-no-reread/efficient-coding'}
 for k,p in sources.items():shutil.copytree(p,frozen/k,dirs_exist_ok=True)
 arms={'none':[],'karpathy':['karpathy'],'shipped':['shipped'],'lean-parent':['lean-parent'],'no-reread':['no-reread'],'both':['karpathy','no-reread']}
 imageid=call(['docker','image','inspect',IMAGE,'--format','{{.Id}}']).stdout.decode().strip()
 jobs=[(h,a) for h in ('pi','codex') for a in arms];random.Random(105).shuffle(jobs)
 prompts={a:(TASK/'instruction.md').read_text()+ ('\n\nApply supplied skill instructions:\n\n'+'\n\n'.join((frozen/k/'SKILL.md').read_text() for k in ks) if ks else '') for a,ks in arms.items()}
 for a,p in prompts.items():(OUT/(a+'-prompt.txt')).write_text(p)
 plan={'purpose':'development only, previously exposed task; not sealed confirmation','maximum_attempts':12,'timeout_seconds':180,'maximum_actor_seconds':2160,'rounds':1,'order_seed':105,'sampling_seed':'TBD','jobs':jobs,'arms':arms,'image':IMAGE,'image_id':imageid,'skills':{k:sha(frozen/k/'SKILL.md') for k in sources},'verifier':'Exact test.sh pytest invocation; bootstrap dependencies preinstalled; offline credential-free container','task_sha256':{str(p.relative_to(TASK)):sha(p) for p in TASK.rglob('*') if p.is_file()},'model':'gpt-6.1-sol','billing_usd':'TBD','skill_delivery':'uniform inline markdown; no auto discovery','git_history':'preserved from task image'}
 (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 baseline=Path('/tmp/solpi-terminal-baseline');baseline.mkdir(exist_ok=True)
 cname='solpi-terminal-source';call(['docker','create','--name',cname,IMAGE]);r=call(['docker','cp',cname+':/app/dclm/.',str(baseline)]);assert r.returncode==0;call(['docker','rm',cname])
 assert grade(baseline,OUT/'sanity-baseline')==1
 with tempfile.TemporaryDirectory(prefix='terminal-oracle-') as tmp:
  w=Path(tmp)/'workspace';shutil.copytree(baseline,w)
  r=call(['docker','run','--rm','--network','none','--mount',f'type=bind,src={w},dst=/app/dclm','--mount',f'type=bind,src={TASK}/solution,dst=/solution,readonly',IMAGE,'bash','/solution/solve.sh'],timeout=180)
  (OUT/'sanity-oracle-execution.txt').write_bytes(r.stdout+r.stderr);assert r.returncode==0
  assert grade(w,OUT/'sanity-oracle')==0
 spec=importlib.util.spec_from_file_location('collect',ROOT/'tests/framework/trials/collect.py');collect=importlib.util.module_from_spec(spec);spec.loader.exec_module(collect)
 results=[];blocked=set()
 for index,(h,a) in enumerate(jobs):
  dest=OUT/h/a;dest.mkdir(parents=True)
  rec={'harness':h,'arm':a,'task':'terminal-bench-2/sanitize-git-repo','round':1,'billing_cost_usd':None,'configured_model':'gpt-6.1-sol'}
  if h in blocked:rec.update(execution_status='not_attempted_auth_or_quota',solved=None,reported_total_tokens=None)
  else:
   with tempfile.TemporaryDirectory(prefix='terminal-native-') as tmp:
    work=Path(tmp)/'workspace';shutil.copytree(baseline,work)
    name='solpi-terminal-'+h+'-'+a
    command=['docker','run','--rm','--name',name,'-e','HOME=/tmp/eval-home','--mount',f'type=bind,src={work},dst=/app/dclm','-w','/app/dclm']
    if h=='pi':command+=['-e','PI_CODING_AGENT_DIR=/auth/.pi/agent','--mount',f'type=bind,src={Path.home()}/.pi/agent/auth.json,dst=/auth/.pi/agent/auth.json,readonly',imageid,'pi','--offline','--mode','json','--print','--no-session','--no-extensions','--no-context-files','--no-skills','--no-prompt-templates','--no-themes','--provider','openai','--model','gpt-6.1-sol','--thinking','low',prompts[a]]
    else:command+=['-e','CODEX_HOME=/tmp/codex','--mount',f'type=bind,src={Path.home()}/.codex/auth.json,dst=/tmp/codex/auth.json,readonly',imageid,'codex','exec','--json','--skip-git-repo-check','--dangerously-bypass-approvals-and-sandbox','-m','gpt-6.1-sol',prompts[a]]
    start=time.monotonic();timeout=False
    try:r=call(command,timeout=180);stdout,stderr,code=r.stdout,r.stderr,r.returncode
    except subprocess.TimeoutExpired as e:stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True;call(['docker','rm','-f',name])
    elapsed=time.monotonic()-start;(dest/'stdout.jsonl').write_bytes(stdout);(dest/'stderr.txt').write_bytes(stderr)
    g=grade(work,dest/'verifier')
    diff=call(['git','-C',str(work),'diff','--binary']);(dest/'workspace.patch').write_bytes(diff.stdout)
    status=call(['git','-C',str(work),'status','--porcelain']);(dest/'workspace-status.txt').write_bytes(status.stdout)
    txt=(stdout+stderr).decode(errors='replace').lower();autherror=any(s in txt for s in ['out of extra usage','authentication failed','invalid api key','insufficient_quota','usage limit','login required','credential store modify failed'])
    if autherror:blocked.add(h)
    total,basis=collect.token_total(h,collect.events(dest/'stdout.jsonl'))
    rec.update(execution_status='blocked_auth_or_quota' if autherror else 'timeout' if timeout else 'completed' if code==0 else 'agent_error',exit_code=code,timeout=timeout,elapsed_seconds=elapsed,grade_exit_code=g,solved=None if autherror or g not in (0,1) else g==0,reported_total_tokens=total,token_basis=basis,transcript_sha256=sha(dest/'stdout.jsonl'),patch_sha256=sha(dest/'workspace.patch'))
    call(['docker','run','--rm','--network','none','--mount',f'type=bind,src={work},dst=/app/dclm',imageid,'chown','-R',f'{os.getuid()}:{os.getgid()}','/app/dclm'])
  (dest/'result.json').write_text(json.dumps(rec,indent=2)+'\n');results.append(rec);(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(rec),flush=True)
if __name__=='__main__':main()
