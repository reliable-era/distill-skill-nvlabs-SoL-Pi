"""Reuse pinned first-control worker on remaining fixed tasks;two bounded workers."""
import concurrent.futures,datetime,hashlib,json,pathlib,subprocess,sys,threading
R=pathlib.Path(__file__).resolve().parent;template=(R/'run_first_terminal_controls.py').read_text();inventory=json.loads((R/'terminal-readiness-inventory.json').read_text());tasks=inventory['tasks'][1:];private=pathlib.Path('/tmp/solpi-remaining-terminal-controls-v1');private.mkdir(mode=0o700,exist_ok=False)
def sha(data):return hashlib.sha256(data).hexdigest()
def generated(t):
 s=template.replace("SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/break-filter-js-from-html')","SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/"+t['id']+"')").replace("PRIVATE=pathlib.Path('/tmp/solpi-first-terminal-controls-v1')","PRIVATE=pathlib.Path('/tmp/solpi-controls-"+t['id']+"-v1')").replace("TASK='break-filter-js-from-html'","TASK="+repr(t['id']))
 s=s.replace('terminal-first-control-plan.json','control-'+t['id']+'-plan.json').replace('terminal-first-controls-progress.json','control-'+t['id']+'-progress.json').replace('terminal-first-controls.json','control-'+t['id']+'-result.json')
 s=s.replace("'cpus':1,'memory_mb':2048","'cpus':"+str(t['declared_cpus'])+",'memory_mb':"+str(t['memory_mb'])).replace("'--cpus','1','--memory','2048m'","'--cpus',"+repr(str(t['declared_cpus']))+",'--memory',"+repr(str(t['memory_mb'])+'m'))
 assert "TASK="+repr(t['id']) in s and "'--memory',"+repr(str(t['memory_mb'])+'m') in s
 return s
stopped=threading.Event()
sources={t['id']:generated(t) for t in tasks};plan={'tasks':[t['id'] for t in tasks],'first_task_controls_reused':True,'template_sha256':sha(template.encode()),'generated_worker_sha256':{k:sha(v.encode()) for k,v in sources.items()},'maximum_parallel_workers':2,'maximum_worker_seconds':1800,'oracle_seconds':300,'verifier_seconds':600,'retries':0,'model_POSTs':0,'candidate_changes_allowed':False,'task_substitutions_allowed':False};(R/'remaining-terminal-control-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
def worker(t):
 if stopped.is_set():return {'task':t['id'],'status':'unstarted_after_uncertain_cleanup'}
 code=sources[t['id']];log=private/(t['id']+'.log');launch="exec(compile("+repr(code)+",'pinned-control-worker','exec'),{'__name__':'__main__','__file__':"+repr(str(R/'run_first_terminal_controls.py'))+"})"
 with log.open('wb') as f:
  try:p=subprocess.run([sys.executable,'-c',launch],stdout=f,stderr=subprocess.STDOUT,timeout=1800);row={'task':t['id'],'worker_exit':p.returncode}
  except subprocess.TimeoutExpired:row={'task':t['id'],'status':'worker_deadline_cleanup_requires_review'}
 result=R/('control-'+t['id']+'-result.json')
 if result.exists():
  x=json.loads(result.read_text());row.update(valid_pair=x['valid_baseline_gold_pair'],controls=[{k:c.get(k) for k in ['control','oracle_exit','reward','test_events','error_type','owned_container_absent']} for c in x['controls']])
 if row.get('status')=='worker_deadline_cleanup_requires_review' or ('controls' in row and any(c.get('owned_container_absent') is not True for c in row['controls'])):stopped.set()
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(worker,tasks))
out={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tasks':rows,'model_POSTs':0,'first_task_not_repeated':True,'scope':'Official environment baseline/gold controls;not model comparison or final certification'};(R/'remaining-terminal-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
