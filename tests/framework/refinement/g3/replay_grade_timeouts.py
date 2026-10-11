"""Exact original-test artifact replay for two diagnosed nonterminating solutions.
No actor inference, no solution/test edit, no model-cell retry, same180s tests.
"""
import concurrent.futures as F,datetime,json,os,pathlib,subprocess,time,uuid
from run_cell import H,sha,tree
from transport import save
CELLS=('g3-r1-t132-K','g3-r1-t132-Both')
def main():
 wave=json.loads((H/'waves/r1-w03/result.json').read_text());plan=json.loads((H/'plan.json').read_text());rows={r['cell_id']:r for r in wave['attempts']};task='javascript/exercises/practice/sum-of-multiples';image=plan['images']['javascript'];gold=pathlib.Path(plan['prepared_tasks'][task]);private=pathlib.Path('/tmp/solpi-g3-grade-timeout-replay-'+uuid.uuid4().hex[:10]);private.mkdir(mode=0o700)
 assert not (H/'grade-timeout-replay-launch.json').exists()
 save(H/'grade-timeout-replay-launch.json',dict(pid=os.getpid(),root=str(private),model_calls=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 jobs=[]
 for cell in CELLS:
  r=rows[cell];d=pathlib.Path(r['root']);assert r['verifier_exit']==2 and not r['grade_valid'] and (d/'verifier.log').read_text().strip()=='TimeoutExpired';assert tree(d/'final-work')==r['final_work_hashes'];assert tree(d/'grader')==plan['grader_trees'][task]
  jobs.append((cell,d/'final-work',d/'grader',r))
 jobs.append(('gold',gold/'reference',gold/'grader',None))
 def grade(job):
  cell,work,grader,row=job;name='solpi-g3-grade-timeout-'+uuid.uuid4().hex[:10];log=private/(cell+'.log');cmd=['docker','run','--rm','--name',name,'--network','none','--cpus','1','--memory','2g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,exec,size=1g','-e','HOME=/tmp','--entrypoint','python3','-v',str(work)+':/workspace:ro','-v',str(grader)+':/grader:ro','-v','/tmp/solpi-g1-js-deps:/npm-install:ro',image,'/grader/grade.py']
  if cell=='gold':cmd.append('--reference-control')
  start=time.monotonic()
  try:
   with log.open('xb') as out:z=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=300)
   result=dict(cell_id=cell,exit=z.returncode,seconds=time.monotonic()-start,log=str(log),log_sha256=sha(log),original_tests_unmodified=True,captured_work_unmodified=True,model_calls=0)
  finally:
   subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);probe=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15);assert probe.returncode and 'No such' in probe.stderr
  if row:result.update(raw_attempt_result_sha256=sha(pathlib.Path(row['root'])/'attempt-result.json'),captured_work_hashes=row['final_work_hashes'])
  return result
 with F.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(grade,jobs))
 save(H/'grade-timeout-replay-result.json',dict(rows=results,model_calls=0,all_owned_grader_containers_absent=True))
if __name__=='__main__':main()
