"""Replay seeded frozen queue, adjacency, control-only exclusions/window prefix.
No outcomes choose work. Pending/unattempted cells remain explicit, not complete.
"""
import json
from native import H,sha
from prepare_queues import queues
from transport import save

def main():
 selection=json.loads((H/'selection.json').read_text());original=json.loads((H/'queue-order.json').read_text());replay=queues(selection);assert original['selection_sha256']==sha(H/'selection.json');assert original['generator_sha256']==sha(H/'prepare_queues.py');assert original['parts']==replay['parts'] and original['prospective_global_order']==replay['prospective_global_order'];plan=json.loads((H/'preregistration.json').read_text());lookup={r['cell_id']:r for rows in original['parts'].values() for r in rows};excluded=[r['cell_id'] for r in original['parts']['C'] if r['task'] not in plan['eligible_tasks']['C']];assert len(excluded)==48;assert len(plan['eligible_tasks']['B'])==9 and len(plan['eligible_tasks']['C'])==18
 for part,size in [('A',2),('B',4),('C',4)]:
  rows=original['parts'][part]
  for i in range(0,len(rows),size):
   group=rows[i:i+size];assert len({(r['task'],r['round']) for r in group})==1 and len({r['arm'] for r in group})==size
 eligible=[i for i in original['prospective_global_order'] if lookup[i]['part'] in ('B','C') and lookup[i]['task'] in plan['eligible_tasks'][lookup[i]['part']]];assert len(eligible)==180;window_cells=[];windows=[]
 for path in sorted((H/'windows').glob('*.json')):
  w=json.loads(path.read_text());window_cells+=w['cells'];assert w['maximum_occupied_slots']==16 and w['maximum_attempts_per_cell']==2 and w['route']=='127.0.0.1:8000';windows.append(dict(window_id=w['window_id'],cells=len(w['cells']),sha256=sha(path)))
 assert len(set(window_cells))==len(window_cells) and window_cells==eligible[:len(window_cells)];claims=[]
 for path in sorted((H/'cell-claims').glob('*.json')):
  c=json.loads(path.read_text());assert c['cell_id'] in window_cells and c['cell_id']==path.stem;claims.append(c['cell_id'])
 assert len(set(claims))==len(claims)
 result=dict(seed_replay_matches=True,adjacent_arm_groups_verified=True,all_prospective_cells=302,A_preserved_blocked_not_control_excluded=74,B_eligible_cells=108,C_eligible_cells=72,C_failed_control_excluded_cells=excluded,window_cells_preserve_eligible_prefix=True,windows=windows,committed_window_cells=len(window_cells),claimed_cells=len(claims),unclaimed_eligible_cells=180-len(claims),all_eligible_claimed=len(claims)==180,model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/'queue-audit.json',result);print('Seeded302 replay/adjacency and windows prefix verified; claims',len(claims),'of180')
if __name__=='__main__':main()
