"""PMARS missing binary vs unsupported source layout;no actor/grader execution."""
import json,pathlib,re,subprocess,urllib.parse
from matched_html_support import DockerHTTP
from artifact_capture import CaptureError
BINARY='/usr/local/bin/pmars'
def classify(diff,binary_present):
 if type(binary_present)!=bool:raise CaptureError('missing PMARS binary presence proof')
 paths=set()
 for line in diff.splitlines():
  if len(line)<3 or line[:2] not in ['A ','C ','D ']:raise CaptureError('malformed Docker diff')
  if line[:2]!='D ':paths.add(line[2:])
 roots=sorted(p for p in paths if re.fullmatch(r'/app/pmars-[A-Za-z0-9.+_-]+',p))
 if len(roots)>1:raise CaptureError('ambiguous Debian source layout')
 if binary_present and len(roots)!=1:raise CaptureError('installed binary without supported source layout')
 return {'output_state':'present' if binary_present else 'absent','source_directory':roots[0] if roots else None,'binary_absent_verified':not binary_present,'unsupported_layout':False,'grading_verified':False,'cost_eligibility':False}
def classify_stopped(container,image_id,connection=DockerHTTP,run=subprocess.run):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned container')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();body=r.read(262145)
   if r.status!=200 or len(body)>262144:raise CaptureError('PMARS actor unavailable')
   x=json.loads(body)
   if x['Image']!=image_id or x['State']['Running'] or x['State'].get('Paused'):raise CaptureError('PMARS actor image/state changed')
   if any(m['Destination']=='/' or m['Destination'] in ['/app','/tests','/solution','/logs','/usr/local'] or m['Destination'].startswith(('/app/','/tests/','/solution/','/logs/','/usr/local/')) for m in x.get('Mounts',[])):raise CaptureError('PMARS actor exposes host output/trusted material')
   return x['Id']
  identity=inspect();diff=run(['docker','diff',container],capture_output=True,text=True,check=True,timeout=15).stdout;c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':BINARY}));r=c.getresponse();r.read()
  if r.status not in [200,404]:raise CaptureError('ambiguous PMARS binary presence')
  result=classify(diff,r.status==200)
  if inspect()!=identity:raise CaptureError('PMARS actor changed during inspection')
  result.update(stopped_actor_verified=True,image_id=image_id,container_id=identity,docker_diff=diff);return result
 finally:c.close()
