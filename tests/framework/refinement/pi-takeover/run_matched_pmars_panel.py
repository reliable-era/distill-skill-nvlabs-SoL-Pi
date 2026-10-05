"""Third fixed task using owned capacity v2;no retries or previous-cohort pooling."""
import pathlib
import run_matched_cython_panel as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('PMARS replacement not unique '+old[:75])
 code=code.replace(old,new)
replace("SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-cython-ext')","SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-pmars')")
replace('from stopped_cython_output import classify_stopped','from pmars_output_state import classify_stopped')
replace('from cython_partial_output import capture_partial,replay_partial','from pmars_partial_output import capture_partial,replay_partial')
replace('from cython_grader_inputs import inputs as grader_inputs,docker_options as grader_options,prepare as prepare_grader',"from pmars_grader_setup import prepare as prepare_grader,grade_argv\nfrom prospective_body_capacity import factory,session_factory\nfrom private_rejection_journal import RejectionJournal\nfrom owned_capacity_proxy import build as build_proxy,create_args as proxy_args,collect as collect_proxy\ndef grader_options(spec):return ['-v','/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro']\ndef grader_inputs():return {'image_id':recipe('build-pmars')['grader_image_id'],'setup_module_sha256':sha(R/'pmars_grader_setup.py')}")
replace('cython-partial-grade-repair-result.json','pmars-partial-grade-probe.json') if code.count('cython-partial-grade-repair-result.json')==1 else None
# Named references occur repeatedly;rename all while preserving other historical artifacts.
code=code.replace('cython-partial-grade-repair-result.json','pmars-partial-grade-probe.json').replace('cython-capture-v2-build-cython-ext-result.json','file-capture-build-pmars-result.json')
replace("controls['test_events']==11","len(controls['test_results'])==4")
replace("['selected_tasks'][1]['id']","['selected_tasks'][2]['id']")
replace("'New four-arm second-fixed-task Cython development panel;not representative confirmation'","'New four-arm third-fixed-task PMARS development panel;not representative confirmation'")
replace("protocol='matched-cython-prospective-v1'","protocol='matched-pmars-capacity-v2'")
replace("'grading_policy':'Original trusted image;bounded source+installed extension/metadata or source-only absent-installation replay;offline generic dependencies only;never rebuild target'","'grading_policy':'Original trusted image;binary+Debian source or verified source-only absence;trusted public software preload then network-disconnected unchanged officialscript;never build target'")
replace("['run_matched_cython_panel.py','actor_public_inputs.py','public_artifact_cache.py','discover_task_layout.py','stopped_cython_output.py','cython_partial_output.py','cython_grader_inputs.py'", "['run_matched_pmars_panel.py','owned_capacity_proxy.py','private_rejection_journal.py','prospective_body_capacity.py','pmars_output_state.py','pmars_partial_output.py','pmars_grader_setup.py','actor_public_inputs.py','public_artifact_cache.py','discover_task_layout.py'")
replace(" plan.update(public_recipe=public,", " capacity_protocol=json.loads((R/'owned-capacity-protocol-v2.json').read_text());assert all(sha(R/n)==v for n,v in capacity_protocol['owned_module_pins'].items());assert capacity_protocol['model']=='Qwen3.8-27B-FP8'\n plan.update(capacity_protocol_sha256=sha(R/'owned-capacity-protocol-v2.json'),body_byte_cap=8388608,setup_seconds_cap=300,public_recipe=public,")
replace("trusted_runner_cache_sha256=sha(R/'cython-grader-wheels-cache.json')", "trusted_setup_gate_sha256=sha(R/'pmars-partial-grade-probe.json')")
replace("root=pathlib.Path('/tmp/solpi-mc-'+digest[:20])","root=pathlib.Path('/tmp/solpi-mp-'+digest[:20])")
replace("prefix='solpi-tcp-'+uuid.uuid4().hex[:10]","prefix='solpi-tpp-'+uuid.uuid4().hex[:10]")
replace("session=PanelSession(S.Session(root/'transport'", "proxy_spec=build_proxy(root/'proxy-bundle',D/'runtime',plan['runtime_hashes']);host_rejections=RejectionJournal(root/'broker-rejections.json');capacity_server=factory(D/'runtime/server.py',plan['runtime_hashes']['server.py'],host_rejections);capacity_session=session_factory(D/'runtime/session.py',plan['runtime_hashes']['session.py']);session=PanelSession(capacity_session.Session(root/'transport'")
replace("handler=type('PrefixHandler',(B.PostHandler,),{'session':session});server=B.OwnedUnixServer", "handler=type('PrefixHandler',(capacity_server.PostHandler,),{'session':session});server=capacity_server.OwnedUnixServer")
old="docker('create','--pull=never','--name',proxy,'--network',net,'--network-alias','proxy','--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',str(D)+':/app:ro','--entrypoint','python3',S.IMAGE,'/app/runtime/stream_proxy.py');docker('start',proxy)"
replace(old,"docker(*proxy_args(proxy_spec,proxy,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));docker('start',proxy)\n   ready_deadline=time.monotonic()+20\n   while 'owned_capacity_proxy_ready' not in docker('logs',proxy):\n    if time.monotonic()>ready_deadline:raise RuntimeError('owned proxy startup timeout')\n    time.sleep(.1)")
replace("dynamic=state['dynamic']","dynamic={'source_directory':state['source_directory']}") if code.count("dynamic=state['dynamic']")==1 else None
code=code.replace("dynamic=state['dynamic']","dynamic={'source_directory':state['source_directory']}")
replace("'--name',grade,'--network','none'","'--name',grade,'--network','bridge'")
replace("prepare_grader(grade,image,installation_absent=not present)","prepare_grader(grade,image,d)")
replace("subprocess.run(['docker','exec',grade,'bash','/tests/test.sh'],stdout=out,stderr=subprocess.STDOUT,timeout=600)","subprocess.run(grade_argv(grade),stdout=out,stderr=subprocess.STDOUT,timeout=600)")
replace("    if len(events)!=11","    if len(events)!=4")
replace("requests=session.accounting_rows(arm);", "row['proxy_rejections']=collect_proxy(proxy_spec);row['broker_rejections']=list(host_rejections.records);requests=session.accounting_rows(arm);")
replace("  for name in owned:subprocess.run", "  proxy_journal=None\n  if 'proxy_spec' in globals():\n   try:\n    if proxy in owned:subprocess.run(['docker','stop','-t','3',proxy],capture_output=True,timeout=10)\n    proxy_journal=collect_proxy(proxy_spec)\n   except Exception as e:\n    if error is None:error={'type':type(e).__name__,'message':'proxy journal cleanup '+str(e)[:100]}\n  for name in owned:subprocess.run")
replace("'scope':plan['scope'],'scheduler_wait_seconds'", "'scope':plan['scope'],'proxy_journal':proxy_journal,'scheduler_wait_seconds'")
code=code.replace('matched-cython-plan.json','matched-pmars-plan.json').replace('matched-cython-progress.json','matched-pmars-progress.json').replace('matched-cython-result.json','matched-pmars-result.json')
compile(code,'matched-pmars-generated','exec')
if __name__=='__main__':exec(compile(code,'matched-pmars-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
