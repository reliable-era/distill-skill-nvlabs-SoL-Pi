"""Four-arm first-selected-task pilot,existing broker;not confirmation certificate."""
import contextlib,hashlib,importlib.util,json,os,pathlib,random,shutil,subprocess,sys,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage';sys.path.insert(0,str(D/'runtime'))
import session as S,server as B,wrapper as W,actor_profile as A
from matched_html_support import PanelSession,verify_live_sources,stopped_output_present,PEER
from task_artifacts import capture_stopped_actor
from task_replay import replay_capture
from actor_public_inputs import recipe,docker_options,verify_actor_inspect
from financial_output import classify_stopped,capture_stopped as capture_financial,replay as replay_financial
from uniform_budget_notice import add_notice
from financial_grader_setup import prepare as prepare_grader,grade_argv
from prospective_body_capacity import factory,session_factory
from private_rejection_journal import RejectionJournal
from owned_capacity_proxy import build as build_proxy,create_args as proxy_args,collect as collect_proxy
def grader_options(spec):return ['-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']
def grader_inputs():return {'image_id':recipe('financial-document-processor')['grader_image_id'],'setup_module_sha256':sha(R/'financial_grader_setup.py')}
SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor');BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex');EXPECTED='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
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
 controls=json.loads((R/'financial-missing-grade-repair.json').read_text());assert controls['passed'] and controls['cleanup_verified'] and len(controls['test_results'])==7;assert sha(BINARY)==EXPECTED
 assert json.loads((R/'terminal-10pct-selection.json').read_text())['selected_tasks'][3]['id']==SOURCE.name
 tools=json.loads((R/'public-financial-tools-draft.json').read_text());assert tools['passed'] and tools['cleanup_verified'] and tools['original_app_files_unchanged'] and tools['target_outputs_absent'];public=recipe(SOURCE.name);assert public['actor_image_id']==tools['original_actor_image_id'];public['actor_image_id']=tools['actor_image_id'];public['guidance']+='\nGeneric public software is installed: python3,pdftotext,tesseract (English). Original /app documents unchanged;no submitted outputs prebuilt.\n';trusted_inputs=grader_inputs();assert trusted_inputs['image_id']==tools['original_grader_image_id']
 transfer=json.loads((R/'file-capture-financial-document-processor-result.json').read_text());assert transfer['baseline']['reward']=='0' and transfer['replay']['reward']=='1' and transfer['cleanup_verified'] and transfer['source_unchanged'] and transfer['same_test_collection'];assert {t['name'] for t in transfer['replay']['tests']}=={t['name'] for t in controls['test_results']}
 sdk=json.loads((R/'terminal-prefix-sdk-init-review.json').read_text());assert sdk['initialization_response'] and sdk['exit']==0
 cache=json.loads((R/'terminal-selected-image-cache.json').read_text());image=next(x['image']['image_id'] for x in cache['tasks'] if x['task']==SOURCE.name)
 prior=json.loads((D/'plan.json').read_text());arms=['none','K','candidate','Both'];random.Random(20261004).shuffle(arms)
 plan={'task':SOURCE.name,'selection_sha256':sha(R/'terminal-10pct-selection.json'),'controls_sha256':sha(R/'financial-missing-grade-repair.json'),'image_id':image,'binary_sha256':EXPECTED,'candidate_sha256':sha(D/'frozen/candidate/SKILL.md'),'runtime_hashes':{p.name:sha(p) for p in (D/'runtime').glob('*.py')},'schedule':arms,'native_starts_cap':4,'provider_POST_cap':64,'per_actor_POST_cap':16,'actor_seconds':600,'completion_grace_seconds':240,'grader_seconds':600,'cpus':1,'memory_mb':2048,'retries':0,'route':'http://127.0.0.1:18001/v1','backend_policy':'All arms/every POST direct pinned replica18001;both replicas idleness/source checks;no old cohort pooling','grading_policy':'Original trusted image;three exact directories or verifiedabsence;public runner/pandas preload thennetwork-disconnected unchanged7officialtests;neverrepairoutputs','scope':'First fixed-selected task four-arm adapter/scoring pilot;not nine-task confirmation or population estimate'}
 plan.update(previous_adapter_attempt={'native_starts':1,'provider_POST':0,'result_path':'terminal-prefix-native-init-failure/terminal-prefix-result.json','preserved':True},sdk_init_review_sha256=sha(R/'terminal-prefix-sdk-init-review.json'),output_transfer_control_sha256=sha(R/'file-capture-financial-document-processor-result.json'),orchestration_sha256=sha(pathlib.Path(__file__)),frozen_skills_manifest=W.files(D/'frozen'),task_source_manifest=W.files(SOURCE),nginx_config_sha256=sha(R/'qwen-load-balancer/nginx.conf'),prior_model_protocol_sha256=sha(D/'plan.json'))
 plan.update(prospective_module_hashes={n:sha(R/n) for n in ['run_matched_financial_panel.py','run_matched_pmars_panel.py','run_matched_cython_panel.py','run_matched_html_panel.py','uniform_budget_notice.py','financial_output.py','financial_grader_setup.py','prepare_financial_actor_tools.py','owned_capacity_proxy.py','private_rejection_journal.py','prospective_body_capacity.py','actor_public_inputs.py','public_artifact_cache.py','discover_task_layout.py','matched_html_support.py','prospective_broker_session.py','prospective_sse_bridge.py','prospective_reasoning_adapter.py','pinned_backend_connection.py','task_artifacts.py','task_replay.py','artifact_capture.py','directory_capture.py','executable_capture.py','protected_inputs.py']},template_sha256=sha(R/'run_terminal_prefix.py'),transport_conformance_audit_sha256=sha(R/'real-provider-conformance-audit.json'),strict_conformance_ACK_gate=False,protocol='matched-financial-budget-capacity-v3-preflight-r1',scope='New four-arm fourth-fixed-task financial development panel;not representative confirmation',missing_output_policy='Independently verified stopped actor plus archive404 means output absent;grade original baseline;unsupported capture stops,not quality failure')
 assert json.loads((R/'real-provider-conformance-audit.json').read_text())['transport_and_accounting_conformance']
 capacity_protocol=json.loads((R/'owned-capacity-protocol-v2.json').read_text());assert all(sha(R/n)==v for n,v in capacity_protocol['owned_module_pins'].items());assert capacity_protocol['model']=='Qwen3.8-27B-FP8'
 plan.update(actor_image_id=public['actor_image_id'],public_tools_manifest_sha256=sha(R/'public-financial-tools-draft.json'),uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'])
 plan.update(capacity_protocol_sha256=sha(R/'owned-capacity-protocol-v2.json'),body_byte_cap=8388608,setup_seconds_cap=300,public_recipe=public,trusted_recipe=trusted_inputs,public_recipe_sha256=sha(R/'actor-public-input-recipes.json'),partial_gate_sha256=sha(R/'financial-missing-grade-repair.json'),trusted_setup_gate_sha256=sha(R/'financial-missing-grade-repair.json'))
 assert image==trusted_inputs['image_id'];actor_image=public['actor_image_id']
 (R/'matched-financial-plan.json').write_text(json.dumps(plan,indent=2)+'\n');digest=sha(R/'matched-financial-plan.json');root=pathlib.Path('/tmp/solpi-mf-'+digest[:20]);root.mkdir(mode=0o700,exist_ok=False);prefix='solpi-tfp-'+uuid.uuid4().hex[:10];owned=[];snapshots=[];net=prefix+'-net';server=None;session=None;rows=[];error=None
 try:
  with S.inference_locks(prior['shared_inference_locks']):
   plan_peers=verify_live_sources();(root/'live-source-pins.json').write_text(json.dumps(plan_peers,indent=2))
   for i in range(3):idle(root/('initial-idle-'+str(i)+'.json'));time.sleep(1)
   docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net)
   topology=json.loads(docker('network','inspect',net))[0];assert topology['Internal'] and not topology['EnableIPv6'] and all(not x.get('Gateway') for x in topology['IPAM']['Config'])
   sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';assert len(os.fsencode(sock))<108;proxy_spec=build_proxy(root/'proxy-bundle',D/'runtime',plan['runtime_hashes']);host_rejections=RejectionJournal(root/'broker-rejections.json');capacity_server=factory(D/'runtime/server.py',plan['runtime_hashes']['server.py'],host_rejections);capacity_session=session_factory(D/'runtime/session.py',plan['runtime_hashes']['session.py']);session=PanelSession(capacity_session.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net}));handler=type('PrefixHandler',(capacity_server.PostHandler,),{'session':session});server=capacity_server.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);threading.Thread(target=server.serve_forever,daemon=True).start()
   proxy=prefix+'-proxy';owned.append(proxy);docker(*proxy_args(proxy_spec,proxy,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));docker('start',proxy)
   ready_deadline=time.monotonic()+20
   while 'owned_capacity_proxy_ready' not in docker('logs',proxy):
    if time.monotonic()>ready_deadline:raise RuntimeError('owned proxy startup timeout')
    time.sleep(.1)
   for arm in arms:
    checked_public=recipe(SOURCE.name);checked_tools=json.loads((R/'public-financial-tools-draft.json').read_text());checked_public['actor_image_id']=checked_tools['actor_image_id'];checked_public['guidance']+='\nGeneric public software is installed: python3,pdftotext,tesseract (English). Original /app documents unchanged;no submitted outputs prebuilt.\n';assert checked_public==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe'];assert sha(R/'public-financial-tools-draft.json')==plan['public_tools_manifest_sha256']
    assert verify_live_sources()==plan_peers
    assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items())
    assert W.files(D/'frozen')==plan['frozen_skills_manifest'] and W.files(SOURCE)==plan['task_source_manifest'] and sha(BINARY)==EXPECTED
    assert all(sha(D/'runtime'/k)==v for k,v in plan['runtime_hashes'].items()) and sha(R/'qwen-load-balancer/nginx.conf')==plan['nginx_config_sha256']
    d=root/arm;d.mkdir();(d/'skills').mkdir();(d/'home').mkdir();(d/'home/.codex').mkdir();keys=W.ARMS[arm]
    for key in keys:shutil.copytree(D/'frozen'/key,d/'skills'/key)
    prompt=add_notice((SOURCE/'instruction.md').read_text(),public['guidance'],[(D/'frozen'/k/'SKILL.md').read_text() for k in keys]);(d/'prompt.txt').write_text(prompt)
    session.begin(arm,idle(d/'idle.json'));name=prefix+'-'+arm;owned.append(name);env=['HOME=/root/solpi-home','CODEX_HOME=/root/solpi-home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']
    args=['create','--pull=never','--name',name,'--network',net,'--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(d/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/app','--entrypoint','/bin/sh']
    for e in env:args+=['-e',e]
    args+=docker_options(public)
    argv=A.argv('codex',8000,d);assert argv[0]=='codex';docker(*args,actor_image,'-c','mkdir -p "$CODEX_HOME" && exec /opt/solpi/codex "$@"','pilot',*argv[1:]);inspect=json.loads(docker('inspect',name))[0];verify_actor_inspect(inspect,public,net,{'/skills':str(d/'skills'),'/opt/solpi/codex':str(BINARY)})
    row={'arm':arm};start=time.monotonic()
    with (d/'native.jsonl').open('wb') as out:
     p=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT)
     try:p.wait(timeout=max(.1,session.deadline-time.monotonic()-10))
     except subprocess.TimeoutExpired:row['actor_deadline_interrupted']=True
     docker('stop','-t','0',name);p.wait(timeout=5)
    row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start)
    captured=d/'captured';state=classify_stopped(name,actor_image);row['output_classification']=state;row['output_present']=all(s['state']=='directory' for s in state['paths'].values());row['capture']=capture_financial(name,actor_image,captured)
    grade=prefix+'-grade-'+arm;owned.append(grade);logs=d/'logs';(logs/'verifier').mkdir(parents=True)
    grade_args=['create','--pull=never','--name',grade,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SOURCE/'tests')+':/tests:ro','-v',str(logs)+':/logs']
    grade_args+=grader_options(trusted_inputs)
    docker(*grade_args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')
    row['replay']=replay_financial(captured,grade,image,actor_image_id=actor_image)
    row['dependency_setup']=prepare_grader(grade,image,d)
    with (d/'verifier.log').open('wb') as out:
     p=subprocess.run(grade_argv(grade),stdout=out,stderr=subprocess.STDOUT,timeout=600)
    docker('stop','-t','0',grade);docker('rm',grade);owned.remove(grade);assert absent(grade)
    reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json'
    # Read verifier artifacts through Docker-owned files without publishing content.
    row['reward']=reward.read_text().strip() if reward.exists() else None;events=json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else [];row['test_events']=len(events);row['solved']=row['reward']=='1' and bool(events) and all(x['status']=='passed' for x in events)
    row['proxy_rejections']=collect_proxy(proxy_spec);row['broker_rejections']=list(host_rejections.records);requests=session.accounting_rows(arm);row['raw_invalid_requests']=[x['request'] for x in requests if x['raw_provider_protocol_valid'] is not True];row['corrected_requests']=[x['request'] for x in requests if x['correction_applied']];row.update(provider_POST=len(requests),provider_tokens_lower_bound=known_cost_lower_bound(requests),unknown_cost_requests=[x['request'] for x in requests if not x.get('usage_complete')],cost_complete=bool(requests) and all(x.get('usage_complete') and not x.get('error') and x.get('provider_status')==200 for x in requests),backends=[x.get('provider_backend') for x in requests]);session.finish(True);rows.append(row);(R/'matched-financial-progress.json').write_text(json.dumps({'plan_sha256':digest,'rows':rows,'POST':session.posts,'starts':session.starts},indent=2)+'\n')
    if len(events)!=7 or row['reward'] not in ['0','1']:raise RuntimeError('official grading unavailable')
    if not row['cost_complete'] or any(x!=PEER for x in row['backends']):raise RuntimeError('accounting/routing incomplete')
 except Exception as e:error={'type':type(e).__name__,'message':str(e)[:180]}
 finally:
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
  out={'plan_sha256':digest,'rows':rows,'errors':[error] if error else [],'starts':session.starts if session else 0,'POST':session.posts if session else 0,'cleanup_containers_absent':all(absent(n) for n in owned),'scope':plan['scope'],'proxy_journal':proxy_journal,'scheduler_wait_seconds':scheduler_wait_seconds};(R/'matched-financial-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
