"""Fixed30 official SWE gold/no-op checks. No agent/provider requests.
Four isolated pair workers; unmodified official harness, full original F2P/P2P
coverage; owned immutable images, original base checkout, resources/cleanup.
"""
import argparse,concurrent.futures,datetime,hashlib,json,os,pathlib,re,subprocess,sys,threading,time,uuid
H=pathlib.Path(__file__).resolve().parent
SOURCE='/tmp/solpi-confirmation-clean-official/SWE-bench-SWE-bench-02e7a74'
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 p=pathlib.Path(p);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n');os.replace(tmp,p)
def validate(entry,spec,statuses,found,kind,resolve,classification):
 if not found or classification is not None or entry.get('infra_failure') is not False or entry.get('infra_failure_reason'):raise RuntimeError('Official control infrastructure/collection failure')
 coverage={}
 for category,expected in [('FAIL_TO_PASS',spec.FAIL_TO_PASS),('PASS_TO_PASS',spec.PASS_TO_PASS)]:
  detail=entry['tests_status'][category];reported=detail['success']+detail['failure']
  if len(reported)!=len(expected) or set(reported)!=set(expected):raise RuntimeError('Original expected-test coverage mismatch')
  keys=[resolve(x,statuses) for x in expected]
  if any(k is None for k in keys):raise RuntimeError('Missing/ambiguous original test statuses')
  values=[statuses[k] for k in keys]
  if any(v not in ('PASSED','FAILED') for v in values):raise RuntimeError('Incomplete original tests')
  coverage[category]=dict(expected=len(expected),passed=values.count('PASSED'),failed=values.count('FAILED'))
 if not spec.FAIL_TO_PASS or coverage['PASS_TO_PASS']['failed']:raise RuntimeError('No original F2P or original P2P regression')
 if kind=='gold':
  if entry.get('patch_successfully_applied') is not True or entry.get('resolved') is not True or coverage['FAIL_TO_PASS']['failed']:raise RuntimeError('Original gold did not resolve')
 elif entry.get('resolved') is not False or not coverage['FAIL_TO_PASS']['failed']:raise RuntimeError('No-op did not demonstrate original F2P failure')
 return coverage

def worker(index,private):
 plan=json.loads((H/'C-controls-plan.json').read_text());assert sha(__file__)==plan['runner_sha256']
 for p,d in plan['official_source_hashes'].items():assert sha(p)==d
 assert sha(plan['private_dataset'])==plan['private_dataset_sha256'];tasks=json.loads(pathlib.Path(plan['private_dataset']).read_text());task=tasks[index];iid=task['instance_id'];assert iid==plan['tasks'][index] and re.fullmatch('[0-9a-f]{40}',task['base_commit']);image=plan['images'][iid]
 sys.path.insert(0,SOURCE)
 import docker
 from swebench.harness.utils import make_test_spec
 from swebench.harness.run_evaluation import run_instance,LOG_TEST_OUTPUT,LOG_INSTANCE
 from swebench.harness.grading import get_logs_eval,_resolve_case
 from swebench.harness.infra_failure import classify_logs
 task=dict(task,image=image);spec=make_test_spec(task);real=docker.from_env(timeout=20);row=dict(task=iid,image_id=image,controls=[],model_calls=0)
 for kind in ('nop','gold'):
  directory=private/iid/kind;directory.mkdir(parents=True,mode=0o700);os.chdir(directory);runid='g4-'+uuid.uuid4().hex[:16];owned=[];proofs=[];c=dict(kind=kind,private_root=str(directory),valid=False);row['controls'].append(c);started=time.monotonic()
  class Proxy:
   def __init__(self,container):self.inner=container
   def __getattr__(self,k):return getattr(self.inner,k)
   def start(self):
    self.inner.start();r=self.inner.exec_run(['git','-C','/testbed','checkout','--detach',task['base_commit']]);assert r.exit_code==0
    r=self.inner.exec_run(['git','-C','/testbed','reset','--hard',task['base_commit']]);assert r.exit_code==0
    r=self.inner.exec_run(['git','-C','/testbed','rev-parse','HEAD']);assert r.exit_code==0 and r.output.decode().strip()==task['base_commit'];proofs.append(dict(original_base_commit_verified=task['base_commit']))
  class Images:
   def get(self,name):
    if name!=image:raise RuntimeError('Unfrozen image')
    img=real.images.get(name);assert img.id==image;return img
   def pull(self,*a,**k):raise RuntimeError('Implicit pull prohibited')
   def build(self,*a,**k):raise RuntimeError('Implicit build prohibited')
  class Containers:
   def get(self,name):
    if name not in owned:raise RuntimeError('Unowned container access prohibited')
    return real.containers.get(name)
   def create(self,*a,**kw):
    name=kw.get('name');assert name and name.startswith('sweb.eval.'+iid.lower()+'.'+runid) and not owned;owned.append(name);save(directory/'owned.json',dict(names=owned,run_id=runid));kw.update(network_mode='none',network_disabled=False,nano_cpus=1_000_000_000,mem_limit='8g',pids_limit=512,security_opt=['no-new-privileges']);ctr=real.containers.create(*a,**kw);ctr.reload();host=ctr.attrs['HostConfig'];assert host['NetworkMode']=='none' and host['Memory']==8*1024**3 and host['NanoCpus']==1_000_000_000 and host['PidsLimit']==512 and not host['Privileged'] and not host.get('DeviceRequests');save(directory/'container-inspect.json',ctr.attrs);proofs.append(dict(name=name,image_id=ctr.attrs['Image'],inspect_sha256=sha(directory/'container-inspect.json')));return Proxy(ctr)
  class Client:
   images=Images();containers=Containers();api=real.api
  try:
   pred=dict(instance_id=iid,model_name_or_path='g4-control',model_patch=task['patch'] if kind=='gold' else '');run_instance(spec,pred,Client(),runid,timeout=600,skip_patch=kind=='nop');reports=list(directory.rglob('report.json'));assert len(reports)==1;entry=json.loads(reports[0].read_text())[iid];statuses,found=get_logs_eval(spec,str(reports[0].parent/LOG_TEST_OUTPUT));c['resolved']=entry.get('resolved');c['coverage']=validate(entry,spec,statuses,found,kind,_resolve_case,classify_logs(reports[0].parent/LOG_TEST_OUTPUT,reports[0].parent/LOG_INSTANCE));c['valid']=True
  except Exception as e:c['error']=dict(type=type(e).__name__,message=str(e)[:500])
  finally:
   for name in owned:
    try:real.containers.get(name).remove(force=True)
    except docker.errors.NotFound:pass
    try:real.containers.get(name);raise RuntimeError('Owned control remains')
    except docker.errors.NotFound:proofs.append(dict(name=name,absence_verified=True))
   c['proofs']=proofs;c['seconds']=time.monotonic()-started;c['artifacts']={str(p.relative_to(directory)):sha(p) for p in directory.rglob('*') if p.is_file()};save(private/iid/'result.json',row)
 row['valid_pair']=len(row['controls'])==2 and all(c['valid'] for c in row['controls']);save(private/iid/'result.json',row);real.close()

def launch():
 plan=json.loads((H/'C-controls-plan.json').read_text());assert sha(__file__)==plan['runner_sha256'] and len(plan['tasks'])==30
 if (H/'C-controls-launch.json').exists():raise RuntimeError('Existing launch: reconcile, never observation-timeout restart')
 root=pathlib.Path('/tmp/solpi-g4-C-controls-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);save(H/'C-controls-launch.json',dict(pid=os.getpid(),root=str(root),model_calls=0,plan_sha256=sha(H/'C-controls-plan.json'),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));rows=[];stop=threading.Event()
 def pair(index):
  if stop.is_set():raise RuntimeError('New control admission halted after owned worker failure')
  log=root/(str(index)+'.worker.private.log')
  with log.open('xb') as out:os.chmod(log,0o600);p=subprocess.run([PYTHON,str(H/'C_controls.py'),'--worker',str(index),'--private',str(root)],stdout=out,stderr=subprocess.STDOUT)
  result=root/plan['tasks'][index]/'result.json'
  if p.returncode or not result.exists():
   stop.set();raise RuntimeError('Owned worker failed; reconcile its recorded containers/logs before continuation')
  return json.loads(result.read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(pair,i) for i in range(30)]
  for f in concurrent.futures.as_completed(futures):rows.append(f.result());save(H/'C-controls-progress.json',dict(rows=rows,model_calls=0));print(len(rows),rows[-1]['task'],rows[-1]['valid_pair'],flush=True)
 save(H/'C-controls-result.json',dict(rows=rows,all30_completed=len(rows)==30,valid_pairs=sum(r['valid_pair'] for r in rows),model_calls=0,private_root=str(root)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',type=int);p.add_argument('--private',type=pathlib.Path);a=p.parse_args()
 if a.worker is None:launch()
 else:worker(a.worker,a.private)
