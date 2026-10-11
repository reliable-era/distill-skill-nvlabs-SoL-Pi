"""Recheck all nine original Terminal gold/no-op pairs, zero provider calls.
Adapted from immutable G1 run_terminal_controls.py; new roots/results only.
Four control workers, original task resources/timeouts, no GPUs/host mounts.
"""
import concurrent.futures,datetime,hashlib,json,os,pathlib,subprocess,time,uuid
H=pathlib.Path(__file__).resolve().parent
SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def execute(name,command,log,seconds):
 with log.open('xb') as out:
  os.chmod(log,0o600)
  try:return dict(exit_code=subprocess.run(['docker','exec',name,*command],stdout=out,stderr=subprocess.STDOUT,timeout=seconds).returncode,log_sha256=sha(log))
  except subprocess.TimeoutExpired:return dict(exit_code=None,timeout=True,log_sha256=sha(log))
def control(task,private):
 source=SOURCE/task['task'];row=dict(task=task['task'],image_id=task['image_id'],controls=[],model_calls=0);start=time.monotonic()
 assert all(sha(source/p)==s for p,s in task['source_hashes'].items())
 for mode in ('nop','gold'):
  directory=private/task['task']/mode;logs=directory/'logs';(logs/'verifier').mkdir(parents=True);logs.chmod(0o777);(logs/'verifier').chmod(0o777);name='solpi-g4-B-control-'+uuid.uuid4().hex[:12];c=dict(mode=mode,container_name=name,expected_reward='1' if mode=='gold' else '0',private_root=str(directory));row['controls'].append(c);created=False
  try:
   e=task['environment'];cmd=['docker','create','--pull=never','--name',name,'--cpus',str(e['cpus']),'--memory',str(e['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(source/'tests')+':/tests:ro','-v',str(source/'solution')+':/solution:ro','-v',str(logs)+':/logs','--entrypoint','/bin/sh',task['image_id'],'-c','sleep infinity'];subprocess.run(cmd,capture_output=True,check=True,timeout=30);created=True;subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=30)
   ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=30))[0];assert ins['Image']==task['image_id'] and not ins['HostConfig'].get('DeviceRequests') and not ins['HostConfig']['Privileged'];save(directory/'container-inspect.json',ins);c['inspect_sha256']=sha(directory/'container-inspect.json')
   if mode=='gold':
    c['oracle']=execute(name,['bash','/solution/solve.sh'],directory/'oracle.private.log',min(3600,task['agent'].get('timeout_sec',3600)))
    if c['oracle'].get('timeout'):raise RuntimeError('Original gold deadline; remove owned container before verifier')
   c['verifier']=execute(name,['bash','/tests/test.sh'],directory/'verifier.private.log',task['verifier']['timeout_sec']);reward=logs/'verifier/reward.txt';c['reward']=reward.read_text().strip() if reward.exists() else None
   ctrf=logs/'verifier/ctrf.json'
   if ctrf.exists():c['test_events']=len(json.loads(ctrf.read_text()).get('results',{}).get('tests',[]));c['ctrf_sha256']=sha(ctrf)
   c['valid_expected_reward']=c['reward']==c['expected_reward'] and not c['verifier'].get('timeout') and (mode=='nop' or c['oracle']['exit_code']==0)
  except Exception as error:c.update(error=dict(type=type(error).__name__,message=str(error)[:400]),valid_expected_reward=False)
  finally:
   if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
   gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15);c['owned_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr
  if not c['owned_container_absent']:raise RuntimeError('Owned control cleanup uncertain')
 row.update(valid_pair=len(row['controls'])==2 and all(c['valid_expected_reward'] for c in row['controls']),seconds=time.monotonic()-start);assert all(sha(source/p)==s for p,s in task['source_hashes'].items());save(private/task['task']/'result.json',row);return row
def main():
 plan=json.loads((H/'B-controls-plan.json').read_text());images=json.loads((H/'B-images.json').read_text());assert sha(H/'B-images.json')==plan['images_manifest_sha256'] and sha(__file__)==plan['runner_sha256'];assert len(images['rows'])==9 and plan['model_calls']==0 and plan['concurrent_controls']==4
 if (H/'B-controls-launch.json').exists():raise RuntimeError('Existing launch: reconcile it, never restart on observation timeout')
 private=pathlib.Path('/tmp/solpi-g4-B-controls-'+uuid.uuid4().hex[:12]);private.mkdir(mode=0o700);save(H/'B-controls-launch.json',dict(pid=os.getpid(),root=str(private),plan_sha256=sha(H/'B-controls-plan.json'),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),model_calls=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));rows=[];start=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(control,r,private):r['task'] for r in images['rows']}
  for f in concurrent.futures.as_completed(futures):rows.append(f.result());save(H/'B-controls-progress.json',dict(rows=rows,model_calls=0));print(len(rows),futures[f],rows[-1]['valid_pair'],flush=True)
 save(H/'B-controls-result.json',dict(rows=rows,model_calls=0,all_nine_completed=len(rows)==9,valid_pairs=sum(r['valid_pair'] for r in rows),private_root=str(private),seconds=time.monotonic()-start))
if __name__=='__main__':main()
