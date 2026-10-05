"""Read-onlyexplicitstrategycontrast;NOTcausaleffect/privateanswerextraction."""
import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-mf16-7cd69b82b6a7aff8ad');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def reasoning(arm):
 out=[]
 for line in (ROOT/arm/'native.jsonl').read_text().splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  i=e.get('item',{})
  if e.get('type')=='item.completed' and i.get('type')=='reasoning':out.append(i.get('text',''))
 return out
if __name__=='__main__':
 cand=reasoning('candidate');both=reasoning('Both');assert any('Too big for the final version, but useful as a baseline' in s and 'After that, we can quantize' in s for s in cand);assert any('first measure vocab size and baseline accuracy with a config that fits' in s for s in both);assert any('First, try Plan A' in s and 'If it\'s too low' in s for s in both)
 result={'stage_plan_sha256':sha(R/'measured-feasibility-fasttext-plan.json'),'native_hashes':{arm:sha(ROOT/arm/'native.jsonl') for arm in ['candidate','Both']},'explicit_strategy_evidence':{'candidate_knew_hard_limit_and_intentionally_selected_nonconforming_baseline_then_conversion':True,'Both_selected_fitting_baseline_then_improve_if_needed':True,'candidate_missing_driver_measurement_not_full_explanation':True},'separate_official_grades':{'candidate':0,'Both':1},'hypothesis':'feasible-firstend-to-endstrategy/notcheapmeasurementalone','limits':['strategyassociationNOTcauseofgrade/token/wall','doNOTcopytaskparams/publicevalasprivategrade','avoidblanketbanonnecessarycheckedintermediateconversions','no budget/source/taskselectionchanges'],'model_calls_added':0,'promotion':False,'goal_complete':False};(R/'feasible-first-choice-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
