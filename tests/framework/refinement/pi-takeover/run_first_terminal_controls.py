"""One prospective baseline/gold pair;opaque official oracle/tests;no actor calls."""
import datetime,hashlib,json,pathlib,subprocess,time,uuid
R=pathlib.Path(__file__).resolve().parent;SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/break-filter-js-from-html');PRIVATE=pathlib.Path('/tmp/solpi-first-terminal-controls-v1');TASK='break-filter-js-from-html'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p):return {str(x.relative_to(p)):sha(x) for x in sorted(p.rglob('*')) if x.is_file()}
if __name__=='__main__':
 PRIVATE.mkdir(mode=0o700,exist_ok=False)
 cache=json.loads((R/'terminal-selected-image-cache.json').read_text());image=next(x['image']['image_id'] for x in cache['tasks'] if x['task']==TASK)
 candidate=R.parent/'development/pi-takeover-qwen-incremental-coverage/frozen/candidate/SKILL.md'
 plan={'task':TASK,'image_id':image,'source_hashes':tree(SOURCE),'candidate_sha256':sha(candidate),'controls':['baseline','gold'],'cpus':1,'memory_mb':2048,'oracle_seconds':300,'verifier_seconds':600,'retry':0,'model_POSTs':0,'network':'Docker bridge for official dependency/source downloads;no host credentials/model config','candidate_changes_allowed':False}
 (PRIVATE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');(R/'terminal-first-control-plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 for kind in plan['controls']:
  d=PRIVATE/kind;d.mkdir();logs=d/'logs';(logs/'verifier').mkdir(parents=True);name='solpi-tb-control-'+uuid.uuid4().hex[:12];row={'control':kind,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};created=False
  try:
   subprocess.run(['docker','create','--pull=never','--name',name,'--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SOURCE/'tests')+':/tests:ro','-v',str(SOURCE/'solution')+':/solution:ro','-v',str(logs)+':/logs','--entrypoint','/bin/sh',image,'-c','sleep infinity'],capture_output=True,check=True,timeout=15);created=True
   subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=15)
   if kind=='gold':
    with (d/'oracle.log').open('wb') as f:
     p=subprocess.run(['docker','exec',name,'bash','/solution/solve.sh'],stdout=f,stderr=subprocess.STDOUT,timeout=300);row['oracle_exit']=p.returncode
   with (d/'verifier.log').open('wb') as f:
    start=time.monotonic();p=subprocess.run(['docker','exec',name,'bash','/tests/test.sh'],stdout=f,stderr=subprocess.STDOUT,timeout=600);row.update(verifier_exit=p.returncode,verifier_seconds=time.monotonic()-start)
   reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json';row['reward']=reward.read_text().strip() if reward.exists() else None;row['ctrf_present']=ctrf.exists()
   if ctrf.exists():
    data=json.loads(ctrf.read_text());events=data.get('results',{}).get('tests',[]);row['test_status_counts']={s:sum(e.get('status')==s for e in events) for s in sorted({e.get('status') for e in events})};row['test_events']=len(events)
   row['artifacts_sha256']=tree(d)
  except Exception as e:row.update(error_type=type(e).__name__,status='control_infrastructure_failure')
  finally:
   if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
   p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);row['owned_container_absent']=p.returncode!=0 and name in p.stderr and 'No such' in p.stderr
  rows.append(row);(R/'terminal-first-controls-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
  if not row['owned_container_absent']:break
 assert sha(candidate)==plan['candidate_sha256'] and tree(SOURCE)==plan['source_hashes']
 valid=len(rows)==2 and all(x.get('ctrf_present') and x.get('test_events',0)>0 and x['owned_container_absent'] for x in rows) and rows[0]['reward']=='0' and rows[1]['reward']=='1' and rows[1].get('oracle_exit')==0
 out={'plan_sha256':sha(PRIVATE/'plan.json'),'controls':rows,'valid_baseline_gold_pair':valid,'model_POSTs':0,'candidate_changed':False,'selection_changed':False,'scope':'First selected task official controls only;not representative scored inference or full9task certification'};(R/'terminal-first-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
