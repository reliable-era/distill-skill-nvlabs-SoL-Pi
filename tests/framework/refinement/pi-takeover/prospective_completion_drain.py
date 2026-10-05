"""Undeployedpassivecompletiongate;no actorcontinuation/retry/deadlineextension."""
import math,time
RESERVE=10.0
GRACE=240.0
def drain(session,now=time.monotonic,sleep=time.sleep):
 raw=getattr(session,'raw_session',session);epoch=(raw.active,raw.deadline);posts=raw.posts
 if not isinstance(epoch[0],str) or not isinstance(epoch[1],(int,float)) or not math.isfinite(epoch[1]):raise ValueError('active finite original actor deadline required')
 limit=epoch[1]-RESERVE+GRACE;start=now();lock=getattr(session,'forward_lock',None)
 while True:
  if (raw.active,raw.deadline)!=epoch or raw.posts!=posts:raise RuntimeError('drain epoch/forward count changed')
  with raw.lock:pending=len(raw.connections)
  acquired=lock.acquire(False) if lock is not None else True
  if acquired:
   try:
    with raw.lock:pending=len(raw.connections)
    if pending==0:return {'drained':True,'wait_seconds':max(0,now()-start),'deadline_unchanged':True,'actor_continued':False,'extra_POST':0,'completion_limit':limit}
   finally:
    if lock is not None:lock.release()
  remaining=limit-now()
  if remaining<=0:return {'drained':False,'wait_seconds':max(0,now()-start),'deadline_unchanged':True,'actor_continued':False,'extra_POST':0,'completion_limit':limit,'unresolved_connections':pending,'usage_remains_unavailable':True}
  sleep(min(.01,remaining))
