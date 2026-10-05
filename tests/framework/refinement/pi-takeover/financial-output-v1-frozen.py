"""Fixed directory-state capture:absence is replayed as absence,no target repair."""
import base64,json,pathlib,re,subprocess,urllib.parse
from matched_html_support import DockerHTTP
from artifact_capture import CaptureError
from task_artifacts import descriptor,docker_archive
from directory_capture import capture_directory
from task_replay import verify_payload
TASK='financial-document-processor';PROTOCOL='financial-directory-state-v1';PATHS=[x['path'] for x in descriptor(TASK)]
def classify_stopped(container,image_id,connection=DockerHTTP):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned container')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();b=r.read(262145)
   if r.status!=200 or len(b)>262144:raise CaptureError('financial actor unavailable')
   x=json.loads(b)
   if x['Image']!=image_id or x['State']['Running'] or x['State'].get('Paused'):raise CaptureError('actor image/state changed')
   if any(m['Destination']=='/' or m['Destination'] in ['/app','/tests','/solution','/logs'] or m['Destination'].startswith(('/app/','/tests/','/solution/','/logs/')) for m in x.get('Mounts',[])):raise CaptureError('host output/trusted material mount')
   return x['Id']
  identity=inspect();states={}
  for path in PATHS:
   c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':path}));r=c.getresponse();r.read()
   if r.status==404:states[path]={'state':'absent','archive_status':404}
   elif r.status==200:
    try:s=json.loads(base64.b64decode(r.getheader('X-Docker-Container-Path-Stat'),validate=True));mode=s['mode']
    except Exception as e:raise CaptureError('unverified directory stat') from e
    if type(mode)!=int or mode&0x08000000 or not mode&0x80000000:raise CaptureError('unsupported non-directory/link output')
    states[path]={'state':'directory','archive_status':200}
   else:raise CaptureError('unsupported archive status')
  if inspect()!=identity:raise CaptureError('actor changed during inspection')
  return {'container_id':identity,'image_id':image_id,'stopped_actor_verified':True,'paths':states}
 finally:c.close()
def capture_stopped(container,image_id,destination):
 before=classify_stopped(container,image_id);root=pathlib.Path(destination);root.mkdir(mode=0o700,exist_ok=False);records={}
 for i,item in enumerate(descriptor(TASK)):
  path=item['path'];state=before['paths'][path]['state'];rec={**item,'state':state}
  if state=='directory':
   payload=root/('payload-'+str(i))
   with docker_archive(container,path) as stream:rec.update(capture_directory(stream,payload,pathlib.PurePosixPath(path).name,item['max_bytes']))
   rec.update(local_payload=payload.name,directories=sorted(p.relative_to(payload).as_posix() for p in payload.rglob('*') if p.is_dir()))
  records[path]=rec
 after=classify_stopped(container,image_id);(root/'presence-proof.json').write_text(json.dumps({'before':before,'after':after},indent=2)+'\n')
 if before!=after:raise CaptureError('stopped directory state changed')
 cap={'task':TASK,'protocol':PROTOCOL,'capture_complete':True,'stopped_actor_verified':True,'image_id':image_id,'presence_proof':before,'artifacts':records,'grading_verified':False,'cost_eligibility':False};(root/'capture.json').write_text(json.dumps(cap,indent=2)+'\n');return cap

def verify(root,image_id):
 root=pathlib.Path(root)
 if root.is_symlink() or (root/'capture.json').is_symlink():raise CaptureError('linked capture')
 cap=json.loads((root/'capture.json').read_text());proof=cap.get('presence_proof',{})
 if cap.get('task')!=TASK or cap.get('protocol')!=PROTOCOL or cap.get('image_id')!=image_id or cap.get('capture_complete') is not True or cap.get('stopped_actor_verified') is not True or proof.get('stopped_actor_verified') is not True or proof.get('image_id')!=image_id:raise CaptureError('unverified financial capture')
 if set(cap['artifacts'])!=set(PATHS) or set(proof['paths'])!=set(PATHS):raise CaptureError('fixed directory contract mismatch')
 for i,item in enumerate(descriptor(TASK)):
  rec=cap['artifacts'][item['path']];state=rec.get('state')
  if any(rec.get(k)!=v for k,v in item.items()) or state not in ['directory','absent'] or proof['paths'][item['path']]!={'state':state,'archive_status':200 if state=='directory' else 404}:raise CaptureError('descriptor/presence mismatch')
  if state=='absent':
   if set(rec)!=set(item)|{'state'} or (root/('payload-'+str(i))).exists():raise CaptureError('absent path has fabricated payload')
  else:
   if rec.get('local_payload')!='payload-'+str(i):raise CaptureError('unsafe payload reference')
   p=root/rec['local_payload'];verify_payload(p,rec)
   if sorted(q.relative_to(p).as_posix() for q in p.rglob('*') if q.is_dir())!=rec.get('directories'):raise CaptureError('directory identities changed')
 return cap

def replay(root,container,image_id,run=subprocess.run):
 cap=verify(root,image_id);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or x[0]['Image']!=image_id or x[0]['State']['Running'] or x[0]['State'].get('Paused') or x[0]['State'].get('Status')!='created':raise CaptureError('fresh original idle-shell grader required')
 if x[0]['Config'].get('Entrypoint')!=['/bin/sh'] or x[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('unexpected trusted runtime')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith('/app/') for m in x[0].get('Mounts',[])):raise CaptureError('host output mounts forbidden')
 run(['docker','start',container],capture_output=True,check=True,timeout=15);restored=[];absent=[]
 for path in PATHS:
  run(['docker','exec',container,'rm','-rf','--',path],capture_output=True,check=True,timeout=15);rec=cap['artifacts'][path]
  if rec['state']=='absent':absent.append(path);run(['docker','exec',container,'test','!','-e',path],capture_output=True,check=True,timeout=15)
  else:
   run(['docker','cp',str(pathlib.Path(root)/rec['local_payload']),container+':'+path],capture_output=True,check=True,timeout=60);restored.append(path)
 return {'replay_complete':True,'restored_paths':restored,'absent_paths_preserved':absent,'rebuild_performed':False,'grading_verified':False,'cost_eligibility':False}
