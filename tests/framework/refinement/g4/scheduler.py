"""G4 shared16 rolling B/C slots, frozen order/windows, no performance stop.
All attempts durable, uniform once-only proven never-model/refused/reset retry.
8000 outage pauses admission with evidence, never repairs/falls back.
"""
import argparse,concurrent.futures,datetime,fcntl,hashlib,json,os,pathlib,subprocess,threading,time
from transport import metadata,waiting_zero,check_model,save
from native import H,authorized

def retry_eligible(row):
 if not row.get('owned_cleanup_verified') or row.get('timeout') or row.get('grader_timeout') or row.get('requests',60)>=60:return False
 root=pathlib.Path(row['root']);ledger=root/'transport/ledger.json'
 if not ledger.exists():return row.get('native_started') is False and row.get('requests')==0
 data=json.loads(ledger.read_text());records=data['records']
 if data['provider_POST']!=row['requests'] or len(records)!=row['requests']:return False
 if any(r.get('provider_status') not in (None,200) or r.get('terminal_completed',0) and not r.get('connection_infra_failure') for r in records):return False
 for r in records:
  response=root/'transport'/('response-'+str(r['request'])+'.sse')
  if response.exists():
   for line in response.read_bytes().splitlines():
    if not line.startswith(b'data: ') or line==b'data: [DONE]':continue
    try:event=json.loads(line[6:])
    except ValueError:continue
    if event.get('type') in ('response.failed','response.incomplete'):return False
 return row['requests']==0 or any(r.get('proven_zero_model_refusal') or r.get('connection_infra_failure') for r in records)

def load_committed(path,commit):
 path=pathlib.Path(path).resolve();repo=H.parents[3];path.relative_to(H);relative=path.relative_to(repo);subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=repo,check=True,capture_output=True,timeout=10);raw=subprocess.check_output(['git','show',commit+':'+str(relative)],cwd=repo,timeout=10)
 if raw!=path.read_bytes():raise RuntimeError('Committed input changed: '+str(path))
 return json.loads(raw)

class Queue:
 def __init__(self,plan,window,root):
  self.plan=plan;self.window=window;self.root=pathlib.Path(root);self.lock=threading.RLock();self.active={};self.stop=False;self.samples=[]
 def observation(self):
  try:return metadata('/get_load')
  except Exception as e:return dict(error=type(e).__name__,message=str(e),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 def sample(self,value):
  with self.lock:self.samples.append(value);save(self.root/'admission-observations.json',self.samples)
 def start_callback(self,cell,number):
  while True:
   with self.lock:
    if self.stop:raise RuntimeError('Admission stopped for owned cleanup uncertainty')
    if cell['cell_id'] not in self.active or len(self.active)>16:raise RuntimeError('Occupied slot proof missing')
    load=self.observation();self.sample(load)
    if waiting_zero(load):return dict(load=load,occupied_slots_after_admission=len(self.active),cell_id=cell['cell_id'],attempt=number)
   time.sleep(2)
 def run_cell(self,cell):
  from run_swe_cell import attempt as swe
  from run_terminal_cell import attempt as terminal
  runner=swe if cell['part']=='C' else terminal;rows=[]
  try:
   for number in (1,2):
    row=runner(cell,number,self.root/(cell['cell_id']+'-a'+str(number)),self.plan,self.window,self.start_callback);rows.append(row);save(self.root/(cell['cell_id']+'-attempts.json'),rows)
    if not row.get('owned_cleanup_verified'):
     with self.lock:self.stop=True
     raise RuntimeError('Owned cleanup uncertain; no new admission')
    if number==2 or not retry_eligible(row):break
   return rows
  except Exception as e:
   with self.lock:self.stop=True
   save(self.root/(cell['cell_id']+'-execution-error.json'),dict(type=type(e).__name__,message=str(e)[:500],durable_attempts=len(rows)));raise
  finally:
   with self.lock:self.active.pop(cell['cell_id'],None)
 def run(self,cells):
  futures=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
   for cell in cells:
    while True:
     with self.lock:
      if self.stop:raise RuntimeError('Execution stopped for owned evidence/cleanup uncertainty')
      load=self.observation();self.sample(load)
      if len(self.active)<16 and waiting_zero(load):
       self.active[cell['cell_id']]=dict(part=cell['part'],task=cell['task']);futures.append(pool.submit(self.run_cell,cell));break
     time.sleep(2)
   for future in concurrent.futures.as_completed(futures):future.result()
  save(self.root/'window-result.json',dict(cells=[c['cell_id'] for c in cells],occupied_slots=len(self.active),model_route='127.0.0.1:8000',performance_gate=False,completed=True))

def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',type=pathlib.Path,required=True);p.add_argument('--plan-commit',required=True);p.add_argument('--window',type=pathlib.Path,required=True);p.add_argument('--window-commit',required=True);p.add_argument('--root',type=pathlib.Path,required=True);a=p.parse_args();slot_lock=(H/'shared-run-slots.lock').open('a')
 try:fcntl.flock(slot_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise RuntimeError('Another owned G4 scheduler holds shared16 slots; reconcile/wait, never overlap')
 plan=load_committed(a.plan,a.plan_commit);w=load_committed(a.window,a.window_commit);window=dict(w,file=str(a.window.resolve()),commit=a.window_commit)
 if plan.get('full_preregistration') is not True or w.get('plan_sha256')!=hashlib.sha256(a.plan.read_bytes()).hexdigest():raise RuntimeError('All-parts preregistration binding required')
 order=json.loads((H/'queue-order.json').read_text());allcells={c['cell_id']:c for rows in order['parts'].values() for c in rows};cells=[allcells[i] for i in w['cells']]
 if any(c['part'] not in ('B','C') or c['task'] not in plan['eligible_tasks'][c['part']] for c in cells):raise RuntimeError('Ineligible/unimplemented part cell')
 expected=[i for i in order['prospective_global_order'] if i in w['cells']]
 if expected!=w['cells'] or len(set(w['cells']))!=len(w['cells']):raise RuntimeError('Frozen window order/uniqueness mismatch')
 for cell in cells:authorized(cell,plan,window)
 a.root.mkdir(mode=0o700)
 claim=H/('window-'+w['window_id']+'-launch.json')
 with claim.open('x') as out:json.dump(dict(pid=os.getpid(),root=str(a.root),plan_sha256=hashlib.sha256(a.plan.read_bytes()).hexdigest(),window_commit=a.window_commit,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),out,indent=2)
 claims=H/'cell-claims';claims.mkdir(exist_ok=True)
 for cell in cells:
  with (claims/(cell['cell_id']+'.json')).open('x') as out:json.dump(dict(window_id=w['window_id'],root=str(a.root),cell_id=cell['cell_id']),out)
 while True:
  try:models=check_model();save(a.root/'models-metadata.json',models);break
  except Exception as e:
   save(a.root/'route-paused.json',dict(error=type(e).__name__,message=str(e),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),model_calls=0,action='Pause; no fallback/repair'));time.sleep(5)
 Queue(plan,window,a.root).run(cells)
if __name__=='__main__':main()
