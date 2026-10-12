"""Neutral missing Python relay runtime, before inference; preserve originals.
Five proved empty command-v/exit127 checks. Public python3 only; no task edits.
Recheck BOTH original controls on each owned derivative; every arm shares it.
"""
import concurrent.futures,json,os,pathlib,subprocess,uuid
from B_controls import H,sha,save,control

def main():
 if (H/'B-python-launch.json').exists():raise RuntimeError('Existing handle; reconcile, no automatic restart')
 checks=json.loads((H/'B-runtime-check-result.json').read_text());tasks=json.loads((H/'B-images.json').read_text())['rows'];bad={r['task'] for r in checks['rows'] if r.get('exit_code')==127};assert len(bad)==5;root=pathlib.Path('/tmp/solpi-g4-B-python-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);save(H/'B-python-launch.json',dict(pid=os.getpid(),root=str(root),tasks=sorted(bad),model_calls=0,runner_sha256=sha(__file__),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),concurrent_workers=2));results=[]
 def prepare(task):
  directory=root/task['task'];directory.mkdir();name='solpi-g4-B-python-'+uuid.uuid4().hex[:12];tag='solpi-g4-python:'+uuid.uuid4().hex[:12];r=dict(task=task['task'],original_image_id=task['image_id'],model_calls=0,no_task_test_or_gold_edits=True);created=False
  try:
   subprocess.run(['docker','create','--pull=never','--name',name,'--cpus','1','--memory','2g','--pids-limit','512','--security-opt','no-new-privileges','--entrypoint','sh',task['image_id'],'-c','apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 && python3 -c "import http.server,socketserver,json,threading" && dpkg-query -W python3'],capture_output=True,check=True,timeout=30);created=True
   with (directory/'install.private.log').open('xb') as out:p=subprocess.run(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,timeout=600)
   ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0];assert p.returncode==0 and ins['State']['ExitCode']==0;subprocess.run(['docker','commit',name,tag],capture_output=True,check=True,timeout=120);image=json.loads(subprocess.check_output(['docker','image','inspect',tag],timeout=20))[0]['Id'];r.update(image_id=image,image_tag=tag,install_log_sha256=sha(directory/'install.private.log'));r['pair']=control(dict(task,image_id=image),directory/'controls');r['valid_pair']=r['pair']['valid_pair']
  except Exception as e:r.update(valid_pair=False,error=dict(type=type(e).__name__,message=str(e)[:400]))
  finally:
   if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
   gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);r['prepare_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr;save(directory/'result.json',r)
  return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(prepare,t) for t in tasks if t['task'] in bad]
  for f in concurrent.futures.as_completed(futures):results.append(f.result());save(H/'B-python-progress.json',dict(rows=results,model_calls=0))
 save(H/'B-python-result.json',dict(rows=results,model_calls=0,all5_valid=len(results)==5 and all(r['valid_pair'] and r['prepare_container_absent'] for r in results),original_checks_controls_images_retained=True))
if __name__=='__main__':main()
