"""Prepare fixed30 original C snapshots/prompts; gold never enters actors.
Scoped reuse of prepare_swe.py semantics, with bounded owned resources/cleanup.
Remove upstream Git objects/history; export source bytes and single snapshot.
No model/agent calls; no replacement if preparation fails.
"""
import datetime,hashlib,json,os,pathlib,re,shutil,subprocess,uuid
H=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def run(*args,**kw):return subprocess.run(list(args),check=True,capture_output=True,timeout=120,**kw)
def main():
 if (H/'C-source-launch.json').exists():raise RuntimeError('Existing preparation handle; reconcile, no restart')
 plan=json.loads((H/'C-controls-plan.json').read_text());assert sha(plan['private_dataset'])==plan['private_dataset_sha256'];rows=json.loads(pathlib.Path(plan['private_dataset']).read_text());assert [r['instance_id'] for r in rows]==plan['tasks'];root=pathlib.Path('/tmp/solpi-g4-C-prepared-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);save(H/'C-source-launch.json',dict(pid=os.getpid(),root=str(root),model_calls=0,runner_sha256=sha(__file__),commit=run('git','rev-parse','HEAD',cwd=H).stdout.decode().strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));records=[]
 for row in rows:
  iid=row['instance_id'];base=row['base_commit'];assert re.fullmatch('[0-9a-f]{40}',base);directory=root/iid;directory.mkdir();name='solpi-g4-C-prepare-'+uuid.uuid4().hex[:12];image=plan['images'][iid];record=dict(task=iid,base_commit=base,image_id=image,private_root=str(directory),model_calls=0,gold_in_actor=False,upstream_history_in_actor=False);created=False
  try:
   run('docker','create','--pull=never','--name',name,'--network','none','--cpus','1','--memory','8g','--pids-limit','512','--security-opt','no-new-privileges','--entrypoint','git',image,'-C','/testbed','checkout','--detach',base);created=True;run('docker','start','-a',name);ins=json.loads(run('docker','inspect',name).stdout)[0];assert ins['State']['ExitCode']==0 and ins['Image']==image;save(directory/'prepare-inspect.json',ins);run('docker','cp',name+':/testbed/.',str(directory/'workspace'));work=directory/'workspace';head=run('git','-C',str(work),'rev-parse','HEAD').stdout.decode().strip();assert head==base
   # Preserve preinstalled compilation assets, but no future refs/history.
   shutil.rmtree(work/'.git');run('git','-C',str(work),'init','--quiet');run('git','-C',str(work),'add','.');run('git','-C',str(work),'-c','user.name=Evaluation','-c','user.email=evaluation@example.invalid','commit','--quiet','-m','Original task snapshot');record['snapshot_commit']=run('git','-C',str(work),'rev-parse','HEAD').stdout.decode().strip()
   prompt='<issue>\n'+row['problem_statement']+'\n</issue>\n\nThe repository at /testbed is the original issue revision. Resolve the issue by editing non-test source files. Do not modify existing tests. Python uses the preinstalled testbed environment. When done, stop.\n';(directory/'prompt.txt').write_text(prompt);record['prompt_sha256']=sha(directory/'prompt.txt');record['source_tree']={str(p.relative_to(work)):({'symlink':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(work.rglob('*')) if (p.is_file() or p.is_symlink()) and '.git' not in p.relative_to(work).parts};record['prepared']=True
  except Exception as e:record['prepared']=False;record['error']=dict(type=type(e).__name__,message=str(e)[:400])
  finally:
   if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
   gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);record['owned_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr
  if not record['owned_container_absent']:raise RuntimeError('Owned preparation cleanup uncertain')
  save(directory/'manifest.json',record);records.append(record);save(H/'C-source-progress.json',dict(rows=records,model_calls=0));print(iid,record['prepared'],flush=True)
 save(H/'C-prepared-sources.json',dict(rows=records,model_calls=0,all30_prepared=len(records)==30 and all(r['prepared'] for r in records),private_root=str(root),dataset_sha256=plan['private_dataset_sha256']))
if __name__=='__main__':main()
