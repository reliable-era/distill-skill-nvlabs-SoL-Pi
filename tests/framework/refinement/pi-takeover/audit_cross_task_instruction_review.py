"""Bounded existing-trace review; metadata only, no trials or grade reinterpretation."""
import pathlib,json,hashlib,re,shlex
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def commands(p):
 out=[];ignored=[]
 for n,line in enumerate(p.read_text().split('\n'),1):
  if not line.strip():continue
  try:e=json.loads(line)
  except ValueError:ignored.append(n);continue
  i=e.get('item',{})
  if e.get('type')=='item.completed' and i.get('type')=='command_execution':out.append((n,i))
 return out,ignored

def main():
 pins={};profiles={}
 roots={'sparql':'/tmp/solpi-bs16-97c98798a00417f997','financial':'/tmp/solpi-sbf-4cea54e5b8829ceddc'}
 for task,root in roots.items():
  profiles[task]={}
  for arm in ['candidate','none']:
   p=pathlib.Path(root)/arm/'native.jsonl';items,ignored=commands(p);assert items;assert ignored==[1];pins[str(p)]=sha(p)
   profiles[task][arm]={'completed_commands':len(items),'nonzero_completed_commands':sum(i.get('exit_code')!=0 for _,i in items),'ignored_non_JSON_lines':ignored,'events':[{'line':n,'command_sha256':hashlib.sha256(i['command'].encode()).hexdigest(),'exit_code':i.get('exit_code'),'native_output_bytes_NOT_model_tokens':len(i.get('aggregated_output','').encode())} for n,i in items]}
 qroot=pathlib.Path(roots['sparql']);items,_=commands(qroot/'candidate/native.jsonl');d=dict(items);assert all(d[n]['exit_code']==0 for n in [16,20,24]);script=shlex.split(d[16]['command'])[2];m=re.search(r"<<'?EOF'?\n(.*?)\nEOF",script,re.S);assert m;initial_hash=hashlib.sha256((m[1]+'\n').encode()).hexdigest();payload=qroot/'candidate/captured/payload-0';assert initial_hash==sha(payload);pins[str(payload)]=sha(payload)
 assert 'cat /app/solution.sparql' in d[24]['command'] and "open('/app/solution.sparql').read()" in d[24]['command'];assert "open('/app/solution.sparql').read()" in d[16]['command'];assert not any(x in d[20]['command'] for x in ['cat >','write(','mv ','rm '])
 parent=R.parent/'candidates/coalesced-verification/efficient-coding/SKILL.md';text=parent.read_text();assert 'Do not add a separate artifact dump or repeat a successful check just to prepare the final report' in text;pins[str(parent)]=sha(parent)
 for name in ['behavior-first-sparql-audit.json','source-backed-financial-audit.json','recovery-context-fasttext-audit.json']:
  pins[name]=sha(R/name)
 financial=json.loads((R/'source-backed-financial-audit.json').read_text());sparql=json.loads((R/'behavior-first-sparql-audit.json').read_text())
 assert all(x['solved'] and x['official_reward']=='1' and x['provider_cost_complete'] for x in financial['rows'] if x['arm'] in ['candidate','none'])
 assert {x['arm'] for x in financial['rows']}=={'candidate','Both','none','K'}
 assert all(x['solved'] for x in sparql['rows'])
 out={'read_only':True,'trace_profiles_SEPARATE_COHORTS':profiles,'sparql_repeat':{'first_successful_run_event':16,'distinct_diagnostic_event_NOT_redundant_by_default':20,'later_dump_and_rerun_event':24,'first_write_equals_final_captured_hash':initial_hash,'observed_intermediate_command_read_only':True,'global_ambient_state_unchanged_proven':False,'possible_avoidable_repeat_not_causal_cost_proof':True},'financial_counterexample':{'candidate_completed_commands':profiles['financial']['candidate']['completed_commands'],'none_completed_commands':profiles['financial']['none']['completed_commands'],'both_originally_solved':True,'candidate_successful_mutation_with_checks_then_stop':True,'none_additional_reads_and_failed_image_helper_NOT_proven_unnecessary':True},'decision':'Observed repeat already addressed by coalesced verification clause. Reject duplicate clause and blanket removal of independent checks. No materially different successor established by this review.','limits':['Different candidates/tasks not pooled or treated as randomized mechanism comparison','Original passing grades retained, not reinterpreted','Static bytes/native outputs/command counts not model tokens or marginal causal costs','Prompt delivery not adherence or effectiveness','No private answers/parameters/source payload exported into a skill','Recent zero-solve fastText cohorts do not test every consequence of the SPARQL repeat rule'], 'artifact_hashes':pins,'new_actor_model_POST':0,'new_training_grading':0,'promotion':False,'goal_complete':False};(R/'cross-task-instruction-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='artifact_hashes'},indent=2))
if __name__=='__main__':main()
