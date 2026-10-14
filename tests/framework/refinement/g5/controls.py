"""Stage2: all500 official pairs, JIT images, compact public progress only.
No model calls; no eligibility filtering before each original pair is tried.
"""
import concurrent.futures,csv,datetime,json,pathlib,subprocess,sys,threading
from common import H,sha,save,private_root,verify_preregistration,disk_free
from images import Images,StorageBlocked
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
class ControlHarnessFailed(RuntimeError):pass
def cleanup_worker(directory,iid):
 for kind in ('nop','gold'):
  p=directory/kind/'owned.json'
  if p.exists():
   for name in json.loads(p.read_text())['names']:
    assert name.startswith('sweb.eval.'+iid.lower()+'.g5-grade-')
    subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);r=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);assert r.returncode and 'No such' in r.stderr

def main():
 prereg=verify_preregistration();root=private_root();session=__import__('os').environ.get('G5_CONTROL_SESSION','controls');launch=root/(session+'-launch.json');assert not launch.exists(),'Existing controls: inspect/wait, never restart';save(launch,dict(pid=__import__('os').getpid(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),model_calls=0));tasks=json.loads((root/'dataset.json').read_text());assert len(tasks)==500 and all(all(k in t for k in ('eval_script','log_parser','eval_type')) for t in tasks),'Verify official500-field enrichment before controls';template=json.loads((root/'grader-template.json').read_text());images=Images(root);rows=[];lock=threading.RLock();stop=threading.Event()
 def pair(task):
  if stop.is_set():raise RuntimeError('Admission stopped after ownership/storage uncertainty')
  iid=task['instance_id'];d=root/session/iid;d.mkdir(parents=True,exist_ok=True)
  try:
   lease=images.acquire(iid,session);plan=dict(template,images={iid:lease['image_id']});save(d/'task.json',[task]);plan.update(private_dataset=str(d/'task.json'),private_dataset_sha256=sha(d/'task.json'));save(d/'grader-plan.json',plan)
   with (d/'worker.log').open('xb') as out:
    try:p=subprocess.run([PYTHON,str(H/'control_worker.py'),str(d),str(d/'grader-plan.json')],stdout=out,stderr=subprocess.STDOUT,timeout=1800)
    except subprocess.TimeoutExpired:cleanup_worker(d,iid);raise RuntimeError('Official control worker safety timeout')
   f=d/'control-result.json'
   if p.returncode or not f.exists():cleanup_worker(d,iid);raise ControlHarnessFailed('Control runner failed before valid pair result; do not exclude issue')
   result=json.loads(f.read_text());assert all(c['owned_containers_absent'] for c in result['controls']);result['image_lease']=lease
  except (StorageBlocked,ControlHarnessFailed):stop.set();raise
  except Exception as e:
   cleanup_worker(d,iid);result=dict(task=iid,valid_pair=False,controls=[dict(kind=k,valid=False,classification=type(e).__name__) for k in ('nop','gold')],infrastructure_error=dict(type=type(e).__name__,message=str(e)),model_calls=0)
  finally:
   try:images.release(iid)
   except Exception:stop.set();raise
  save(d/'final-control.json',result)
  with lock:
   rows.append(dict(task=iid,eligible=result['valid_pair'],gold_valid=next(c['valid'] for c in result['controls'] if c['kind']=='gold'),nop_valid=next(c['valid'] for c in result['controls'] if c['kind']=='nop'),failure_category='none' if result['valid_pair'] else 'official_control_failure',private_result_sha256=sha(d/'final-control.json')));save(root/'control-summary.json',rows);save(H/'progress.json',dict(stage='controls',completed_issues=len(rows),eligible_issues=sum(r['eligible'] for r in rows),failed_controls=sum(not r['eligible'] for r in rows),total_issues=500,model_calls=0,root_free_bytes=disk_free()));print('controls',len(rows),'of500;eligible',sum(r['eligible'] for r in rows),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(pair,t) for t in tasks]
  for f in concurrent.futures.as_completed(futures):f.result()
 assert len(rows)==500 and len({r['task'] for r in rows})==500
 with (H/'control-summary.csv').open('w') as out:
  writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(sorted(rows,key=lambda r:r['task']))
 save(root/'controls-complete.json',dict(control_session=session,completed_issues=500,eligible_tasks=[r['task'] for r in rows if r['eligible']],failed_tasks=[r['task'] for r in rows if not r['eligible']],model_calls=0,summary_sha256=sha(H/'control-summary.csv')));save(H/'progress.json',dict(stage='controls_complete',completed_issues=500,eligible_issues=sum(r['eligible'] for r in rows),excluded_issues=sum(not r['eligible'] for r in rows),model_calls=0));print('STAGE BOUNDARY: all500 official gold/no-op control pairs completed; no model calls.',flush=True)
if __name__=='__main__':main()
