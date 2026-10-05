"""Four-arm first-selected-task pilot,existing broker;not confirmation certificate."""
import contextlib,hashlib,importlib.util,json,os,pathlib,random,shutil,subprocess,sys,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent.parent;D=R.parent/'development/pi-takeover-qwen-coalesced-verification-admission-16k';sys.path.insert(0,str(D/'runtime'))
import session as S,server as B,wrapper as W,actor_profile as A
from budget_panel import PanelSession,verify_live_sources,stopped_output_present,PEER
from prospective_task_capture import build as diagnostic_capture
from prospective_controller_cell import run_cell,persist
from prospective_owned_epoch import stop as stop_epoch,finish_failure
from task_replay import replay_capture
from actor_public_inputs import docker_options,verify_actor_inspect
from fasttext_output_presence import stopped_output_present
from actor_public_inputs import recipe
from uniform_budget_notice import add_notice
from fasttext_grader_setup_r2 import prepare as prepare_grader,grade_argv,inputs as cached_inputs
from broker_admission import factory as admission_factory,AdmissionJournal
from prospective_body_capacity import factory,session_factory
from private_rejection_journal import RejectionJournal
from owned_capacity_proxy import build as build_proxy,create_args as proxy_args,collect as collect_proxy
def grader_options(spec):return [x for mount in spec['cache_inputs']['mounts'] for x in ['-v',mount]]
def grader_inputs():return {'image_id':recipe('train-fasttext')['grader_image_id'],'setup_module_sha256':sha(R/'fasttext_grader_setup_r2.py'),'cache_inputs':cached_inputs()}
SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/train-fasttext');BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex');EXPECTED='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def known_cost_lower_bound(requests):
  return sum(x['usage_audit']['gross_tokens'] for x in requests if x.get('usage_complete') and type(x.get('usage_audit',{}).get('gross_tokens')) is int)
def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.PIPE,text=True,timeout=timeout).strip()
scheduler_wait_seconds=0.0
def idle(path):
  global scheduler_wait_seconds
  started=time.monotonic();deadline=started+max(0,300-scheduler_wait_seconds)
  while True:
   try:v=S.fetch_idle();path.write_text(json.dumps(v));scheduler_wait_seconds+=time.monotonic()-started;return v
   except Exception:
    if time.monotonic()>=deadline:raise
    time.sleep(5)
def absent(name):
  p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);return p.returncode!=0 and name in p.stderr and 'No such' in p.stderr
if __name__=='__main__':
  raise SystemExit('prepared-only draft;not scheduled;no actor/model execution')
  controls=json.loads((R/'fasttext-readiness-probe-r3.json').read_text());assert controls['passed'] and controls['cleanup_verified'] and len(controls['collected_original_tests'])==2;assert sha(BINARY)==EXPECTED
  assert json.loads((R/'terminal-10pct-selection.json').read_text())['selected_tasks'][8]['id']==SOURCE.name
  public=recipe(SOURCE.name);trusted_inputs=grader_inputs()
  transfer=json.loads((R/'file-capture-train-fasttext-result.json').read_text());assert transfer['baseline']['reward']=='0' and transfer['replay']['reward']=='1' and transfer['cleanup_verified'] and transfer['source_unchanged'] and transfer['same_test_collection'];assert {t['name'] for t in transfer['replay']['tests']}==set(controls['collected_original_tests'])
  sdk=json.loads((R/'terminal-prefix-sdk-init-review.json').read_text());assert sdk['initialization_response'] and sdk['exit']==0
  cache=json.loads((R/'terminal-selected-image-cache.json').read_text());image=next(x['image']['image_id'] for x in cache['tasks'] if x['task']==SOURCE.name)
  prior=json.loads((R.parent/'development/pi-takeover-qwen-source-backed-verification/plan.json').read_text());assert len(prior['shared_inference_locks'])==2;arms=['none','K'];random.Random(20261004).shuffle(arms)
  plan={'task':SOURCE.name,'selection_sha256':sha(R/'terminal-10pct-selection.json'),'controls_sha256':sha(R/'fasttext-readiness-probe-r3.json'),'image_id':image,'binary_sha256':EXPECTED,'candidate_sha256':sha(D/'frozen/candidate/SKILL.md'),'runtime_hashes':{p.name:sha(p) for p in (D/'runtime').glob('*.py')},'schedule':arms,'native_starts_cap':2,'provider_POST_cap':32,'per_actor_POST_cap':16,'actor_seconds':600,'completion_grace_seconds':240,'grader_seconds':600,'cpus':1,'memory_mb':2048,'retries':0,'route':'http://127.0.0.1:18001/v1','backend_policy':'All arms/every POST direct pinned replica18001;both replicas idleness/source checks;no old cohort pooling','grading_policy':'Originalimage/stoppedmodel.binonlyorverifiedabsence;cachedpublicCP31114/networkNONEthroughout/unchanged2officialtests/privatewritabletests-copyfortar;no semanticrepairormodeltrainingbygrader','scope':'First fixed-selected task four-arm adapter/scoring pilot;not nine-task confirmation or population estimate'}
  plan.update(previous_adapter_attempt={'native_starts':1,'provider_POST':0,'result_path':'terminal-prefix-native-init-failure/terminal-prefix-result.json','preserved':True},sdk_init_review_sha256=sha(R/'terminal-prefix-sdk-init-review.json'),output_transfer_control_sha256=sha(R/'file-capture-train-fasttext-result.json'),orchestration_sha256=sha(pathlib.Path(__file__)),frozen_skills_manifest=W.files(D/'frozen'),task_source_manifest=W.files(SOURCE),nginx_config_sha256=sha(R/'qwen-load-balancer/nginx.conf'),prior_model_protocol_sha256=sha(R.parent/'development/pi-takeover-qwen-source-backed-verification/plan.json'))
  plan.update(prospective_module_hashes={n:sha(R/n) for n in ['run_coalesced_fasttext_screen.py','fasttext_output_presence.py','fasttext_grader_setup.py','fasttext_grader_setup_r2.py','run_behavior_first_sparql_screen.py','sparql_output_presence.py','sparql_public_inputs.py','sparql_grader_setup.py','prospective_broker_admission.py','prospective_output_budget.py','run_16k_regex_screen.py','regex_output_presence.py','regex_actor_inputs.py','cached_grader_setup.py','run_16k_tex_screen_r2.py','run_16k_tex_screen.py','run_source_backed_doom_screen.py','run_source_backed_financial_screen.py','run_matched_financial_panel.py','run_matched_pmars_panel.py','run_matched_cython_panel.py','run_matched_html_panel.py','uniform_budget_notice.py','tex_protected_baseline.py','tex_grader_setup.py','financial_grader_setup.py','audit_skill_delivery.py','owned_capacity_proxy.py','private_rejection_journal.py','prospective_body_capacity.py','actor_public_inputs.py','public_artifact_cache.py','discover_task_layout.py','matched_html_support.py','prospective_broker_session.py','prospective_sse_bridge.py','prospective_reasoning_adapter.py','pinned_backend_connection.py','prospective_controller_cell.py','prospective_failure_guard.py','prospective_completion_drain.py','prospective_task_capture.py','prospective_diagnostic_capture.py','prospective_capture_rejection.py','prepare_failure_safe_fasttext_controller_r2.py','prepare_failure_safe_fasttext_controller_r3.py','prospective_owned_epoch.py','task_artifacts.py','task_replay.py','artifact_capture.py','directory_capture.py','executable_capture.py','protected_inputs.py']},template_sha256=sha(R/'run_terminal_prefix.py'),transport_conformance_audit_sha256=sha(R/'real-provider-conformance-audit.json'),strict_conformance_ACK_gate=False,protocol='failure-safe-cell-admission16k-fasttext-unstarted-only-v1',scope='ONEverificationsequencingbullet/nextfixedindex8fastText/uniform16K/privateadmission/publictrainingsoftwareALLarms;freshdevelopmentnotsealedconfirmation/nomatrixoldcohortpoolorcausalclaim',missing_output_policy='Stoppedactor/doubleidentityarchive404 verifiesabsence;freshoriginalgrade—notinferred0;directory/link/oversize/ambiguous capture unavailable')
  assert json.loads((R/'real-provider-conformance-audit.json').read_text())['transport_and_accounting_conformance']
  capacity_protocol=json.loads((R/'owned-capacity-protocol-v2.json').read_text());assert all(sha(R/n)==v for n,v in capacity_protocol['owned_module_pins'].items());assert capacity_protocol['model']=='Qwen3.8-27B-FP8'
  freeze=json.loads((D/'freeze-manifest.json').read_text());assert freeze['candidate_sha256']==sha(D/'frozen/candidate/SKILL.md');assert freeze['runtime_hashes']==plan['runtime_hashes'] and freeze['frozen_manifest']==W.files(D/'frozen')
  plan.update(parent_partial_plan_sha256=sha(R/'coalesced-fasttext-plan.json'),parent_failure_audit_sha256=sha(R/'coalesced-fasttext-failure-audit.json'),consumed_original_starts=2,consumed_original_POST=31,started_arms_never_repeated=['candidate','Both'],new_protocol_no_comparator_or_promotion_claim=True)
  plan.update(new_candidate_freeze_sha256=sha(D/'freeze-manifest.json'),comparator_Both_definition=freeze['comparator_Both_definition'],previous_candidate_rejected=True,previous_model_outcomes_not_reused=True)
  plan.update(cpus=public['cpus'],memory_mb=public['memory_mb'],actor_image_id=public['actor_image_id'],uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'],configured_output_cap=16384,arm_recipe=freeze['arm_recipe'],public_training_cache_sha256=sha(R/'public-fasttext-wheels-cache.json'),native16k_gate_sha256=sha(R/'16k-native-probe.json'),admission_native_gate_sha256=sha(R/'admission-native-probe-audit.json'),admission_wait_seconds_cap=2.0);assert freeze['arm_recipe']==W.ARMS and freeze['comparator_Both_definition']=='currentcandidate+frozenKarpathy';assert json.loads((R/'16k-native-probe.json').read_text())['passed'];assert json.loads((R/'admission-native-probe-audit.json').read_text())['gate_passed'];assert sha(D/'runtime/broker_admission.py')==json.loads((R/'admission-native-probe-plan.json').read_text())['prospective_module_sha256']
  plan.update(capacity_protocol_sha256=sha(R/'owned-capacity-protocol-v2.json'),body_byte_cap=8388608,setup_seconds_cap=90,public_recipe=public,trusted_recipe=trusted_inputs,public_recipe_sha256=sha(R/'actor-public-input-recipes.json'),partial_gate_sha256=sha(R/'fasttext-readiness-probe-r3.json'),trusted_setup_gate_sha256=sha(R/'fasttext-readiness-probe-r3.json'))
  assert image==trusted_inputs['image_id'];actor_image=public['actor_image_id']
  (R/'failure-safe-fasttext-plan.json').write_text(json.dumps(plan,indent=2)+'\n');digest=sha(R/'failure-safe-fasttext-plan.json');root=pathlib.Path('/tmp/solpi-fs16-'+digest[:18]);root.mkdir(mode=0o700,exist_ok=False);prefix='solpi-fs16-'+uuid.uuid4().hex[:10];owned=[];snapshots=[];net=prefix+'-net';server=None;session=None;admission_journal=None;rows=[];error=None
  try:
   with S.inference_locks(prior['shared_inference_locks']):
    plan_peers=verify_live_sources();(root/'live-source-pins.json').write_text(json.dumps(plan_peers,indent=2))
    for i in range(3):idle(root/('initial-idle-'+str(i)+'.json'));time.sleep(1)
    docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net)
    topology=json.loads(docker('network','inspect',net))[0];assert topology['Internal'] and not topology['EnableIPv6'] and all(not x.get('Gateway') for x in topology['IPAM']['Config'])
    sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';assert len(os.fsencode(sock))<108;proxy_spec=build_proxy(root/'proxy-bundle',D/'runtime',plan['runtime_hashes']);host_rejections=RejectionJournal(root/'broker-rejections.json');admission_journal=AdmissionJournal(root/'admission-rejections.json');capacity_server=admission_factory(D/'runtime/server.py',plan['runtime_hashes']['server.py'],host_rejections,admission_journal);capacity_session=session_factory(D/'runtime/session.py',plan['runtime_hashes']['session.py']);session=PanelSession(capacity_session.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net}));handler=type('PrefixHandler',(capacity_server.PostHandler,),{'session':session});server=capacity_server.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);threading.Thread(target=server.serve_forever,daemon=True).start()
    proxy=prefix+'-proxy';owned.append(proxy);docker(*proxy_args(proxy_spec,proxy,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));docker('start',proxy)
    ready_deadline=time.monotonic()+20
    while 'owned_capacity_proxy_ready' not in docker('logs',proxy):
     if time.monotonic()>ready_deadline:raise RuntimeError('owned proxy startup timeout')
     time.sleep(.1)
    for arm in arms:
     actor_context=None;row=None;name=None
     assert sha(R/'public-fasttext-wheels-cache.json')==plan['public_training_cache_sha256']
     assert recipe(SOURCE.name)==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe'];assert W.ARMS==plan['arm_recipe']
     assert verify_live_sources()==plan_peers
     assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items())
     assert sha(D/'freeze-manifest.json')==plan['new_candidate_freeze_sha256']
     assert W.files(D/'frozen')==plan['frozen_skills_manifest'] and W.files(SOURCE)==plan['task_source_manifest'] and sha(BINARY)==EXPECTED
     assert all(sha(D/'runtime'/k)==v for k,v in plan['runtime_hashes'].items()) and sha(R/'qwen-load-balancer/nginx.conf')==plan['nginx_config_sha256']
     d=root/arm;d.mkdir();(d/'skills').mkdir();(d/'home').mkdir();(d/'home/.codex').mkdir();keys=W.ARMS[arm]
     for key in keys:shutil.copytree(D/'frozen'/key,d/'skills'/key)
     prompt=add_notice((SOURCE/'instruction.md').read_text(),public['guidance'],[(D/'frozen'/k/'SKILL.md').read_text() for k in keys]);(d/'prompt.txt').write_text(prompt);assert W.files(d/'skills')=={n:h for n,h in plan['frozen_skills_manifest'].items() if n.split('/')[0] in keys};assert all(prompt.count((D/'frozen'/k/'SKILL.md').read_text())==1 for k in keys)
     row={'arm':arm,'official_grade_available':False,'native_completed_usage':None,'phase':'before_native_creation'};rows.append(row);persist(d/'partial-row.json',row)
     session.begin(arm,idle(d/'idle.json'));name=prefix+'-'+arm;owned.append(name);env=['HOME=/root/solpi-home','CODEX_HOME=/root/solpi-home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']
     actor_context={'arm':arm,'deadline':session.deadline,'name':name,'image':actor_image,'container_id':None,'row':row,'path':d/'partial-row.json'}
     args=['create','--pull=never','--name',name,'--network',net,'--cpus',str(public['cpus']),'--memory',str(public['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(d/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/app','--entrypoint','/bin/sh']
     for e in env:args+=['-e',e]
     args+=docker_options(public)
     argv=A.argv('codex',8000,d);assert argv[0]=='codex';docker(*args,actor_image,'-c','mkdir -p "$CODEX_HOME" && exec /opt/solpi/codex "$@"','pilot',*argv[1:]);inspect=json.loads(docker('inspect',name))[0];verify_actor_inspect(inspect,public,net,{'/skills':str(d/'skills'),'/opt/solpi/codex':str(BINARY)});assert inspect['Image']==actor_image;actor_context['container_id']=inspect['Id']
     admission_mark=len(admission_journal.records);start=time.monotonic()
     with (d/'native.jsonl').open('wb') as out:
      p=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT)
      try:p.wait(timeout=max(.1,session.deadline-time.monotonic()-10))
      except subprocess.TimeoutExpired:row['actor_deadline_interrupted']=True
      docker('stop','-t','0',name);p.wait(timeout=5)
     row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start);persist(d/'partial-row.json',row)
     private_capture=diagnostic_capture(R,plan['prospective_module_hashes']['task_artifacts.py'],plan['prospective_module_hashes']['artifact_capture.py'],d/'capture-rejections.json')
     def stop_owned_issuer():return stop_epoch(session,actor_context,docker,owned)
     def capture_callback():
      captured=d/'captured';present=stopped_output_present(name,actor_image);row['output_present']=present
      if present:row['capture']=private_capture(SOURCE.name,name,actor_image,captured)
      else:row['capture']={'capture_complete':False,'output_absent_verified':True,'not_unsupported_layout':True,'path':'/app/model.bin','actor_image_id':actor_image}
      return row['capture']
     def grade_callback():
      grade=prefix+'-grade-'+arm;owned.append(grade);logs=d/'logs';(logs/'verifier').mkdir(parents=True)
      trusted_tests=d/'trusted-tests-copy';shutil.copytree(SOURCE/'tests',trusted_tests);assert W.files(trusted_tests)==W.files(SOURCE/'tests');row['private_trusted_tests_copy_verified']=True
      grade_args=['create','--pull=never','--name',grade,'--network','none','--cpus',str(public['cpus']),'--memory',str(public['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(trusted_tests)+':/tests:rw','-v',str(logs)+':/logs']
      grade_args+=grader_options(trusted_inputs)
      docker(*grade_args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')
      if row['output_present']:row['replay']=replay_capture(SOURCE.name,d/'captured',grade,image,actor_image_id=actor_image)
      else:
       docker('start',grade);docker('exec',grade,'/bin/sh','-c','test ! -e /app/model.bin && test ! -L /app/model.bin');row['replay']={'verified_original_output_absence':True,'rebuild_performed':False}
      row['dependency_setup']=prepare_grader(grade,image,d);row['original_test_manifest_before']=W.files(SOURCE/'tests');row['admission_rejections']=admission_journal.records[admission_mark:]
      with (d/'verifier.log').open('wb') as out:
       p=subprocess.run(grade_argv(grade),stdout=out,stderr=subprocess.STDOUT,timeout=600)
      docker('stop','-t','0',grade);docker('rm',grade);owned.remove(grade);assert absent(grade)
      assert all(sha(trusted_tests/n)==h for n,h in row['original_test_manifest_before'].items());row['original_test_files_unchanged_after_grading']=True
      reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json'
      # Read verifier artifacts through Docker-owned files without publishing content.
      row['reward']=reward.read_text().strip() if reward.exists() else None;events=json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else [];row['test_events']=len(events);row['solved']=row['reward']=='1' and bool(events) and all(x['status']=='passed' for x in events)
      return {'reward':row['reward'],'solved':row['solved'],'test_events':row['test_events']}
     def accounting_callback():
      requests=session.accounting_rows(arm)
      row.update(provider_POST=len(requests),provider_tokens_lower_bound=known_cost_lower_bound(requests),unknown_cost_requests=[x['request'] for x in requests if not x.get('usage_complete')],cost_complete=bool(requests) and all(x.get('usage_complete') and not x.get('error') and x.get('provider_status')==200 for x in requests),backends=[x.get('provider_backend') for x in requests])
      return {'started_stage_POST':session.posts,'requests':requests}
     def teardown_cell():
      if not row.get('completion_drain',{}).get('drained'):session.abort_owned_connections()
      limit=time.monotonic()+3
      while session.forward_lock.locked() and time.monotonic()<limit:time.sleep(.01)
      if session.forward_lock.locked():raise RuntimeError('providerworker finalization unavailable afterboundedabort')
     run_cell(session,row,d/'partial-row.json',stop_owned_issuer,capture_callback,grade_callback,teardown_cell,accounting_callback)
     if row.get('failure'):raise RuntimeError('cellfailed:'+row['failure']['type'])
     row['proxy_rejections']=collect_proxy(proxy_spec);row['broker_rejections']=list(host_rejections.records);requests=session.accounting_rows(arm);row['raw_invalid_requests']=[x['request'] for x in requests if x['raw_provider_protocol_valid'] is not True];row['corrected_requests']=[x['request'] for x in requests if x['correction_applied']];row.update(provider_POST=len(requests),provider_tokens_lower_bound=known_cost_lower_bound(requests),unknown_cost_requests=[x['request'] for x in requests if not x.get('usage_complete')],cost_complete=bool(requests) and all(x.get('usage_complete') and not x.get('error') and x.get('provider_status')==200 for x in requests),backends=[x.get('provider_backend') for x in requests]);session.finish(True);(R/'failure-safe-fasttext-progress.json').write_text(json.dumps({'plan_sha256':digest,'rows':rows,'POST':session.posts,'starts':session.starts},indent=2)+'\n')
     if row['test_events']!=2 or row['reward'] not in ['0','1']:raise RuntimeError('official grading unavailable')
     if not row['cost_complete'] or any(x!=PEER for x in row['backends']):raise RuntimeError('accounting/routing incomplete')
  except Exception as e:error={'type':type(e).__name__,'message':str(e)[:180]}
  finally:
   if session and session.active is not None:
    finish_failure(session,actor_context if 'actor_context' in globals() else None,docker,owned)
   proxy_journal=None
   if 'proxy_spec' in globals():
    try:
     if proxy in owned:subprocess.run(['docker','stop','-t','3',proxy],capture_output=True,timeout=10)
     proxy_journal=collect_proxy(proxy_spec)
    except Exception as e:
     if error is None:error={'type':type(e).__name__,'message':'proxy journal cleanup '+str(e)[:100]}
   for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
   if session:session.abort_owned_connections()
   if server:server.cleanup()
   subprocess.run(['docker','network','rm',net],capture_output=True,timeout=20)
   for image in snapshots:subprocess.run(['docker','image','rm',image],capture_output=True,timeout=20)
   out={'plan_sha256':digest,'rows':rows,'errors':[error] if error else [],'starts':session.starts if session else 0,'POST':session.posts if session else 0,'cleanup_containers_absent':all(absent(n) for n in owned),'scope':plan['scope'],'proxy_journal':proxy_journal,'admission_journal':{'sha256':sha(root/'admission-rejections.json'),'records':admission_journal.records} if admission_journal else None,'scheduler_wait_seconds':scheduler_wait_seconds};(R/'failure-safe-fasttext-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
