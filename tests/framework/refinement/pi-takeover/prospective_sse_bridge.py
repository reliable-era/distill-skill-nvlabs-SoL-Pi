"""Undeployed prospective SSE metadata bridge;raw bytes remain independently available."""
import json,re
from prospective_reasoning_adapter import derive
class SSEBridge:
 def __init__(self,emit,max_bytes=2097152):
  self.emit=emit;self.limit=max_bytes;self.raw=bytearray();self.pending=bytearray();self.frames=[];self.held=[];self.events=[];self.finished=False;self.detached=False;self.malformed_data=False;self.delivered=bytearray()
 def _emit(self,data):
  self.delivered.extend(data)
  if not self.detached:
   try:self.emit(data)
   except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError,TimeoutError):self.detached=True
 @staticmethod
 def parse(frame):
  lines=[line for line in frame.splitlines() if line.startswith(b'data:')]
  if len(lines)!=1:return None
  payload=lines[0][5:].strip()
  if payload==b'[DONE]':return '[DONE]'
  try:return json.loads(payload)
  except (ValueError,UnicodeDecodeError):return None
 def feed(self,chunk):
  if self.finished:raise ValueError('bridge already finalized')
  if not isinstance(chunk,bytes):raise TypeError('byte chunks required')
  if len(self.raw)+len(chunk)>self.limit:raise ValueError('SSE response byte cap')
  self.raw.extend(chunk);self.pending.extend(chunk)
  while True:
   match=re.search(br'\r?\n\r?\n',self.pending)
   if not match:break
   frame=bytes(self.pending[:match.end()]);del self.pending[:match.end()];event=self.parse(frame);self.frames.append(frame)
   if event is not None:self.events.append(event)
   if any(line.startswith(b'data:') for line in frame.splitlines()) and not(isinstance(event,dict) or event=='[DONE]'):self.malformed_data=True
   if self.held or isinstance(event,dict) and event.get('type')=='response.completed':self.held.append(frame)
   else:self._emit(frame)
 def finish(self,stream_eof,provenance):
  if self.finished:raise ValueError('bridge already finalized')
  self.finished=True
  # Incomplete framing is never repaired and never treated as an EOF receipt.
  valid_framing=not self.pending and not self.malformed_data
  view=derive(self.events,stream_eof is True and valid_framing,provenance)
  if view['correction_applied']:
   replacement=next(e for e in view['derived_events'] if isinstance(e,dict) and e.get('type')=='response.completed')
   changed=False
   for frame in self.held:
    event=self.parse(frame)
    if isinstance(event,dict) and event.get('type')=='response.completed':
     lines=frame.splitlines(keepends=True);encoded=json.dumps(replacement,separators=(',',':'),ensure_ascii=False).encode()
     for i,line in enumerate(lines):
      if line.startswith(b'data:'):
       ending=b'\r\n' if line.endswith(b'\r\n') else b'\n' if line.endswith(b'\n') else b'';lines[i]=b'data: '+encoded+ending
     self._emit(b''.join(lines));changed=True
    else:self._emit(frame)
   if not changed:raise RuntimeError('correction without held terminal')
  else:
   for frame in self.held:self._emit(frame)
  if self.pending:self._emit(bytes(self.pending))
  view.update(consumer_detached=self.detached,framing_complete=valid_framing,raw_bytes=bytes(self.raw),derived_stream_bytes=bytes(self.delivered),broker_deployed=False)
  return view
