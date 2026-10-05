"""ONEbounded2casefullSession/SSE/broker/proxy failure-drain gate;FAKEONLY."""
import pathlib,json,hashlib,sys,threading,http.server,http.client,time,uuid
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-coalesced-verification-admission-16k/runtime';sys.path.insert(0,str(D))
import session as S
from broker_session import ProspectiveSession
from reasoning_adapter import MODEL,SOURCE_PINS,SOURCE
from prospective_body_capacity import session_factory,proxy_factory
from prospective_broker_admission import factory,AdmissionJournal
from private_rejection_journal import RejectionJournal
from prospective_completion_drain import drain
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def frame(event):return b'data: '+json.dumps(event).encode()+b'\n\n'
def scenario(root,expired,pins):
 root.mkdir(mode=0o700);ready=threading.Event();release=threading.Event();fakecalls=[];client_result={};worker_result={};timer=None
 created=frame({'type':'response.created','response':{'id':'synthetic','status':'in_progress','usage':None,'output':[]}});terminal=frame({'type':'response.completed','response':{'id':'synthetic','model':MODEL,'max_output_tokens':16384,'status':'completed','incomplete_details':None,'output':[],'usage':{'input_tokens':5,'output_tokens':3,'total_tokens':8,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':0},'output_tokens_details':{'reasoning_tokens':0}}}})
 class Upstream(http.server.BaseHTTPRequestHandler):
  protocol_version='HTTP/1.1'
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    body=self.rfile.read(int(self.headers['Content-Length']));assert json.loads(body)['max_output_tokens']==16384;fakecalls.append(body);self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Transfer-Encoding','chunked');self.end_headers();self.wfile.write(f'{len(created):x}\r\n'.encode()+created+b'\r\n');self.wfile.flush();ready.set();assert release.wait(4)
    self.wfile.write(f'{len(terminal):x}\r\n'.encode()+terminal+b'\r\n0\r\n\r\n');self.wfile.flush()
   except (OSError,AssertionError):pass
 upstream=http.server.ThreadingHTTPServer(('127.0.0.1',0),Upstream);assert upstream.server_port not in [18001,18002,8000];ut=threading.Thread(target=upstream.serve_forever);ut.start()
 class Response:
  def __init__(self,r):self.r=r
  def __getattr__(self,k):return getattr(self.r,k)
  def getheader(self,k,default=None):return '127.0.0.1:18001' if k.lower()=='x-solpi-upstream' else self.r.getheader(k,default)
 class FakeConnection(http.client.HTTPConnection):
  def __init__(self,*a,timeout=None,**kw):super().__init__('127.0.0.1',upstream.server_port,timeout=min(timeout,4))
  def getresponse(self):return Response(super().getresponse())
 class Synthetic(ProspectiveSession):
  def forward(self,path,body,emit):return super().forward(path,body,emit,connect=FakeConnection)
 cap=session_factory(D/'session.py',pins['session.py']);raw=cap.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'FAKE-no-container'});prov={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'};session=Synthetic(raw,{'127.0.0.1:18001':prov});byte=RejectionJournal(root/'body.json');admit=AdmissionJournal(root/'admission.json');proxybyte=RejectionJournal(root/'proxy-body.json');m=factory(D/'server.py',pins['server.py'],byte,admit);pm=proxy_factory(D/'stream_proxy.py',pins['stream_proxy.py'],proxybyte);sock=root/'broker.sock';handler=type('FailureDrainBroker',(m.PostHandler,),{'session':session});broker=m.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);proxyhandler=type('FailureDrainProxy',(pm.StreamingProxy,),{'authority':'provider.example:8000','unix_socket':str(sock)});proxy=m.OwnedServer(('127.0.0.1',0),proxyhandler);threads=[]
 for server in [broker,proxy]:t=threading.Thread(target=server.serve_forever);t.start();threads.append(t)
 client=http.client.HTTPConnection('127.0.0.1',proxy.server_port,timeout=5)
 def consume():
  try:client.request('POST','http://provider.example:8000/v1/responses',json.dumps({'model':MODEL,'stream':True,'input':'SYNTHETIC_ONLY'}).encode(),{'Content-Type':'application/json'});r=client.getresponse();client_result.update(status=r.status,body=r.read().decode())
  except Exception as e:client_result.update(error=type(e).__name__)
 ct=threading.Thread(target=consume);report={}
 try:
  session.begin('synthetic-expired' if expired else 'synthetic-complete',[{'num_reqs':0,'num_waiting_reqs':0}]);epoch=(raw.active,raw.deadline);ct.start();assert ready.wait(3);assert raw.posts==1 and raw.connections and session.forward_lock.locked();report['injected_failure']='synthetic_capture_error/no artifact';report['stopped_actor_surrogate_no_new_issuance']=True
  if expired:
   clock=raw.deadline-10+240+.01;gate=drain(session,now=lambda:clock);assert not gate['drained'];raw.abort_owned_connections();release.set()
  else:
   timer=threading.Timer(.08,release.set);timer.start();gate=drain(session);assert gate['drained']
  until=time.monotonic()+3
  while (broker.workers or session.forward_lock.locked()) and time.monotonic()<until:time.sleep(.01)
  assert not session.forward_lock.locked() and (raw.active,raw.deadline)==epoch and raw.posts==len(fakecalls)==1;assert len(raw.records)==len(session.prospective_records)==1;r=raw.records[0];av=session.prospective_records[0]['accounting_view'];cost=av['derived_cost']
  if expired:assert cost['gross_tokens'] is None and not cost['provider_cost_complete']
  else:assert r['stream_eof'] and r['error'] is None and cost['provider_cost_complete'] and cost['protocol_valid'] and cost['gross_tokens']==8;assert (root/'transport/response-1.sse').read_bytes()==created+terminal==(root/'transport/derived-response-1.sse').read_bytes()
  report.update(gate=gate,request_error=r['error'],stream_eof=r['stream_eof'],usage_complete=cost['provider_cost_complete'],synthetic_gross_usage_NOTbilling=cost['gross_tokens'],deadline_epoch_and_POST_conserved=True,provider_peer_IS_FAKE_metadata_not_real_Qwen=True,real_model_POST=0,admission_denials=admit.records,byte_denials=byte.records+proxybyte.records);assert not admit.records and not byte.records and not proxybyte.records
 finally:
  release.set()
  if timer:timer.cancel();timer.join(1)
  raw.abort_owned_connections();client.close();ct.join(3)
  for server in [proxy,broker]:server.cleanup()
  for t in threads:t.join(3)
  upstream.shutdown();upstream.server_close();ut.join(3);assert not ct.is_alive() and not ut.is_alive() and all(not t.is_alive() for t in threads) and not broker.workers and not proxy.workers;report['cleanup_verified']=True
 return report
if __name__=='__main__':
 assert not (R/'failure-drain-integration-plan.json').exists(),'oneboundedgate/no repeat';root=pathlib.Path('/tmp/solpi-failure-drain-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);pins=json.loads((D.parent/'freeze-manifest.json').read_text())['runtime_hashes'];assert all(sha(D/n)==h for n,h in pins.items());plan={'scope':'2FAKEforwardscases/fullpinnedSessionSSEprivateproxybroker/capturefailurecleanup','seconds_cap':30,'fake_POST_cap':2,'real_model_POST_cap':0,'native_scored_grader_gold_runs_cap':0,'root':str(root),'runtime_hashes':pins,'source_hashes':{n:sha(R/n) for n in ['run_failure_drain_integration.py','prospective_completion_drain.py','prospective_body_capacity.py','prospective_broker_admission.py']}};(R/'failure-drain-integration-plan.json').write_text(json.dumps(plan,indent=2)+'\n');start=time.monotonic();result={'plan_sha256':sha(R/'failure-drain-integration-plan.json'),'real_model_POST':0,'native_scored_grader_gold_runs':0,'deployed':False,'goal_complete':False}
 try:result.update(complete=scenario(root/'complete',False,pins),expired=scenario(root/'expired',True,pins));assert time.monotonic()-start<30;result['passed']=True
 except Exception as e:result.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:400]})
 result['seconds']=time.monotonic()-start;result['original_runtime_unchanged']=all(sha(D/n)==h for n,h in pins.items());result['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'failure-drain-integration-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='artifact_hashes'},indent=2))
