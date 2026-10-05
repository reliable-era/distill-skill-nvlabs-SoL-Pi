"""Draft owned frontend byte capacity;no live/shared runtime mutation."""
import hashlib,pathlib,types
BODY_CAP=8388608

def expanded_component(source_path,expected_sha256,kind):
 raw=pathlib.Path(source_path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('frozen capacity component changed')
 guards={'proxy':('if not 0<=n<=262144:self.send_error(413);return','if not 0<=n<=8388608:self.send_error(413);return'),'session':('or len(body)>262144:','or len(body)>8388608:')}
 if kind not in guards:raise ValueError('unknown capacity component')
 old,new=guards[kind];source=raw.decode()
 if source.count(old)!=1:raise ValueError('unknown capacity component guard')
 derived=source.replace(old,new);compile(derived,'<pinned-capacity-'+kind+'>','exec');return derived

def proxy_factory(source_path,expected_sha256,reject):
 derived=expanded_component(source_path,expected_sha256,'proxy');old="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:self.send_error(413);return\n  if not 0<=n<=8388608:self.send_error(413);return"
 new="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:record_reject('invalid_content_length',None);self.send_error(413);return\n  if not 0<=n<=8388608:record_reject('body_byte_cap',n);self.send_error(413);return"
 if derived.count(old)!=1:raise ValueError('unknown proxy rejection guard')
 def record_reject(reason,length):reject({'reason':reason,'declared_body_bytes':length,'body_byte_cap':BODY_CAP,'status':413,'provider_forwarded':False,'provider_POST':0})
 module=types.ModuleType('owned_capacity_proxy');module.__dict__['record_reject']=record_reject;exec(compile(derived.replace(old,new),'<pinned-proxy-journal>','exec'),module.__dict__);return module

def session_factory(source_path,expected_sha256):
 derived=expanded_component(source_path,expected_sha256,'session');module=types.ModuleType('owned_capacity_session');exec(compile(derived,'<pinned-capacity-session>','exec'),module.__dict__);return module
def factory(source_path,expected_sha256,reject):
 """Trusted source hash and one exact guard only. Caller owns rejection journal."""
 raw=pathlib.Path(source_path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('frozen broker source changed')
 source=raw.decode();old="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:self.send_error(413);return\n  if not 0<=n<=262144:self.send_error(413);return"
 new="  try:n=int(self.headers.get('Content-Length','-1'))\n  except ValueError:record_reject(self,'invalid_content_length',None);self.send_error(413);return\n  if not 0<=n<=8388608:record_reject(self,'body_byte_cap',n);self.send_error(413);return"
 if source.count(old)!=1:raise ValueError('unknown broker framing guard')
 def record_reject(handler,reason,length):
  reject({'reason':reason,'declared_body_bytes':length,'body_byte_cap':BODY_CAP,'status':413,'provider_forwarded':False,'provider_POST':0})
 module=types.ModuleType('owned_draft_capacity');module.__dict__['record_reject']=record_reject;exec(compile(source.replace(old,new),'<pinned-owned-capacity-draft>','exec'),module.__dict__)
 module.source_sha256=expected_sha256;module.derived_sha256=hashlib.sha256(source.replace(old,new).encode()).hexdigest();module.body_byte_cap=BODY_CAP;return module
