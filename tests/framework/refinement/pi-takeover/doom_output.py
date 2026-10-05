"""Doom target presence/absence with witnesses;no target repair or VM substitution."""
import base64,json,pathlib,re,subprocess,urllib.parse
from matched_html_support import DockerHTTP
from artifact_capture import CaptureError,capture_file
from task_artifacts import descriptor,docker_archive,capture_stopped_actor
from task_replay import verify_payload,replay_capture
TASK='make-doom-for-mips';TARGET='/app/doomgeneric_mips';PROTOCOL='doom-missing-target-v1'
def classify_stopped(container,image_id,connection=DockerHTTP):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned container')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();b=r.read(262145)
   if r.status!=200 or len(b)>262144:raise CaptureError('Doom actor unavailable')
   x=json.loads(b)
   if x['Image']!=image_id or x['State']['Running'] or x['State'].get('Paused'):raise CaptureError('Doom actor image/state changed')
   if any(m['Destination']=='/' or m['Destination'] in ['/app','/tests','/solution','/logs'] or m['Destination'].startswith(('/app/','/tests/','/solution/','/logs/')) for m in x.get('Mounts',[])):raise CaptureError('actor exposeshost output/trustedmaterial')
   return x['Id']
  identity=inspect();c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':TARGET}));r=c.getresponse();r.read()
  if r.status==404:present=False
  elif r.status==200:
   try:mode=json.loads(base64.b64decode(r.getheader('X-Docker-Container-Path-Stat'),validate=True))['mode']
   except Exception as e:raise CaptureError('unverified target file stat') from e
   if type(mode)!=int or mode&0xfffff000:raise CaptureError('unsupported target file type/link')
   present=True # Wrongregularbytes/architecture remainfunctionalgraderfailures,notmissing.
  else:raise CaptureError('ambiguous target presence')
  if inspect()!=identity:raise CaptureError('Doom actor identity changed')
  return {'output_state':'present' if present else 'absent','binary_absent_verified':not present,'container_id':identity,'image_id':image_id,'stopped_actor_verified':True,'grading_verified':False,'cost_eligibility':False}
 finally:c.close()
def capture_missing(container,image_id,root):
 proof=classify_stopped(container,image_id)
 if not proof['binary_absent_verified']:raise CaptureError('targetmustbeverifiedabsent')
 root=pathlib.Path(root);root.mkdir(mode=0o700,exist_ok=False);records={}
 for i,item in enumerate(descriptor(TASK)[1:]):
  path=item['path'];payload=root/('witness-'+str(i))
  with docker_archive(container,path) as stream:rec=capture_file(stream,payload,pathlib.PurePosixPath(path).name,item['max_bytes'])
  records[path]={**item,**rec,'local_payload':payload.name}
 after=classify_stopped(container,image_id);(root/'presence-proof.json').write_text(json.dumps({'before':proof,'after':after},indent=2)+'\n')
 if after!=proof:raise CaptureError('Doom stoppedtargetstatechanged')
 cap={'task':TASK,'protocol':PROTOCOL,'image_id':image_id,'capture_complete':True,'stopped_actor_verified':True,'absence_proof':proof,'artifacts':records,'grading_verified':False,'cost_eligibility':False};(root/'capture.json').write_text(json.dumps(cap,indent=2)+'\n');return cap

def verify_missing(root,image_id):
 root=pathlib.Path(root)
 if root.is_symlink() or (root/'capture.json').is_symlink():raise CaptureError('linkedDoomcapture')
 cap=json.loads((root/'capture.json').read_text());p=cap.get('absence_proof',{})
 if cap.get('task')!=TASK or cap.get('protocol')!=PROTOCOL or cap.get('image_id')!=image_id or cap.get('capture_complete') is not True or cap.get('stopped_actor_verified') is not True or p.get('image_id')!=image_id or p.get('stopped_actor_verified') is not True or p.get('output_state')!='absent' or p.get('binary_absent_verified') is not True:raise CaptureError('unverifiedDoomabsencecapture')
 items=descriptor(TASK)[1:]
 if set(cap['artifacts'])!={i['path'] for i in items}:raise CaptureError('witnesscontractmismatch')
 for n,item in enumerate(items):
  rec=cap['artifacts'][item['path']]
  if any(rec.get(k)!=v for k,v in item.items()) or rec.get('local_payload')!='witness-'+str(n):raise CaptureError('unsafeDoomwitnessdescriptor')
  verify_payload(root/rec['local_payload'],rec)
 return cap

def replay_missing(root,container,image_id,actor_image_id=None,run=subprocess.run):
 cap=verify_missing(root,actor_image_id or image_id);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or x[0]['Image']!=image_id or x[0]['State']['Running'] or x[0]['State'].get('Paused') or x[0]['State'].get('Status')!='created':raise CaptureError('freshoriginalDoomgraderrequired')
 if x[0]['Config'].get('Entrypoint')!=['/bin/sh'] or x[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('unexpectedtrustedruntime')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith('/app/') for m in x[0].get('Mounts',[])):raise CaptureError('hostoutputmountforbidden')
 run(['docker','start',container],capture_output=True,check=True,timeout=15);run(['docker','exec',container,'test','!','-e',TARGET],capture_output=True,check=True,timeout=10)
 return {'replay_complete':True,'installed_binary_absence_preserved':True,'witness_paths_not_replayed':list(cap['artifacts']),'original_vm_and_wad_retained':True,'rebuild_performed':False,'grading_verified':False,'cost_eligibility':False}
