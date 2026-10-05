"""Samefrozencandidate,nextfixedprimarytask;new task-specificcapture/originalgrade."""
import pathlib
import run_source_backed_financial_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('Doomreplacementnotunique '+old[:80])
 code=code.replace(old,new)
replace("SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor')","SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/make-doom-for-mips')")
replace('from financial_output import classify_stopped,capture_stopped as capture_financial,replay as replay_financial','from doom_output import classify_stopped,capture_missing,replay_missing')
replace('from financial_grader_setup import prepare as prepare_grader,grade_argv','from doom_grader_setup import prepare as prepare_grader,grade_argv')
replace("def grader_inputs():return {'image_id':recipe('financial-document-processor')['grader_image_id'],'setup_module_sha256':sha(R/'financial_grader_setup.py')}","def grader_inputs():return {'image_id':recipe('make-doom-for-mips')['grader_image_id'],'setup_module_sha256':sha(R/'doom_grader_setup.py')}")
code=code.replace('financial-missing-grade-repair.json','doom-missing-probe.json').replace('file-capture-financial-document-processor-result.json','file-capture-make-doom-for-mips-result.json').replace('public-financial-tools-draft.json','doom-dependency-actor-image.json')
replace("len(controls['test_results'])==7","len(controls['test_results'])==3")
line=next(l for l in code.splitlines() if l.startswith(' tools=json.loads'))
replace(line," tools=json.loads((R/'doom-dependency-actor-image.json').read_text());assert tools['prepared'] and tools['cleanup_verified'] and tools['app_source_inputs_unchanged'] and tools['target_binary_absent'];public=recipe(SOURCE.name);trusted_inputs=grader_inputs();assert public['actor_image_id']==tools['prepared_actor_image_id'] and trusted_inputs['image_id']==tools['base_image_id']")
line=next(l for l in code.splitlines() if 'checked_public=recipe' in l)
replace(line,"    assert recipe(SOURCE.name)==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe'];assert sha(R/'doom-dependency-actor-image.json')==plan['public_tools_manifest_sha256']")
replace("['selected_tasks'][3]['id']","['selected_tasks'][4]['id']")
replace("'run_source_backed_financial_screen.py','run_matched_financial_panel.py'","'run_source_backed_doom_screen.py','run_source_backed_financial_screen.py','run_matched_financial_panel.py'")
replace("'financial_output.py','financial_grader_setup.py','prepare_financial_actor_tools.py'","'doom_output.py','doom_grader_setup.py'")
replace("protocol='source-backed-financial-development-v1'","protocol='source-backed-doom-development-v1'")
replace("'Single source-backed-verification hypothesis on explicitlyexposed financialdevelopmenttask;freshfour-arm cohort,notsealedconfirmation'","'Samefrozencandidate nextfixedprimaryindex4Doomgeneralization;freshfour-armdevelopment,notsealedconfirmation'")
replace("'grading_policy':'Original trusted image;three exact directories or verifiedabsence;public runner/pandas preload thennetwork-disconnected unchanged7officialtests;neverrepairoutputs'","'grading_policy':'Original trustedVM/WAD;binary-onlyoutputorverifiedabsence plusnonreplayedinputwitnesses;publicrunner/numpy/pillowpreload thendisconnectedunchanged3officialtests;no rebuild'")
replace("historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward']", "historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'],trusted_vm_sha256=controls['original_vm_sha256'],trusted_wad_sha256=controls['capture']['artifacts']['/app/doom.wad']['sha256']")
replace("root=pathlib.Path('/tmp/solpi-sbf-'+digest[:18])","root=pathlib.Path('/tmp/solpi-sbd-'+digest[:18])")
replace("prefix='solpi-sbf-'+uuid.uuid4().hex[:10]","prefix='solpi-sbd-'+uuid.uuid4().hex[:10]")
replace("captured=d/'captured';state=classify_stopped(name,actor_image);row['output_classification']=state;row['output_present']=all(s['state']=='directory' for s in state['paths'].values());row['capture']=capture_financial(name,actor_image,captured)","captured=d/'captured';state=classify_stopped(name,actor_image);row['output_classification']=state;row['output_present']=state['output_state']=='present'\n    if row['output_present']:row['capture']=capture_stopped_actor(SOURCE.name,name,actor_image,captured)\n    else:row['capture']=capture_missing(name,actor_image,captured)")
replace("row['replay']=replay_financial(captured,grade,image,actor_image_id=actor_image)","if row['output_present']:row['replay']=replay_capture(SOURCE.name,captured,grade,image,actor_image_id=actor_image)\n    else:row['replay']=replay_missing(captured,grade,image,actor_image_id=actor_image)\n    original_hashes=docker('exec',grade,'sha256sum','/app/vm.js','/app/doom.wad').splitlines();assert [line.split()[0] for line in original_hashes]==[plan['trusted_vm_sha256'],plan['trusted_wad_sha256']];row['original_vm_wad_verified']=True")
replace('if len(events)!=7','if len(events)!=3')
code=code.replace('source-backed-financial-plan.json','source-backed-doom-plan.json').replace('source-backed-financial-progress.json','source-backed-doom-progress.json').replace('source-backed-financial-result.json','source-backed-doom-result.json')
compile(code,'source-backed-doom-generated','exec')
if __name__=='__main__':exec(compile(code,'source-backed-doom-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
