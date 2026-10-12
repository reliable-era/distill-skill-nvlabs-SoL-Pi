"""Actual all-attempt request/wall/output limits and once-only retry eligibility.
No models, no retries executed; denied requests remain explicit and uncharged
only where broker records forwarded=False. Unknown grade != native timeout.
"""
import argparse,json,pathlib
from native import H,sha
from scheduler_v2 import retry_eligible
from transport import save

def audit(window):
 root=pathlib.Path(json.loads((H/f'window-{window}-launch.json').read_text())['root']);cells=json.loads((H/f'windows/{window}.json').read_text())['cells'];proofs=[];pending=[];errors=[]
 for cell in cells:
  p=root/(cell+'-attempts.json')
  if not p.exists():pending.append(cell);continue
  rows=json.loads(p.read_text());bad=[]
  if not 1<=len(rows)<=2 or [r['attempt'] for r in rows]!=list(range(1,len(rows)+1)):bad.append('once-only retry/attempt sequence')
  if len(rows)==2 and not retry_eligible(rows[0]):bad.append('unproved infrastructure rerun')
  for r in rows:
   directory=pathlib.Path(r['root']);ledger=json.loads((directory/'transport/ledger.json').read_text());checks=[]
   if r['cell_id']!=cell or ledger['provider_POST']!=r['requests'] or not 0<=r['requests']<=60:checks.append('60-request cap/count')
   if r.get('wall_seconds') is not None and not 0<=r['wall_seconds']<=7200:checks.append('7200 native wall bound')
   for record in ledger['records']:
    req=json.loads((directory/f"transport/forwarded-request-{record['request']}.json").read_text())
    if req.get('max_output_tokens')!=16384:checks.append('16384 effective output limit')
   denials=ledger['budget_denials']
   if any(d.get('forwarded') is not False or d.get('reason') not in ('request_cap','wall_cap') for d in denials):checks.append('unproved unforwarded denial')
   if any(d['reason']=='request_cap' for d in denials) and r['requests']!=60:checks.append('cap refusal/count disagreement')
   if r.get('timeout') and len(rows)>r['attempt']:checks.append('native timeout rerun')
   if checks:bad+=checks
   proofs.append(dict(cell_id=cell,attempt=r['attempt'],requests=r['requests'],native_wall_seconds=r.get('wall_seconds'),native_timeout=r['timeout'],grader_timeout=r['grader_timeout'],request_cap_denials=sum(d['reason']=='request_cap' for d in denials),wall_cap_denials=sum(d['reason']=='wall_cap' for d in denials),ledger_sha256=sha(directory/'transport/ledger.json'),all_checks_passed=not checks))
  if bad:errors.append(dict(cell_id=cell,checks=bad))
 result=dict(window=window,proofs=proofs,pending=pending,errors=errors,all_caps_retries_verified=not errors and not pending,model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/f'window-{window}-caps-retries-audit.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('Caps/retry proofs',len(r['proofs']),'pending',r['pending'],'errors',r['errors'])
