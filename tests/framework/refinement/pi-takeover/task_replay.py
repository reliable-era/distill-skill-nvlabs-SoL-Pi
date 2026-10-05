"""Verified capture->fresh trusted container replay. No model,build,or grading calls."""
import hashlib,json,pathlib,stat,subprocess
from artifact_capture import CaptureError
from task_artifacts import descriptor

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_payload(path,record):
 if path.is_symlink():raise CaptureError('linked replay payload')
 if record['kind']=='directory':
  if not path.is_dir():raise CaptureError('missing directory payload')
  files={}
  for child in path.rglob('*'):
   mode=child.lstat().st_mode
   if stat.S_ISDIR(mode):continue
   if not stat.S_ISREG(mode):raise CaptureError('unsafe directory replay member')
   files[child.relative_to(path).as_posix()]={'bytes':child.stat().st_size,'sha256':digest(child)}
  if files!=record['files'] or sum(x['bytes'] for x in files.values())!=record['bytes']:raise CaptureError('directory payload manifest mismatch')
 else:
  if not path.is_file() or not stat.S_ISREG(path.lstat().st_mode) or path.stat().st_size!=record['bytes'] or digest(path)!=record['sha256']:raise CaptureError('file payload manifest mismatch')
  if record['kind']=='executable' and stat.S_IMODE(path.stat().st_mode)!=record['restored_mode']:raise CaptureError('executable mode changed after capture')

def replay_capture(task,capture_root,container,image_id,dynamic=None,run=subprocess.run,actor_image_id=None):
 root=pathlib.Path(capture_root)
 if root.is_symlink():raise CaptureError('linked capture root')
 if (root/'capture.json').is_symlink():raise CaptureError('linked capture manifest')
 capture=json.loads((root/'capture.json').read_text())
 if capture.get('task')!=task or capture.get('capture_complete') is not True or capture.get('stopped_actor_verified') is not True or capture.get('image_id')!=(actor_image_id or image_id):raise CaptureError('unverified stopped-actor capture')
 if task=='overfull-hbox' and capture.get('protected_input_gate_passed') is not True:raise CaptureError('protected TeX input changed or baseline absent')
 expected=descriptor(task,dynamic);records=capture['artifacts']
 if set(records)!={x['path'] for x in expected}:raise CaptureError('artifact path contract mismatch')
 payloads=[]
 for index,item in enumerate(expected):
  record=records[item['path']]
  if any(record.get(k)!=v for k,v in item.items()) or record.get('local_payload')!='payload-'+str(index):raise CaptureError('artifact descriptor mismatch')
  path=root/record['local_payload'];verify_payload(path,record)
  if item['purpose']=='output':payloads.append((item,path,record))
 # Verify all bytes before the first container mutation.
 metadata=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(metadata)!=1 or metadata[0]['Image']!=image_id:raise CaptureError('trusted replay image mismatch')
 if metadata[0]['State']['Running'] or metadata[0]['State'].get('Paused') or metadata[0]['State'].get('Status')!='created':raise CaptureError('trusted replay container must be never started')
 if metadata[0]['Config'].get('Entrypoint')!=['/bin/sh'] or metadata[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('trusted replay entrypoint must be fixed idle shell')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith('/app/') or m['Destination']=='/usr/local' or m['Destination'].startswith('/usr/local/') for m in metadata[0].get('Mounts',[])):raise CaptureError('trusted output paths must not be host mounts')
 # Directory removal needs a running trusted shell. Execute only fixed,validated paths.
 # Caller must create a fresh container with a sleep entrypoint;never actor code.
 run(['docker','start',container],capture_output=True,check=True,timeout=15)
 uid=run(['docker','exec',container,'id','-u'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
 gid=run(['docker','exec',container,'id','-g'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
 if not uid.isdecimal() or not gid.isdecimal():raise CaptureError('trusted runtime identity unavailable')
 restored=[]
 for item,path,record in payloads:
  target=item['path'];parent=str(pathlib.PurePosixPath(target).parent)
  run(['docker','exec',container,'/bin/sh','-c','mkdir -p -- "$1" && rm -rf -- "$2"','replay',parent,target],capture_output=True,check=True,timeout=15)
  run(['docker','cp',str(path),container+':'+target],capture_output=True,check=True,timeout=60)
  run(['docker','exec','--user','0:0',container,'chown','-R','--',uid+':'+gid,target],capture_output=True,check=True,timeout=30)
  if item['kind']=='executable':run(['docker','exec',container,'chmod',format(record['restored_mode'],'o'),target],capture_output=True,check=True,timeout=10)
  restored.append(target)
 return {'task':task,'replay_complete':True,'restored_paths':restored,'witness_paths_not_replayed':[x['path'] for x in expected if x['purpose']!='output'],'trusted_image_id':image_id,'actor_image_id':actor_image_id or image_id,'trusted_payload_owner':uid+':'+gid,'rebuild_performed':False,'official_grade_available':False,'cost_eligibility':False}
