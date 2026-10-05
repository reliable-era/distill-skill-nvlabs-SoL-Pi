"""Read-onlyexistingpublicinstruction/native/request chronology;no actor/privategrade repair."""
import pathlib,json,hashlib,re
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-bb16-ece5d6219354bfddd1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 p=ROOT/'candidate/native.jsonl';native=[];malformed=0;reasons=[]
 for line in p.read_text().splitlines():
  try:e=json.loads(line)
  except ValueError:malformed+=1;continue
  i=e.get('item',{})
  if e.get('type')=='item.completed' and i.get('type')=='command_execution':native.append(i)
  if e.get('type')=='item.completed' and i.get('type')=='reasoning':reasons.append(i.get('text',''))
 train=next(i for i in native if 'train_supervised(' in i.get('command',''));measure=next(i for i in native if 'from collections import Counter' in i.get('command',''));assert native.index(train)<native.index(measure);assert '180281405' in train['aggregated_output'];assert any('0.61' in i.get('aggregated_output','') and 'm.test(' in i.get('command','') for i in native);assert any('No wait, to save time' in text and 'full dataset' in text for text in reasons);assert any('vocab is about 150k' in text for text in reasons)
 qpath=ROOT/'transport/request-15.json';q=json.loads(qpath.read_text());waits=[];measurement_wait=None
 for i in q['input']:
  if i.get('type')!='function_call_output':continue
  s=i['output'];w=re.search(r'Wall time: ([0-9.]+)',s)
  if 'session ID 25151' in s or ('Original token count: 68447' in s):waits.append(float(w[1]))
  if 'minCount>=2: 458930' in s:measurement_wait=float(w[1])
 # Nativeaggregate273786 impliesproducerestimate68447;thisisNOTQwentokens.
 assert measurement_wait==12.8424;assert len(waits)==4
 instruction=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/train-fasttext/instruction.md');header=json.loads((ROOT/'candidate/capture-rejections.json').read_text())[0];out={'native_sha256':sha(p),'request15_sha256':sha(qpath),'public_instruction_sha256':sha(instruction),'native_malformed_nonJSON_lines':malformed,'sequence_evidence':{'public_size_and_private_accuracy_constraints_known_before_training':True,'pretrain_size_driver_used_guessed_vocabulary_not_measurement':True,'small_pipeline_smoke_explicitly_skipped':True,'first_full_training_before_cheap_driver_measurement':True,'first_training_reported_tool_waits_NOT_CPU_time':waits,'first_training_reported_wait_sum_seconds':sum(waits),'cheap_later_measurement_tool_seconds':measurement_wait,'saved_file_declared_bytes':header['declared_size'],'public_eval_accuracy':.61,'private_original_grade':'UNAVAILABLE_NOT_INFERRED_FROM_PUBLIC_ACCURACY','second_training_started_but_not_completed_at_stop':True},'hypothesis':'measure cheap uncertain feasibility driver BEFORE expensive work;notmore genericconstraintreminders/alreadyrecognized','limits':['no private test contents/accuracy inference','no causal CPU/time/token benefit proved','no size-boundincrease/repair/retraining/actorretry','no task-specific formulas/parameters transfer toskill'],'real_model_POST_added':0,'goal_complete':False};(R/'byte-bounded-feasibility-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
