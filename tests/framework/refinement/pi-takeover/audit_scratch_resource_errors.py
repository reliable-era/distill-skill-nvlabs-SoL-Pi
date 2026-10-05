"""Bounded symptom metadata only; signals/patterns are not causal attribution."""
import pathlib,json,hashlib,re
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-sc16-696a7f783127bdae63')
def main():
 rows=[]
 for arm in ['candidate','Both','none','K']:
  p=ROOT/arm/'native.jsonl';data=p.read_bytes();ev=[]
  for l in data.decode().splitlines():
   try:ev.append(json.loads(l))
   except ValueError:pass
  cmds=[e for e in ev if e.get('item',{}).get('type')=='command_execution'];symptoms=[];limit_reads=[]
  for j,e in enumerate(cmds):
   i=e['item'];c=i.get('command','');s=i.get('aggregated_output','')
   if e.get('type')=='item.completed' and any(x in c for x in ['pids.max','cpu.max','cpu.cfs_quota','memory.max']):limit_reads.append(j)
   if e.get('type')=='item.completed' and i.get('exit_code') not in [0,None] and any(x in s for x in ['pthread_create failed','Resource temporarily unavailable']):symptoms.append({'command_event_index':j,'exit_code':i.get('exit_code'),'pthread_failure': 'pthread_create failed' in s,'resource_unavailable':'Resource temporarily unavailable' in s})
  assert symptoms;rows.append({'arm':arm,'native_sha256':hashlib.sha256(data).hexdigest(),'completed_resource_symptoms':symptoms,'explicit_limit_read_indices':limit_reads,'limit_read_precedes_first_observed_resource_symptom':bool(limit_reads) and min(limit_reads)<min(x['command_event_index'] for x in symptoms),'original_grade':0})
 out={'rows':rows,'all4_have_observed_resource_symptoms':True,'no_first_limit_read_precedes_symptom':all(not x['limit_read_precedes_first_observed_resource_symptom'] for x in rows),'limits':['Only nonzero completed commands counted; successful diagnostics and masked pipeline failures are excluded.','Matching symptoms can have multiple causes, not proof of exact PID/CPU limit exhaustion.','Explicit source patterns do not cover every implicit knowledge/read.','A later cgroup read is not proof no constraint knowledge existed earlier.','Better diagnosis/parallelism is not proven to yield correct classifier or lower complete tokens per solve.','Missing-package and API-attribute failures are separate symptoms, not resource failures.'],'new_model_POST':0,'new_actor_or_training_grading':0,'promotion':False,'goal_complete':False};(R/'scratch-resource-error-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
