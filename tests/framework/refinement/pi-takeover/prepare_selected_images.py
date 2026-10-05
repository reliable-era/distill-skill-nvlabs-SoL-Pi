"""Bounded fixed-allocation cache warming only;never reads task/gold/test content."""
import concurrent.futures,datetime,hashlib,json,pathlib,subprocess,time
R=pathlib.Path(__file__).resolve().parent;inventory=json.loads((R/'terminal-readiness-inventory.json').read_text());selection_sha=hashlib.sha256((R/'terminal-10pct-selection.json').read_bytes()).hexdigest();PRIVATE=pathlib.Path('/tmp/solpi-terminal-selected-image-prep');PRIVATE.mkdir(mode=0o700,exist_ok=True)
def prepare(task):
 start=time.monotonic();image=task['declared_image'];cached=subprocess.run(['docker','image','inspect',image],capture_output=True,timeout=10);status='already_cached' if cached.returncode==0 else 'not_cached';log=PRIVATE/(task['id']+'.pull.log');rc=None
 if status=='not_cached':
  with log.open('ab') as f:
   try:p=subprocess.run(['docker','pull',image],stdout=f,stderr=subprocess.STDOUT,timeout=180);rc=p.returncode;status='cached' if rc==0 else 'pull_failed'
   except subprocess.TimeoutExpired:status='pull_timeout_no_retry'
 artifact={}
 if status in ('cached','already_cached'):
  x=json.loads(subprocess.check_output(['docker','image','inspect',image],timeout=10))[0];artifact={'image_id':x['Id'],'repo_digests':x['RepoDigests'],'size_bytes':x['Size'],'architecture':x['Architecture'],'os':x['Os']}
 return {'task':task['id'],'declared_image':image,'status':status,'pull_returncode':rc,'elapsed_seconds':time.monotonic()-start,'image':artifact,'model_POSTs':0,'grader_calls':0}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(prepare,inventory['tasks']))
 assert hashlib.sha256((R/'terminal-10pct-selection.json').read_bytes()).hexdigest()==selection_sha
 out={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection_sha256':selection_sha,'fixed_tasks':len(results),'maximum_concurrent_pulls':2,'maximum_pull_seconds_each':180,'automatic_retries':0,'tasks':results,'model_POSTs':0,'grader_calls':0,'task_instructions_tests_solutions_read':False,'scope':'Image cache preparation only;not environment controls,agent readiness or scored inference;unavailable tasks retained without substitution'}
 (R/'terminal-selected-image-cache.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
