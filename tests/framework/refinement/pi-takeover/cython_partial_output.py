"""Bounded source-only replay. Never installs or rebuilds a missing target package."""
import json,pathlib,subprocess,urllib.parse
from stopped_cython_output import classify_stopped
from matched_html_support import DockerHTTP
from artifact_capture import CaptureError
from directory_capture import capture_directory
from task_artifacts import docker_archive
from task_replay import verify_payload
SOURCE='/app/pyknotid';ITEM={'path':SOURCE,'kind':'directory','max_bytes':536870912,'purpose':'output'}

def inspect(container,image_id,run=subprocess.run):
 x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or x[0]['Image']!=image_id or x[0]['State']['Running'] or x[0]['State'].get('Paused'):raise CaptureError('wrong stopped container image/state')
 if any(m['Destination']=='/' or m['Destination'] in ['/tests','/solution','/logs','/app'] or m['Destination'].startswith(('/tests/','/solution/','/logs/','/app/')) for m in x[0].get('Mounts',[])):raise CaptureError('actor exposes trusted material or host output')
 return x[0]

def capture_partial(container,image_id,destination,run=subprocess.run,connection=DockerHTTP):
 metadata=inspect(container,image_id,run);absence=classify_stopped(container,image_id,connection,run)
 if absence['output_state']!='absent':raise CaptureError('partial protocol requires verified absent installation')
 c=connection()
 try:
  c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':SOURCE}));response=c.getresponse();response.read()
  if response.status not in [200,404]:raise CaptureError('ambiguous source presence')
  present=response.status==200
 finally:c.close()
 if inspect(container,image_id,run)['Id']!=metadata['Id']:raise CaptureError('actor changed during source check')
 root=pathlib.Path(destination);root.mkdir(mode=0o700,exist_ok=False);records={}
 if present:
  with docker_archive(container,SOURCE) as stream:record=capture_directory(stream,root/'payload-0','pyknotid',ITEM['max_bytes'])
  records[SOURCE]={**ITEM,**record,'local_payload':'payload-0'}
 result={'task':'build-cython-ext','protocol':'cython-source-only-v1','capture_complete':True,'stopped_actor_verified':True,'image_id':image_id,'container_id':metadata['Id'],'installation_absence':absence,'source_present':present,'artifacts':records,'rebuild_performed':False,'grading_verified':False,'cost_eligibility':False}
 (root/'capture.json').write_text(json.dumps(result,indent=2)+'\n');return result

def verify_partial(root,image_id):
 root=pathlib.Path(root)
 if root.is_symlink() or (root/'capture.json').is_symlink():raise CaptureError('linked partial capture')
 cap=json.loads((root/'capture.json').read_text());a=cap.get('installation_absence',{})
 if cap.get('protocol')!='cython-source-only-v1' or cap.get('task')!='build-cython-ext' or cap.get('capture_complete') is not True or cap.get('stopped_actor_verified') is not True or cap.get('image_id')!=image_id:raise CaptureError('unverified partial capture')
 if a.get('output_state')!='absent' or a.get('installation_absent_verified') is not True or a.get('stopped_actor_verified') is not True or a.get('image_id')!=image_id or a.get('container_id')!=cap.get('container_id') or any(a.get('presence',{}).values()):raise CaptureError('installation absence not bound to actor')
 from stopped_cython_output import PATHS,classify
 if set(a.get('presence',{}))!=set(PATHS) or classify(a['docker_diff'],a['presence'])['output_state']!='absent':raise CaptureError('absence proof invalid')
 present=cap.get('source_present');records=cap.get('artifacts',{})
 if type(present)!=bool or set(records)!=({SOURCE} if present else set()):raise CaptureError('partial artifact set mismatch')
 if present:
  record=records[SOURCE]
  if any(record.get(k)!=v for k,v in ITEM.items()) or record.get('local_payload')!='payload-0':raise CaptureError('partial descriptor mismatch')
  verify_payload(root/'payload-0',record)
 return cap

def replay_partial(root,container,image_id,run=subprocess.run):
 cap=verify_partial(root,image_id);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or x[0]['Image']!=image_id or x[0]['State']['Running'] or x[0]['State'].get('Paused') or x[0]['State'].get('Status')!='created':raise CaptureError('partial replay requires fresh original grader')
 if x[0]['Config'].get('Entrypoint')!=['/bin/sh'] or x[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('grader must use fixed idle shell')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith('/app/') or m['Destination']=='/usr/local' or m['Destination'].startswith('/usr/local/') for m in x[0].get('Mounts',[])):raise CaptureError('host output mount forbidden')
 run(['docker','start',container],capture_output=True,check=True,timeout=15)
 if cap['source_present']:
  run(['docker','exec',container,'mkdir','-p','/app'],capture_output=True,check=True,timeout=10)
  run(['docker','exec',container,'rm','-rf','--',SOURCE],capture_output=True,check=True,timeout=15)
  run(['docker','cp',str(pathlib.Path(root)/'payload-0'),container+':'+SOURCE],capture_output=True,check=True,timeout=60)
  uid=run(['docker','exec',container,'id','-u'],capture_output=True,text=True,check=True,timeout=10).stdout.strip();gid=run(['docker','exec',container,'id','-g'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
  if not uid.isdecimal() or not gid.isdecimal():raise CaptureError('trusted identity unavailable')
  run(['docker','exec','--user','0:0',container,'chown','-R','--',uid+':'+gid,SOURCE],capture_output=True,check=True,timeout=30)
 return {'replay_complete':True,'source_present':cap['source_present'],'missing_installation_preserved':True,'restored_paths':[SOURCE] if cap['source_present'] else [],'trusted_image_id':image_id,'rebuild_performed':False,'grading_verified':False,'cost_eligibility':False}
