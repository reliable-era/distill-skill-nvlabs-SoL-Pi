"""Same independentaudit,newcohortpaths/runtime/freeze;no model/controlrerun."""
import pathlib
R=pathlib.Path(__file__).resolve().parent
code=(R/'audit_matched_financial.py').read_text()
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('auditreplacementnotunique '+old[:75])
 code=code.replace(old,new)
code=code.replace('matched-financial-plan.json','source-backed-financial-plan.json').replace('matched-financial-result.json','source-backed-financial-result.json').replace('matched-financial-progress.json','source-backed-financial-progress.json').replace('matched-financial-audit.json','source-backed-financial-audit.json')
replace("root=pathlib.Path('/tmp/solpi-mf-'+digest[:20])","root=pathlib.Path('/tmp/solpi-sbf-'+digest[:18])")
replace("runtime=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime'","runtime=R.parent/'development/pi-takeover-qwen-source-backed-verification/runtime'")
replace("ledger=json.loads((root/'transport/ledger.json').read_text())", "freeze_path=runtime.parent/'freeze-manifest.json';assert sha(freeze_path)==plan['new_candidate_freeze_sha256'];freeze=json.loads(freeze_path.read_text());assert freeze['candidate_sha256']==plan['candidate_sha256']==sha(runtime.parent/'frozen/candidate/SKILL.md');assert plan['previous_candidate_rejected'] and plan['previous_model_outcomes_not_reused'];assert plan['comparator_Both_definition']==freeze['comparator_Both_definition'];ledger=json.loads((root/'transport/ledger.json').read_text())")
replace("cap=verify(root/arm/'captured',plan['actor_image_id']);", "cap=verify(root/arm/'captured',plan['actor_image_id']);from collections import Counter;inputs=json.loads((R/'public-financial-tools-draft.json').read_text())['app_file_manifest'];original_ids=Counter((pathlib.PurePosixPath(p).name,r['bytes'],r['sha256']) for p,r in inputs.items());moved_ids=Counter((pathlib.PurePosixPath(p).name,r['bytes'],r['sha256']) for folder,rec in cap['artifacts'].items() if folder!='/app/documents' for p,r in rec.get('files',{}).items() if not(folder=='/app/invoices' and p=='summary.csv'));source_observation={'original_inputs':sum(original_ids.values()),'original_identities_preserved_once':all(moved_ids[k]==v for k,v in original_ids.items()),'output_documents':sum(moved_ids.values()),'remaining_documents':len(cap['artifacts']['/app/documents'].get('files',{})),'official_grade_not_reinterpreted':True};")
replace("'directory_states':", "'source_identity_observation':source_observation,'directory_states':")
code=code.replace('name=solpi-tfp','name=solpi-sbf')
compile(code,'source-backed-financial-audit','exec')
if __name__=='__main__':exec(compile(code,'source-backed-financial-audit','exec'),{'__name__':'__main__','__file__':str(__file__)})
