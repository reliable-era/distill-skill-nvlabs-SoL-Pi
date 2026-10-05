"""Read-only stopped-actor layout discovery;unsupported layouts never become grades."""
import json,pathlib,re,subprocess
from artifact_capture import CaptureError
from task_artifacts import SITE,descriptor

def discover_from_diff(task,text):
 if not isinstance(text,str):raise CaptureError('invalid Docker diff')
 paths=set()
 for line in text.splitlines():
  if len(line)<3 or line[:2] not in ['A ','C ','D ']:raise CaptureError('malformed Docker diff record')
  if line[:2] in ['A ','C ']:paths.add(line[2:])
 if task=='build-pmars':
  dirs=sorted(p for p in paths if re.fullmatch(r'/app/pmars-[A-Za-z0-9.+_-]+',p))
  if len(dirs)!=1:raise CaptureError('missing or ambiguous Debian source directory')
  dynamic={'source_directory':dirs[0]}
 elif task=='build-cython-ext':
  distributions=sorted(p for p in paths if p.startswith(SITE+'/pyknotid-') and p.endswith('.dist-info') and p.count('/')==SITE.count('/')+1)
  if distributions!=[SITE+'/pyknotid-0.5.3.dist-info']:raise CaptureError('unsupported or ambiguous installed package metadata')
  normal=SITE+'/pyknotid' in paths
  sidecars=sorted(p for p in paths if p.startswith(SITE+'/__editable__') and 'pyknotid' in pathlib.PurePosixPath(p).name and (p.endswith('.pth') or p.endswith('_finder.py')))
  if normal and sidecars:raise CaptureError('ambiguous normal/editable installation')
  dynamic={'distribution':distributions[0],'layout':'normal' if normal else 'editable'}
  if not normal:dynamic['sidecars']=sidecars
 else:dynamic={}
 descriptor(task,dynamic);return dynamic

def discover_stopped_layout(task,container,image_id,run=subprocess.run):
 metadata=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(metadata)!=1 or metadata[0]['Image']!=image_id or metadata[0]['State']['Running'] or metadata[0]['State'].get('Paused'):raise CaptureError('layout discovery requires matching stopped actor')
 if task not in ['build-pmars','build-cython-ext']:return discover_from_diff(task,'')
 diff=run(['docker','diff',container],capture_output=True,text=True,check=True,timeout=15).stdout
 return discover_from_diff(task,diff)
