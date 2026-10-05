"""Single guarded zero-start resumption; immutable original plan/result, bounded wait."""
import pathlib,json,hashlib,time,fcntl,os,http.client,subprocess
from run_output_contract_preflight_fasttext_screen import code as original_code
R=pathlib.Path(__file__).resolve().parent
PLAN=R/'output-contract-preflight-fasttext-plan.json'
RESULT=R/'output-contract-preflight-fasttext-result.json'
CONTRACT=R/'output-contract-preflight-resume-contract.json'
WAIT=R/'output-contract-preflight-resume-wait.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate_zero(result,entries):
 if type(result.get('starts')) is not int or type(result.get('POST')) is not int or result['starts']!=0 or result['POST']!=0 or result.get('rows')!=[]:raise RuntimeError('not a zero-start panel')
 if set(entries)!={'live-source-pins.json'}:raise RuntimeError('unexpected existing actor/transport state')
def transformed():
 s=original_code
 pairs=[("(R/'output-contract-preflight-fasttext-plan.json').write_text(json.dumps(plan,indent=2)+'\\n')","assert_frozen_plan(plan)"),('root.mkdir(mode=0o700,exist_ok=False)','assert_zero_root(root)'),("scheduler_wait_seconds=0.0","scheduler_wait_seconds=resume_wait_seconds"),("root/'live-source-pins.json'","root/'live-source-pins-resume.json'"),('output-contract-preflight-fasttext-result.json','output-contract-preflight-fasttext-resume-result.json'),('output-contract-preflight-fasttext-progress.json','output-contract-preflight-fasttext-resume-progress.json')]
 for a,b in pairs:
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 compile(s,'guarded-zero-start-resume','exec');return s

def main():
 fd=os.open(R/'output-contract-preflight-resume.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  assert not CONTRACT.exists(),'ONE resumption attempt only'
  plan_bytes=PLAN.read_bytes();p=json.loads(plan_bytes);digest=sha(PLAN);prior=json.loads(RESULT.read_text());assert prior['plan_sha256']==digest
  root=pathlib.Path('/tmp/solpi-oc16-'+digest[:18]);validate_zero(prior,[x.name for x in root.iterdir()]);assert not pathlib.Path('/proc/1413967').exists()
  for args in [['docker','ps','-a','--filter','name=solpi-oc16','--format','{{.Names}}'],['docker','network','ls','--filter','name=solpi-oc16','--format','{{.Name}}']]:assert not subprocess.check_output(args,text=True,timeout=10).strip()
  s=transformed();contract={'original_plan_sha256':digest,'original_result_sha256':sha(RESULT),'original_generated_code_sha256':hashlib.sha256(original_code.encode()).hexdigest(),'resume_generated_code_sha256':hashlib.sha256(s.encode()).hexdigest(),'resume_script_sha256':sha(pathlib.Path(__file__)),'changed_behavior':'zero-start-only activation; preserve original evidence; cumulative metadata wait charged to existing300s idle ceiling','actor_runtime_delta':'NONE','remaining_starts':4,'remaining_POST':64,'retry_of_started_actor':False,'model':'localQwen3.8-27B-FP8 only','max_scheduler_wait_seconds':300,'promotion':False,'goal_complete':False};CONTRACT.write_text(json.dumps(contract,indent=2)+'\n')
  start=time.monotonic();observations=[];ready=False
  while time.monotonic()-start<300:
   c=http.client.HTTPConnection('127.0.0.1',8000,timeout=min(2,300-(time.monotonic()-start)))
   try:
    c.request('GET','/get_load');z=c.getresponse();b=z.read(65537);v=json.loads(b) if len(b)<=65536 else None
    counts=[{k:x.get(k) for k in ['num_reqs','num_waiting_reqs']} for x in v] if isinstance(v,list) and all(isinstance(x,dict) for x in v) else None
    ready=z.status==200 and bool(counts) and all(type(x[k]) is int and x[k]==0 for x in counts for k in ['num_reqs','num_waiting_reqs'])
    observations.append({'elapsed':time.monotonic()-start,'status':z.status,'counts':counts,'body_sha256':hashlib.sha256(b).hexdigest()})
   except Exception as e:observations.append({'elapsed':time.monotonic()-start,'error_type':type(e).__name__})
   finally:c.close()
   used=time.monotonic()-start;WAIT.write_text(json.dumps({'observations':observations,'ready':ready,'consumed_scheduler_wait_seconds':used,'model_POST':0,'original_admission_cause_inferred':False},indent=2)+'\n')
   if ready:break
   time.sleep(max(0,min(10,300-used)))
  used=time.monotonic()-start
  ready=ready and used<300
  WAIT.write_text(json.dumps({'observations':observations,'ready':ready,'consumed_scheduler_wait_seconds':used,'model_POST':0,'original_admission_cause_inferred':False},indent=2)+'\n')
  if not ready:print('BLOCKED: existing300s scheduler ceiling; no actors; original evidence unchanged');return
  def assert_plan(current):
   assert PLAN.read_bytes()==plan_bytes
   assert (json.dumps(current,indent=2)+'\n').encode()==plan_bytes,'frozen plan regeneration mismatch'
  def assert_root(current):
   assert current==root;validate_zero(prior,[x.name for x in root.iterdir()])
  exec(compile(s,'guarded-zero-start-resume','exec'),{'__name__':'__main__','__file__':str(R/'run_output_contract_preflight_fasttext_screen.py'),'assert_frozen_plan':assert_plan,'assert_zero_root':assert_root,'resume_wait_seconds':used})
  assert PLAN.read_bytes()==plan_bytes and sha(RESULT)==contract['original_result_sha256']
if __name__=='__main__':main()
