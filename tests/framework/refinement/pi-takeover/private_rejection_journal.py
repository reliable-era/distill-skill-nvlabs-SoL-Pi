"""Private, bounded durable local HTTP rejection records;never provider charges."""
import json,os,pathlib,threading
FIELDS={'reason','declared_body_bytes','body_byte_cap','status','provider_forwarded','provider_POST'}
class RejectionJournal:
 def __init__(self,path,max_records=128):
  self.path=pathlib.Path(path);self.maximum=max_records;self.lock=threading.Lock();self.records=[]
  if type(max_records)!=int or not 1<=max_records<=1024 or self.path.exists() or self.path.is_symlink():raise ValueError('journal must be fresh and bounded')
  if self.path.parent.is_symlink() or not self.path.parent.is_dir():raise ValueError('private journal parent unavailable')
  if self.path.parent.stat().st_mode&0o077:raise ValueError('journal parent must be private')
  self._persist()
 def _persist(self):
  tmp=self.path.with_name(self.path.name+'.pending');data=json.dumps({'protocol':'local-rejections-v1','maximum_records':self.maximum,'records':self.records},indent=2)+'\n';fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  try:
   with os.fdopen(fd,'w') as out:out.write(data);out.flush();os.fsync(out.fileno())
   os.replace(tmp,self.path);d=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY)
   try:os.fsync(d)
   finally:os.close(d)
  finally:
   if tmp.exists():tmp.unlink()
 def __call__(self,record):
  if set(record)!=FIELDS or record['reason'] not in ['body_byte_cap','invalid_content_length'] or record['status']!=413 or record['provider_forwarded'] is not False or record['provider_POST']!=0 or record['body_byte_cap']!=8388608:raise ValueError('unknown rejection shape')
  n=record['declared_body_bytes']
  if n is not None and (type(n)!=int or len(str(n))>32):raise ValueError('invalid or oversized rejection number')
  with self.lock:
   if len(self.records)>=self.maximum:raise ValueError('private rejection journal cap reached')
   self.records.append(dict(record));self._persist()
