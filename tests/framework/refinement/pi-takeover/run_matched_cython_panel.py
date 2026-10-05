"""Next fixed selected task;uniform public inputs and missing-target preservation."""
import pathlib
import run_matched_html_panel as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('Cython replacement not unique '+old[:80])
 code=code.replace(old,new)
replace('from task_replay import replay_capture','from task_replay import replay_capture\nfrom actor_public_inputs import recipe,docker_options,verify_actor_inspect\nfrom stopped_cython_output import classify_stopped\nfrom cython_partial_output import capture_partial,replay_partial\nfrom cython_grader_inputs import inputs as grader_inputs,docker_options as grader_options,prepare as prepare_grader')
replace("SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/break-filter-js-from-html')","SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-cython-ext')")
replace(" controls=json.loads((R/'terminal-first-controls.json').read_text());assert controls['valid_baseline_gold_pair'];assert sha(BINARY)==EXPECTED"," controls=json.loads((R/'cython-partial-grade-repair-result.json').read_text());assert controls['passed'] and controls['cleanup_verified'] and controls['test_events']==11;assert sha(BINARY)==EXPECTED\n assert json.loads((R/'terminal-10pct-selection.json').read_text())['selected_tasks'][1]['id']==SOURCE.name\n public=recipe(SOURCE.name);trusted_inputs=grader_inputs();assert public['actor_image_id']==trusted_inputs['image_id']")
replace("transfer=json.loads((R/'terminal-output-transfer-control.json').read_text());assert transfer['passed'] and transfer['cleanup_done']","transfer=json.loads((R/'cython-capture-v2-build-cython-ext-result.json').read_text());assert transfer['valid_output_replay'] and transfer['cleanup_verified'] and transfer['source_unchanged'] and transfer['same_test_collection'];assert {t['name'] for t in transfer['replay']['tests']}=={t['name'] for t in controls['test_results']}")
replace("'controls_sha256':sha(R/'terminal-first-controls.json')","'controls_sha256':sha(R/'cython-partial-grade-repair-result.json')")
replace("output_transfer_control_sha256=sha(R/'terminal-output-transfer-control.json')","output_transfer_control_sha256=sha(R/'cython-capture-v2-build-cython-ext-result.json')")
replace("'grading_policy':'Original trusted image/filter/test environment;only captured /app/out.html supplied;not actor image or modified executables'","'grading_policy':'Original trusted image;bounded source+installed extension/metadata or source-only absent-installation replay;offline generic dependencies only;never rebuild target'")
replace("'New four-arm first-fixed-task matched replica panel;not representative confirmation'","'New four-arm second-fixed-task Cython development panel;not representative confirmation'")
replace("protocol='matched-html-prospective-v1'","protocol='matched-cython-prospective-v1'")
replace("['matched_html_support.py','prospective_broker_session.py'","['run_matched_cython_panel.py','actor_public_inputs.py','public_artifact_cache.py','discover_task_layout.py','stopped_cython_output.py','cython_partial_output.py','cython_grader_inputs.py','matched_html_support.py','prospective_broker_session.py'")
replace(" (R/'matched-html-plan.json').write_text", " plan.update(public_recipe=public,trusted_recipe=trusted_inputs,public_recipe_sha256=sha(R/'actor-public-input-recipes.json'),partial_gate_sha256=sha(R/'cython-partial-grade-repair-result.json'),trusted_runner_cache_sha256=sha(R/'cython-grader-wheels-cache.json'))\n assert image==public['actor_image_id']==trusted_inputs['image_id']\n (R/'matched-html-plan.json').write_text")
replace("root=pathlib.Path('/tmp/solpi-mh-'+digest[:20])","root=pathlib.Path('/tmp/solpi-mc-'+digest[:20])")
replace("prefix='solpi-tbp-'+uuid.uuid4().hex[:10]","prefix='solpi-tcp-'+uuid.uuid4().hex[:10]")
replace("   for arm in arms:\n    assert verify_live_sources()==plan_peers","   for arm in arms:\n    assert recipe(SOURCE.name)==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe']\n    assert verify_live_sources()==plan_peers")
replace("prompt=(SOURCE/'instruction.md').read_text()+'\\n\\nUse supplied skills", "prompt=(SOURCE/'instruction.md').read_text()+'\\n\\n'+public['guidance']+'\\n\\nUse supplied skills")
replace("    argv=A.argv('codex',8000,d);", "    args+=docker_options(public)\n    argv=A.argv('codex',8000,d);")
replace("inspect=json.loads(docker('inspect',name))[0];assert set(inspect['NetworkSettings']['Networks'])=={net} and inspect['HostConfig']['Memory']==2147483648 and inspect['HostConfig']['NanoCpus']==1000000000 and len(inspect['Mounts'])==2 and not any(x['Destination'] in ['/tests','/solution','/broker'] for x in inspect['Mounts'])", "inspect=json.loads(docker('inspect',name))[0];verify_actor_inspect(inspect,public,net,{'/skills':str(d/'skills'),'/opt/solpi/codex':str(BINARY)})")
old="    captured=d/'captured';present=stopped_output_present(name,image);row['output_present']=present\n    if present:\n     row['capture']=capture_stopped_actor(SOURCE.name,name,image,captured)\n    else:row['capture']={'capture_complete':False,'output_absent_verified':True,'not_unsupported_layout':True}"
new="    captured=d/'captured';state=classify_stopped(name,image);present=state['output_state']=='present';row['output_present']=present;row['output_classification']=state\n    if present:\n     row['capture']=capture_stopped_actor(SOURCE.name,name,image,captured,dynamic=state['dynamic'])\n    else:row['capture']=capture_partial(name,image,captured)"
replace(old,new)
replace("grade_args=['create','--pull=never','--name',grade,'--network','bridge'", "grade_args=['create','--pull=never','--name',grade,'--network','none'")
replace("    docker(*grade_args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')", "    grade_args+=grader_options(trusted_inputs)\n    docker(*grade_args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')")
replace("     row['replay']=replay_capture(SOURCE.name,captured,grade,image)\n     row['graded_output_sha256']=row['capture']['artifacts']['/app/out.html']['sha256']\n    else:docker('start',grade)", "     row['replay']=replay_capture(SOURCE.name,captured,grade,image,dynamic=state['dynamic'])\n    else:row['replay']=replay_partial(captured,grade,image)\n    row['dependency_setup']=prepare_grader(grade,image,installation_absent=not present)")
replace("docker('rm',grade);owned.remove(grade);assert absent(grade)","docker('stop','-t','0',grade);docker('rm',grade);owned.remove(grade);assert absent(grade)")
replace("    if not events or row['reward'] not in ['0','1']:","    if len(events)!=11 or row['reward'] not in ['0','1']:")
code=code.replace('matched-html-plan.json','matched-cython-plan.json').replace('matched-html-progress.json','matched-cython-progress.json').replace('matched-html-result.json','matched-cython-result.json')
compile(code,'matched-cython-generated','exec')
if __name__=='__main__':exec(compile(code,'matched-cython-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
