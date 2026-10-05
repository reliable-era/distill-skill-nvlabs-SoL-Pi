"""Owned matched HTML stage helpers;no standalone inference entrypoint."""
import hashlib,http.client,json,pathlib,re,socket,subprocess,urllib.parse
from broker_session import ProspectiveSession
from reasoning_adapter import SOURCE_PINS,SOURCE,MODEL
from pinned_backend_connection import factory
from artifact_capture import CaptureError
PEER='127.0.0.1:18001'
PROVENANCE={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':PEER}
class PanelSession(ProspectiveSession):
 def __init__(self,raw):super().__init__(raw,{PEER:PROVENANCE})
 def forward(self,path,body,emit):return super().forward(path,body,emit,connect=factory(PEER))
 def accounting_rows(self,actor):
  views={x['request']:x['accounting_view'] for x in self.prospective_records if x['actor']==actor};rows=[]
  for row in self.raw_session.records:
   if row['actor']!=actor:continue
   if row['request'] not in views:raise RuntimeError('unmatched prospective receipt')
   view=views[row['request']];cost=view['derived_cost'];rows.append({**row,'raw_usage_audit':row['usage_audit'],'usage_audit':cost,'usage_complete':cost.get('provider_cost_complete') is True,'raw_provider_protocol_valid':view['raw_provider_protocol_valid'],'correction_applied':view['correction_applied']})
  return rows

def verify_live_sources():
 root='/sgl-workspace/sglang/python/sglang/';files={'dflash_worker_sha256':root+'srt/speculative/dflash_worker_v2.py','dflash_utils_sha256':root+'srt/speculative/dflash_utils.py','schedule_batch_sha256':root+'srt/managers/schedule_batch.py','dflash_kernel_sha256':root+'kernels/ops/speculative/dflash.py','output_streamer_sha256':root+'srt/managers/scheduler_components/output_streamer.py'};result=[]
 for name in ['jev-pi-qwen38-replica-20261004-nccl-only','ykw-qwen38-dflash2-tp2']:
  info=json.loads(subprocess.check_output(['docker','inspect',name],text=True,timeout=10))[0];cmd=info['Config'].get('Cmd') or [];assert info['State']['Running'] and not info['State']['Paused'] and 'DFLASH' in ' '.join(cmd) and '--speculative-num-draft-tokens 8' in ' '.join(cmd)
  raw=subprocess.check_output(['docker','exec',name,'sha256sum',*files.values()],text=True,timeout=15);pins={k:line.split()[0] for k,line in zip(files,raw.splitlines())};assert pins=={**SOURCE_PINS,'output_streamer_sha256':SOURCE};result.append({'name':name,'id':info['Id'],'source_pins':pins,'custom_all_reduce_disabled':'--disable-custom-all-reduce' in cmd})
 c=http.client.HTTPConnection('127.0.0.1',18001,timeout=3)
 try:
  c.request('GET','/v1/models');response=c.getresponse();body=response.read(65537)
  if response.status!=200 or len(body)>65536 or not any(x['id']==MODEL for x in json.loads(body)['data']):raise RuntimeError('pinned Qwen model advertisement changed')
 finally:c.close()
 return result
class DockerHTTP(http.client.HTTPConnection):
 def __init__(self):super().__init__('owned-docker',timeout=5)
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(5);self.sock.connect('/var/run/docker.sock')
def stopped_output_present(container,image_id,connection=DockerHTTP):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',container):raise CaptureError('invalid owned container identifier')
 c=connection()
 try:
  def inspect():
   c.request('GET','/v1.41/containers/'+container+'/json');r=c.getresponse();body=r.read(262145)
   if r.status!=200 or len(body)>262144:raise CaptureError('stopped actor identity unavailable')
   value=json.loads(body)
   if value['Image']!=image_id or value['State']['Running'] or value['State'].get('Paused'):raise CaptureError('actor image/state invalid')
   return value['Id']
  identifier=inspect();c.request('HEAD','/v1.41/containers/'+container+'/archive?'+urllib.parse.urlencode({'path':'/app/out.html'}));r=c.getresponse();r.read()
  if r.status==200:return True
  if r.status==404:
   if inspect()!=identifier:raise CaptureError('actor identity changed during missing-output check')
   return False
  raise CaptureError('ambiguous archive presence response')
 finally:c.close()
