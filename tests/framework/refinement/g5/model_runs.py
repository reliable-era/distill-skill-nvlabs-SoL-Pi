"""G5 stage3: exact fixed queue,16 rolling cell workers,4 JIT image groups.
Only starts after all500 controls/committed runtime specification. No metadata
health calls, no queue gating, no third attempts or outcome-selected issues.
"""
import argparse,concurrent.futures,datetime,json,os,pathlib,re,subprocess,threading,time
from common import H,R,sha,save,private_root,verify_preregistration,disk_free
from model_images import ModelImages,ImageUnavailable
from prepare_source import prepare
from retry_policy import classify
from archive_records import compress
from run_swe_cell import attempt
from images import StorageBlocked
from storage_watch import Watch

def verify_barrier(root,commit):
 p=verify_preregistration();c=json.loads((root/'controls-complete.json').read_text());assert c['completed_issues']==500 and c['model_calls']==0;assert c['summary_sha256']==sha(H/'control-summary.csv');m=json.loads((H/'model-stage.json').read_text());assert m['control_summary_sha256']==c['summary_sha256'] and m['eligible_tasks_sha256']==sha(root/'controls-complete.json')
 for f,d in m['source_sha256'].items():assert sha(H/f)==d
 assert re.fullmatch('[0-9a-f]{40}',commit);subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=R,check=True,capture_output=True,timeout=10);path=(H/'model-stage.json').relative_to(R);assert subprocess.check_output(['git','show',commit+':'+str(path)],cwd=R,timeout=10)==(H/'model-stage.json').read_bytes(),'Committed model allowance required';return p,c

def main(commit):
 root=private_root();p,controls=verify_barrier(root,commit);assert not (root/'models-launch.json').exists(),'Existing model handle: reconcile/wait, never restart';save(root/'models-launch.json',dict(pid=os.getpid(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),slots=16));queue=json.loads((root/'queue.json').read_text());assert sha(root/'queue.json')==p['queue_sha256'];eligible=set(controls['eligible_tasks']);cells=[c for c in queue if c['task'] in eligible];assert len(cells)==4*len(eligible);lookup={r['instance_id']:r for r in json.loads((root/'dataset.json').read_text())};template=json.loads((root/'grader-template.json').read_text());session=controls['control_session'];images=ModelImages(root);group_permits=threading.Semaphore(4);mutex=threading.RLock();active={};stop=threading.Event();results=[];contexts={};admissions=[]
 for cell in cells:
  iid=cell['task']
  if iid not in contexts:contexts[iid]=dict(lock=threading.RLock(),prepared=False,remaining=4,failures=[],directory=root/'models'/iid,owns_permit=False)
 def group_ready(iid):
  ctx=contexts[iid]
  with ctx['lock']:
   if ctx['prepared']:return ctx
   if stop.is_set():raise RuntimeError('Owned/storage uncertainty; no new model admission')
   group_permits.acquire();ctx['owns_permit']=True;ctx['directory'].mkdir(parents=True,exist_ok=True);control=json.loads((root/session/iid/'final-control.json').read_text());assert control['valid_pair'];original_lease=control['image_lease']
   for n in (1,2):
    try:
     lease=images.acquire_control_image(iid,original_lease);prepared=ctx['directory']/('source-'+str(n));prepare(lookup[iid],lease['image_id'],prepared);ctx['baseline']=prepared;ctx['lease']=lease;break
    except StorageBlocked:stop.set();raise
    except subprocess.CalledProcessError as e:ctx['failures'].append(dict(category='container_failure_before_native',type=type(e).__name__));images.release(iid)
    except ImageUnavailable as e:ctx['failures'].append(dict(category='image_failure',type=type(e).__name__));images.release(iid)
   if ctx.get('baseline'):
    baseline=ctx['baseline'];plan=dict(all500_controls_complete=True,eligible_tasks=sorted(eligible),caps=p['caps'],images={iid:ctx['lease']['image_id']},prepared_tasks={iid:str(baseline)},wheelhouse=template['wheelhouse'],grader_python='/tmp/solpi-refinement-harbor-venv/bin/python',arm_skills={'none':[],'K':['K'],'ours':['ours'],'Both':['K','ours']},skills={'ours':dict(path=str(R/'skills/efficient-coding'),SKILL_sha256=p['skills_sha256']['skills/efficient-coding/SKILL.md']),'K':dict(path=str(R/'tests/framework/refinement/g2/frozen/karpathy'),SKILL_sha256=p['skills_sha256']['tests/framework/refinement/g2/frozen/karpathy/SKILL.md'])});taskfile=ctx['directory']/'task.json';save(taskfile,[lookup[iid]]);grader=dict(template,images=plan['images'],private_dataset=str(taskfile),private_dataset_sha256=sha(taskfile));graderfile=ctx['directory']/'grader-plan.json';save(graderfile,grader);plan['grader_plan']=str(graderfile);ctx['plan']=plan
   ctx['prepared']=True;return ctx
 def callback(cell,n):
  with mutex:
   if stop.is_set():raise RuntimeError('Owned/storage uncertainty; no new admission')
   assert cell['cell_id'] in active and 1<=len(active)<=16
   a=dict(cell_id=cell['cell_id'],attempt=n,occupied_slots_after_admission=len(active),plain_client=True,route='127.0.0.1:8000',utc=datetime.datetime.now(datetime.timezone.utc).isoformat());admissions.append(a);save(root/'model-admissions.json',admissions);return a
 def zero_failure(cell,n,error):
  d=contexts[cell['task']]['directory']/(cell['cell_id']+'-a'+str(n));d.mkdir(mode=0o700);r=dict(cell_id=cell['cell_id'],part='C',task=cell['task'],arm=cell['arm'],round=1,attempt=n,root=str(d),native_started=False,requests=0,known_tokens_lower_bound=0,cost_complete=True,solved=None,grade_valid=False,timeout=False,grader_timeout=False,owned_cleanup_verified=True,error=error);save(d/'attempt-result.json',r);return r
 def cell_run(cell):
  iid=cell['task'];ctx=contexts[iid];rows=[]
  with mutex:active[cell['cell_id']]=dict(task=iid);assert len(active)<=16
  try:
   ctx=group_ready(iid)
   for n,e in enumerate(ctx['failures'],1):rows.append(zero_failure(cell,n,e))
   if len(rows)<2 and ctx.get('baseline'):
    plan=ctx['plan'];window=dict(cells=[c['cell_id'] for c in cells],full_G5_allowance=True)
    for n in range(len(rows)+1,3):
     row=attempt(cell,n,ctx['directory']/(cell['cell_id']+'-a'+str(n)),plan,window,callback)
     if not row['native_started'] and (row.get('error') or {}).get('type')=='CalledProcessError':row['error']['category']='container_failure_before_native';save(pathlib.Path(row['root'])/'attempt-result.json',row)
     rows.append(row)
     if (row.get('error') or {}).get('type')=='StorageBlocked':stop.set();raise StorageBlocked('Early storage guard; retain current attempt, no new admission')
     policy=classify(row);save(ctx['directory']/(cell['cell_id']+'-attempts.json'),rows);save(ctx['directory']/(cell['cell_id']+'-retry-policy.json'),policy)
     if policy.get('stop'):stop.set();raise RuntimeError('Unclassified runner/cleanup failure; inspect before further admission')
     if not policy['retry']:break
   assert 1<=len(rows)<=2;save(ctx['directory']/(cell['cell_id']+'-attempts.json'),rows);last=rows[-1];summary=dict(cell_id=cell['cell_id'],task=iid,arm=cell['arm'],attempts=len(rows),scored_attempt=last['attempt'],grade_valid=last['grade_valid'],solved=last['solved'] if last['grade_valid'] else None,requests=sum(r['requests'] for r in rows),known_tokens_lower_bound=sum(r['known_tokens_lower_bound'] for r in rows),cost_complete=all(r['cost_complete'] for r in rows),native_timeouts=sum(r['timeout'] for r in rows),grader_timeouts=sum(r['grader_timeout'] for r in rows),attempt_rows=rows)
   with mutex:results.append(summary);save(root/'model-summary.json',results);save(H/'progress.json',dict(stage='models',completed_cells=len(results),planned_eligible_cells=len(cells),solves=sum(r['solved'] is True for r in results),requests=sum(r['requests'] for r in results),known_tokens_lower_bound=sum(r['known_tokens_lower_bound'] for r in results),root_free_bytes=disk_free()));print('models',len(results),'of',len(cells),flush=True)
   return summary
  except BaseException:stop.set();raise
  finally:
   try:
    with ctx['lock']:
     ctx['remaining']-=1
     if ctx['remaining']==0:
      images.release(iid)
      if ctx['owns_permit']:group_permits.release()
      # Compression/owned cleanup remain inside the occupied run slot.
      if not stop.is_set():save(root/'archives'/('group-'+iid+'.json'),compress(ctx['directory'],root/'archives',root))
   except BaseException:stop.set();raise
   finally:
    with mutex:active.pop(cell['cell_id'],None)
 watch=Watch(root,stop);watch.start()
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
   futures=[pool.submit(cell_run,c) for c in cells]
   for f in concurrent.futures.as_completed(futures):f.result()
 finally:watch.close()
 assert len(results)==len(cells) and not active;save(root/'models-complete.json',dict(cells=len(cells),attempts=sum(r['attempts'] for r in results),all_results_retained=True));print('STAGE BOUNDARY: eligible G5 model cells/grades finished; reconcile audits/analysis before completion.',flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--allowance-commit',required=True);args=parser.parse_args();main(args.allowance_commit)
