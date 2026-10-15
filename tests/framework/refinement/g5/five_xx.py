"""User policy2026-10-16:terminal5xx up to5 attempts,backoff,circuit log.
No load/metadata probes,server actions,model-error retries or cost imputation.
"""
import collections,datetime,fcntl,json,pathlib,random,threading,time,uuid
from retry_policy import native_http5xx
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def append(path,event):
 path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a') as f:fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps(event,separators=(',',':'))+'\n');f.flush();fcntl.flock(f,fcntl.LOCK_UN)
def record(directory,global_log,cell,attempt,status,request_index,source,event_id=None,event_time=None):
 event=dict(event_id=event_id or uuid.uuid4().hex,observed_utc=utc(),event_time=event_time,status=status,cell=cell,attempt=attempt,request_index=request_index,source=source);append(pathlib.Path(directory)/'http5xx.jsonl',event)
 if global_log:append(global_log,event)
 return event

def decision(row,total_attempts,raw):
 evidence=native_http5xx(raw);ended=evidence['connection_infra_failure'];ordinary_cap=row.get('timeout') or row.get('grader_timeout');retry=ended and not ordinary_cap and total_attempts<5
 other_connection=bool(row.get('connection_infra_failure')) and not ended
 completed=any(b'"turn.completed"' in line for line in raw.splitlines())
 if other_connection and not completed and not ordinary_cap and total_attempts<2:retry=True
 return dict(connection_infra_failure=ended or other_connection,ended_on_5xx=ended,retry=retry,infra_exhausted=ended and total_attempts>=5,reason='final native HTTP5xx' if ended else ('once-only other connection failure' if retry else 'ordinary outcome;no5xx retry'),native_evidence=evidence)
def backoff(finished_attempts,rng=random):
 base=min(900,60*2**max(0,finished_attempts-1));return min(900,base+rng.uniform(0,base*.2))
class Circuit:
 def __init__(self,log,clock=time.time):self.log=pathlib.Path(log);self.clock=clock;self.lock=threading.RLock();self.recent=collections.deque(maxlen=16);self.until=0;self.finished_count=0
 def finish(self,ended5xx,cell,attempt):
  with self.lock:
   self.recent.append(bool(ended5xx));self.finished_count+=1
   if len(self.recent)==16 and sum(self.recent)>=8:
    self.until=max(self.until,self.clock()+600);append(self.log,dict(kind='circuit_pause',utc=utc(),pause_until_epoch=self.until,pause_seconds=600,last16_5xx=sum(self.recent),finished_count=self.finished_count,cell=cell,attempt=attempt))
 def wait(self,stop=None):
  while True:
   with self.lock:remaining=self.until-self.clock()
   if remaining<=0:return
   if stop and stop.is_set():raise RuntimeError('Owned safety stop')
   time.sleep(min(1,remaining))
