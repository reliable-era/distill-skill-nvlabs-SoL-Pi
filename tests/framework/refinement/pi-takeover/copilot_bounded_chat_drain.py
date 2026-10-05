"""Undeployed bounded chat drain. No actor/HTTP/provider launch or resends.
read(remaining_seconds) MUST enforce its socket timeout; deadline never extended.
Provenance stability is not independent source authentication.
"""
import copy,hashlib,math,os,pathlib,time
from copilot_chat_stream_receipt import ChatReceipt
from prospective_controller_cell import persist

def drain_chat(read,emit,model,deadline,guard,current_scope,root,now=time.monotonic,max_bytes=2097152):
 if type(deadline) not in [int,float] or not math.isfinite(deadline):raise ValueError('finite fixed deadline')
 root=pathlib.Path(root)
 if not root.is_dir() or root.is_symlink():raise ValueError('private existing directory required')
 if any((root/n).exists() or (root/n).is_symlink() for n in ['provider-stream.sse','drain-row.json']):raise FileExistsError('immutable receipt already exists; no reread')
 original=copy.deepcopy(current_scope())
 if not isinstance(original,dict) or original.get('model')!=model or not all(isinstance(original.get(k),str) and original[k] for k in ['request_id','source_identity','epoch']):raise ValueError('explicit stable request/source/epoch required')
 errors=[];eof=False;owned_stop=None;read_calls=0;transport_bytes=0;transport_hash=hashlib.sha256()
 def stop(reason):
  nonlocal owned_stop
  owned_stop=guard.abort(reason)
  if not owned_stop['owned_stop_verified']:raise RuntimeError('owned stop unverified')
 def guarded_emit(chunk):
  try:emit(chunk)
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError,TimeoutError):
   stop('consumer_detached_before_passive_tail');raise
 c=ChatReceipt(guarded_emit,model,max_bytes=max_bytes)
 try:
  while True:
   if current_scope()!=original:raise RuntimeError('request_source_epoch_changed')
   remaining=deadline-now()
   if remaining<=0:raise TimeoutError('fixed_drain_deadline_exhausted')
   read_calls+=1;chunk=read(remaining)
   if not isinstance(chunk,bytes):raise TypeError('read must return bytes')
   transport_bytes+=len(chunk);transport_hash.update(chunk)
   changed=current_scope()!=original;late=now()>=deadline
   if changed or late:
    c.bridge.detached=True
    if chunk:c.feed(chunk)
    if changed:raise RuntimeError('request_source_epoch_changed')
    raise TimeoutError('read_completed_after_fixed_deadline')
   if not chunk:eof=True;break
   c.feed(chunk)
 except Exception as e:
  errors.append({'type':type(e).__name__,'message':str(e)[:120]})
  try:stop(type(e).__name__)
  except Exception as failed:errors.append({'type':type(failed).__name__,'message':'stop_unverified_usage_unavailable'})
 view=c.finish(eof)
 if not view['receipt_complete']:
  try:stop('incomplete_provider_receipt')
  except Exception as failed:errors.append({'type':type(failed).__name__,'message':'stop_unverified_usage_unavailable'})
 if errors:
  view['receipt_complete']=False;view['eligible_usage']=None
 raw=view.pop('raw_bytes');path=root/'provider-stream.sse'
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw)
 row={'scope':original,'raw_receipt':{'file':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'receipt':view,'drain_errors':errors,'owned_stop':owned_stop,'read_calls':read_calls,'transport_bytes_read':transport_bytes,'sha256_all_transport_bytes_read':transport_hash.hexdigest(),'fixed_deadline':deadline,'deadline_unchanged':True,'no_resend_or_new_issuance':True,'source_identity_independently_checked':False,'real_scored_eligible':False}
 persist(root/'drain-row.json',row)
 return row
