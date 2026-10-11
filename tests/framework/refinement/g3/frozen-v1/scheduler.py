"""G3 rolling18-slot committed-window queue. No fallback or model-cell restart.
Durable attempt roots permit recovery without rerunning completed inference.
"""
import argparse,concurrent.futures as F,datetime,json,pathlib,subprocess,threading,time,uuid
from run_cell import H,attempt,tree,sha
from transport import check_model,metadata,waiting_zero,save

def load_plan():
 plan=json.loads((H/'plan.json').read_text())
 for name,digest in plan['implementation_sha256'].items():
  if sha(H/name)!=digest:raise RuntimeError('Frozen implementation changed: '+name)
 for key,s in plan['skills'].items():
  if tree(pathlib.Path(s['path']))!=s['tree']:raise RuntimeError('Frozen skill changed: '+key)
 for path,digest in plan['protected_files'].items():
  if sha(path)!=digest:raise RuntimeError('Protected source changed: '+path)
 return plan

def prior_attempts():
 rows=[]
 for file in sorted(H.glob('waves/*/progress.json')):
  launch=json.loads(file.with_name('launch.json').read_text());pid=launch['pid']
  if not file.with_name('result.json').exists() and subprocess.run(['ps','-p',str(pid),'-o','pid='],capture_output=True,text=True).stdout.strip():raise RuntimeError('Existing live window; never duplicate')
  rows.extend(json.loads(file.read_text())['attempts'])
 keys=[(r['cell_id'],r['attempt']) for r in rows]
 if len(keys)!=len(set(keys)):raise RuntimeError('Duplicate attempt records')
 # Any launched but unprojected private result is reconciled, not retried.
 for launch_file in H.glob('waves/*/launch.json'):
  root=pathlib.Path(json.loads(launch_file.read_text())['root'])
  for result in root.glob('*/attempt-result.json'):
   r=json.loads(result.read_text());key=(r['cell_id'],r['attempt'])
   if key not in keys:rows.append(r);keys.append(key)
  for directory in root.iterdir():
   if directory.is_dir() and not (directory/'attempt-result.json').exists():raise RuntimeError('Unclassified started/prepared attempt requires local artifact reconciliation: '+str(directory))
 return rows

def next_attempt(cell,rows):
 rr=[r for r in rows if r['cell_id']==cell['cell_id']]
 if not rr:return 1
 rr=sorted(rr,key=lambda r:r['attempt'])
 if any(r['cleanup_errors'] for r in rr):raise RuntimeError('Owned cleanup uncertain')
 if len(rr)==1 and rr[0]['infra_retry_eligible']:return 2
 return None

class Queue:
 def __init__(self,plan,cells,prior,out,root,latest):
  self.plan=plan;self.cells=cells;self.prior=prior;self.out=out;self.root=root;self.latest=latest;self.rows=[];self.events=[];self.lock=threading.RLock();self.condition=threading.Condition(self.lock);self.sequence=0;self.settled=set();self.stop=None;self.active=0;self.max_active=0
 def persist(self):
  with self.lock:save(self.out/'progress.json',dict(attempts=self.rows,events=self.events,active_slots=self.active,maximum_active_slots=self.max_active,stop=self.stop,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 def settle(self,seq):
  with self.condition:
   self.settled.add(seq)
   while self.sequence in self.settled:self.sequence+=1
   self.condition.notify_all()
 def admit(self,seq,initial,ident,_ignored):
  start=time.monotonic()
  with self.condition:
   if initial:
    while self.sequence!=seq and not self.stop:self.condition.wait(1)
   while True:
    if self.stop:raise RuntimeError('Queue stopped: '+self.stop)
    if time.time()>=self.latest:raise RuntimeError('Committed latest-start expired')
    try:load=metadata('/get_load')
    except Exception as e:
     self.stop='9012 metadata outage: '+str(e);self.persist();self.condition.notify_all();raise
    if waiting_zero(load):
     self.events.append(dict(kind='admitted',attempt_id=ident,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),load=load,wait_seconds=time.monotonic()-start,slots=self.active));self.persist()
     if initial:self.settle(seq)
     return load
    if time.monotonic()-start>=600:raise RuntimeError('Bounded600s waiting-zero admission expired')
    self.condition.wait(1)
 def run(self,seq,cell,number):
  with self.lock:self.active+=1;self.max_active=max(self.max_active,self.active);assert self.active<=18;self.persist()
  try:
   for num in range(number,3):
    # Before preparing anything, honor closed allowance / outage. Such cells
    # remain pending, not fabricated zero-model failed experimental attempts.
    if self.stop or time.time()>=self.latest:break
    d=self.root/(cell['cell_id']+'-a'+str(num))
    r=attempt(cell,num,d,self.plan,None,lambda ident,ignored:self.admit(seq,num==number,ident,ignored))
    with self.lock:self.rows.append(r);self.events.append(dict(kind='terminal_attempt',cell_id=cell['cell_id'],attempt=num,infra_retry_eligible=r['infra_retry_eligible'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));self.persist()
    self.settle(seq)
    if r['cleanup_errors']:
     with self.lock:self.stop='Owned cleanup uncertain';self.persist();self.condition.notify_all()
     break
    if not r['infra_retry_eligible'] or num==2:break
    if self.stop or time.time()>=self.latest:break
    # Uniform once-only retry. Same18-slot run remains occupied; original
    # attempt/cost stays in durable rows. No retries for caps/model errors.
   return cell['cell_id']
  finally:
   self.settle(seq)
   with self.lock:self.active-=1;self.persist()

def window(marker):
 commit,stamp=subprocess.check_output(['git','log','-1','--format=%H|%cI','--',str(marker)],cwd=H,text=True).strip().split('|');t=datetime.datetime.fromisoformat(stamp);return dict(commit=commit,start=t.isoformat(),end=(t+datetime.timedelta(hours=4)).isoformat(),latest=(t+datetime.timedelta(hours=2)).isoformat())
def main():
 p=argparse.ArgumentParser();p.add_argument('wave');p.add_argument('--round',type=int,required=True,choices=(1,2,3));p.add_argument('--max-primary',type=int,default=72);args=p.parse_args();assert 1<=args.max_primary<=784;plan=load_plan();prior=prior_attempts()
 if args.round>1:
  expected={c['cell_id'] for c in plan['schedule'] if c['round']<args.round};assert all(next_attempt(c,prior) is None for c in plan['schedule'] if c['cell_id'] in expected)
  gate=json.loads((H/'analysis/round1.json').read_text());assert gate['round1_survived'] and not gate['round1_negative_stop']
 if any(r['round']>args.round for r in prior):raise RuntimeError('Round order violated')
 marker=H/'windows'/(args.wave+'.md');assert marker.exists();w=window(marker);latest=datetime.datetime.fromisoformat(w['latest']).timestamp();assert time.time()<latest
 out=H/'waves'/args.wave;out.mkdir(parents=True,exist_ok=True);assert not (out/'launch.json').exists()
 identity=check_model();root=pathlib.Path('/tmp/solpi-g3-'+args.wave+'-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700)
 cells=[c for c in plan['schedule'] if c['round']==args.round and next_attempt(c,prior) is not None][:args.max_primary]
 save(out/'launch.json',dict(pid=__import__('os').getpid(),root=str(root),window=w,plan_sha256=sha(H/'plan.json'),model_identity=identity,round=args.round,scheduled_cells=[c['cell_id'] for c in cells],utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 q=Queue(plan,cells,prior,out,root,latest);q.persist();error=None
 try:
  with F.ThreadPoolExecutor(max_workers=18) as pool:
   jobs={};index=0
   while index<len(cells) or jobs:
    while index<len(cells) and len(jobs)<18 and time.time()<latest and not q.stop:
     c=cells[index];seq=index;future=pool.submit(q.run,seq,c,next_attempt(c,prior));jobs[future]=c['cell_id'];index+=1
    if not jobs:break
    done,_=F.wait(jobs,timeout=5,return_when=F.FIRST_COMPLETED)
    for f in done:
     f.result();jobs.pop(f)
    if q.stop and not jobs:break
 except Exception as e:error={'type':type(e).__name__,'message':str(e)}
 q.persist();save(out/'result.json',dict(attempts=q.rows,events=q.events,stop=q.stop,error=error,maximum_active_slots=q.max_active,window=w,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));print(json.dumps(dict(wave=args.wave,attempts=len(q.rows),stop=q.stop,error=error)))
if __name__=='__main__':main()
