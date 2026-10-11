"""Only six diagnosed adapter/grade-count repairs; zero model calls.
Original211 control records and logs stay immutable. Separate new gold/starter
checks establish repaired adapter validity before any candidate inference.
"""
import concurrent.futures as F
import datetime,json,os,pathlib,subprocess,time,uuid
from run_controls import H,control,save,sha
TASKS=['cpp/exercises/practice/binary-search-tree','cpp/exercises/practice/circular-buffer','java/exercises/practice/connect','javascript/exercises/practice/grep','javascript/exercises/practice/palindrome-products','javascript/exercises/practice/robot-name']
def main():
 plan=json.loads((H/'controls-repair-plan.json').read_text());assert plan['tasks']==TASKS
 for name,digest in plan['implementation_sha256'].items():assert sha(H/name)==digest
 assert not (H/'controls-repair-launch.json').exists()
 original=json.loads((H/'controls-result.json').read_text());assert original['completed_tasks']==211
 launch=json.loads((H/'controls-launch.json').read_text());assert not subprocess.run(['ps','-p',str(launch['pid']),'-o','pid='],capture_output=True,text=True).stdout.strip()
 root=pathlib.Path('/tmp/solpi-g3-control-repairs-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);save(H/'controls-repair-launch.json',dict(pid=os.getpid(),root=str(root),plan_sha256=sha(H/'controls-repair-plan.json'),original_result_sha256=sha(H/'controls-result.json'),model_calls=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 rows=[]
 with F.ThreadPoolExecutor(max_workers=4) as pool:
  for row in pool.map(lambda t:control(t,root,plan['images']),TASKS):rows.append(row);save(H/'controls-repair-progress.json',dict(rows=rows,model_calls=0));print(row['task'],row['valid_pair'],flush=True)
 save(H/'controls-repair-result.json',dict(rows=rows,model_calls=0,original_result_sha256=sha(H/'controls-result.json')))
if __name__=='__main__':main()
