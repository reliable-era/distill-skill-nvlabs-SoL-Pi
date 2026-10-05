"""ONEownedgenericDockerfixture/actualdraftcallbacks/CaptureError;0LLM/native/gold."""
import pathlib,json,hashlib,ast,subprocess,types,threading,time,uuid
from prospective_controller_cell import run_cell
from prospective_task_capture import build
from prospective_owned_epoch import stop as stop_epoch,finish_failure
from fasttext_output_presence import stopped_output_present
R=pathlib.Path(__file__).resolve().parent;D=R/'prepared-failure-safe-fasttext-r3';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'owned-docker-failure-gate-plan.json').exists(),'ONEfixture/no retry';old=json.loads((R/'coalesced-fasttext-plan.json').read_text());image=old['actor_image_id'];name='solpi-owned-failure-'+uuid.uuid4().hex[:10];root=pathlib.Path('/tmp/'+name);root.mkdir(mode=0o700);code=(D/'controller.py').read_text();manifest=json.loads((D/'manifest.json').read_text());assert sha(D/'controller.py')==manifest['controller_sha256'];plan={'scope':'oneisolatedgenericDockerfixture/NOactorCLI/LLM/training/data/tests/gold;ASTactualdraftcallbacks','owned_name':name,'image_id':image,'seconds_cap':45,'fixture_container_cap':1,'real_model_POST_cap':0,'root':str(root),'controller_sha256':sha(D/'controller.py'),'source_hashes':{n:sha(R/n) for n in ['run_owned_docker_failure_gate.py','prospective_owned_epoch.py','prospective_task_capture.py','prospective_controller_cell.py']}};(R/'owned-docker-failure-gate-plan.json').write_text(json.dumps(plan,indent=2)+'\n');deadline=time.monotonic()+45;result={'plan_sha256':sha(R/'owned-docker-failure-gate-plan.json'),'real_model_POST':0,'actorCLI_training_gold_official_runs':0,'fixture_starts':0,'goal_complete':False};owned=[]
 def docker(*a):return subprocess.check_output(['docker',*a],stderr=subprocess.PIPE,text=True,timeout=min(10,max(.1,deadline-time.monotonic()))).strip()
 try:
  docker('image','inspect',image);docker('create','--pull=never','--name',name,'--network','none','--cpus','1','--memory','128m','--pids-limit','32','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh',image,'-c','truncate -s 167772161 /app/model.bin && exec sleep 90');owned.append(name);metadata=json.loads(docker('inspect',name))[0];assert metadata['Image']==image and metadata['HostConfig']['NetworkMode']=='none' and not metadata['Mounts'];docker('start',name);result['fixture_starts']=1
  until=time.monotonic()+3
  while True:
   try:assert docker('exec',name,'stat','-c','%s','/app/model.bin')=='167772161';break
   except Exception:
    if time.monotonic()>until:raise
    time.sleep(.05)
  row={'arm':'none','native_exit':None,'actor_seconds':None,'fixture_not_actor':True};s=types.SimpleNamespace(active='none',deadline=time.monotonic()+600,posts=0,lock=threading.Lock(),connections={},forward_lock=threading.Lock());s.accounting_rows=lambda arm:[];s.abort_owned_connections=lambda:None;ctx={'arm':'none','deadline':s.deadline,'name':name,'container_id':metadata['Id'],'image':image,'row':row,'path':root/'partial-row.json'};private=build(R,sha(R/'task_artifacts.py'),sha(R/'artifact_capture.py'),root/'capture-rejections.json');ns={'row':row,'d':root,'name':name,'arm':'none','actor_image':image,'actor_context':ctx,'owned':owned,'stop_epoch':stop_epoch,'docker':docker,'json':json,'time':time,'SOURCE':types.SimpleNamespace(name='train-fasttext'),'private_capture':private,'stopped_output_present':stopped_output_present,'session':s,'known_cost_lower_bound':lambda requests:0}
  callbacks=[n for n in ast.walk(ast.parse(code)) if isinstance(n,ast.FunctionDef) and n.name in ['stop_owned_issuer','capture_callback','grade_callback','accounting_callback','teardown_cell']];assert len(callbacks)==5;exec(compile(ast.fix_missing_locations(ast.Module(body=callbacks,type_ignores=[])),'actualR3callbacks','exec'),ns)
  run_cell(s,row,root/'partial-row.json',ns['stop_owned_issuer'],ns['capture_callback'],ns['grade_callback'],ns['teardown_cell'],ns['accounting_callback']);assert row['failure']['type']=='CaptureError' and not row['official_grade_available'] and row['completion_drain']['drained'] and row['teardown_complete'];assert json.loads((root/'capture-rejections.json').read_text())[0]['reason']=='size_cap';assert not (root/'captured/payload-0').exists();assert s.posts==0;assert not json.loads(docker('inspect',name))[0]['State']['Running'];result.update(passed=True,identity_epoch_bound_stop_verified=True,actualDocker_tar_capture_error=True,partial_row_and_header_reason_verified=True,no_payload_or_grade=True,fixture_deadline_and_POST_unchanged=True)
 except Exception as e:result.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:240]})
 finally:
  cleanup=[]
  for n in owned:
   subprocess.run(['docker','rm','-f',n],capture_output=True,timeout=15);p=subprocess.run(['docker','inspect',n],capture_output=True,text=True,timeout=10);cleanup.append(p.returncode!=0 and 'No such' in p.stderr)
  result['cleanup_verified']=len(cleanup)==len(owned) and all(cleanup);result['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'owned-docker-failure-gate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='artifact_hashes'},indent=2))
