"""NextFIXEDRegex/newfour-arm16Kdevelopment;reusecontrolsnotoutcomes."""
import pathlib
import run_16k_tex_screen_r2 as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('Regex replacementnotunique '+old[:70])
 code=code.replace(old,new)
code=code.replace('overfull-hbox','regex-log').replace('tex-wiring-probe.json','regex-readiness-probe.json')
replace('from tex_protected_baseline import capture_before,compare_original','from regex_output_presence import stopped_output_present\nfrom regex_actor_inputs import recipe')
replace('from tex_grader_setup import prepare as prepare_grader,grade_argv','from cached_grader_setup import prepare as prepare_grader,grade_argv,inputs as cached_inputs')
# Later originalpublicimport mustNOToverwriteRegexprospectiverecipe.
replace('from actor_public_inputs import recipe,docker_options,verify_actor_inspect','from actor_public_inputs import docker_options,verify_actor_inspect')
replace("def grader_options(spec):return ['-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']","def grader_options(spec):return [x for mount in spec['cache_inputs']['mounts'] for x in ['-v',mount]]")
replace("def grader_inputs():return {'image_id':recipe('regex-log')['grader_image_id'],'setup_module_sha256':sha(R/'tex_grader_setup.py')}","def grader_inputs():return {'image_id':recipe('regex-log')['grader_image_id'],'setup_module_sha256':sha(R/'cached_grader_setup.py'),'cache_inputs':cached_inputs()}")
replace("len(controls['collected_original_tests'])==4","len(controls['collected_original_tests'])==1")
replace("['selected_tasks'][5]['id']","['selected_tasks'][6]['id']")
replace("protected_inputs_original=transfer['protected_before'],","public_python_binding_sha256=sha(R/'regex-public-python-binding.json'),")
replace("    baseline=capture_before(name,actor_image,d/'before');compare_original(baseline,transfer)\n    row={'arm':arm,'protected_before':baseline};start=time.monotonic()","    row={'arm':arm};start=time.monotonic()")
replace("    captured=d/'captured';row['capture']=capture_stopped_actor(SOURCE.name,name,actor_image,captured,protected_baseline=baseline['protected_baseline']);assert row['capture']['protected_input_gate_passed']","    captured=d/'captured';present=stopped_output_present(name,actor_image);row['output_present']=present\n    if present:row['capture']=capture_stopped_actor(SOURCE.name,name,actor_image,captured)\n    else:row['capture']={'capture_complete':False,'output_absent_verified':True,'not_unsupported_layout':True,'path':'/app/regex.txt','actor_image_id':actor_image}")
replace("    row['replay']=replay_capture(SOURCE.name,captured,grade,image,actor_image_id=actor_image)","    if present:row['replay']=replay_capture(SOURCE.name,captured,grade,image,actor_image_id=actor_image)\n    else:\n     docker('start',grade);docker('exec',grade,'/bin/sh','-c','test ! -e /app/regex.txt && test ! -L /app/regex.txt');row['replay']={'verified_original_output_absence':True,'rebuild_performed':False}")
replace("grade,'--network','bridge'","grade,'--network','none'")
replace('if len(events)!=4','if len(events)!=1')
replace("'Beforeactorprotectedmain.tex/synonyms.txtbaseline;stoppedinput.texonlyreplay;genericrunnerpreload/disconnectedunchanged4officialtests;no semanticrepair'","'Originalimage/stoppedregex.txtonlyorverifiedabsence;cachedpublicrunner/networkNONEthroughout/unchangedONEofficialtest;no semanticrepair'")
replace("'Originalinput.texexists;deleted/linked/unsupportedoutputorforbiddenprotectedchangesstopcapture,notcheapquality0'","'Stoppedactor/doubleidentityarchive404 verifiesabsence;freshoriginalgrade—notinferred0;directory/link/oversize/ambiguous capture unavailable'")
replace("'Samecandidate nextfixedprimaryindex5TeX/newuniform16Kprotocol;freshfour-armdevelopment,notsealedconfirmation'","'Samecandidate nextfixedprimaryindex6Regex/newuniform16Kprotocol/publicPythonALLarms/cachegrader;freshfour-armdevelopment,notsealedconfirmation'")
replace("protocol='source-backed-16k-tex-development-r2'","protocol='source-backed-16k-regex-development-v1'")
replace("'run_16k_tex_screen_r2.py','run_16k_tex_screen.py'","'run_16k_regex_screen.py','regex_output_presence.py','regex_actor_inputs.py','cached_grader_setup.py','run_16k_tex_screen_r2.py','run_16k_tex_screen.py'")
replace("    assert recipe(SOURCE.name)==plan['public_recipe']", "    assert sha(R/'regex-public-python-binding.json')==plan['public_python_binding_sha256']\n    assert recipe(SOURCE.name)==plan['public_recipe']")
code=code.replace('16k-tex-r2-plan.json','16k-regex-plan.json').replace('16k-tex-r2-result.json','16k-regex-result.json').replace('16k-tex-r2-progress.json','16k-regex-progress.json').replace("'/tmp/solpi-t16-'","'/tmp/solpi-r16-'").replace("prefix='solpi-t16-'","prefix='solpi-r16-'")
compile(code,'16k-regex-generated','exec')
if __name__=='__main__':
 assert not (R/'16k-regex-plan.json').exists(),'no actorretry/controlleroverwrite'
 exec(compile(code,'16k-regex-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
