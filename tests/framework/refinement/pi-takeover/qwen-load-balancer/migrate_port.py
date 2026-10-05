"""User-authorized 8000 ->18002 backend move; only the named model and own Nginx."""
import fcntl,http.client,json,os,pathlib,subprocess,time
R=pathlib.Path(__file__).resolve().parent;PREFIX=pathlib.Path('/tmp/solpi-qwen-load-balancer-18080');NAME='ykw-qwen38-dflash2-tp2';BACKUP=NAME+'-pre-lb-20261004'
PRIVATE=pathlib.Path('/tmp/solpi-qwen-port-migration-20261004');PRIVATE.mkdir(mode=0o700,exist_ok=False)
class DockerHTTP(http.client.HTTPConnection):
 def connect(self):
  import socket
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(120);self.sock.connect('/var/run/docker.sock')
def docker(*args):return subprocess.check_output(['docker',*args],timeout=300).decode().strip()
def get(port,path):
 c=http.client.HTTPConnection('127.0.0.1',port,timeout=3)
 try:c.request('GET',path);r=c.getresponse();body=json.loads(r.read());return r.status,body
 finally:c.close()
def empty(port):
 status,load=get(port,'/get_load')
 if status!=200 or not isinstance(load,list) or not load or any(x.get('num_reqs')!=0 or x.get('num_waiting_reqs')!=0 for x in load):raise RuntimeError('Backend busy; do not stop: '+str(port))
def nginx_reload():
 cmd=['/usr/sbin/nginx','-p',str(PREFIX)+'/', '-c',str(R/'nginx.conf')]
 subprocess.run(cmd+['-t'],check=True);subprocess.run(cmd+['-s','reload'],check=True)
locks=[];created=None;renamed=False;old=None
pending=(R/'nginx.conf').read_text()
previous=pending.replace('server 127.0.0.1:18002 down; # enabled after relocated backend is healthy','server 127.0.0.1:8000 max_fails=1 fail_timeout=5s;').replace('listen 127.0.0.1:8000;\n        listen 127.0.0.1:18080; # initial endpoint compatibility','listen 127.0.0.1:18080;').replace('"backends":[18002,18001]','"backends":[8000,18001]')
(PRIVATE/'rollback-nginx.conf').write_text(previous)
try:
 root=R.parents[5]
 for path in [root/'eval/pruned/model.lock',root/'distill-skill-nvlabs-SoL-Pi/tests/eval/pruned/model.lock']:
  fd=os.open(path,os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(fd)
 audit=json.loads((R.parent/'patch-first-audit.json').read_text())
 if audit['status']!='PASS' or not audit['complete']:raise RuntimeError('Existing frozen panel not audited terminal')
 expected=int(json.loads((R/'deployment.json').read_text())['pid'])
 cmdline=pathlib.Path('/proc/'+str(expected)+'/cmdline').read_bytes()
 if str(PREFIX).encode() not in cmdline:raise RuntimeError('Owned Nginx identity mismatch')
 for _ in range(3):empty(8000);time.sleep(1)
 old=json.loads(docker('inspect',NAME))[0]
 if old['Config']['Cmd'].count('8000')!=1 or 'NVIDIA_VISIBLE_DEVICES=2,3' not in old['Config']['Env']:raise RuntimeError('Unexpected source launch/devices')
 (PRIVATE/'original-container.json').write_text(json.dumps(old));(PRIVATE/'original-container.json').chmod(0o600)
 docker('stop','-t','30',NAME);print('Stopped idle GPU2/3 model backend',flush=True)
 # Stopped writable layer is preserved too, not just a potentially stale image tag.
 image=docker('commit',NAME);docker('rename',NAME,BACKUP);renamed=True
 nginx_reload() # 8000 now serves the still-running GPU0/1 replica while2/3 warms.
 config=dict(old['Config']);config['Image']=image;config['Cmd']=list(config['Cmd']);config['Cmd'][config['Cmd'].index('8000')]='18002';config.pop('Hostname',None);config['HostConfig']=old['HostConfig']
 c=DockerHTTP('docker');c.request('POST','/v1.41/containers/create?name='+NAME,json.dumps(config),{'Content-Type':'application/json'});response=c.getresponse();body=json.loads(response.read());c.close()
 if response.status!=201:raise RuntimeError('Docker create failed: '+str(response.status))
 created=body['Id'];docker('start',created);print('Relocated backend starting on18002; frontend8000 available via18001',flush=True)
 until=time.monotonic()+900
 while time.monotonic()<until:
  try:
   status,models=get(18002,'/v1/models')
   if status==200 and [m['id'] for m in models.get('data',[])]==['Qwen3.8-27B-FP8']:break
  except (OSError,ValueError,http.client.HTTPException):pass
  if json.loads(docker('inspect',created))[0]['State']['Status'] not in ['running','restarting']:raise RuntimeError('Relocated backend exited')
  time.sleep(5)
 else:raise RuntimeError('Relocated backend readiness deadline')
 (R/'nginx.conf').write_text(pending.replace('server 127.0.0.1:18002 down; # enabled after relocated backend is healthy','server 127.0.0.1:18002 max_fails=1 fail_timeout=5s;'))
 nginx_reload();result={'status':'complete','frontend':'http://127.0.0.1:8000/v1','backends':[18002,18001],'original_container':old['Id'],'backup_name':BACKUP,'new_container':created,'snapshot_image':image,'private_backup':str(PRIVATE),'hardware_GPU_reset':False};(R/'migration.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
except Exception:
 # Roll back only resources identified by this migration; keep GPU0/1 intact.
 (R/'nginx.conf').write_text(previous)
 try:nginx_reload();time.sleep(1)
 except Exception:pass
 if created:
  try:docker('rm','-f',created)
  except Exception:pass
 if renamed:docker('rename',BACKUP,NAME)
 if old:docker('start',old['Id'])
 raise
finally:
 for fd in locks:os.close(fd)
