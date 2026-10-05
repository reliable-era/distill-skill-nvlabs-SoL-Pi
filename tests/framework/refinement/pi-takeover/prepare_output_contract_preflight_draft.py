"""One portable unscored output-contract preflight clause; no runtime/actor."""
import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parent
PARENT=R.parent/'candidates/coalesced-verification/efficient-coding/SKILL.md'
CANDIDATE=R.parent/'candidates/output-contract-preflight/efficient-coding/SKILL.md'
CLAUSE='Before expensive upstream work, cheaply exercise unverified result-handling steps with disposable inputs; dependency imports alone do not verify the output contract.'
ANCHOR='For irreversible actions, check the required safeguards first; do not weaken final acceptance or verification.'
def draft(text):
 assert text.count(ANCHOR)==1 and CLAUSE not in text
 return text.replace(ANCHOR,CLAUSE+' '+ANCHOR)
def main():
 parent=PARENT.read_text();assert hashlib.sha256(PARENT.read_bytes()).hexdigest()=='cff132600efdd10e64ec47283e164be66c0992ce1d610ce442f6715a705aad87';text=draft(parent)
 assert text.replace(CLAUSE+' ','')==parent
 evidence=json.loads((R/'pending-work-output-contract-audit.json').read_text());assert len(evidence['output_contract_witnesses'])==2 and evidence['new_actor_model_POST']==0
 CANDIDATE.parent.mkdir(parents=True,exist_ok=True);CANDIDATE.write_text(text)
 manifest={'candidate_sha256':hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),'parent_sha256':hashlib.sha256(PARENT.read_bytes()).hexdigest(),'changed_bullet':'reversible end-to-end behavior bullet only','clause':CLAUSE,'parent_words':len(parent.split()),'candidate_words':len(text.split()),'evidence_sha256':hashlib.sha256((R/'pending-work-output-contract-audit.json').read_bytes()).hexdigest(),'counterexample':'historical passing Both saved successfully without separate preflight','mechanism':'conditional cheap downstream output-contract exercise, not resource measurement/defaults/polling/recovery environment retention','unfrozen':True,'unscored':True,'new_actor_model_POST':0,'no_runtime_change':True,'no_task_parameters_answers_paths_or_API_names':True,'promotion':False,'goal_complete':False}
 (R/'output-contract-preflight-draft.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
