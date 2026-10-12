"""Uniform zero-model C captured-patch regrade for window01 mkdir failure.
Never rerun actors; original attempts/costs/errors retained. Unmodified adapter.
Require all8 C durable cleanup rows. At most8 B slots plus4 regraders <=12;
no new model cells admitted by the already fully claimed16-cell window.
"""
import concurrent.futures,json,os,pathlib,subprocess
from native import H,sha
from transport import save

def main():
 launch=json.loads((H/'window-01-launch.json').read_text());root=pathlib.Path(launch['root']);live=subprocess.run(['ps','-p',str(launch['pid']),'-o','args='],capture_output=True,text=True).stdout
 # The original16 window is fully claimed. Completed8 C slots stay released;
 # even all8 remaining B runs plus4 zero-model graders are within16.
 assert len(list((H/'cell-claims').glob('*.json')))==16
 cells=json.loads((H/'windows/01.json').read_text())['cells'];plan=json.loads((H/'preregistration.json').read_text());rows=[]
 for cell in cells:
  if not cell.startswith('g4-C-'):continue
  attempts=json.loads((root/(cell+'-attempts.json')).read_text());assert len(attempts)==1 and attempts[0]['owned_cleanup_verified'];row=attempts[0];rows.append(row)
 assert len(rows)==8
 if (H/'window-01-C-regrade-launch.json').exists():raise RuntimeError('Existing regrade handle; reconcile, no automatic restart')
 save(H/'window-01-C-regrade-launch.json',dict(pid=os.getpid(),window_root=str(root),cells=[r['cell_id'] for r in rows],model_calls=0,scheduler_live_at_regrade_launch=bool(live.strip()),maximum_combined_slots=12,runner_sha256=sha(__file__),adapter_sha256=sha(H/'grade_swe.py'),reason='Original runner precreated adapter root, FileExistsError; all C captured patches regraded uniformly with unchanged official adapter',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),workers=4));results=[]
 def grade(row):
  attempt=pathlib.Path(row['root']);patch=attempt/'model.patch';assert sha(patch)==row['patch_sha256'];destination=attempt/'grade-recheck-01';assert not destination.exists()
  with (attempt/'grader-recheck-01.private.log').open('xb') as log:process=subprocess.run([plan['grader_python'],str(H/'grade_swe.py'),str(destination),row['task'],str(patch),plan['grader_plan']],stdout=log,stderr=subprocess.STDOUT,timeout=900)
  result=destination/'grade-result.json'
  if process.returncode or not result.exists():raise RuntimeError('Regrade failed; retain artifacts and reconcile owned handles')
  g=json.loads(result.read_text());assert g['owned_containers_absent'];return dict(cell_id=row['cell_id'],attempt=1,root=str(destination),model_calls=0,patch_sha256=sha(patch),original_attempt_sha256=sha(attempt/'attempt-result.json'),original_failed_grader_log_sha256=sha(attempt/'grader.private.log'),grade_sha256=sha(result),solved=g['solved'],grade_valid=g['grade_valid'],owned_containers_absent=g['owned_containers_absent'],errors=g['errors'],no_actor_or_model_rerun=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for future in concurrent.futures.as_completed([pool.submit(grade,row) for row in rows]):results.append(future.result());save(H/'window-01-C-regrade-progress.json',dict(rows=results,model_calls=0))
 save(H/'window-01-C-regrade-result.json',dict(rows=results,model_calls=0,all8_graded=len(results)==8,original_attempts_costs_errors_retained=True))
if __name__=='__main__':main()
