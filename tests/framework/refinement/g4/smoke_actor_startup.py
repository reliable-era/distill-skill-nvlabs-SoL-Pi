"""Zero-model integrated C actor source/environment/relay/Codex startup check.
No broker is started; only --version, Python imports and Git snapshot checks.
No hidden verifier/gold mounts. Real resources/mounts checked then removed.
"""
import datetime,json,os,pathlib,subprocess,uuid
from native import H,create_args,BINARY,BINARY_SHA,sha

def main():
 if (H/'actor-startup-smoke-launch.json').exists():raise RuntimeError('Existing smoke handle; reconcile, no automatic restart')
 source=json.loads((H/'C-prepared-sources.json').read_text())['rows'][0];baseline=pathlib.Path(source['private_root']);plan=json.loads((H/'C-controls-offline-plan.json').read_text());assert sha(BINARY)==BINARY_SHA;root=pathlib.Path('/tmp/solpi-g4-actor-startup-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);(root/'skills').mkdir();(root/'transport/socket').mkdir(parents=True);name='solpi-g4-actor-smoke-'+uuid.uuid4().hex[:16];launch=dict(pid=os.getpid(),root=str(root),container_name=name,task=source['task'],model_calls=0,broker_started=False,runner_sha256=sha(__file__),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip());(H/'actor-startup-smoke-launch.json').write_text(json.dumps(launch,indent=2)+'\n');result=dict(model_calls=0,broker_started=False,errors=[]);created=False
 try:
  subprocess.run(create_args(name,source['image_id'],root,'C',8192,'/testbed',plan['wheelhouse']),check=True,capture_output=True,timeout=30);created=True;subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=30);subprocess.run(['docker','exec',name,'sh','-c','rm -rf /testbed; mkdir /testbed'],check=True,capture_output=True,timeout=30);subprocess.run(['docker','cp',str(baseline/'workspace')+'/.',name+':/testbed'],check=True,capture_output=True,timeout=120)
  with (root/'startup.private.log').open('xb') as log:
   p=subprocess.run(['docker','exec',name,'bash','-lc','source /opt/miniconda3/bin/activate && conda activate testbed && python3 -c "import http.server,socketserver,json,threading" && /opt/solpi/codex --version && git -C /testbed rev-list --count HEAD && git -C /testbed rev-parse HEAD'],stdout=log,stderr=subprocess.STDOUT,timeout=60)
  result['exit_code']=p.returncode;result['startup_log_sha256']=sha(root/'startup.private.log');text=(root/'startup.private.log').read_text();assert p.returncode==0 and 'codex-cli 0.160.0' in text and source['snapshot_commit'] in text and '\n1\n' in text
  ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0];host=ins['HostConfig'];assert host['NetworkMode']=='none' and host['Memory']==8*1024**3 and host['NanoCpus']==1000000000 and not host['Privileged'] and not host.get('DeviceRequests');assert not any(m['Destination'] in ('/tests','/solution','/var/run/docker.sock') for m in ins['Mounts']);(root/'inspect.json').write_text(json.dumps(ins,indent=2));result.update(passed=True,inspect_sha256=sha(root/'inspect.json'),snapshot_commit=source['snapshot_commit'],gold_in_actor=False,upstream_history_in_actor=False)
 except Exception as e:result.update(passed=False,errors=[dict(type=type(e).__name__,message=str(e)[:400])])
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);result['owned_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr;result['root']=str(root);(H/'actor-startup-smoke-result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
