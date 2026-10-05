"""Existing trace only. Exact pending-repeat test and output-contract evidence."""
import pathlib,json,hashlib,re
R=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/tmp/solpi-rc16-2bf91f1a6f8f4113a5')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def events(p):
 for n,line in enumerate(p.read_text().split('\n'),1):
  if not line.strip():continue
  try:e=json.loads(line)
  except ValueError:
   assert (n==1 and line=='Reading additional input from stdin...') or re.fullmatch(r'\d{4}-\d\d-\d\dT\S+ ERROR codex_core::tools::router: error=Goal tools require a persistent thread\.',line)
   continue
  yield n,e

def main():
 pins={};arms={}
 for arm in ['candidate','Both','none','K']:
  p=ROOT/arm/'native.jsonl';pins[str(p)]=sha(p);active={};duplicates=[];overlaps=[];completed=0
  for n,e in events(p):
   i=e.get('item',{})
   if i.get('type')!='command_execution':continue
   key=i['id'];digest=hashlib.sha256(i.get('command','').encode()).hexdigest()
   if e.get('type')=='item.started':
    assert key not in active
    same=[x['id'] for x in active.values() if x['command_sha256']==digest]
    if same:duplicates.append({'event':n,'already_pending_item_ids':same})
    if active:overlaps.append({'event':n,'pending_item_ids':list(active),'exact_duplicate':bool(same)})
    active[key]={'id':key,'start_event':n,'command_sha256':digest}
   elif e.get('type')=='item.completed':
    assert key in active and active[key]['command_sha256']==digest
    del active[key];completed+=1
  arms[arm]={'completed_command_items':completed,'overlapping_native_item_starts':overlaps,'exact_command_hash_restarts_while_pending':duplicates,'items_without_native_completion_at_stop':list(active.values()),'unmatched_item_NOT_proof_process_alive':True}
 assert not any(a['exact_command_hash_restarts_while_pending'] for a in arms.values())
 data={n:e['item'] for n,e in events(ROOT/'Both/native.jsonl') if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'}
 witnesses=[]
 for n,pattern,kind in [(54,"has no attribute 'saveModel'",'unsupported_output_method'),(68,'too many values to unpack','result_selection_arity')]:
  i=data[n];assert pattern in i['aggregated_output'];assert re.search(r'(?m)^exit=1\s*$',i['aggregated_output']);assert 'echo' in i['command'] and '$?' in i['command'];assert i['exit_code']==0
  witnesses.append({'native_event':n,'kind':kind,'native_outer_exit':0,'actor_printed_inner_exit':1,'actual_exception_prevented_that_output_path':True,'inner_exit_from_actor_echo_NOT_transport_patch':True,'output_sha256':hashlib.sha256(i['aggregated_output'].encode()).hexdigest()})
 assert 'train_supervised' in data[48]['command'] and 'save_model' not in data[48]['command'] and 'saveModel' not in data[48]['command']
 prior=pathlib.Path('/tmp/solpi-mf16-7cd69b82b6a7aff8ad/Both/native.jsonl');pins[str(prior)]=sha(prior);successful=[i for _,e in events(prior) if e.get('type')=='item.completed' and (i:=e.get('item',{})).get('type')=='command_execution' and 'train_supervised' in i['command']];assert len(successful)==1 and 'save_model' in successful[0]['command']
 grade=json.loads((R/'measured-feasibility-fasttext-audit.json').read_text());assert next(x for x in grade['rows'] if x['arm']=='Both')['official_grade']==1;pins['measured-feasibility-fasttext-audit.json']=sha(R/'measured-feasibility-fasttext-audit.json');pins['recovery-context-fasttext-audit.json']=sha(R/'recovery-context-fasttext-audit.json')
 out={'read_only':True,'pending_work_review':arms,'pending_duplicate_hypothesis':'NOT_SUPPORTED by exact native command-hash overlap; modified/similar jobs or live CPU overlap not ruled out','output_contract_witnesses':witnesses,'cheap_prior_training_trial_did_NOT_exercise_output_method':True,'successful_counterexample':{'historical_measured_Both_original_grade':1,'single_completed_training_command_also_saved_model':True,'separate_preflight_NOT_necessary_for_every_success':True},'candidate_mechanism_to_review':'Conditional cheap disposable exercise of unverified downstream result-handling before expensive upstream work; distinct from resource feasibility/default choice/recovery conditions/poll duration','limits':['Original grades/costs unchanged; not a causal economy or quality proof','Echo can make outer status0 while explicit inner status1 remains visible; do not equate these','Printed inner status is actor evidence, not independently certified subcommand process status','Correcting observed interface failures does not guarantee private accuracy or a valid final artifact','No model call/probe/training/grade retry or task parameters exported'], 'source_pins':pins,'new_actor_model_POST':0,'new_training_grading':0,'promotion':False,'goal_complete':False};(R/'pending-work-output-contract-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='source_pins'},indent=2))
if __name__=='__main__':main()
