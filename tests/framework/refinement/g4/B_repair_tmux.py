"""Pre-inference neutral missing-tool repair; retain original failed control pair.
Original git-multibranch oracle/test untouched. Only its final keepalive tmux
command lacked the public tool (exit127 despite verifier reward1). Install the
missing tool in an owned derivative image, then recheck both controls there.
"""
import datetime,json,pathlib,subprocess,uuid,os
from B_controls import H,sha,save,control

def main():
 plan=json.loads((H/'B-tmux-plan.json').read_text());assert sha(__file__)==plan['runner_sha256']
 if (H/'B-tmux-launch.json').exists():raise RuntimeError('Existing owned preparation; reconcile rather than restart')
 task=next(r for r in json.loads((H/'B-images.json').read_text())['rows'] if r['task']=='git-multibranch');assert task['image_id']==plan['base_image_id'];root=pathlib.Path('/tmp/solpi-g4-B-tmux-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);name='solpi-g4-B-tmux-'+uuid.uuid4().hex[:12];tag='solpi-g4-gitmultibranch-tmux:'+uuid.uuid4().hex[:12];save(H/'B-tmux-launch.json',dict(pid=os.getpid(),root=str(root),container_name=name,image_tag=tag,model_calls=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip()));created=False;result=dict(model_calls=0,base_image_id=task['image_id'],original_failed_pair_retained=True,no_test_or_oracle_edits=True,neutral_change='Install missing tmux; same image for both controls and every eventual model arm')
 try:
  subprocess.run(['docker','create','--pull=never','--name',name,'--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','--entrypoint','bash',task['image_id'],'-lc','apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tmux && dpkg-query -W tmux && sha256sum /usr/bin/tmux'],capture_output=True,check=True,timeout=30);created=True
  with (root/'install.private.log').open('xb') as log:
   os.chmod(log.name,0o600);p=subprocess.run(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,timeout=900)
  result['installation_exit']=p.returncode;result['installation_log_sha256']=sha(root/'install.private.log');ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0];assert not ins['HostConfig'].get('DeviceRequests') and not ins['HostConfig']['Privileged'] and ins['State']['Status']=='exited';save(root/'prepare-inspect.json',ins)
  if p.returncode!=0 or ins['State']['ExitCode']!=0:raise RuntimeError('Neutral public-tool installation failed')
  subprocess.run(['docker','commit',name,tag],capture_output=True,check=True,timeout=120);img=json.loads(subprocess.check_output(['docker','image','inspect',tag],timeout=20))[0];task=dict(task,image_id=img['Id']);result['derivative_image_id']=img['Id'];result['image_tag']=tag;result['control_pair']=control(task,root/'controls');result['valid_pair']=result['control_pair']['valid_pair']
 except Exception as e:result['error']=dict(type=type(e).__name__,message=str(e)[:500]);result['valid_pair']=False
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);result['prepare_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr;result['private_root']=str(root);save(H/'B-tmux-result.json',result)
if __name__=='__main__':main()
