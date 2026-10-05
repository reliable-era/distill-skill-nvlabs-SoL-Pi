"""Samecandidate,nextfixedTeXtask/fresh16Kprotocol;no old outcomes borrowed."""
import pathlib
import run_source_backed_doom_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('TeXreplacementnotunique '+old[:80])
 code=code.replace(old,new)
code=code.replace('pi-takeover-qwen-source-backed-verification','pi-takeover-qwen-source-backed-16k').replace('make-doom-for-mips','overfull-hbox')
replace('from matched_html_support import PanelSession,verify_live_sources,stopped_output_present,PEER','from budget_panel import PanelSession,verify_live_sources,stopped_output_present,PEER')
replace('from doom_output import classify_stopped,capture_missing,replay_missing','from tex_protected_baseline import capture_before,compare_original')
replace('from doom_grader_setup import prepare as prepare_grader,grade_argv','from tex_grader_setup import prepare as prepare_grader,grade_argv')
code=code.replace('doom_grader_setup.py','tex_grader_setup.py').replace('doom_output.py','tex_protected_baseline.py').replace('doom-missing-probe.json','tex-wiring-probe.json')
replace("len(controls['test_results'])==3","len(controls['collected_original_tests'])==4")
replace("['selected_tasks'][4]['id']","['selected_tasks'][5]['id']")
line=next(l for l in code.splitlines() if l.startswith(' tools=json.loads'));replace(line," public=recipe(SOURCE.name);trusted_inputs=grader_inputs()")
replace("assert {t['name'] for t in transfer['replay']['tests']}=={t['name'] for t in controls['test_results']}","assert {t['name'] for t in transfer['replay']['tests']}==set(controls['collected_original_tests'])")
replace("prior=json.loads((D/'plan.json').read_text())","prior=json.loads((R/'source-backed-doom-plan.json').read_text())")
replace("sha(D/'plan.json')","sha(R/'source-backed-doom-plan.json')")
line=next(l for l in code.splitlines() if "plan.update(cpus=public['cpus']" in l);replace(line," plan.update(cpus=public['cpus'],memory_mb=public['memory_mb'],actor_image_id=public['actor_image_id'],uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'],configured_output_cap=16384,arm_recipe=freeze['arm_recipe'],protected_inputs_original=transfer['protected_before'],native16k_gate_sha256=sha(R/'16k-native-probe.json'));assert freeze['arm_recipe']==W.ARMS and freeze['comparator_Both_definition']=='currentcandidate+frozenKarpathy';assert json.loads((R/'16k-native-probe.json').read_text())['passed']")
line=next(l for l in code.splitlines() if 'assert recipe(SOURCE.name)' in l);replace(line,"    assert recipe(SOURCE.name)==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe'];assert W.ARMS==plan['arm_recipe']")
replace("'run_source_backed_doom_screen.py','run_source_backed_financial_screen.py'","'run_16k_tex_screen.py','run_source_backed_doom_screen.py','run_source_backed_financial_screen.py'")
replace("'tex_protected_baseline.py','tex_grader_setup.py'","'tex_protected_baseline.py','tex_grader_setup.py','financial_grader_setup.py','audit_skill_delivery.py'")
replace("protocol='source-backed-doom-development-v1'","protocol='source-backed-16k-tex-development-v1'")
replace("'Samefrozencandidate nextfixedprimaryindex4Doomgeneralization;freshfour-armdevelopment,notsealedconfirmation'","'Samecandidate nextfixedprimaryindex5TeX/newuniform16Kprotocol;freshfour-armdevelopment,notsealedconfirmation'")
replace("'grading_policy':'Original trustedVM/WAD;binary-onlyoutputorverifiedabsence plusnonreplayedinputwitnesses;publicrunner/numpy/pillowpreload thendisconnectedunchanged3officialtests;no rebuild'","'grading_policy':'Beforeactorprotectedmain.tex/synonyms.txtbaseline;stoppedinput.texonlyreplay;genericrunnerpreload/disconnectedunchanged4officialtests;no semanticrepair'")
replace("missing_output_policy='Independently verified stopped actor plus archive404 means output absent;grade original baseline;unsupported capture stops,not quality failure'","missing_output_policy='Originalinput.texexists;deleted/linked/unsupportedoutputorforbiddenprotectedchangesstopcapture,notcheapquality0'")
replace("(d/'prompt.txt').write_text(prompt)","(d/'prompt.txt').write_text(prompt);assert W.files(d/'skills')=={n:h for n,h in plan['frozen_skills_manifest'].items() if n.split('/')[0] in keys};assert all(prompt.count((D/'frozen'/k/'SKILL.md').read_text())==1 for k in keys)")
replace("    row={'arm':arm};start=time.monotonic()","    baseline=capture_before(name,actor_image,d/'before');compare_original(baseline,transfer)\n    row={'arm':arm,'protected_before':baseline};start=time.monotonic()")
start=code.index("    captured=d/'captured';state=classify_stopped");end=code.index("    grade=prefix+'-grade-'",start);code=code[:start]+"    captured=d/'captured';row['capture']=capture_stopped_actor(SOURCE.name,name,actor_image,captured,protected_baseline=baseline['protected_baseline']);assert row['capture']['protected_input_gate_passed']\n"+code[end:]
start=code.index("    if row['output_present']:row['replay']");end=code.index("    row['dependency_setup']",start);code=code[:start]+"    row['replay']=replay_capture(SOURCE.name,captured,grade,image,actor_image_id=actor_image)\n"+code[end:]
code=code.replace('if len(events)!=3','if len(events)!=4').replace('source-backed-doom-progress.json','16k-tex-progress.json').replace('source-backed-doom-result.json','16k-tex-result.json')
replace("(R/'source-backed-doom-plan.json').write_text","(R/'16k-tex-plan.json').write_text")
replace("digest=sha(R/'source-backed-doom-plan.json')","digest=sha(R/'16k-tex-plan.json')")
replace("root=pathlib.Path('/tmp/solpi-sbd-'+digest[:18])","root=pathlib.Path('/tmp/solpi-t16-'+digest[:18])");replace("prefix='solpi-sbd-'+uuid.uuid4().hex[:10]","prefix='solpi-t16-'+uuid.uuid4().hex[:10]")
compile(code,'16k-tex-generated','exec')
if __name__=='__main__':exec(compile(code,'16k-tex-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
