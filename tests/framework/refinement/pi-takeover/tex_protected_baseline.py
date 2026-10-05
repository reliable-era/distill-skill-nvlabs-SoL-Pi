"""Before-inference protected-inputsnapshot;no tasksolution/testmaterial."""
import json,pathlib,subprocess
from artifact_capture import capture_file,CaptureError
from task_artifacts import GUARDS,docker_archive
from protected_inputs import check_protected_inputs

def capture_before(container,image_id,root):
 x=json.loads(subprocess.check_output(['docker','inspect',container],text=True,timeout=10))[0]
 if x['Image']!=image_id or x['State'].get('Status')!='created' or x['State']['Running'] or x['State'].get('Paused'):raise CaptureError('freshneverstartedTeXactorrequired')
 if any(m['Destination']=='/' or m['Destination']=='/app' or m['Destination'].startswith(('/app/','/tests','/solution','/logs')) for m in x.get('Mounts',[])):raise CaptureError('hostoutput/trustedmountforbidden')
 identity=x['Id'];root=pathlib.Path(root);root.mkdir(mode=0o700,exist_ok=False);records={}
 for n,path in enumerate(GUARDS['overfull-hbox']):
  with docker_archive(container,path) as stream:r=capture_file(stream,root/('input-'+str(n)),pathlib.PurePosixPath(path).name,33554432)
  records[path]=r
 after=json.loads(subprocess.check_output(['docker','inspect',container],text=True,timeout=10))[0]
 if after['Id']!=identity or after['Image']!=image_id or after['State']['Status']!='created':raise CaptureError('TeXactorchangedduringbaseline')
 result={'container_id':identity,'image_id':image_id,'before_actor_start_verified':True,'protected_baseline':records,'grading_verified':False};(root/'baseline.json').write_text(json.dumps(result,indent=2)+'\n');return result

def compare_original(baseline,control):
 result=check_protected_inputs(control['protected_before'],baseline['protected_baseline'],GUARDS['overfull-hbox'])
 if not result['unchanged']:raise CaptureError('originalTeXprotectedinputsidentitychanged')
 return result
