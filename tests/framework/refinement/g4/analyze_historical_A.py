"""Original CLI estimate/lower-bound A analysis, NEVER provider repricing.
All original amounts preserved; incomplete totals make ratios undefined.
Separate historical instrumentation unit; paired task clusters/rounds retained.
"""
import collections,json,random
from native import H,sha
from analyze import percentile
from transport import save

def main():
 historical=json.loads((H/'historical-A.json').read_text());totals={};arms=['none','K','ours','Both','solpi','solpi_K'];pairs=[(a,b) for a in arms for b in ('none','K') if a!=b]
 for cell in historical['cells']:
  row=cell['original_row'];target=totals.setdefault((cell['task'],cell['arm']),dict(amount=0,solves=0,complete=True,cells=0));target['amount']+=row['total_tokens'];target['solves']+=row['resolved'] is True;target['complete']&=row['usage_complete'];target['cells']+=1
 tasks=sorted({task for task,arm in totals});rng=random.Random(2026101211);draws={a+'/'+b:[] for a,b in pairs}
 def ratio(sample,a,b):
  if not sample or any((task,a) not in totals or (task,b) not in totals for task in sample):return None
  aa=[totals[t,a] for t in sample];bb=[totals[t,b] for t in sample]
  if not all(r['complete'] for r in aa+bb):return None
  ca=sum(r['amount'] for r in aa);cb=sum(r['amount'] for r in bb);sa=sum(r['solves'] for r in aa);sb=sum(r['solves'] for r in bb)
  return ca*sb/(cb*sa) if sa and sb and cb else None
 for _ in range(20000):
  sample=rng.choices(tasks,k=len(tasks))
  for a,b in pairs:draws[a+'/'+b].append(ratio(sample,a,b))
 comparisons={}
 for a,b in pairs:
  values=draws[a+'/'+b];defined=[v for v in values if v is not None];comparisons[a+'/'+b]=dict(point=ratio(tasks,a,b),draws=values,defined_draws=len(defined),undefined_draws=20000-len(defined),bootstrap95=[percentile(defined,.025),percentile(defined,.975)],interval_conditional_on_defined_draws=len(defined)!=20000,cross_harness_informational_only=a.startswith('solpi'),new_upstream_unattempted=a.startswith('solpi'))
 save(H/'analysis-A-historical.json',dict(historical_source_sha256=sha(H/'historical-A.json'),analysis_source_sha256=sha(__file__),seed=2026101211,draws=20000,task_clusters=len(tasks),original_cells=len(historical['cells']),cost_unit='Original CLI query-pipeline estimate; incomplete records lower bound, NOT exact provider tokens or dollars',original_amounts_unchanged=True,no_cost_imputation=True,descriptive_only=True,comparisons=comparisons));print('Original148 cells/16 clusters;20k paired draws, CLI costs unchanged; fresh blocked ratios null')
if __name__=='__main__':main()
