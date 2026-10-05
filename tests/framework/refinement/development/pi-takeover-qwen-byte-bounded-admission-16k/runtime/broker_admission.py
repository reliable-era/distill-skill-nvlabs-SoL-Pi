"""Undeployedboundedfollow-upadmission;nevermutatesfrozen/live servers."""
import hashlib,json,os,pathlib,threading,time,types
WAIT_CAP_SECONDS=2.0
class AdmissionJournal:
 def __init__(self,path):
  self.path=pathlib.Path(path);self.records=[];self.lock=threading.Lock()
  if self.path.exists() or self.path.is_symlink() or self.path.parent.is_symlink() or self.path.parent.stat().st_mode&0o077:raise ValueError('freshprivatejournalrequired')
  self.persist()
 def persist(self):
  tmp=self.path.with_name(self.path.name+'.pending');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as out:out.write(json.dumps({'protocol':'local-admission-rejections-v1','maximum_records':128,'records':self.records},indent=2)+'\n');out.flush();os.fsync(out.fileno())
  os.replace(tmp,self.path)
 def __call__(self,record):
  keys={'reason','status','provider_forwarded','provider_POST','wait_seconds'}
  if set(record)!=keys or record['reason'] not in ['missing_actor_epoch','actor_cleanup_reserve','busy_wait_cap','actor_epoch_changed'] or record['status']!=429 or record['provider_forwarded'] is not False or record['provider_POST']!=0 or type(record['wait_seconds']) not in [int,float] or not 0<=record['wait_seconds']<=WAIT_CAP_SECONDS+.1:raise ValueError('invalidadmissionmetadata')
  with self.lock:
   if len(self.records)>=128:raise ValueError('admissionjournalfull')
   self.records.append(dict(record));self.persist()
def admission(handler,reject,clock=time.monotonic):
 start=clock();actor=getattr(handler.session,'active',None);deadline=getattr(handler.session,'deadline',None)
 def deny(reason):
  reject({'reason':reason,'status':429,'provider_forwarded':False,'provider_POST':0,'wait_seconds':round(min(WAIT_CAP_SECONDS, max(0,clock()-start)),6)});handler.send_error(429);return False
 if not isinstance(actor,str) or not actor or type(deadline) not in [int,float]:return deny('missing_actor_epoch')
 remaining=deadline-10-clock() # SAMEexistingactorcleanupreserve;neverextendsdeadline
 if remaining<=0:return deny('actor_cleanup_reserve')
 if not handler.server.busy.acquire(timeout=min(WAIT_CAP_SECONDS,remaining)):return deny('busy_wait_cap' if clock()<deadline-10 else 'actor_cleanup_reserve')
 if (getattr(handler.session,'active',None),getattr(handler.session,'deadline',None))!=(actor,deadline):handler.server.busy.release();return deny('actor_epoch_changed')
 if clock()>=deadline-10:handler.server.busy.release();return deny('actor_cleanup_reserve')
 return True # originalPostHandlerfinallyreleasesexactlyonce

def factory(path,expected_sha256,byte_reject,admission_reject):
 raw=pathlib.Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('originalserverpinchanged')
 source=raw.decode();old='  if not self.server.busy.acquire(False):self.send_error(429);return';new='  if not admit_request(self):return'
 if source.count(old)!=1:raise ValueError('unknownbrokerbusyguard')
 source=source.replace(old,new);old="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:self.send_error(413);return\n  if not 0<=n<=262144:self.send_error(413);return";new="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:record_reject('invalid_content_length',None);self.send_error(413);return\n  if not 0<=n<=8388608:record_reject('body_byte_cap',n);self.send_error(413);return"
 if source.count(old)!=1:raise ValueError('unknownbrokerbodyguard')
 source=source.replace(old,new);m=types.ModuleType('prospective_admission_server');m.__dict__.update(admit_request=lambda h:admission(h,admission_reject),record_reject=lambda reason,n:byte_reject({'reason':reason,'declared_body_bytes':n,'body_byte_cap':8388608,'status':413,'provider_forwarded':False,'provider_POST':0}));exec(compile(source,'<prospective-bounded-admission>','exec'),m.__dict__);m.source_sha256=expected_sha256;m.derived_sha256=hashlib.sha256(source.encode()).hexdigest();m.derived_source=source;m.deployed=False;return m
