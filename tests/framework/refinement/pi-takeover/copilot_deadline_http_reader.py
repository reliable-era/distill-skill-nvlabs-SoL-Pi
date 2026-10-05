"""Deadline-bound read adapter for an already-owned HTTP response/socket.
Does not connect, authenticate, select routes, retry, extend deadlines or launch.
"""
import math,time
class DeadlineHTTPReader:
 def __init__(self,response,sock,deadline,now=time.monotonic):
  if type(deadline) not in [int,float] or not math.isfinite(deadline):raise ValueError('finite deadline required')
  self.response=response;self.sock=sock;self.deadline=deadline;self.now=now
 def __call__(self,remaining):
  if type(remaining) not in [int,float] or not math.isfinite(remaining) or remaining<=0:raise ValueError('positive remaining seconds')
  timeout=min(remaining,self.deadline-self.now())
  if timeout<=0:raise TimeoutError('original HTTP deadline expired')
  if self.response.isclosed():return b''
  self.sock.settimeout(timeout)
  chunk=self.response.read1(8192)
  # Return late observed bytes to drain accounting rather than silently drop.
  # drain_chat rechecks original deadline before attribution/delivery.
  return chunk
