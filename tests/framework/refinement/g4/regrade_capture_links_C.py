"""Uniform all4 original official grades of committed capture-only projections.
Never rerun models/actors. Require window05 exit/zero slots and exclusive lock.
Retain original failure/attempt/native/cost and every grade/projection artifact.
"""
import concurrent.futures,fcntl,json,os,pathlib,subprocess
from native import H,sha
from transport import save,metadata,waiting_zero

def main():
 launch=json.loads((H/'window-05-launch.json').read_text());root=pathlib.Path(launch['root']);scope=json.loads((H/'capture-link-projection-plan.json').read_text());patches=json.loads((H/'window-05-capture-patch-projection.json').read_text());plan=json.loads((H/'preregistration-v2.json').read_text())
 if subprocess.run(['ps','-p',str(launch['pid']),'-o','args='],capture_output=True,text=True).stdout.strip():raise RuntimeError('Original window05 scheduler live: wait, no overlap/restart')
 final=json.loads((root/'window-result.json').read_text());assert final['completed'] and final['occupied_slots']==0
 lock=(H/'shared-run-slots.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert sha(H/'capture-link-projection-plan.json')==patches['plan_sha256'];assert sha(H/'recover_ignored_capture_links.py')==scope['projection_sha256']
 assert subprocess.check_output(['git','show','HEAD:tests/framework/refinement/g4/regrade_capture_links_C.py'],cwd=H)==pathlib.Path(__file__).read_bytes()
 assert all(sha(f)==d for f,d in plan['runtime_hashes'].items());assert all(sha(f)==d for f,d in plan['input_hashes'].items())
 assert len(patches['proofs'])==4 and {r['cell_id'] for r in patches['proofs']}=={r['cell_id'] for r in scope['cells']}
 rows=[]
 for patch in patches['proofs']:
  original=root/(patch['cell_id']+'-a'+str(patch['attempt']));row=json.loads((original/'attempt-result.json').read_text());assert row['owned_cleanup_verified'] and row['error']['type']=='AbsoluteLinkError' and row['task']==scope['task'];assert sha(original/'attempt-result.json')==patch['original_attempt_sha256'];destination=pathlib.Path(patch['root']);proof=json.loads((destination/'projection-proof.json').read_text());assert sha(destination/'projection-proof.json')==patch['projection_proof_sha256'];assert sha(original/'captured.tar')==proof['captured_tar_sha256'];assert sha(destination/'model.patch')==patch['patch_sha256']==proof['patch_sha256'];rows.append((row,patch))
 if (H/'window-05-C-capture-regrade-launch.json').exists():raise RuntimeError('Existing regrade handle: reconcile, no automatic restart')
 load=metadata('/get_load')
 if not waiting_zero(load):raise RuntimeError('Fresh8000 zero-wait proof required; pause, no fallback')
 save(H/'window-05-C-capture-regrade-launch.json',dict(load_admission=load,pid=os.getpid(),workers=4,cells=[r['cell_id'] for r,p in rows],maximum_occupied_slots=4,model_calls=0,actor_reruns=0,scheduler_exited=True,exclusive_shared_lock=True,runner_sha256=sha(__file__),adapter_sha256=sha(H/'grade_swe.py'),patch_projection_sha256=sha(H/'window-05-capture-patch-projection.json'),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip()))
 def grade(pair):
  row,patch=pair;directory=pathlib.Path(patch['root']);destination=directory/'grade';assert not destination.exists();errors=[]
  try:
   with (directory/'grader.private.log').open('xb') as log:process=subprocess.run([plan['grader_python'],str(H/'grade_swe.py'),str(destination),row['task'],str(directory/'model.patch'),plan['grader_plan']],stdout=log,stderr=subprocess.STDOUT,timeout=900)
   if process.returncode or not (destination/'grade-result.json').exists():errors.append('Original adapter failed; retain artifacts')
  except Exception as e:errors.append(type(e).__name__+': '+str(e))
  finally:
   owned=destination/'owned.json'
   if owned.exists():
    for name in json.loads(owned.read_text())['names']:
     if not name.startswith('sweb.eval.'+row['task'].lower()+'.g4-grade-'):errors.append('unverified ownership');continue
     check=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
     if check.returncode==0:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
     check=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
     if check.returncode==0 or 'No such' not in check.stderr:errors.append('owned absence unverified:'+name)
  result=destination/'grade-result.json';g=json.loads(result.read_text()) if result.exists() else {};errors+=g.get('errors',[])
  return dict(cell_id=row['cell_id'],attempt=row['attempt'],original_attempt_sha256=patch['original_attempt_sha256'],original_capture_sha256=sha(pathlib.Path(row['root'])/'captured.tar'),capture_projection_root=str(directory),capture_projection_proof_sha256=patch['projection_proof_sha256'],projected_patch_sha256=patch['patch_sha256'],authoritative_grade_root=str(destination),authoritative_grade_sha256=sha(result) if result.exists() else None,grade_valid=g.get('grade_valid',False),solved=g.get('solved'),owned_containers_absent=g.get('owned_containers_absent',False) and not errors,errors=errors,model_calls=0,actor_reruns=0,reason='Original capture AbsoluteLinkError; uniform all4 captured-only patch projection, unchanged official grader')
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for future in concurrent.futures.as_completed([pool.submit(grade,pair) for pair in rows]):results.append(future.result());save(H/'window-05-C-capture-regrade-progress.json',dict(rows=results,model_calls=0))
 valid=len(results)==4 and all(r['grade_valid'] and r['owned_containers_absent'] and not r['errors'] for r in results);save(H/'window-05-C-capture-regrade-result.json',dict(rows=results,all4_graded=valid,occupied_slots=0,model_calls=0,actor_reruns=0,original_attempts_costs_errors_retained=True))
 if valid:save(H/'window-05-C-grade-projection.json',dict(rows=results,model_calls=0,actor_reruns=0,uniform_all4=True))
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
