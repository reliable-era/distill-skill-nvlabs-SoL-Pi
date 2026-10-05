"""One newcandidate hypothesis;reuse readytask/transport,notpreviousoutcomes."""
import pathlib
import run_matched_financial_panel as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('source-backed replacement notunique '+old[:80])
 code=code.replace(old,new)
replace("D=R.parent/'development/pi-takeover-qwen-incremental-coverage'","D=R.parent/'development/pi-takeover-qwen-source-backed-verification'")
replace("'run_matched_financial_panel.py','run_matched_pmars_panel.py'","'run_source_backed_financial_screen.py','run_matched_financial_panel.py','run_matched_pmars_panel.py'")
replace("protocol='matched-financial-budget-capacity-v3-preflight-r2'","protocol='source-backed-financial-development-v1'")
replace("'New four-arm fourth-fixed-task financial development panel;not representative confirmation'","'Single source-backed-verification hypothesis on explicitlyexposed financialdevelopmenttask;freshfour-arm cohort,notsealedconfirmation'")
replace("root=pathlib.Path('/tmp/solpi-mf-'+digest[:20])","root=pathlib.Path('/tmp/solpi-sbf-'+digest[:18])")
replace("prefix='solpi-tfp-'+uuid.uuid4().hex[:10]","prefix='solpi-sbf-'+uuid.uuid4().hex[:10]")
replace(" plan.update(cpus=public['cpus'],memory_mb=public['memory_mb'],actor_image_id=public['actor_image_id']", " freeze=json.loads((D/'freeze-manifest.json').read_text());assert freeze['candidate_sha256']==sha(D/'frozen/candidate/SKILL.md');assert freeze['runtime_hashes']==plan['runtime_hashes'] and freeze['frozen_manifest']==W.files(D/'frozen')\n plan.update(new_candidate_freeze_sha256=sha(D/'freeze-manifest.json'),comparator_Both_definition=freeze['comparator_Both_definition'],previous_candidate_rejected=True,previous_model_outcomes_not_reused=True)\n plan.update(cpus=public['cpus'],memory_mb=public['memory_mb'],actor_image_id=public['actor_image_id']")
replace("    assert W.files(D/'frozen')", "    assert sha(D/'freeze-manifest.json')==plan['new_candidate_freeze_sha256']\n    assert W.files(D/'frozen')")
code=code.replace('matched-financial-plan.json','source-backed-financial-plan.json').replace('matched-financial-progress.json','source-backed-financial-progress.json').replace('matched-financial-result.json','source-backed-financial-result.json')
compile(code,'source-backed-financial-generated','exec')
if __name__=='__main__':exec(compile(code,'source-backed-financial-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
