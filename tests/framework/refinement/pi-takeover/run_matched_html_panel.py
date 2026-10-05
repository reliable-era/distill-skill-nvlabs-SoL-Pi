"""Reuse frozen first-task orchestration in separately frozen matched prospective cohort."""
import pathlib
R=pathlib.Path(__file__).resolve().parent;template=R/'run_terminal_prefix.py';code=template.read_text()
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('template replacement not unique: '+old[:80])
 code=code.replace(old,new)
replace('import session as S,server as B,wrapper as W,actor_profile as A','import session as S,server as B,wrapper as W,actor_profile as A\nfrom matched_html_support import PanelSession,verify_live_sources,stopped_output_present,PEER\nfrom task_artifacts import capture_stopped_actor\nfrom task_replay import replay_capture')
replace("'backend_policy':'unchanged uniform least_conn;record every peer;no causal claim or cross-cohort pooling'","'backend_policy':'All arms/every POST direct pinned replica18001;both replicas idleness/source checks;no old cohort pooling'")
replace("'route':'http://127.0.0.1:8000/v1'","'route':'http://127.0.0.1:18001/v1'")
replace(" (R/'terminal-prefix-plan.json').write_text", " plan.update(prospective_module_hashes={n:sha(R/n) for n in ['matched_html_support.py','prospective_broker_session.py','prospective_sse_bridge.py','prospective_reasoning_adapter.py','pinned_backend_connection.py','task_artifacts.py','task_replay.py','artifact_capture.py','directory_capture.py','executable_capture.py','protected_inputs.py']},template_sha256=sha(R/'run_terminal_prefix.py'),transport_conformance_audit_sha256=sha(R/'real-provider-conformance-audit.json'),strict_conformance_ACK_gate=False,protocol='matched-html-prospective-v1',scope='New four-arm first-fixed-task matched replica panel;not representative confirmation',missing_output_policy='Independently verified stopped actor plus archive404 means output absent;grade original baseline;unsupported capture stops,not quality failure')\n assert json.loads((R/'real-provider-conformance-audit.json').read_text())['transport_and_accounting_conformance']\n (R/'terminal-prefix-plan.json').write_text")
replace("root=pathlib.Path('/tmp/solpi-tp-'+digest)","root=pathlib.Path('/tmp/solpi-mh-'+digest[:20])")
replace("   for i in range(3):idle(root/('initial-idle-'+str(i)+'.json'));time.sleep(1)","   plan_peers=verify_live_sources();(root/'live-source-pins.json').write_text(json.dumps(plan_peers,indent=2))\n   for i in range(3):idle(root/('initial-idle-'+str(i)+'.json'));time.sleep(1)")
replace("session=S.Session(root/'transport'","session=PanelSession(S.Session(root/'transport'")
replace("'actor_network':net});handler=","'actor_network':net}));handler=")
replace("   for arm in arms:","   for arm in arms:\n    assert verify_live_sources()==plan_peers\n    assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items())")
old="    captured=d/'captured';captured.mkdir();docker('cp',name+':/app/.',str(captured),timeout=30);row['captured_app_manifest']=W.files(captured);docker('rm',name);owned.remove(name);assert absent(name)"
new="    captured=d/'captured';present=stopped_output_present(name,image);row['output_present']=present\n    if present:\n     row['capture']=capture_stopped_actor(SOURCE.name,name,image,captured)\n    else:row['capture']={'capture_complete':False,'output_absent_verified':True,'not_unsupported_layout':True}\n    docker('rm',name);owned.remove(name);assert absent(name)"
replace(old,new)
old="    output=captured/'out.html'\n    docker(*grade_args,'--entrypoint','/bin/bash',image,'/tests/test.sh')\n    if output.is_file() and not output.is_symlink():\n     row['graded_output_sha256']=sha(output);docker('cp',str(output),grade+':/app/out.html')\n    with (d/'verifier.log').open('wb') as out:\n     p=subprocess.run(['docker','start','-a',grade],stdout=out,stderr=subprocess.STDOUT,timeout=600)"
new="    docker(*grade_args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')\n    if present:\n     row['replay']=replay_capture(SOURCE.name,captured,grade,image)\n     row['graded_output_sha256']=row['capture']['artifacts']['/app/out.html']['sha256']\n    else:docker('start',grade)\n    with (d/'verifier.log').open('wb') as out:\n     p=subprocess.run(['docker','exec',grade,'bash','/tests/test.sh'],stdout=out,stderr=subprocess.STDOUT,timeout=600)"
replace(old,new)
replace("requests=[x for x in session.records if x['actor']==arm]","requests=session.accounting_rows(arm);row['raw_invalid_requests']=[x['request'] for x in requests if x['raw_provider_protocol_valid'] is not True];row['corrected_requests']=[x['request'] for x in requests if x['correction_applied']]")
replace("any(x not in ['127.0.0.1:18001','127.0.0.1:18002'] for x in row['backends'])","any(x!=PEER for x in row['backends'])")
replace("  if server:server.shutdown();server.server_close()","  if server:server.cleanup()")
code=code.replace('terminal-prefix-plan.json','matched-html-plan.json').replace('terminal-prefix-progress.json','matched-html-progress.json').replace('terminal-prefix-result.json','matched-html-result.json')
# Do not rewrite historical artifact references during renaming.
code=code.replace('terminal-prefix-native-init-failure/matched-html-result.json','terminal-prefix-native-init-failure/terminal-prefix-result.json')
replace('def idle(path):', 'scheduler_wait_seconds=0.0\ndef idle(path):\n global scheduler_wait_seconds')
replace(' deadline=time.monotonic()+300', ' started=time.monotonic();deadline=started+max(0,300-scheduler_wait_seconds)')
replace("try:v=S.fetch_idle();path.write_text(json.dumps(v));return v", "try:v=S.fetch_idle();path.write_text(json.dumps(v));scheduler_wait_seconds+=time.monotonic()-started;return v")
replace("'scope':plan['scope']", "'scope':plan['scope'],'scheduler_wait_seconds':scheduler_wait_seconds")
compile(code,str(template),'exec')
if __name__=='__main__':exec(compile(code,str(template),'exec'),{'__name__':'__main__','__file__':str(__file__)})
