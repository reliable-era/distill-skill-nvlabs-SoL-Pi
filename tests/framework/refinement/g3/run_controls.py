"""G3 full eligible gold/starter controls: no model calls, private logs."""
import concurrent.futures as F
import datetime, hashlib, importlib.util, json, os, pathlib, subprocess, time, uuid
H=pathlib.Path(__file__).resolve().parent
SOURCE=pathlib.Path('/tmp/solpi-polyglot-grader-source')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2)+'\n');os.replace(t,p)
def control(task,private,images):
 row={'task':task,'controls':[],'model_calls':0};out=private/task.split('/')[0]/task.split('/')[-1]
 try:
  spec=importlib.util.spec_from_file_location('g3_polyglot',H/'adapter/polyglot.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
  a.prepare(SOURCE,task,out);row.update(private_preparation=str(out),manifest_sha256=sha(out/'manifest.json'),image_id=images[task.split('/')[0]])
  for mode in ('reference','workspace'):
   name='solpi-g3-control-'+uuid.uuid4().hex[:12];log=out/(mode+'.private.log');image=row['image_id']
   cmd=['docker','run','--rm','--name',name,'--network','none','--cpus','1','--memory','2g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,exec,size=1g','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','--entrypoint','python3','-v',str(out/mode)+':/workspace:ro','-v',str(out/'grader')+':/grader:ro']
   if task.startswith('javascript/'):cmd+=['-v','/tmp/solpi-g1-js-deps:/npm-install:ro']
   cmd += [image,'/grader/grade.py']+(['--reference-control'] if mode=='reference' else [])
   c=dict(mode=mode,container_name=name,expected_exit=0 if mode=='reference' else 1);start=time.monotonic()
   try:
    with log.open('xb') as f:os.chmod(log,0o600);c['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=300).returncode
   except subprocess.TimeoutExpired:c.update(timeout=True,exit_code=None)
   finally:
    subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
    gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15);c.update(seconds=time.monotonic()-start,private_log_sha256=sha(log),owned_container_absent=gone.returncode!=0 and 'No such' in gone.stderr)
   row['controls'].append(c)
   if not c['owned_container_absent']:raise RuntimeError('Owned cleanup uncertain')
  row['valid_pair']=all(c['exit_code']==c['expected_exit'] and c['owned_container_absent'] for c in row['controls'])
 except Exception as e:row.update(valid_pair=False,error={'type':type(e).__name__,'message':str(e)})
 return row

def main():
 plan=json.loads((H/'controls-plan.json').read_text());assert len(plan['tasks'])==211
 assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()==plan['source_revision']
 for p,d in plan['implementation_sha256'].items():assert sha(H/p)==d
 if (H/'controls-launch.json').exists():raise RuntimeError('Existing controls launch; reconcile before rerun')
 private=pathlib.Path('/tmp/solpi-g3-controls-'+uuid.uuid4().hex[:12]);private.mkdir(mode=0o700)
 save(H/'controls-launch.json',dict(pid=os.getpid(),private_root=str(private),plan_sha256=sha(H/'controls-plan.json'),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),model_calls=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 rows=[];start=time.monotonic()
 with F.ThreadPoolExecutor(max_workers=4) as pool:
  jobs={pool.submit(control,t,private,plan['images']):t for t in plan['tasks']}
  for future in F.as_completed(jobs):
   rows.append(future.result());save(H/'controls-progress.json',dict(rows=sorted(rows,key=lambda r:r['task']),model_calls=0));print(len(rows),jobs[future],rows[-1]['valid_pair'],flush=True)
 save(H/'controls-result.json',dict(rows=sorted(rows,key=lambda r:r['task']),completed_tasks=len(rows),valid_pairs=sum(r['valid_pair'] for r in rows),model_calls=0,seconds=time.monotonic()-start,private_root=str(private)))
if __name__=='__main__':main()
