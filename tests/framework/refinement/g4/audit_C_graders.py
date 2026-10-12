"""Independent actual C official grader resource/artifact/absence proofs.
Only recorded owned names inspected; no actors/models/grader reruns.
"""
import argparse,json,pathlib,subprocess
from native import H,sha
from transport import save

def audit(window):
 plan=json.loads((H/'preregistration.json').read_text());launch=json.loads((H/f'window-{window}-launch.json').read_text());root=pathlib.Path(launch['root']);cells=[i for i in json.loads((H/f'windows/{window}.json').read_text())['cells'] if i.startswith('g4-C-')];projection=H/f'window-{window}-C-grade-projection.json';repair={r['cell_id']:r for r in json.loads(projection.read_text())['rows']} if projection.exists() else {};proofs=[];pending=[];errors=[]
 for cell in cells:
  attempts=root/(cell+'-attempts.json')
  if not attempts.exists():pending.append(cell);continue
  row=json.loads(attempts.read_text())[-1];directory=pathlib.Path(repair[cell]['authoritative_grade_root']) if cell in repair else pathlib.Path(row['root'])/'grade';result=directory/'grade-result.json'
  if not result.exists():pending.append(cell);continue
  g=json.loads(result.read_text());bad=[]
  if not g['owned_containers_absent']:bad.append('cleanup flag')
  if not g['grade_valid']:bad.append('grade unavailable: retain explicit unknown, reconcile reason')
  if g['patch_sha256']!=row['patch_sha256'] or g['image_id']!=plan['images'][row['task']]:bad.append('patch/image identity')
  for relative,digest in g['artifacts'].items():
   if sha(directory/relative)!=digest:bad.append('original artifact changed:'+relative)
  owned=json.loads((directory/'owned.json').read_text())['names'];ins=json.loads((directory/'container-inspect.json').read_text());host=ins['HostConfig'];mounts=ins['Mounts']
  if not (host['NetworkMode']=='none' and host['Memory']==8*1024**3 and host['NanoCpus']==1000000000 and host['PidsLimit']==512 and not host['Privileged'] and not host.get('DeviceRequests')):bad.append('original resource regime')
  if not any(m['Destination']=='/wheelhouse' and m['Source']==plan['wheelhouse'] and m['RW'] is False for m in mounts):bad.append('readonly offline wheel regime')
  for name in owned:
   if not name.startswith('sweb.eval.'+row['task'].lower()+'.g4-grade-'):bad.append('ownership');continue
   p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
   if p.returncode==0 or 'No such' not in p.stderr:bad.append('actual owned absence:'+name)
  if bad:errors.append(dict(cell_id=cell,checks=bad))
  proofs.append(dict(cell_id=cell,grade_valid=g['grade_valid'],solved=g['solved'],grade_sha256=sha(result),inspect_sha256=sha(directory/'container-inspect.json'),owned_names=owned,all_checks_passed=not bad))
 r=dict(window=window,proofs=proofs,pending_cells=pending,errors=errors,official_grader_evidence_verified=not errors and not pending,model_calls=0,not_a_completion_audit=True);save(H/f'window-{window}-C-grader-audit.json',r);return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('C grader proofs',len(r['proofs']),'pending',r['pending_cells'],'errors',r['errors'])
