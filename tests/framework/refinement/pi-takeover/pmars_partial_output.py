"""Preserve source-only PMARS work without creating a missing installed binary."""
import json,pathlib,re,subprocess
from pmars_output_state import classify_stopped,classify
from directory_capture import capture_directory
from task_artifacts import docker_archive
from task_replay import verify_payload
from artifact_capture import CaptureError
LIMIT=536870912

def capture_partial(container,image_id,destination):
 proof=classify_stopped(container,image_id)
 if proof['output_state']!='absent':raise CaptureError('partial PMARS protocol requires absent binary')
 root=pathlib.Path(destination);root.mkdir(mode=0o700,exist_ok=False);records={};path=proof['source_directory']
 if path:
  with docker_archive(container,path) as stream:record=capture_directory(stream,root/'payload-0',pathlib.PurePosixPath(path).name,LIMIT)
  records[path]={'path':path,'kind':'directory','max_bytes':LIMIT,'purpose':'output','local_payload':'payload-0',**record}
 after=classify_stopped(container,image_id)
 (root/'pre-post-state.json').write_text(json.dumps({'before':proof,'after':after},indent=2)+'\n')
 def output_diff(p):return {line for line in p['docker_diff'].splitlines() if line[2:]=='/app' or line[2:].startswith('/app/') or line[2:]=='/usr/local/bin/pmars'}
 if {k:v for k,v in after.items() if k!='docker_diff'}!={k:v for k,v in proof.items() if k!='docker_diff'} or output_diff(after)!=output_diff(proof):raise CaptureError('PMARS stopped output/identity changed during capture')
 cap={'task':'build-pmars','protocol':'pmars-source-only-v1','capture_complete':True,'image_id':image_id,'stopped_actor_verified':True,'absence_proof':proof,'artifacts':records,'rebuild_performed':False,'grading_verified':False,'cost_eligibility':False};(root/'capture.json').write_text(json.dumps(cap,indent=2)+'\n');return cap

def verify_partial(root,image_id):
 root=pathlib.Path(root)
 if root.is_symlink() or (root/'capture.json').is_symlink():raise CaptureError('linked PMARS capture')
 cap=json.loads((root/'capture.json').read_text());p=cap.get('absence_proof',{})
 if cap.get('task')!='build-pmars' or cap.get('protocol')!='pmars-source-only-v1' or cap.get('capture_complete') is not True or cap.get('stopped_actor_verified') is not True or cap.get('image_id')!=image_id:raise CaptureError('unverified PMARS partial capture')
 if p.get('image_id')!=image_id or p.get('stopped_actor_verified') is not True or p.get('output_state')!='absent' or p.get('binary_absent_verified') is not True:raise CaptureError('unverified PMARS binary absence')
 observed=classify(p['docker_diff'],False)
 if observed['source_directory']!=p.get('source_directory'):raise CaptureError('source layout proof mismatch')
 path=p.get('source_directory');records=cap.get('artifacts',{})
 if set(records)!=({path} if path else set()):raise CaptureError('partial source artifact mismatch')
 if path:
  if not re.fullmatch(r'/app/pmars-[A-Za-z0-9.+_-]+',path):raise CaptureError('unsafe PMARS source path')
  record=records[path];expected={'path':path,'kind':'directory','max_bytes':LIMIT,'purpose':'output','local_payload':'payload-0'}
  if any(record.get(k)!=v for k,v in expected.items()):raise CaptureError('partial source descriptor mismatch')
  verify_payload(root/'payload-0',record)
 return cap

def replay_partial(root,container,image_id,run=subprocess.run):
 cap=verify_partial(root,image_id);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or x[0]['Image']!=image_id or x[0]['State']['Running'] or x[0]['State'].get('Paused') or x[0]['State'].get('Status')!='created':raise CaptureError('fresh original PMARS grader required')
 if x[0]['Config'].get('Entrypoint')!=['/bin/sh'] or x[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('fixed idle shell required')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith('/app/') or m['Destination']=='/usr/local' or m['Destination'].startswith('/usr/local/') for m in x[0].get('Mounts',[])):raise CaptureError('host output mount forbidden')
 run(['docker','start',container],capture_output=True,check=True,timeout=15);restored=[]
 path=cap['absence_proof']['source_directory']
 if path:
  run(['docker','exec',container,'rm','-rf','--',path],capture_output=True,check=True,timeout=15);run(['docker','cp',str(pathlib.Path(root)/'payload-0'),container+':'+path],capture_output=True,check=True,timeout=60);restored.append(path)
 return {'replay_complete':True,'restored_paths':restored,'installed_binary_absence_preserved':True,'rebuild_performed':False,'trusted_image_id':image_id,'grading_verified':False,'cost_eligibility':False}
