"""Actual attempt2 Docker image/resource/mount proofs, not A inspection."""
import json,pathlib
from native import H,BINARY,sha
from transport import save

def audit():
 plan=json.loads((H/'preregistration.json').read_text());root=pathlib.Path(json.loads((H/'BC-retry-launch.json').read_text())['root']);manifest=json.loads((H/'BC-retry-manifest.json').read_text());proofs=[];errors=[];pending=[]
 for c in manifest['rows']:
  cell=c['cell_id'];d=root/(cell+'-a2');record=d/'actor-inspect.json'
  if not record.exists():pending.append(cell);continue
  ins=json.loads(record.read_text());host=ins['HostConfig'];mounts={m['Destination']:m for m in ins['Mounts']};image=plan['images'][c['task']] if c['part']=='C' else plan['terminal_tasks'][c['task']]['image_id'];memory=8192 if c['part']=='C' else plan['terminal_tasks'][c['task']]['environment']['memory_mb'];bad=[]
  for condition,label in [(ins['Image']==image,'same frozen image'),(host['NanoCpus']==1000000000,'CPU1'),(host['Memory']==memory*1024**2,'memory'),(host['PidsLimit']==512,'pids512'),(host['NetworkMode']=='none','network-none'),(not host['Privileged'] and not host.get('DeviceRequests'),'nonprivileged/noGPU'),(ins['Config']['User']=='0','UID0'),(not any(p in mounts for p in ('/tests','/solution','/var/run/docker.sock')),'no gold/test/Docker mounts')]:
   if not condition:bad.append(label)
  for target,source in [('/skills',d/'skills'),('/opt/solpi/codex',BINARY),('/opt/solpi/relay.py',H/'relay.py'),('/broker',d/'transport/socket')]:
   if target not in mounts or mounts[target]['Source']!=str(source.resolve()) or mounts[target]['RW'] is not False:bad.append('readonly '+target)
  if c['part']=='C' and ('/wheelhouse' not in mounts or mounts['/wheelhouse']['Source']!=plan['wheelhouse'] or mounts['/wheelhouse']['RW'] is not False):bad.append('readonly frozen offline cache')
  if bad:errors.append(dict(cell_id=cell,checks=bad))
  proofs.append(dict(cell_id=cell,attempt=2,part=c['part'],arm=c['arm'],inspect_sha256=sha(record),image_id=ins['Image'],memory_mb=memory,all_checks_passed=not bad))
 result=dict(proofs=proofs,pending_cells=pending,errors=errors,all_actor_resources_verified=not errors and not pending,model_calls=0,not_a_goal_completion_audit=True,auditor_sha256=sha(__file__));save(H/'BC-retry-resource-audit.json',result);return result
if __name__=='__main__':
 r=audit();print('Attempt2 resource proofs',len(r['proofs']),'pending',r['pending_cells'],'errors',r['errors'])
