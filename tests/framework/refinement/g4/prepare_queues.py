"""Freeze ALL302 prospective cell orders before inference; no run authorization.
Failed controls can only mark cells ineligible, never replace/resample/reorder.
Historical Claude rows are reused and are NOT new queue cells.
"""
import hashlib,json,pathlib,random
H=pathlib.Path(__file__).resolve().parent
def shuffled_groups(units,arms,seed,part):
 rng=random.Random(seed);units=list(units);rng.shuffle(units);rows=[]
 for task,round in units:
  order=list(arms);rng.shuffle(order)
  rows.extend(dict(part=part,task=task,round=round,arm=arm) for arm in order)
 return rows

def queues(selection):
 seeds=selection['queue_seeds'];a=selection['part_A'];units=[]
 for split in ('dev','heldout'):
  for task in a['synthetic_'+split]:
   units.extend(('diagnostic/'+split+'/'+task,r) for r in range(1,a['synthetic_rounds'][split]+1))
 units.extend(('swe/'+t,r) for t in a['swe_tasks'] for r in range(1,a['swe_rounds']+1));A=shuffled_groups(units,a['arms'],seeds['A'],'A');B=[]
 for r in (1,2,3):B+=shuffled_groups([(t,r) for t in selection['part_B']['tasks']],['none','K','ours','Both'],seeds['B_round'+str(r)],'B')
 C=shuffled_groups([(t,1) for t in selection['part_C']['selected_in_draw_order']],['none','K','ours','Both'],seeds['C'],'C')
 for part,rows in [('A',A),('B',B),('C',C)]:
  for i,row in enumerate(rows,1):row['cell_id']='g4-'+part+'-'+str(i).zfill(3)
 assert [len(A),len(B),len(C)]==[74,108,120]
 bc=[]
 for i in range(max(len(B),len(C))//4):bc+=B[i*4:i*4+4]+C[i*4:i*4+4]
 return dict(parts=dict(A=A,B=B,C=C),prospective_global_order=[r['cell_id'] for r in bc+A],queue_seeds=seeds,status='ORDER_ONLY_NOT_FULL_PREREGISTRATION_OR_INFERENCE_AUTHORIZATION',eligibility_policy='Only failed controls exclude cells; no substitution/resampling/reordering',A_launch_policy='After B/C; upstream source/security/startup requirements must be satisfied or report blocked',historical_Claude_new_cells=0)
def main():
 p=H/'queue-order.json'
 if p.exists():raise RuntimeError('Existing immutable order; verify it rather than regenerate')
 source=(H/'selection.json').read_bytes();v=queues(json.loads(source));v.update(selection_sha256=hashlib.sha256(source).hexdigest(),generator_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest());p.write_text(json.dumps(v,indent=2)+'\n')
if __name__=='__main__':main()
