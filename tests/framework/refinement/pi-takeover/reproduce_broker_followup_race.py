"""Exact8MiBprivateproxy+Unixbroker/fakeSession;zero realnative/model/benchmark."""
import hashlib,http.client,json,pathlib,tempfile,threading,time
from prospective_body_capacity import factory as old_factory,proxy_factory
from prospective_broker_admission import factory as new_factory,AdmissionJournal
from private_rejection_journal import RejectionJournal
R=pathlib.Path(__file__).resolve().parent
FRAME=b'data: {"type":"response.completed","response":{"status":"completed","output":[]}}\n\n'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def probe(root,new=False):
 root=pathlib.Path(root);root.mkdir(mode=0o700);plan=json.loads((R/'16k-regex-plan.json').read_text());runtime=R.parent/'development/pi-takeover-qwen-source-backed-16k/runtime';bytesjournal=RejectionJournal(root/'broker-byte-rejections.json');proxyjournal=RejectionJournal(root/'proxy-byte-rejections.json');admit=AdmissionJournal(root/'admission-rejections.json');servermodule=(new_factory(runtime/'server.py',plan['runtime_hashes']['server.py'],bytesjournal,admit) if new else old_factory(runtime/'server.py',plan['runtime_hashes']['server.py'],bytesjournal));proxymodule=proxy_factory(runtime/'stream_proxy.py',plan['runtime_hashes']['stream_proxy.py'],proxyjournal);release=threading.Event();first_sent=threading.Event();calls=[];history=[];guard=threading.Lock()
 class Fake:
  active='synthetic';deadline=time.monotonic()+30
  def forward(self,path,body,emit):
   with guard:calls.append({'path':path,'body_bytes':len(body)});number=len(calls);history.append(('entered',number,time.monotonic()))
   emit(FRAME)
   if number==1:
    first_sent.set()
    if not release.wait(3):raise RuntimeError('boundedfakeholdexpired')
   with guard:history.append(('finished',number,time.monotonic()))
   return {'client_disconnected':False}
 fake=Fake();sock=root/'broker.sock';handler=type('FakeSessionHandler',(servermodule.PostHandler,),{'session':fake});broker=servermodule.OwnedUnixServer(str(sock),handler);proxyhandler=type('PrivateProxy',(proxymodule.StreamingProxy,),{'authority':'provider.example:8000','unix_socket':str(sock)});proxy=servermodule.OwnedServer(('127.0.0.1',0),proxyhandler)
 for server in [broker,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
 first=second=None;timer=None
 try:
  first=http.client.HTTPConnection('127.0.0.1',proxy.server_port,timeout=4);first.request('POST','http://provider.example:8000/v1/responses',b'{}',{'Content-Type':'application/json'});response=first.getresponse();line=response.readline();assert line+b'\n'==FRAME and response.status==200 and first_sent.wait(1) and not release.is_set()
  if new:timer=threading.Timer(.15,release.set);timer.start()
  second=http.client.HTTPConnection('127.0.0.1',proxy.server_port,timeout=4);start=time.monotonic();second.request('POST','http://provider.example:8000/v1/responses',b'{}',{'Content-Type':'application/json'});follow=second.getresponse();body=follow.read();wait=time.monotonic()-start;assert follow.status==(200 if new else 429);assert len(calls)==(2 if new else 1)
  if new:assert body==FRAME and history[1][0]=='finished' and history[2][0]=='entered' and history[1][1]==1 and history[2][1]==2
  release.set();rest=response.read();assert line+rest==FRAME;assert fake.deadline>time.monotonic()+10
  report={'prospective':new,'terminal_frame_visible_before_first_worker_release':True,'followup_HTTP_status':follow.status,'fake_session_forward_calls':len(calls),'fake_forward_calls_serialized':not new or history[1][0]=='finished','followup_seconds':wait,'response_bytes_unchanged':True,'byte_journal_records':bytesjournal.records,'admission_journal_records':admit.records,'real_provider_POST':0,'real_native_actor_starts':0,'benchmark_or_official_test_runs':0,'source_server_sha256':plan['runtime_hashes']['server.py'],'server_derived_sha256':servermodule.derived_sha256,'source_proxy_sha256':plan['runtime_hashes']['stream_proxy.py']};(root/'result.json').write_text(json.dumps(report,indent=2)+'\n');return report
 finally:
  release.set()
  if timer:timer.cancel();timer.join(1)
  for client in [first,second]:
   if client:client.close()
  for server in [proxy,broker]:server.cleanup()
  assert not proxy.workers and not broker.workers
if __name__=='__main__':
 assert not (R/'broker-followup-race-proof.json').exists(),'proofalreadyrun,reusetheevidence'
 root=pathlib.Path(tempfile.mkdtemp(prefix='solpi-broker-followup-'));root.chmod(0o700);old=probe(root/'old',False);new=probe(root/'prospective',True);report={'root':str(root),'old':old,'prospective':new,'historical_native429_cause_confirmed':False,'scope':'mechanismreproducednotexacthistoricaltiming;prospectiveundeployed','original_runtime_unchanged':True,'real_model_POST':0,'goal_complete':False,'proof_module_hashes':{n:sha(R/n) for n in ['reproduce_broker_followup_race.py','prospective_broker_admission.py','prospective_body_capacity.py','private_rejection_journal.py']},'artifact_hashes':{str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}};(R/'broker-followup-race-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['artifact_hashes']},indent=2))
