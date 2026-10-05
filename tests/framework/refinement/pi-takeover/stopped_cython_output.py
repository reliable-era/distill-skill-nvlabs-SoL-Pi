"""Classify known absent Cython installation separately from unsupported layouts."""
import json,re,subprocess,urllib.parse
from matched_html_support import DockerHTTP
from discover_task_layout import discover_from_diff
from task_artifacts import SITE
from artifact_capture import CaptureError
PATHS=[SITE+'/pyknotid-0.5.3.dist-info',SITE+'/pyknotid',SITE+'/__editable__.pyknotid-0.5.3.pth',SITE+'/__editable___pyknotid_0_5_3_finder.py']

def classify(diff,present):
 if set(present)!=set(PATHS) or any(type(v)!=bool for v in present.values()):raise CaptureError('incomplete presence proof')
 changed=[]
 for line in diff.splitlines():
  if len(line)<3 or line[:2] not in ['A ','C ','D ']:raise CaptureError('malformed Docker diff')
  if line[:2]!='D ':changed.append(line[2:])
 installations=[p for p in changed if '/site-packages/' in p and (path_root(p).startswith('pyknotid') or ('__editable__' in path_root(p) and 'pyknotid' in path_root(p)))]
 if not any(present.values()) and not installations:return {'output_state':'absent','installation_absent_verified':True,'unsupported_layout':False,'grading_verified':False,'cost_eligibility':False,'source_transfer_pending':True}
 # Any alternate package/site or contradictory evidence is not a quality failure.
 if any(not p.startswith(SITE+'/') for p in installations):raise CaptureError('unsupported installation site')
 if not present[PATHS[0]]:raise CaptureError('incomplete or unsupported installation metadata')
 dynamic=discover_from_diff('build-cython-ext',diff)
 expected={PATHS[0],PATHS[1]} if dynamic['layout']=='normal' else {PATHS[0],*dynamic['sidecars']}
 if {p for p,v in present.items() if v}!=expected:raise CaptureError('contradictory layout presence')
 return {'output_state':'present','dynamic':dynamic,'unsupported_layout':False}

def path_root(path):return path.split('/site-packages/',1)[1].split('/',1)[0]

def classify_stopped(container,image_id,connection=DockerHTTP,run=subprocess.run):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned container')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();body=r.read(262145)
   if r.status!=200 or len(body)>262144:raise CaptureError('stopped actor unavailable')
   x=json.loads(body)
   if x['Image']!=image_id or x['State']['Running'] or x['State'].get('Paused'):raise CaptureError('wrong actor image/state')
   return x['Id']
  identity=inspect();diff=run(['docker','diff',container],capture_output=True,text=True,check=True,timeout=15).stdout;present={}
  for path in PATHS:
   c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':path}));r=c.getresponse();r.read()
   if r.status not in [200,404]:raise CaptureError('ambiguous artifact presence')
   present[path]=r.status==200
  if inspect()!=identity:raise CaptureError('actor changed during classification')
  result=classify(diff,present);result.update(stopped_actor_verified=True,image_id=image_id,container_id=identity,presence=present,docker_diff=diff);return result
 finally:c.close()
