"""Independent saved Docker inspect resource/mount/image checks, zero models.
Does not inspect or intervene unrelated containers/services. Actor proofs only;
original grader/control resource evidence remains a separate requirement.
"""
import argparse,json,pathlib
from native import H,BINARY,sha
from transport import save

def audit(window):
 plan=json.loads((H/'preregistration.json').read_text());launch=json.loads((H/f'window-{window}-launch.json').read_text());root=pathlib.Path(launch['root']);cells=json.loads((H/f'windows/{window}.json').read_text())['cells'];order=json.loads((H/'queue-order.json').read_text());lookup={c['cell_id']:c for rows in order['parts'].values() for c in rows};proofs=[];errors=[];pending=[]
 for cell in cells:
  directory=root/(cell+'-a1');record=directory/'actor-inspect.json'
  if not record.exists():pending.append(cell);continue
  c=lookup[cell];ins=json.loads(record.read_text());host=ins['HostConfig'];mounts={m['Destination']:m for m in ins['Mounts']};image=plan['images'][c['task']] if c['part']=='C' else plan['terminal_tasks'][c['task']]['image_id'];memory=8192 if c['part']=='C' else plan['terminal_tasks'][c['task']]['environment']['memory_mb'];bad=[]
  for condition,label in [(ins['Image']==image,'image'),(host['NanoCpus']==1000000000,'CPU1'),(host['Memory']==memory*1024**2,'memory'),(host['PidsLimit']==512,'pids512'),(host['NetworkMode']=='none','network-none'),(not host['Privileged'] and not host.get('DeviceRequests'),'nonprivileged/noGPU'),(ins['Config']['User']=='0','actor UID0'),(not any(p in mounts for p in ('/tests','/solution','/var/run/docker.sock')),'no hidden grader/gold/Docker mounts')]:
   if not condition:bad.append(label)
  for target,source in [('/skills',directory/'skills'),('/opt/solpi/codex',BINARY),('/opt/solpi/relay.py',H/'relay.py'),('/broker',directory/'transport/socket')]:
   if target not in mounts or mounts[target]['Source']!=str(source.resolve()) or mounts[target]['RW'] is not False:bad.append('readonly '+target)
  if c['part']=='C' and ('/wheelhouse' not in mounts or mounts['/wheelhouse']['Source']!=plan['wheelhouse'] or mounts['/wheelhouse']['RW'] is not False):bad.append('same readonly offline cache')
  if bad:errors.append(dict(cell_id=cell,checks=bad))
  proofs.append(dict(cell_id=cell,inspect_sha256=sha(record),image_id=ins['Image'],memory_mb=memory,all_checks_passed=not bad))
 result=dict(window=window,proofs=proofs,pending_cells=pending,errors=errors,all_actor_resources_verified=not errors and not pending,model_calls=0,not_a_completion_audit=True);save(H/f'window-{window}-actor-resource-audit.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('Actor resource proofs',len(r['proofs']),'pending',r['pending_cells'],'errors',r['errors'])
