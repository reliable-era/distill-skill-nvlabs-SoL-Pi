"""Uniform once-only externally proved nginx502 retry; reserved8 B/C slots.
The supervisor owns the other8/A. No original ledger/cell claim overwrite,
no third attempt, no model/cap/timeout reruns, no infrastructure intervention.
"""
import argparse,concurrent.futures,fcntl,json,pathlib,threading,time,datetime
from native import H,authorized,sha
from scheduler_v2 import load_committed
from transport import metadata,save,check_model
ACTIVE=frozenset(('127.0.0.1:9012','127.0.0.1:18001','127.0.0.1:18002'))
REQUIRED=frozenset(('127.0.0.1:18001','127.0.0.1:18002'))
DISABLED=frozenset(('10.193.104.97:18001','10.193.104.97:18002'))
def waiting_zero(record):
 rows=record.get('body')
 if not isinstance(rows,list) or any(not isinstance(r,dict) or r.get('backend') not in ACTIVE|DISABLED for r in rows):return False
 routed=[r for r in rows if isinstance(r,dict) and r.get('backend') in ACTIVE]
 return REQUIRED<={r['backend'] for r in routed} and all(type(r.get('num_waiting_reqs')) is int and r['num_waiting_reqs']==0 and type(r.get('num_reqs')) is int and r['num_reqs']>=0 for r in routed)
def observation():
 try:
  v=metadata('/get_load');rows=v['body'];v['advertised_routed_backend_addresses']=[r.get('backend') for r in rows if r.get('backend') in ACTIVE];v['ignored_nonrouted_backend_addresses']=[r.get('backend') for r in rows if r.get('backend') not in ACTIVE];v['unadvertised_routed_backend_addresses']=sorted(ACTIVE-set(v['advertised_routed_backend_addresses']));return v
 except Exception as e:return dict(error=type(e).__name__,message=str(e),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',type=pathlib.Path,required=True);p.add_argument('--window',type=pathlib.Path,required=True);p.add_argument('--commit',required=True);p.add_argument('--root',type=pathlib.Path,required=True);a=p.parse_args();lock=(H/'BC-reserved-eight-slots.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);plan=load_committed(a.plan,a.commit);w=load_committed(a.window,a.commit);window=dict(w,file=str(a.window.resolve()),commit=a.commit)
 assert w['plan_sha256']==sha(a.plan) and plan['BC_reserved_slots']==8
 for f,h in plan['input_hashes'].items():assert sha(f)==h
 for f,h in plan['source_protection']['protected'].items():assert sha(H.parents[3]/f)==h
 for f,h in plan['source_protection']['unrelated_nginx'].items():assert sha(H.parents[3]/'tests/framework/refinement/pi-takeover/qwen-load-balancer'/f)==h
 order=json.loads((H/'queue-order.json').read_text());lookup={c['cell_id']:c for rows in order['parts'].values() for c in rows};cells=[lookup[i] for i in w['cells']];assert all(c['part'] in ('B','C') for c in cells)
 for cell in cells:authorized(cell,plan,window)
 assert not (H/'BC-retry-launch.json').exists(), 'Existing owned launch: inspect/wait, never restart'
 a.root.mkdir(mode=0o700);save(H/'BC-retry-launch.json',dict(pid=__import__('os').getpid(),root=str(a.root),plan_sha256=sha(a.plan),window_commit=a.commit,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),BC_reserved_slots=8));claims=H/'BC-retry-claims';claims.mkdir(exist_ok=True)
 for c in cells:
  with (claims/(c['cell_id']+'-a2.json')).open('x') as f:json.dump(dict(cell_id=c['cell_id'],attempt=2,root=str(a.root),window_commit=a.commit),f)
 while True:
  try:save(a.root/'models-metadata.json',check_model());break
  except Exception as e:save(a.root/'route-paused.json',dict(error=type(e).__name__,message=str(e),action='Pause metadata; no fallback/probe/repair'));time.sleep(5)
 mutex=threading.RLock();active={};stop=threading.Event();samples=[]
 def sample():
  v=observation();samples.append(v);save(a.root/'admission-observations.json',samples);return v
 def callback(c,n):
  assert n==2
  while True:
   with mutex:
    if stop.is_set():raise RuntimeError('Owned evidence/cleanup uncertainty; admission stopped')
    v=sample();assert c['cell_id'] in active and len(active)<=8
    if waiting_zero(v):return dict(load=v,occupied_slots_after_admission=len(active),BC_reserved_slots=8,supervisor_A_reserved_slots=8,cell_id=c['cell_id'],attempt=2)
   time.sleep(2)
 def run(c):
  from run_swe_cell_v2 import attempt as swe
  from run_terminal_cell import attempt as terminal
  try:
   row=(swe if c['part']=='C' else terminal)(c,2,a.root/(c['cell_id']+'-a2'),plan,window,callback);save(a.root/(c['cell_id']+'-attempts.json'),[row])
   if not row.get('owned_cleanup_verified'):raise RuntimeError('Owned cleanup uncertain')
   return row
  except Exception as e:stop.set();save(a.root/(c['cell_id']+'-execution-error.json'),dict(type=type(e).__name__,message=str(e)));raise
  finally:
   with mutex:active.pop(c['cell_id'],None)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  jobs=[]
  for c in cells:
   while True:
    with mutex:
     if stop.is_set():raise RuntimeError('Admission stopped; never restart')
     if len(active)<8 and waiting_zero(sample()):active[c['cell_id']]=c;jobs.append(pool.submit(run,c));break
    time.sleep(2)
  for f in concurrent.futures.as_completed(jobs):f.result()
 save(a.root/'window-result.json',dict(cells=w['cells'],occupied_slots=len(active),model_route='127.0.0.1:8000',BC_reserved_slots=8,completed=True,third_attempt_authorized=False))
if __name__=='__main__':main()
