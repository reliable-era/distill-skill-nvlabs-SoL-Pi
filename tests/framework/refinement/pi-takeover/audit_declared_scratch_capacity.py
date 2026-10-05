"""Changed read-only question: scratch mount capacity vs filesystem-limit hypothesis."""
import pathlib,json,hashlib,re
from run_documented_baseline_fasttext_screen import code
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-db16-703569da7d9b953094')
def main():
 pre=json.loads((R/'documented-baseline-fasttext-prelaunch.json').read_text());assert hashlib.sha256(code.encode()).hexdigest()==pre['generated_controller_sha256'];assert "'--tmpfs','/tmp:rw,size=128m'" in code;plan=json.loads((R/'documented-baseline-fasttext-plan.json').read_text());rows=[]
 for arm in plan['schedule']:
  p=ROOT/arm/'native.jsonl';data=p.read_bytes();ev=[]
  for l in data.decode().splitlines():
   try:ev.append(json.loads(l))
   except ValueError:pass
  commands=[e for e in ev if e.get('item',{}).get('type')=='command_execution'];started=[e['item'].get('command','') for e in commands if e.get('type')=='item.started'];complete=[e['item'].get('aggregated_output','') for e in commands if e.get('type')=='item.completed'];rows.append({'arm':arm,'native_sha256':hashlib.sha256(data).hexdigest(),'model_save_to_tmp_declared':any(re.search(r"save_model\(['\"]/?tmp/|p=f?['\"]/tmp/",c) for c in started),'reported_128MiB_temporary_file':any('134217728' in s and '/tmp/' in s for s in complete),'df_app_but_no_matched_df_tmp':any('df -h /app' in c for c in started) and not any(re.search(r'df[^\n;]* /tmp',c) for c in started),'explicit_cgroup_limit_reads':any(re.search(r'cpu.max|cpu.cfs_quota|pids.max|memory.max',c) for c in started),'literal_no_space_error_retained':any('No space left on device' in s for s in complete)})
 out={'generated_controller_sha256':pre['generated_controller_sha256'],'declared_actor_scratch_mount':'tmpfs /tmp rw size=128m','declared_capacity_bytes':134217728,'selected_CPU':plan['cpus'],'selected_memory_MiB':plan['memory_mb'],'resource_notice_does_not_disclose_scratch_capacity':True,'rows':rows,'interpretation':'Different from RLIMIT_FSIZE: frozen create command declares bounded scratch mount. Size coincidence + destination is consistent with capacity pressure, not independent proof of exact errno or full causal chain.','limitations':['No actor recreation, training, filesystem probe or post-deletion target repair.','No live mount/df snapshot retained; source specifies creation configuration, not measured filesystem occupancy.','No inference that selecting another directory/concurrency ensures original accuracy or solve economy.','Task parameters/answers are not transferred into skill/cache.'],'new_model_POST':0,'new_actor_training_grading':0,'promotion':False,'goal_complete':False};(R/'declared-scratch-capacity-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
