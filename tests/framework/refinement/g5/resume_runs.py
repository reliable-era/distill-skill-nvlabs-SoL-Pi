"""G5 user-authorized recovery2026-10-16. No metadata/server operations.
Canonical scoring latest attempt,all original costs;5xx max5,circuit/backoff.
"""
import argparse,collections,concurrent.futures,datetime,json,pathlib,random,subprocess,threading,time
from common import H,R,private_root,save,sha,verify_preregistration,disk_free
from run_swe_cell import attempt
from model_images import ModelImages
from prepare_source import prepare
from five_xx import Circuit,backoff,decision,append,record,utc,budget_attempts
from archive_records import compress
from storage_watch import Watch
from audit_receipts import audit

def main(commit):
 root=private_root();verify_preregistration();m=json.loads((H/'resume-stage.json').read_text());assert subprocess.check_output(['git','show',commit+':'+str((H/'resume-stage.json').relative_to(R))],cwd=R)==(H/'resume-stage.json').read_bytes()
 assert set(m['source_sha256'])=={f.name for f in H.glob('*.py')}
 for f,d in m['source_sha256'].items():assert sha(H/f)==d
 assert sha(root/'dataset.json')==m['private_dataset_sha256'] and sha(root/'controls-complete.json')==m['private_controls_sha256']
 phase_name=m['phase'];stop_file=root/'ADMISSIONS-STOP';assert not stop_file.exists(),'Supervisor hold remains';assert sha(root/m['recovery_file'])==m['private_recovery_sha256'];assert not (root/(phase_name+'-launch.json')).exists();save(root/(phase_name+'-launch.json'),dict(pid=__import__('os').getpid(),commit=commit,utc=utc()));recovery=json.loads((root/m['recovery_file']).read_text());controls=json.loads((root/'controls-complete.json').read_text());assert controls['completed_issues']==500 and len(controls['eligible_tasks'])==444;queue=json.loads((root/'queue.json').read_text());assert sha(root/'queue.json')==m['queue_sha256'];queue=[c for c in queue if c['task'] in controls['eligible_tasks']];results=list(recovery['retained_rows']);done={v['cell_id'] for v in results};pending=[c for c in queue if c['cell_id'] not in done];assert len(results)+len(pending)==1776;template=json.loads((root/'grader-template.json').read_text());dataset={v['instance_id']:v for v in json.loads((root/'dataset.json').read_text())};ctxs={};mutex=threading.RLock();active={};stop=threading.Event();permits=threading.Semaphore(4);images=ModelImages(root,phase_name);global_log=root/'http5xx-global.jsonl';circuit=Circuit(root/'http5xx-circuit.jsonl');phase=root/phase_name;admissions=[];charged={k:list(v) for k,v in recovery['prior_attempt_rows'].items()}
 for v in results:charged[v['cell_id']]=v['attempt_rows']
 for seed in recovery['last16_finished_attempts']:circuit.finish(seed['ended5xx'],seed['cell_id'],seed['attempt'])
 for c in pending:
  x=ctxs.setdefault(c['task'],dict(lock=threading.RLock(),ready=False,remaining=0,directory=phase/c['task'],permit=False));x['remaining']+=1
 def stats():
  event_rows=[json.loads(line) for line in global_log.read_text().splitlines()] if global_log.exists() else [];events=len(event_rows);response_events=sum(e['source'] in ('provider_response','broker_proxy_exception','historical_provider_response') for e in event_rows)
  save(H/'progress.json',dict(stage='models',completed_cells=len(results),planned_eligible_cells=1776,active_slots=len(active),rolling_slots=16,http5xx_count=events,http_response_5xx_count=response_events,native_5xx_diagnostic_count=events-response_events,http5xx_count_unit='all recorded observations;response and native diagnostics separately reported',terminal_5xx_attempts=sum(bool(a.get('ended_on_5xx')) for aa in charged.values() for a in aa),solves=sum(v['solved'] is True for v in results),infra_exhausted=sum(v.get('status')=='infra-exhausted' for v in results),requests=sum(a['requests'] for aa in charged.values() for a in aa),known_tokens_lower_bound=sum(a['known_tokens_lower_bound'] for aa in charged.values() for a in aa),retry_overhead_tokens_lower_bound=sum(a['known_tokens_lower_bound'] for aa in charged.values() for a in aa[1:]),root_free_bytes=disk_free(),circuit_pause_until_epoch=circuit.until))
 def group(iid):
  x=ctxs[iid]
  with x['lock']:
   if x['ready']:return x
   if stop.is_set() or stop_file.exists():raise RuntimeError('Owned safety stop')
   permits.acquire();x['permit']=True;x['directory'].mkdir(parents=True,exist_ok=True);v=json.loads((root/controls['control_session']/iid/'final-control.json').read_text());lease=images.acquire_control_image(iid,v['image_lease']);baseline=x['directory']/'source';prepare(dataset[iid],lease['image_id'],baseline);taskfile=x['directory']/'task.json';save(taskfile,[dataset[iid]]);gp=x['directory']/'grader-plan.json';save(gp,dict(template,images={iid:lease['image_id']},private_dataset=str(taskfile),private_dataset_sha256=sha(taskfile)));x['plan']=dict(all500_controls_complete=True,eligible_tasks=controls['eligible_tasks'],caps=dict(requests=60,seconds=7200,output_tokens=16384),images={iid:lease['image_id']},prepared_tasks={iid:str(baseline)},wheelhouse=template['wheelhouse'],grader_python='/tmp/solpi-refinement-harbor-venv/bin/python',grader_plan=str(gp),global_5xx_log=str(global_log),admission_stop_file=str(stop_file),arm_skills={'none':[],'K':['K'],'ours':['ours'],'Both':['K','ours']},skills={k:dict(path=str(R/p),SKILL_sha256=sha(R/p/'SKILL.md')) for k,p in [('ours',pathlib.Path('skills/efficient-coding')),('K',pathlib.Path('tests/framework/refinement/g2/frozen/karpathy'))]});x['ready']=True;return x
 def admit(cell,n):
  circuit.wait(stop)
  with mutex:
   if stop.is_set() or stop_file.exists():raise RuntimeError('Owned safety stop')
   a=dict(cell_id=cell['cell_id'],attempt=n,occupied_slots_after_admission=len(active),route='127.0.0.1:8000',plain_client=True,utc=utc());assert 1<=len(active)<=16;admissions.append(a);save(root/(phase_name+'-admissions.json'),admissions);stats();return a
 def run(cell):
  cid=cell['cell_id'];iid=cell['task'];x=ctxs[iid];rows=list(recovery['prior_attempt_rows'].get(cid,[]))
  with mutex:active[cid]=True;assert len(active)<=16;stats()
  try:
   x=group(iid);last_policy=None
   while budget_attempts(rows)<5:
    n=len(rows)+1
    if rows and rows[-1].get('ended_on_5xx',False):
     delay=backoff(budget_attempts(rows));append(root/'http5xx-backoff.jsonl',dict(utc=utc(),cell=cid,next_attempt=n,seconds=delay));end=time.monotonic()+delay
     while time.monotonic()<end:
      if stop.wait(min(1,max(0,end-time.monotonic()))):raise RuntimeError('Owned safety stop')
    circuit.wait(stop);d=x['directory']/(cid+'-a'+str(n));row=attempt(cell,n,d,x['plan'],dict(cells=[c['cell_id'] for c in queue]),admit);raw=(d/'native.jsonl').read_bytes() if (d/'native.jsonl').exists() else b'';p=decision(row,budget_attempts(rows)+int(not row.get('harness_failure',False)),raw);row['budget_attempt']=budget_attempts(rows)+int(not row.get('harness_failure',False));row['connection_infra_failure']=p['connection_infra_failure'];row['ended_on_5xx']=p['ended_on_5xx'];row['five_xx_policy']=p
    for event in p['native_evidence']['native_http5xx_events']:
     for status in event['status_codes']:record(d/'transport',global_log,cid,n,status,None,'native_event',event_time=event['event_time'])
    if (d/'transport/http5xx.jsonl').exists():
     for line in (d/'transport/http5xx.jsonl').read_text().splitlines():append(root/'http5xx-cells'/(cid+'.jsonl'),json.loads(line))
    rows.append(row);save(d/'attempt-result.json',row);save(x['directory']/(cid+'-all-attempts.json'),rows);audit(row);circuit.finish(p['ended_on_5xx'],cid,n)
    with mutex:charged[cid]=list(rows);stats()
    if row.get('safety_stop') or (row.get('phase')=='capture' and row.get('native_exit')==0 and row.get('error')):
     save(stop_file,dict(reason='native success followed by capture failure',cell_id=cid,attempt=n));stop.set();raise RuntimeError('Capture regression safety stop;cost retained;no new calls')
    if not row['owned_cleanup_verified']:stop.set();raise RuntimeError('Owned cleanup uncertain')
    if not row['native_started'] and row.get('error'):stop.set();raise RuntimeError('Runner setup failure;retain and inspect,not model outcome')
    last_policy=p
    if not p['retry']:break
   assert rows;last=rows[-1];exhausted=(last_policy or {}).get('infra_exhausted',False);solved=last['solved'] if last['grade_valid'] else None
   if exhausted:solved=False
   elif not last.get('connection_infra_failure') and last.get('patch_sha256')=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' and last.get('native_exit') not in (None,0):solved=False
   summary=dict(cell_id=cid,task=iid,arm=cell['arm'],attempts=len(rows),scored_attempt=last['attempt'],grade_valid=last['grade_valid'],solved=solved,status='infra-exhausted' if exhausted else 'finished',budget_attempts=budget_attempts(rows),requests=sum(a['requests'] for a in rows),known_tokens_lower_bound=sum(a['known_tokens_lower_bound'] for a in rows),cost_complete=all(a['cost_complete'] for a in rows),native_timeouts=sum(a['timeout'] for a in rows),grader_timeouts=sum(a['grader_timeout'] for a in rows),retry_overhead_tokens_lower_bound=sum(a['known_tokens_lower_bound'] for a in rows[1:]),attempt_rows=rows)
   with mutex:results.append(summary);save(root/'model-summary.json',results);stats();print('models',len(results),'of1776',flush=True)
  except BaseException:stop.set();raise
  finally:
   try:
    with x['lock']:
     x['remaining']-=1
     if x['remaining']==0:
      images.release(iid)
      if x['permit']:permits.release()
      if not stop.is_set():save(root/('archives-'+phase_name)/('group-'+iid+'.json'),compress(x['directory'],root/('archives-'+phase_name),root))
   finally:
    with mutex:active.pop(cid,None)
 save(root/('model-summary-pre-'+phase_name+'.json'),json.loads((root/'model-summary.json').read_text()));save(root/(phase_name+'-submitted-queue.json'),pending)
 with mutex:save(root/'model-summary.json',results);stats()
 watch=Watch(root,stop,models_dir=phase);watch.start()
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
   fs=[pool.submit(run,c) for c in pending]
   for f in concurrent.futures.as_completed(fs):f.result()
 finally:watch.close()
 assert len(results)==1776;save(root/'models-complete.json',dict(cells=1776,attempts=sum(v['attempts'] for v in results),all_results_retained=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--allowance-commit',required=True);main(p.parse_args().allowance_commit)
