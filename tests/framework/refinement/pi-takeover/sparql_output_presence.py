"""Sparql-onlystopped-outputpresence;notgradeorqualityinference."""
import json,re,urllib.parse
from matched_html_support import DockerHTTP
from artifact_capture import CaptureError
PATH='/app/solution.sparql'
def stopped_output_present(container,image_id,connection=DockerHTTP):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned actor identifier')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();body=r.read(262145)
   if r.status!=200 or len(body)>262144:raise CaptureError('actor identity unavailable')
   v=json.loads(body)
   if v['Image']!=image_id or v['State']['Running'] or v['State'].get('Paused'):raise CaptureError('actor image/state invalid')
   if any(m['Destination']=='/' or m['Destination'] in ['/tests','/solution','/logs','/broker'] or any(m['Destination'].startswith(p+'/') for p in ['/tests','/solution','/logs','/broker']) for m in v.get('Mounts',[])):raise CaptureError('trusted material exposed')
   return v['Id']
  identity=inspect();c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':PATH}));r=c.getresponse();r.read()
  if r.status==200:return True
  if r.status==404:
   if inspect()!=identity:raise CaptureError('actor identity changed')
   return False
  raise CaptureError('ambiguous archive response')
 finally:c.close()
