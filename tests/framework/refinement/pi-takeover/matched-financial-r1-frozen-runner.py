"""Fourthfixeddevelopmenttask,newuniformbudgetnotice/dependency-onlyactorrecipe."""
import pathlib
import run_matched_pmars_panel as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('financial replacement not unique '+old[:90])
 code=code.replace(old,new)
replace("SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-pmars')","SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor')")
replace('from pmars_output_state import classify_stopped\nfrom pmars_partial_output import capture_partial,replay_partial','from financial_output import classify_stopped,capture_stopped as capture_financial,replay as replay_financial\nfrom uniform_budget_notice import add_notice')
replace('from pmars_grader_setup import prepare as prepare_grader,grade_argv','from financial_grader_setup import prepare as prepare_grader,grade_argv')
replace("def grader_options(spec):return ['-v','/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro']","def grader_options(spec):return ['-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']")
replace("def grader_inputs():return {'image_id':recipe('build-pmars')['grader_image_id'],'setup_module_sha256':sha(R/'pmars_grader_setup.py')}","def grader_inputs():return {'image_id':recipe('financial-document-processor')['grader_image_id'],'setup_module_sha256':sha(R/'financial_grader_setup.py')}")
code=code.replace('pmars-partial-grade-probe.json','financial-missing-grade-repair.json').replace('file-capture-build-pmars-result.json','file-capture-financial-document-processor-result.json')
replace("len(controls['test_results'])==4","len(controls['test_results'])==7")
replace("public=recipe(SOURCE.name);trusted_inputs=grader_inputs();assert public['actor_image_id']==trusted_inputs['image_id']","tools=json.loads((R/'public-financial-tools-draft.json').read_text());assert tools['passed'] and tools['cleanup_verified'] and tools['original_app_files_unchanged'] and tools['target_outputs_absent'];public=recipe(SOURCE.name);assert public['actor_image_id']==tools['original_actor_image_id'];public['actor_image_id']=tools['actor_image_id'];public['guidance']+='\\nGeneric public software is installed: python3,pdftotext,tesseract (English). Original /app documents unchanged;no submitted outputs prebuilt.\\n';trusted_inputs=grader_inputs();assert trusted_inputs['image_id']==tools['original_grader_image_id']")
replace("assert transfer['valid_output_replay'] and transfer['cleanup_verified']", "assert transfer['baseline']['reward']=='0' and transfer['replay']['reward']=='1' and transfer['cleanup_verified']")
# ReconstructtheSAMEprospective recipe for every pre-cellcheck,notoldbaseimage.
replace("assert recipe(SOURCE.name)==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe']", "checked_public=recipe(SOURCE.name);checked_tools=json.loads((R/'public-financial-tools-draft.json').read_text());checked_public['actor_image_id']=checked_tools['actor_image_id'];checked_public['guidance']+='\\nGeneric public software is installed: python3,pdftotext,tesseract (English). Original /app documents unchanged;no submitted outputs prebuilt.\\n';assert checked_public==plan['public_recipe'] and grader_inputs()==plan['trusted_recipe'];assert sha(R/'public-financial-tools-draft.json')==plan['public_tools_manifest_sha256']")
replace("['selected_tasks'][2]['id']","['selected_tasks'][3]['id']")
replace("'run_matched_pmars_panel.py','owned_capacity_proxy.py','private_rejection_journal.py','prospective_body_capacity.py','pmars_output_state.py','pmars_partial_output.py','pmars_grader_setup.py'","'run_matched_financial_panel.py','run_matched_pmars_panel.py','run_matched_cython_panel.py','run_matched_html_panel.py','uniform_budget_notice.py','financial_output.py','financial_grader_setup.py','prepare_financial_actor_tools.py','owned_capacity_proxy.py','private_rejection_journal.py','prospective_body_capacity.py'")
replace("protocol='matched-pmars-capacity-v2'","protocol='matched-financial-budget-capacity-v3-preflight-r1'")
replace("'New four-arm third-fixed-task PMARS development panel;not representative confirmation'","'New four-arm fourth-fixed-task financial development panel;not representative confirmation'")
replace("'grading_policy':'Original trusted image;binary+Debian source or verified source-only absence;trusted public software preload then network-disconnected unchanged officialscript;never build target'","'grading_policy':'Original trusted image;three exact directories or verifiedabsence;public runner/pandas preload thennetwork-disconnected unchanged7officialtests;neverrepairoutputs'")
replace("assert image==public['actor_image_id']==trusted_inputs['image_id']","assert image==trusted_inputs['image_id'];actor_image=public['actor_image_id'];plan.update(actor_image_id=actor_image,public_tools_manifest_sha256=sha(R/'public-financial-tools-draft.json'),uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'])")
# Important:additionalplanfieldsmustbeboundBEFORE digest/write,not after.
replace("assert image==trusted_inputs['image_id'];actor_image=public['actor_image_id'];plan.update(actor_image_id=actor_image,public_tools_manifest_sha256=sha(R/'public-financial-tools-draft.json'),uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'])","assert image==trusted_inputs['image_id'];actor_image=public['actor_image_id']")
replace(" plan.update(capacity_protocol_sha256=", " plan.update(actor_image_id=public['actor_image_id'],public_tools_manifest_sha256=sha(R/'public-financial-tools-draft.json'),uniform_budget_notice_sha256=sha(R/'uniform_budget_notice.py'),historical_transfer_controller_gate=transfer['valid_output_replay'],historical_transfer_official_reward=transfer['replay']['reward'])\n plan.update(capacity_protocol_sha256=")
replace("root=pathlib.Path('/tmp/solpi-mp-'+digest[:20])","root=pathlib.Path('/tmp/solpi-mf-'+digest[:20])")
replace("prefix='solpi-tpp-'+uuid.uuid4().hex[:10]","prefix='solpi-tfp-'+uuid.uuid4().hex[:10]")
replace("prompt=(SOURCE/'instruction.md').read_text()+'\\n\\n'+public['guidance']+'\\n\\nUse supplied skills in /skills. No subagents,compaction,web retrieval or external solutions. Work in /app.\\n'+''.join('\\n'+(D/'frozen'/k/'SKILL.md').read_text() for k in keys)","prompt=add_notice((SOURCE/'instruction.md').read_text(),public['guidance'],[(D/'frozen'/k/'SKILL.md').read_text() for k in keys])")
replace("docker(*args,image,'-c'","docker(*args,actor_image,'-c'")
start=code.index("    captured=d/'captured';state=classify_stopped(name,image)");end=code.index("    grade=prefix+'-grade-'+arm",start)
code=code[:start]+"    captured=d/'captured';state=classify_stopped(name,actor_image);row['output_classification']=state;row['output_present']=all(s['state']=='directory' for s in state['paths'].values());row['capture']=capture_financial(name,actor_image,captured)\n"+code[end:]
start=code.index("    if present:",code.index("    grade=prefix+'-grade-'+arm"));end=code.index("    row['dependency_setup']=",start)
code=code[:start]+"    row['replay']=replay_financial(captured,grade,image,actor_image_id=actor_image)\n"+code[end:]
replace("if len(events)!=4","if len(events)!=7")
code=code.replace('matched-pmars-plan.json','matched-financial-plan.json').replace('matched-pmars-progress.json','matched-financial-progress.json').replace('matched-pmars-result.json','matched-financial-result.json')
compile(code,'matched-financial-generated','exec')
if __name__=='__main__':exec(compile(code,'matched-financial-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
