"""Pinned private proxy bundle, startup and durable journal collection."""
import hashlib,json,pathlib,shutil,subprocess
from prospective_body_capacity import expanded_component
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(root,runtime,pins):
 root=pathlib.Path(root);root.mkdir(mode=0o700,exist_ok=False);bundle=root/'runtime';bundle.mkdir(mode=0o700);journal=root/'journal';journal.mkdir(mode=0o700)
 for name in ['server.py','stream_proxy.py']:
  source=pathlib.Path(runtime)/name
  if sha(source)!=pins[name]:raise ValueError('proxy source pin mismatch')
  shutil.copyfile(source,bundle/name)
 expanded_component(bundle/'stream_proxy.py',pins['stream_proxy.py'],'proxy')
 for name in ['prospective_body_capacity.py','private_rejection_journal.py']:shutil.copyfile(R/name,bundle/name)
 launcher="""import json,os,signal,threading
from prospective_body_capacity import proxy_factory,factory
from private_rejection_journal import RejectionJournal
pins=json.load(open('/app/pins.json'))
if os.environ.get('BROKER_SOCKET')!='/broker/broker.sock':raise RuntimeError('fixed private broker path required')
journal=RejectionJournal('/private-journal/proxy.json')
proxy=proxy_factory('/app/stream_proxy.py',pins['stream_proxy.py'],journal)
server_module=factory('/app/server.py',pins['server.py'],lambda r:None)
handler=type('PrivateCapacityProxy',(proxy.StreamingProxy,),{'authority':'provider.example:8000','unix_socket':'/broker/broker.sock'})
server=server_module.OwnedServer(('0.0.0.0',8080),handler)
def stop(*a):threading.Thread(target=server.shutdown,daemon=True).start()
signal.signal(signal.SIGTERM,stop)
print('owned_capacity_proxy_ready',flush=True)
try:server.serve_forever()
finally:server.cleanup()
"""
 (bundle/'launcher.py').write_text(launcher);(bundle/'pins.json').write_text(json.dumps({k:pins[k] for k in ['server.py','stream_proxy.py']},indent=2)+'\n')
 spec={'bundle':str(bundle),'journal':str(journal),'files_sha256':{p.name:sha(p) for p in bundle.iterdir()},'max_body_bytes':8388608,'authority':'provider.example:8000','broker_path':'/broker/broker.sock','journal_path':'/private-journal/proxy.json'};(root/'bundle.json').write_text(json.dumps(spec,indent=2)+'\n');return spec

def verify(spec):
 bundle=pathlib.Path(spec['bundle']);journal=pathlib.Path(spec['journal'])
 if bundle.is_symlink() or journal.is_symlink() or journal.stat().st_mode&0o077:raise ValueError('proxy bundle/journal privacy changed')
 if {p.name:sha(p) for p in bundle.iterdir() if p.is_file() and not p.is_symlink()}!=spec['files_sha256'] or any(p.is_symlink() or not p.is_file() for p in bundle.iterdir()):raise ValueError('proxy bundle hash/layout changed')

def create_args(spec,name,network,image,sockdir,uid,gid):
 verify(spec)
 return ['create','--pull=never','--name',name,'--network',network,'--network-alias','proxy','--user',str(uid)+':'+str(gid),'--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','-e','PYTHONDONTWRITEBYTECODE=1','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',spec['bundle']+':/app:ro','-v',spec['journal']+':/private-journal:rw','--entrypoint','python3',image,'/app/launcher.py']

def collect(spec):
 verify(spec);p=pathlib.Path(spec['journal'])/'proxy.json'
 if p.is_symlink() or not p.is_file() or p.stat().st_mode&0o777!=0o600:raise ValueError('private proxy journal unavailable')
 x=json.loads(p.read_text())
 if x.get('protocol')!='local-rejections-v1' or x.get('maximum_records')!=128 or len(x.get('records',[]))>128:raise ValueError('proxy journal schema changed')
 from private_rejection_journal import FIELDS
 for record in x['records']:
  if set(record)!=FIELDS or record['provider_forwarded'] is not False or record['provider_POST']!=0 or record['status']!=413:raise ValueError('invalid proxy rejection record')
 return {'journal_collected':True,'sha256':sha(p),'records':x['records'],'provider_POST':0,'contains_request_payloads':False}
