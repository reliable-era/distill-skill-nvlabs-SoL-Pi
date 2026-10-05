"""Newinertlineage;scope-boundouterfailurecleanup;NOscoringexecution."""
import pathlib,json,hashlib,ast
import prepare_failure_safe_fasttext_controller_r2 as base
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def materialize():
 code=base.materialize()
 def replace(old,new):
  nonlocal code
  assert code.count(old)==1,old[:90];code=code.replace(old,new)
 replace('from prospective_controller_cell import run_cell,persist','from prospective_controller_cell import run_cell,persist\nfrom prospective_owned_epoch import stop as stop_epoch,finish_failure')
 replace('    for arm in arms:\n','    for arm in arms:\n     actor_context=None;row=None;name=None\n')
 replace("     session.begin(arm,idle(d/'idle.json'));", "     row={'arm':arm,'official_grade_available':False,'native_completed_usage':None,'phase':'before_native_creation'};rows.append(row);persist(d/'partial-row.json',row)\n     session.begin(arm,idle(d/'idle.json'));")
 replace("     args=['create'", "     actor_context={'arm':arm,'deadline':session.deadline,'name':name,'image':actor_image,'container_id':None,'row':row,'path':d/'partial-row.json'}\n     args=['create'")
 old="verify_actor_inspect(inspect,public,net,{'/skills':str(d/'skills'),'/opt/solpi/codex':str(BINARY)})"
 replace(old,old+";assert inspect['Image']==actor_image;actor_context['container_id']=inspect['Id']")
 replace("     row={'arm':arm,'official_grade_available':False,'native_completed_usage':None};rows.append(row);persist(d/'partial-row.json',row);admission_mark=", "     admission_mark=")
 old="""     def stop_owned_issuer():
      docker('stop','-t','0',name)
      metadata=json.loads(docker('inspect',name))[0]
      return metadata['Image']==actor_image and not metadata['State']['Running'] and not metadata['State'].get('Paused')"""
 replace(old,"     def stop_owned_issuer():return stop_epoch(session,actor_context,docker,owned)")
 first=code.index('   if session and session.active is not None:');end=code.index('   proxy_journal=None',first)
 code=code[:first]+"   if session and session.active is not None:\n    finish_failure(session,actor_context if 'actor_context' in globals() else None,docker,owned)\n"+code[end:]
 replace("'prepare_failure_safe_fasttext_controller_r2.py','task_artifacts.py'","'prepare_failure_safe_fasttext_controller_r2.py','prepare_failure_safe_fasttext_controller_r3.py','prospective_owned_epoch.py','task_artifacts.py'")
 ast.parse(code);return code
if __name__=='__main__':
 dest=R/'prepared-failure-safe-fasttext-r3';dest.mkdir(mode=0o700,exist_ok=False);(dest/'controller.py').write_text(materialize());manifest={'prepared_only':True,'controller_sha256':sha(dest/'controller.py'),'source_hashes':{n:sha(R/n) for n in ['prepare_failure_safe_fasttext_controller_r3.py','prepare_failure_safe_fasttext_controller_r2.py','prospective_owned_epoch.py']},'parent_prepared_manifest_sha256':sha(R/'prepared-failure-safe-fasttext-r2/manifest.json'),'real_model_POST':0,'scored_native_runs':0,'limitations':['realownedDockerfixturegatepending','nativeCLI/modelperformanceunverified','oldunknownusageandunavailablegradeunrecoverable'],'goal_complete':False};(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
