"""ONEtwo-exchangeFAKEnativegate;neverconnectstoQwen/no benchmark artifacts."""
import hashlib,http.client,json,os,pathlib,socket,subprocess,sys,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-source-backed-16k';sys.path.insert(0,str(D/'runtime'))
import session as S,actor_profile as A
from broker_session import ProspectiveSession
from reasoning_adapter import SOURCE_PINS,SOURCE,MODEL
from prospective_body_capacity import session_factory
from prospective_broker_admission import factory,AdmissionJournal
from private_rejection_journal import RejectionJournal
from owned_capacity_proxy import build,create_args,collect
BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def wire(number):
 if number==1:item={'id':'fc_synthetic','type':'function_call','call_id':'call_synthetic','name':'exec_command','arguments':json.dumps({'cmd':"printf 'SYNTHETIC_ONLY' > /tmp/synthetic-followup-marker",'max_output_tokens':50}),'status':'completed'}
 else:item={'id':'msg_synthetic','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':'ACK','annotations':[]}]}
 response={'id':'resp_synthetic_'+str(number),'object':'response','created_at':1,'model':MODEL,'status':'completed','incomplete_details':None,'max_output_tokens':16384,'output':[item],'usage':{'input_tokens':100+number,'output_tokens':10+number,'total_tokens':110+2*number,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':0},'output_tokens_details':{'reasoning_tokens':0}}}
 events=[{'type':'response.created','response':dict(response,status='in_progress',output=[],usage=None)},{'type':'response.output_item.added','output_index':0,'item':dict(item,status='in_progress',arguments='' if number==1 else item.get('arguments',''))}]
 if number==1:events.extend([{'type':'response.function_call_arguments.delta','item_id':item['id'],'output_index':0,'delta':item['arguments']},{'type':'response.function_call_arguments.done','item_id':item['id'],'output_index':0,'arguments':item['arguments']}])
 else:
  part=item['content'][0];events.extend([{'type':'response.content_part.added','item_id':item['id'],'output_index':0,'content_index':0,'part':dict(part,text='')},{'type':'response.output_text.delta','item_id':item['id'],'output_index':0,'content_index':0,'delta':'ACK'},{'type':'response.output_text.done','item_id':item['id'],'output_index':0,'content_index':0,'text':'ACK'},{'type':'response.content_part.done','item_id':item['id'],'output_index':0,'content_index':0,'part':part}])
 events.extend([{'type':'response.output_item.done','output_index':0,'item':item},{'type':'response.completed','response':response}]);return b''.join(b'event: '+e['type'].encode()+b'\ndata: '+json.dumps(e).encode()+b'\n\n' for e in events)
if __name__=='__main__':
 assert not (R/'admission-native-probe-plan.json').exists(),'no syntheticnative jobretry'
 old=json.loads((R/'16k-regex-plan.json').read_text());assert all(sha(D/'runtime'/n)==h for n,h in old['runtime_hashes'].items());assert sha(BINARY)==old['binary_sha256'];root=pathlib.Path('/tmp/solpi-admission-native-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);prefix=root.name;net=prefix+'-net';owned=[];server=None;worker=None;raw=None;calls=[];delays=[];deadline=time.monotonic()+90
 plan={'scope':'one FAKE native tool/follow-up gate;NOTskill/model/task evaluation','max_native_fake_jobs':1,'fake_exchange_cap':4,'expected_fake_exchanges':2,'seconds_cap':90,'real_model_POST_cap':0,'original_runtime_hashes':old['runtime_hashes'],'prospective_module_sha256':sha(R/'prospective_broker_admission.py'),'runner_sha256':sha(pathlib.Path(__file__)),'CLI_sha256':sha(BINARY),'controlled_first_post_terminal_hold_seconds':.35,'no_scored_actor_retry':True};(R/'admission-native-probe-plan.json').write_text(json.dumps(plan,indent=2)+'\n');report={'plan_sha256':sha(R/'admission-native-probe-plan.json'),'private_root':str(root),'real_model_POST':0,'real_generated_tokens':0,'scored_actor_starts':0,'official_test_or_gold_runs':0,'synthetic_native_starts':0}
 def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT,text=True,timeout=min(timeout,max(.1,deadline-time.monotonic()))).strip()
 class Sock:
  def shutdown(self,*a):pass
 class Response:
  status=200
  def __init__(self,body):self.body=body;self.index=0
  def getheader(self,name):return '127.0.0.1:18001'
  def read1(self,n):value=self.body[self.index:self.index+137];self.index+=len(value);return value
 class Connection:
  sock=Sock()
  def connect(self):pass
  def close(self):pass
  def request(self,*args):
   if len(calls)>=4:raise RuntimeError('fakeexchangecap')
   calls.append(args);self.number=len(calls)
  def getresponse(self):return Response(wire(self.number))
 class Synthetic(ProspectiveSession):
  def forward(self,path,body,emit):
   result=super().forward(path,body,emit,connect=lambda *a,**kw:Connection())
   if self.raw_session.posts==1:
    start=time.monotonic();time.sleep(.35);delays.append(time.monotonic()-start)
   return result
 try:
  image=old['actor_image_id'];docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net);top=json.loads(docker('network','inspect',net))[0];assert top['Internal'] and not top['EnableIPv6'] and all(not x.get('Gateway') for x in top['IPAM']['Config']);sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';capacity=session_factory(D/'runtime/session.py',old['runtime_hashes']['session.py']);raw=capacity.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net});provenance={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'};session=Synthetic(raw,{provenance['peer']:provenance});byte=RejectionJournal(root/'broker-byte.json');admit=AdmissionJournal(root/'admission.json');m=factory(D/'runtime/server.py',old['runtime_hashes']['server.py'],byte,admit);handler=type('NativeProbe',(m.PostHandler,),{'session':session});server=m.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start();bundle=build(root/'proxy-bundle',D/'runtime',old['runtime_hashes']);proxy=prefix+'-proxy';owned.append(proxy);docker(*create_args(bundle,proxy,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));docker('start',proxy)
  # Onegenericnativecommand;no benchmark inputs/outputs/mounts.
  (root/'prompt.txt').write_text('Synthetic transport integration. Use exec_command to create /tmp/synthetic-followup-marker containing SYNTHETIC_ONLY, then reply ACK. No other tools or files.');argv=A.argv('codex',8000,root);argv[-1]='-';name=prefix+'-native';owned.append(name);args=['create','-i','--name',name,'--network',net,'--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/tmp','--entrypoint','/bin/sh']
  for e in ['HOME=/root/solpi-home','CODEX_HOME=/root/solpi-home/.codex','MOCK_KEY=synthetic-only','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']:args+=['-e',e]
  docker(*args,image,'-c','mkdir -p "$CODEX_HOME" && exec /opt/solpi/codex "$@"','probe',*argv[1:]);metadata=json.loads(docker('inspect',name))[0];assert set(metadata['NetworkSettings']['Networks'])=={net} and len(metadata['Mounts'])==1 and metadata['Mounts'][0]['Destination']=='/opt/solpi/codex';session.begin('synthetic-native',[{'num_reqs':0,'num_waiting_reqs':0}]);actor_deadline=raw.deadline;report['synthetic_native_starts']=1
  with (root/'native.jsonl').open('wb') as log:p=subprocess.run(['docker','start','-a','-i',name],input=(root/'prompt.txt').read_bytes(),stdout=log,stderr=subprocess.STDOUT,timeout=min(60,max(.1,deadline-time.monotonic())))
  end=min(deadline,time.monotonic()+5)
  while server.workers and time.monotonic()<end:time.sleep(.01)
  assert not server.workers and raw.deadline==actor_deadline;session.finish(True);events=[]
  for line in (root/'native.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
  turns=[e for e in events if e.get('type')=='turn.completed'];costs=[r['accounting_view']['derived_cost'] for r in session.prospective_records];assert len(calls)==len(raw.records)==len(costs)==2 and turns and p.returncode==0;assert any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item']['exit_code']==0 for e in events);assert any(e.get('type')=='item.completed' and e.get('item',{}).get('text','').strip()=='ACK' for e in events)
  for nk,ck in [('input_tokens','input_tokens_inclusive'),('output_tokens','output_tokens_inclusive'),('reasoning_output_tokens','reasoning_tokens_reported')]:assert sum(e['usage'][nk] for e in turns)==sum(c[ck] for c in costs)
  assert all(c['provider_cost_complete'] and c['protocol_valid'] for c in costs) and all(json.loads(c[2])['max_output_tokens']==16384 for c in calls);assert admit.records==[];report.update(native_exit=p.returncode,fake_exchanges=2,native_fake_usage_reconciled=True,fake_usage_not_real_billing=True,tool_executed_successfully=True,assistant_ack=True,admission_denials=[],controlled_terminal_holds=delays,deadline_not_extended=True,synthetic_gross_usage=sum(c['gross_tokens'] for c in costs))
  class LocalHTTP(http.client.HTTPConnection):
   def connect(self):self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(5);self.sock.connect(str(sock))
  client=LocalHTTP('private',timeout=5)
  try:client.request('POST','/v1/responses',b'',{'Content-Length':'8388609'});response=client.getresponse();report['overcap_status']=response.status;response.read()
  finally:client.close()
  assert report['overcap_status']==413 and len(calls)==2 and len(byte.records)==1 and byte.records[0]['provider_POST']==0;report['byte_rejections']=byte.records;report['proxy_journal']=collect(bundle);report['passed']=True
 except Exception as e:report.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:400]})
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20)
  if raw:raw.abort_owned_connections()
  if server:server.cleanup()
  if worker:worker.join(3)
  subprocess.run(['docker','network','rm',net],capture_output=True,timeout=20);report['cleanup_containers_absent']=all(subprocess.run(['docker','inspect',n],capture_output=True,timeout=10).returncode!=0 for n in owned);report['cleanup_network_absent']=subprocess.run(['docker','network','inspect',net],capture_output=True,timeout=10).returncode!=0;report['workers_exited']=not worker or not worker.is_alive();report['all_original_runtime_hashes_unchanged']=all(sha(D/'runtime'/n)==h for n,h in old['runtime_hashes'].items());report['goal_complete']=False;report['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'admission-native-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='artifact_hashes'},indent=2))
