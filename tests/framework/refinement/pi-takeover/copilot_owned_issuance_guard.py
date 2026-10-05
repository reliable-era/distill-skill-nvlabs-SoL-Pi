"""Prototype owned-issuer scope: stop verified callback before EOF escapes.
Caller must bind callback to exact currently-owned process/epoch, never loose PID.
No inference/I/O/process launching. Drain/receipt ownership remains caller's duty.
"""
import threading
class IssuanceGuard:
 def __init__(self,cap,stop_owned,record):
  if type(cap) is not int or cap<=0:raise ValueError('positive request cap')
  self.cap=cap;self.stop_owned=stop_owned;self.record=record;self.lock=threading.RLock();self.closed=False;self.accepted=0;self.headers=0;self.denied=0;self.abort_result=None
 def admit(self):
  with self.lock:
   self.headers+=1
   if self.closed or self.accepted>=self.cap:self.denied+=1;return False
   self.accepted+=1;return True
 def abort(self,reason):
  with self.lock:
   self.closed=True
   if self.abort_result is not None:return self.abort_result
   row={'reason':reason,'admission_closed':True,'owned_stop_verified':False,'usage_complete':False}
   # Cache negative result BEFORE callback, including callback exceptions.
   self.abort_result=row
   try:
    row['owned_stop_verified']=self.stop_owned() is True
    if not row['owned_stop_verified']:row['stop_error_type']='UnverifiedOwnedStop'
   except Exception as e:row['stop_error_type']=type(e).__name__
   self.record(dict(row))
   return row

def relay_response(response,write,guard,max_bytes=2097152):
 """Synchronous partial-HTTP detector: issuer stop precedes caller EOF teardown.
No claim of SSE usage completeness: known HTTP length is required here.
"""
 if type(max_bytes) is not int or max_bytes<=0:raise ValueError('byte cap')
 size=0
 try:
  if type(response.length) is not int or response.length<0:raise ValueError('response length unavailable')
  while True:
   chunk=response.read1(8192)
   if not chunk:
    if response.length!=0:raise EOFError('upstream truncated before promised length')
    return size
   size+=len(chunk)
   if size>max_bytes:raise ValueError('response byte cap')
   write(chunk)
 except Exception as e:
  row=guard.abort(type(e).__name__)
  if not row['owned_stop_verified']:raise RuntimeError('issuer stop unverified; unsafe EOF boundary') from e
  raise
