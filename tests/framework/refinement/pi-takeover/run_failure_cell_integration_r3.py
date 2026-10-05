"""ONEchanged-pathgate:actualcaptureexception/disconnectedconsumer/controllercell."""
import pathlib,json,hashlib,time,uuid,socket,io,tarfile
from prospective_output_budget import module
from prospective_controller_cell import run_cell,persist
from prospective_diagnostic_capture import factory as capture_factory
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
P=R/'run_failure_drain_integration.py'

def materialize():
 source=P.read_text().split("if __name__=='__main__':")[0]
 source=source.replace('ct=threading.Thread(target=consume);report={}','ct=threading.Thread(target=consume);report={};response_holder=[];row={"arm":"synthetic", "actor_wall_seconds":0., "native_completed_usage":None}')
 source=source.replace("r=client.getresponse();client_result.update", "r=client.getresponse();response_holder.append(r);client_result.update")
 start=source.index("report['injected_failure']='synthetic_capture_error/no artifact'")
 end=source.index('  until=time.monotonic()+3',start)
 replacement="""until=time.monotonic()+1
  while not response_holder and time.monotonic()<until:time.sleep(.01)
  assert response_holder
  # KillONLYownedFAKEHTTPconsumer socket;no provider teardown beforedrain.
  response_holder[0].fp.raw._sock.shutdown(socket.SHUT_RDWR);ct.join(2);assert not ct.is_alive() and not release.is_set()
  history=[];rejections=[]
  def stop():history.append('verified_consumer_stopped');return not ct.is_alive()
  def rejection(reason):
   assert len(rejections)<4;rejections.append(reason);persist(root/'capture-rejections.json',rejections)
  diagnostic=capture_factory(R/'artifact_capture.py',CAPTURE_SHA,rejection)
  def capture():
   before=json.loads((root/'partial-row.json').read_text());assert before['actor_wall_seconds']==0. and not before['official_grade_available'];history.append('capture')
   header=tarfile.TarInfo('model.bin');header.size=167772161
   return diagnostic.capture_file(io.BytesIO(header.tobuf()),root/'payload','model.bin',167772160)
  def grade():raise AssertionError('mustnotgradeunsupportedcapture')
  def accounting():history.append('accounting_afterdrain');return {'started_POST':raw.posts,'pending_connections':len(raw.connections),'rows':list(raw.records)}
  def teardown():
   history.append('teardown');assert (root/'partial-row.json').exists()
   if expired:raw.abort_owned_connections()
   release.set()
   until=time.monotonic()+2
   while session.forward_lock.locked() and time.monotonic()<until:time.sleep(.01)
   assert not session.forward_lock.locked()
  if not expired:timer=threading.Timer(.08,release.set);timer.start()
  kwargs={'now':lambda:raw.deadline-10+240+.01} if expired else {}
  run_cell(session,row,root/'partial-row.json',stop,capture,grade,teardown,accounting,**kwargs)
  gate=row['completion_drain'];assert row['failure']['type']=='CaptureError' and not row['official_grade_available'] and row['teardown_complete']
  assert rejections[0]['reason']=='size_cap' and not rejections[0]['payload_read'] and not (root/'payload').exists()
  assert history.index('capture')<history.index('accounting_afterdrain')<history.index('teardown') and row['accounting']['started_POST']==1 and len(row['accounting_after_teardown']['rows'])==1
  report.update(actual_capture_exception=True,consumer_stopped_before_completion=True,partial_row_persisted_before_capture=True,header_rejection_reason='size_cap',no_grade_on_unsupported_capture=True,controller_history=history)
"""
 source=source[:start]+replacement+source[end:]
 return module('private_failure_cell_gate',source,{'__file__':str(P),'socket':socket,'io':io,'tarfile':tarfile,'run_cell':run_cell,'persist':persist,'capture_factory':capture_factory,'CAPTURE_SHA':sha(R/'artifact_capture.py')})
if __name__=='__main__':
 assert not (R/'failure-cell-integration-r3-plan.json').exists(),'onechangedpathgate/no repeat';prior=json.loads((R/'failure-drain-integration-plan.json').read_text());assert sha(P)==prior['source_hashes'][P.name];root=pathlib.Path('/tmp/solpi-failure-cell-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);names=['run_failure_cell_integration_r3.py','prospective_controller_cell.py','prospective_failure_guard.py','prospective_completion_drain.py','prospective_diagnostic_capture.py','prospective_capture_rejection.py','artifact_capture.py'];plan={'scope':'actualCaptureError/headerreason/durablepartialrow/disconnectedFAKEconsumer/pinnedSessionSSE/cell-drain-beforeteardown','seconds_cap':30,'fake_POST_cap':2,'real_model_POST_cap':0,'native_scored_grader_gold_runs_cap':0,'root':str(root),'parent_plan_sha256':sha(R/'failure-drain-integration-plan.json'),'source_hashes':{n:sha(R/n) for n in names},'runtime_hashes':prior['runtime_hashes']};(R/'failure-cell-integration-r3-plan.json').write_text(json.dumps(plan,indent=2)+'\n');start=time.monotonic();result={'plan_sha256':sha(R/'failure-cell-integration-r3-plan.json'),'real_model_POST':0,'native_scored_grader_gold_runs':0,'deployed_in_scored_controller':False,'goal_complete':False}
 try:
  m=materialize();result.update(complete=m.scenario(root/'complete',False,plan['runtime_hashes']),expired=m.scenario(root/'expired',True,plan['runtime_hashes']));assert time.monotonic()-start<30;result['passed']=True
 except Exception as e:result.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:400]})
 result['seconds']=time.monotonic()-start;result['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'failure-cell-integration-r3-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='artifact_hashes'},indent=2))
