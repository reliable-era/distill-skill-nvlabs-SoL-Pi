"""Non-inference live quota polling through the owned API-only CONNECT proxy.
No host HOME/config mounts;token only via temporary /dev/shm docker-exec env.
Only numeric scope counters/status leave the client;never persist HTTP bodies,
auth headers,account identity,or exception text. Never create a paid model probe.
"""
import json,subprocess
from common import command
from security import read_token,env_file
CLIENT=r'''
import datetime,json,math,os,urllib.request,urllib.error
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
try:
 request=urllib.request.Request('https://api.anthropic.com/api/oauth/usage',headers={'Authorization':'Bearer '+os.environ['CLAUDE_CODE_OAUTH_TOKEN'],'anthropic-beta':'oauth-2025-04-20','Accept':'application/json'})
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:3128'}),NoRedirect())
 with opener.open(request,timeout=30) as response:
  body=json.loads(response.read(65537));headers={k.lower():v for k,v in response.headers.items()};scopes=[]
  for key,value in body.items():
   if not isinstance(value,dict) or not any(x in key for x in ('hour','day')):continue
   utilization=value.get('utilization');reset=value.get('resets_at')
   if type(utilization) not in (int,float) or not math.isfinite(utilization) or not 0<=utilization<=100 or not isinstance(reset,str):raise ValueError()
   epoch=datetime.datetime.fromisoformat(reset.replace('Z','+00:00')).timestamp()
   if not math.isfinite(epoch):raise ValueError()
   scopes.append(dict(rateLimitType=key,utilization=utilization/100,resetsAt=epoch,status='allowed'))
  if any(k.startswith('anthropic-ratelimit-unified-') and k.endswith('status') and v.lower() in ('rejected','denied') for k,v in headers.items()):
   print(json.dumps(dict(status=429)))
  else:
   by_name={s['rateLimitType']:s for s in scopes}
   for suffix,name in [('5h','five_hour'),('7d','seven_day'),('7d-opus','seven_day_opus'),('7d-sonnet','seven_day_sonnet')]:
    prefix='anthropic-ratelimit-unified-'+suffix
    if prefix+'-utilization' not in headers:continue
    u=float(headers[prefix+'-utilization']);r=float(headers[prefix+'-reset'])
    if not math.isfinite(u) or not 0<=u<=1 or not math.isfinite(r):raise ValueError()
    if name in by_name:
     if by_name[name]['resetsAt']!=r:raise ValueError()
     u=max(u,by_name[name]['utilization'])
    by_name[name]=dict(rateLimitType=name,utilization=u,resetsAt=r,status='allowed')
   if 'seven_day' not in by_name or 'five_hour' not in by_name:raise ValueError()
   print(json.dumps(dict(status=200,scopes=list(by_name.values()),source='live HTTP quota headers/provider numeric usage response;not reset-clock inference')))
except urllib.error.HTTPError as e:print(json.dumps(dict(status=e.code)))
except Exception:print(json.dumps(dict(status=None,error='Quota-only live refresh unavailable;no exception/body/auth persisted')))
'''

def refresh(network):
    obj=json.loads(command(['docker','inspect',network.proxy]).stdout)[0]
    assert obj['Config']['Labels'].get('solpi.g6')==network.root.name and obj['Config']['User']=='1000:1000'
    assert obj['HostConfig']['ReadonlyRootfs'] and 'ALL' in obj['HostConfig']['CapDrop']
    token=read_token()
    with env_file(token) as path:
        result=subprocess.run(['docker','exec','-i','--env-file',path,network.proxy,'python3','-'],input=CLIENT.encode(),capture_output=True,timeout=45)
    if token in result.stdout or token in result.stderr:raise RuntimeError('Credential literal hit during quota refresh')
    if result.returncode or result.stderr or len(result.stdout)>65536:raise RuntimeError('Quota refresh isolation/transport guard')
    data=json.loads(result.stdout)
    if set(data)-{'status','scopes','source','error'}:raise RuntimeError('Quota refresh unexpected metadata')
    return data
