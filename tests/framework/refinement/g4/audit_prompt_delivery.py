"""Verify frozen task/budget/ordered skill bytes reach original AND forwarded POST.
No actor/model calls; only retained request artifacts and local frozen sources.
"""
import argparse,json,pathlib
from native import H,sha
from transport import save
BUDGET='Run budget:60 model requests/7200s wall/16384 output tokens per request. Work only on this task; no network retrieval or subagents. Supplied resources are in /skills.\n'

def text_messages(request):
 return [c['text'] for i in request.get('input',[]) if i.get('role')=='user' for c in i.get('content',[]) if c.get('type')=='input_text']
def audit(window):
 plan=json.loads((H/'preregistration.json').read_text());order=json.loads((H/'queue-order.json').read_text());lookup={r['cell_id']:r for rows in order['parts'].values() for r in rows};root=pathlib.Path(json.loads((H/f'window-{window}-launch.json').read_text())['root']);proofs=[];pending=[];errors=[]
 for cell in json.loads((H/f'windows/{window}.json').read_text())['cells']:
  paths=sorted(p for p in root.glob(cell+'-a*') if p.is_dir())
  if not paths:pending.append(cell);continue
  for directory in paths:
   c=lookup[cell];skills=plan['arm_skills'][c['arm']];bad=[]
   if c['part']=='B':
    source=pathlib.Path(plan['terminal_source'])/c['task'];metadata=plan['terminal_tasks'][c['task']]
    for relative,digest in metadata['source_hashes'].items():
     if sha(source/relative)!=digest:bad.append('original task source')
    expected=(source/'instruction.md').read_text()+'\n\n'+BUDGET
   else:
    source=pathlib.Path(plan['prepared_tasks'][c['task']]);manifest=json.loads((source/'manifest.json').read_text())
    if sha(source/'prompt.txt')!=manifest['prompt_sha256']:bad.append('frozen task prompt')
    expected=(source/'prompt.txt').read_text()+'\n'+BUDGET
   for skill in skills:
    source=pathlib.Path(plan['skills'][skill]['path'])
    if sha(source/'SKILL.md')!=plan['skills'][skill]['SKILL_sha256']:bad.append('frozen skill')
    expected+='\n'+(source/'SKILL.md').read_text()
    for p in source.rglob('*'):
     if p.is_file() and sha(p)!=sha(directory/'skills'/skill/p.relative_to(source)):bad.append('copied skill tree bytes')
   if not skills:expected+='\nNo skill is supplied.\n'
   if (directory/'prompt.txt').read_text()!=expected:bad.append('task/budget/skill order prompt')
   if sorted(p.name for p in (directory/'skills').iterdir())!=sorted(skills):bad.append('unexpected arm skill tree')
   hashes={};requests=[directory/'transport/request-1.json',directory/'transport/forwarded-request-1.json']
   if not all(p.exists() for p in requests):pending.append(directory.name);continue
   for path in requests:
    texts=text_messages(json.loads(path.read_text()))
    if texts.count(expected)!=1:bad.append('exact initial user prompt missing/duplicated:'+path.name)
    hashes[path.name]=sha(path)
   if bad:errors.append(dict(attempt=directory.name,checks=bad))
   proofs.append(dict(attempt=directory.name,cell_id=cell,part=c['part'],arm=c['arm'],ordered_skills=skills,prompt_sha256=sha(directory/'prompt.txt'),request_hashes=hashes,all_checks_passed=not bad))
 result=dict(window=window,proofs=proofs,pending=pending,errors=errors,all_prompt_deliveries_verified=not errors and not pending,model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/f'window-{window}-prompt-delivery-audit.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('Actual prompt proofs',len(r['proofs']),'pending',r['pending'],'errors',r['errors'])
