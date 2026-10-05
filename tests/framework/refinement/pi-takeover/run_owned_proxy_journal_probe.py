"""Owned Docker proxy startup/private mount/collection gate;synthetic HTTP only."""
import hashlib,json,os,pathlib,subprocess,sys,threading,time,types,uuid
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime';sys.path.insert(0,str(D))
import session as S
from prospective_body_capacity import factory
from private_rejection_journal import RejectionJournal
from owned_capacity_proxy import build,create_args,collect

def docker(*args,timeout=30):return subprocess.run(['docker',*args],capture_output=True,text=True,check=True,timeout=timeout)
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-proxy-journal-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';name=root.name+'-proxy';net=root.name+'-net';pins=json.loads((R/'matched-cython-plan.json').read_text())['runtime_hashes'];spec=build(root/'bundle',D,pins);broker_journal=RejectionJournal(root/'broker-rejections.json');m=factory(D/'server.py',pins['server.py'],broker_journal);calls=[];server=None;worker=None;report={'private_root':str(root),'native_starts':0,'real_provider_POST':0,'real_generated_tokens':0,'scope':'new ownedproxy lifecycle/mount/journal gate;syntheticHTTP only,not repetition of nativeSDKprobe','bundle':spec}
 try:
  def forward(path,body,emit):calls.append(body);emit(b'data: {"synthetic":true}\n\n');return {}
  h=type('SyntheticBroker',(m.PostHandler,),{'session':types.SimpleNamespace(forward=forward)});server=m.OwnedUnixServer(str(sock),h);sock.chmod(0o600);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
  docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net);docker(*create_args(spec,name,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));metadata=json.loads(docker('inspect',name).stdout)[0];mounts={x['Destination']:x for x in metadata['Mounts']};assert set(mounts)=={'/app','/broker','/private-journal'} and mounts['/private-journal']['RW'] and not mounts['/app']['RW'] and not mounts['/broker']['RW'];assert metadata['HostConfig']['ReadonlyRootfs'] and metadata['HostConfig']['CapDrop']==['ALL'];docker('start',name)
  end=time.monotonic()+20
  while True:
   log=docker('logs',name).stdout
   if 'owned_capacity_proxy_ready' in log:break
   if time.monotonic()>end:raise RuntimeError('proxy startup timeout')
   time.sleep(.1)
  code="import http.client,json;c=http.client.HTTPConnection('127.0.0.1',8080,timeout=10);body=b'x'*329291;c.request('POST','http://provider.example:8000/v1/responses',body);r=c.getresponse();print(json.dumps({'status':r.status,'body':r.read().decode()}));c.close()";ok=json.loads(docker('exec',name,'python3','-c',code).stdout);assert ok=={'status':200,'body':'data: {"synthetic":true}\n\n'} and calls==[b'x'*329291]
  code="import http.client;c=http.client.HTTPConnection('127.0.0.1',8080,timeout=5);c.request('POST','http://provider.example:8000/v1/responses',b'',{'Content-Length':'8388609'});r=c.getresponse();print(r.status);r.read();c.close()";assert docker('exec',name,'python3','-c',code).stdout.strip()=='413';assert len(calls)==1;report['before_stop_collection']=collect(spec);assert len(report['before_stop_collection']['records'])==1
  docker('stop','-t','3',name);report['after_stop_collection']=collect(spec);assert report['before_stop_collection']==report['after_stop_collection'];report['accepted_body_bytes']=len(calls[0]);report['synthetic_broker_exchanges']=len(calls);report['proxy_ready']=True;report['mounted_private_journal_verified']=True;report['passed']=True
 except Exception as e:report['passed']=False;report['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  if server:server.cleanup()
  if worker:worker.join(3)
  subprocess.run(['docker','network','rm',net],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['container_absent']=p.returncode!=0 and 'No such' in p.stderr;p=subprocess.run(['docker','network','inspect',net],capture_output=True,text=True,timeout=10);report['network_absent']=p.returncode!=0 and 'not found' in p.stderr;report['workers_exited']=not worker or not worker.is_alive();report['module_hashes']={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['owned_capacity_proxy.py','prospective_body_capacity.py','private_rejection_journal.py','run_owned_proxy_journal_probe.py']};report['evidence_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()};(R/'owned-proxy-journal-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
