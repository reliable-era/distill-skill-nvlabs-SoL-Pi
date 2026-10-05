"""Read-only recovery ordering; similar operations are not controlled identical trials."""
import pathlib,json,hashlib,re
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-sc16-696a7f783127bdae63')
def main():
 p=ROOT/'Both/native.jsonl';data=p.read_bytes();ev=[]
 for l in data.decode().splitlines():
  try:ev.append(json.loads(l))
  except ValueError:pass
 rows=[]
 for j,e in enumerate(ev):
  i=e.get('item',{});c=i.get('command','')
  if e.get('type')!='item.completed' or i.get('type')!='command_execution' or 'pd.read_parquet' not in c:continue
  rows.append({'native_event_index':j,'operation_family':'pandas_parquet_read','command_environment_control_present':bool(re.search(r'\bOMP_NUM_THREADS=\d+',c)),'exit_code':i.get('exit_code'),'resource_unavailable_reported':'Resource temporarily unavailable' in i.get('aggregated_output','')})
 pattern=[(x['command_environment_control_present'],x['exit_code'],x['resource_unavailable_reported']) for x in rows];assert pattern==[(False,134,True),(False,134,True),(True,0,False),(False,134,True),(True,0,False)]
 out={'plan_sha256':hashlib.sha256((R/'scratch-capacity-fasttext-plan.json').read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(data).hexdigest(),'rows':rows,'observed_recovery_then_uncontrolled_followup_failure_then_recovery':True,'scope':'explicit per-command conditions/similar parquet operations; not global env or controlled causal experiment','limitations':['Commands differ in selected data and requested observations.','A successful controlled-command condition is not proof that condition alone caused recovery.','Other resource/active-process conditions were not experimentally held constant.','No causal dollar/token saving, exact exhaustion cause, private accuracy or verified solve inferred.','Source declaration of an environment setting is not independent ambient-environment inspection.'],'training_parameter_values_exported':False,'new_model_POST':0,'new_actor_training_grading':0,'promotion':False,'goal_complete':False};(R/'recovery-condition-retention-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
