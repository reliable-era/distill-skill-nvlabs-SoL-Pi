"""Bounded selected SWE image acquisition, zero provider calls/no task replacement.
Only inspect/pull the fixed30 selected official images, never prune shared cache.
"""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,time,uuid
H=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def main():
 plan=json.loads((H/'C-image-plan.json').read_text());assert sha(__file__)==plan['runner_sha256'] and sha(H/'selection.json')==plan['selection_sha256']
 if (H/'C-image-launch.json').exists():raise RuntimeError('Existing preparation handle; reconcile before any new action')
 root=pathlib.Path('/tmp/solpi-g4-C-image-prep-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);docker_root=pathlib.Path(subprocess.check_output(['docker','info','--format','{{.DockerRootDir}}'],text=True,timeout=20).strip());devices={p.stat().st_dev:p for p in (root,docker_root)};before={d:shutil.disk_usage(p).free for d,p in devices.items()};save(H/'C-image-launch.json',dict(pid=os.getpid(),root=str(root),plan_sha256=sha(H/'C-image-plan.json'),model_calls=0,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));rows=[];start=time.monotonic();stop=None
 for task in plan['tasks']:
  free={d:shutil.disk_usage(p).free for d,p in devices.items()}
  if min(free.values())<plan['minimum_free_bytes'] or sum(max(0,before[d]-free[d]) for d in devices)>plan['maximum_growth_bytes']:stop='Disk guard; no pruning or replacement';break
  tag='swebench/sweb.eval.x86_64.'+task.replace('__','_1776_')+':latest';row=dict(task=task,declared_image=tag);rows.append(row);ins=subprocess.run(['docker','image','inspect',tag],capture_output=True,text=True,timeout=20)
  if ins.returncode:
   log=root/(task+'.pull.private.log')
   try:
    with log.open('xb') as out:os.chmod(log,0o600);p=subprocess.run(['docker','pull',tag],stdout=out,stderr=subprocess.STDOUT,timeout=plan['per_pull_seconds'])
    row['pull_exit']=p.returncode
   except subprocess.TimeoutExpired:row['pull_timeout']=True;stop='Owned pull observation timed out; reconcile cache before any retry'
   row['pull_log_sha256']=sha(log);row['pull_log']=str(log);ins=subprocess.run(['docker','image','inspect',tag],capture_output=True,text=True,timeout=20)
  if ins.returncode==0:
   image=json.loads(ins.stdout)[0];row.update(image_id=image['Id'],repo_digests=image.get('RepoDigests'),size_bytes=image['Size'],status='cached')
  else:row['status']='Selected image unavailable; task retained, controls not executed'
  save(H/'C-image-progress.json',dict(rows=rows,model_calls=0))
  if stop:break
 save(H/'C-images.json',dict(rows=rows,all30_cached=len(rows)==30 and all(r.get('status')=='cached' for r in rows),stop=stop,model_calls=0,seconds=time.monotonic()-start,no_task_replacement=True))
if __name__=='__main__':main()
