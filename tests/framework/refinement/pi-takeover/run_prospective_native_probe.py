"""Bounded native SDK + Unix broker + isolated Docker proxy,synthetic upstream only."""
import hashlib,json,os,pathlib,subprocess,threading,time,uuid
from prospective_broker_session import ProspectiveSession
from prospective_reasoning_adapter import SOURCE_PINS,SOURCE,MODEL
import session as S,server as B,actor_profile as A
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage';BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')
def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.PIPE,text=True,timeout=timeout).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def synthetic_wire():
 part={'type':'output_text','text':'ACK','annotations':[]};item={'id':'msg_synthetic','type':'message','role':'assistant','status':'completed','content':[part]};response={'id':'resp_synthetic','object':'response','created_at':1,'model':MODEL,'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},'max_output_tokens':8192,'output':[item],'usage':{'input_tokens':8067,'output_tokens':8190,'total_tokens':16257,'output_tokens_details':{'reasoning_tokens':8193}}}
 events=[{'type':'response.created','response':dict(response,status='in_progress',output=[],usage=None,incomplete_details=None)},{'type':'response.output_item.added','output_index':0,'item':dict(item,status='in_progress',content=[])},{'type':'response.content_part.added','item_id':item['id'],'output_index':0,'content_index':0,'part':dict(part,text='')},{'type':'response.output_text.delta','item_id':item['id'],'output_index':0,'content_index':0,'delta':'ACK'},{'type':'response.output_text.done','item_id':item['id'],'output_index':0,'content_index':0,'text':'ACK'},{'type':'response.content_part.done','item_id':item['id'],'output_index':0,'content_index':0,'part':part},{'type':'response.output_item.done','output_index':0,'item':item},{'type':'response.completed','response':response}]
 return b''.join(b'event: '+e['type'].encode()+b'\ndata: '+json.dumps(e).encode()+b'\n\n' for e in events)
if __name__=='__main__':
 assert sha(BINARY)=='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
 root=pathlib.Path('/tmp/solpi-native-derived-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);prefix=root.name;net=prefix+'-net';owned=[];server=None;worker=None;calls=[];report={'synthetic_only':True,'real_provider_POSTs':0,'real_generated_tokens':0,'native_probe_starts':0,'scope':'SDK transport compatibility;not model accounting conformance or skill evaluation'};wire=synthetic_wire();(root/'synthetic-source.sse').write_bytes(wire)
 class Sock:
  def shutdown(self,*a):pass
 class Response:
  status=200;index=0
  def getheader(self,name):return '127.0.0.1:18001'
  def read1(self,n):
   value=wire[self.index:self.index+137];self.index+=len(value);return value
 class Connection:
  sock=Sock()
  def connect(self):pass
  def close(self):pass
  def request(self,*args):calls.append(args)
  def getresponse(self):return Response()
 class SyntheticSession(ProspectiveSession):
  def forward(self,path,body,emit):return super().forward(path,body,emit,connect=lambda *a,**kw:Connection())
 try:
  cache=json.loads((R/'terminal-selected-image-cache.json').read_text());image=next(x['image']['image_id'] for x in cache['tasks'] if x['task']=='break-filter-js-from-html')
  docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net)
  inspect=json.loads(docker('network','inspect',net))[0];assert inspect['Internal'] and not inspect['EnableIPv6'] and all(not x.get('Gateway') for x in inspect['IPAM']['Config'])
  sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';base=S.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net});p={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'};session=SyntheticSession(base,{p['peer']:p});handler=type('SyntheticHandler',(B.PostHandler,),{'session':session});server=B.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
  proxy=prefix+'-proxy';owned.append(proxy);docker('create','--pull=never','--name',proxy,'--network',net,'--network-alias','proxy','--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',str(D)+':/app:ro','--entrypoint','python3',S.IMAGE,'/app/runtime/stream_proxy.py');docker('start',proxy)
  (root/'prompt.txt').write_text('Synthetic SDK transport probe. Reply ACK only. Do not use tools or inspect files.');argv=A.argv('codex',8000,root);name=prefix+'-native';owned.append(name);args=['create','--pull=never','--name',name,'--network',net,'--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/tmp','--entrypoint','/bin/sh']
  for e in ['HOME=/root/solpi-home','CODEX_HOME=/root/solpi-home/.codex','MOCK_KEY=synthetic-only','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']:args+=['-e',e]
  docker(*args,image,'-c','mkdir -p "$CODEX_HOME" && exec /opt/solpi/codex "$@"','probe',*argv[1:]);actor=json.loads(docker('inspect',name))[0];assert set(actor['NetworkSettings']['Networks'])=={net} and len(actor['Mounts'])==1 and actor['Mounts'][0]['Destination']=='/opt/solpi/codex';session.begin('synthetic-native',[{'num_reqs':0,'num_waiting_reqs':0}]);report['native_probe_starts']=1
  with (root/'native.jsonl').open('wb') as out:result=subprocess.run(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,timeout=60)
  deadline=time.monotonic()+5
  while server.workers and time.monotonic()<deadline:time.sleep(.01)
  assert server.workers==0;session.finish(True);events=[]
  for line in (root/'native.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
  report.update(native_exit=result.returncode,native_event_types=[e.get('type') for e in events],native_turn_completed=any(e.get('type')=='turn.completed' for e in events),assistant_ack=any(e.get('type')=='item.completed' and e.get('item',{}).get('text')=='ACK' for e in events),synthetic_requests=len(calls),raw_protocol_valid=base.records[0]['usage_audit']['protocol_valid'] if base.records else None,correction_applied=session.prospective_records[0]['accounting_view']['correction_applied'] if session.prospective_records else False,raw_status_preserved='incomplete',private_root=str(root))
 except Exception as e:report['error']={'type':type(e).__name__,'message':str(e)[:250]}
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20)
  if server:server.cleanup()
  if worker:worker.join(3)
  subprocess.run(['docker','network','rm',net],capture_output=True,timeout=20)
  report['cleanup_containers_absent']=all(subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in owned);report['cleanup_network_absent']=subprocess.run(['docker','network','inspect',net],capture_output=True,timeout=10).returncode!=0;report['worker_exited']=not worker or not worker.is_alive();report['runner_sha256']=sha(pathlib.Path(__file__));report['passed']=report.get('native_exit')==0 and report.get('native_turn_completed') and report.get('assistant_ack') and report.get('synthetic_requests')==1 and report.get('correction_applied') and report['cleanup_containers_absent'] and report['cleanup_network_absent'] and report['worker_exited'];(R/'prospective-native-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
