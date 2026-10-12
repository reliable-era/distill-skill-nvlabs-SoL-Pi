"""Independent B/C20k task-weight resampling check of frozen analyzer.
No calls to analyzer totals/ratio/percentile; all rounds/retries retained.
Checks each draw, unknown/null handling and per-arm all-attempt metrics.
"""
import argparse,collections,json,math,pathlib,random
from native import sha
from transport import save

def independent(part,cells):
 arms=['none','K','ours','Both'];groups={};arm_rows={a:dict(cells=0,attempts=0,solves=0,failures=0,unknown_grades=0,known_tokens=0,unknown_cost_attempts=0,native_timeouts=0,grader_timeouts=0) for a in arms}
 for cell in cells:
  if cell['part']!=part or not cell['attempts']:continue
  task=cell['task'];arm=cell['arm'];g=groups.setdefault((task,arm),dict(cost=0,solves=0,unknown=False));g['solves']+=cell['verified_solved'] is True;r=arm_rows[arm];r['cells']+=1;r['solves']+=cell['verified_solved'] is True;r['failures']+=cell['verified_solved'] is False;r['unknown_grades']+=cell['verified_solved'] is None
  for attempt in cell['attempts']:
   value=attempt['exact_provider_tokens'];g['unknown']|=value is None;g['cost']+=attempt['known_tokens_lower_bound'];r['attempts']+=1;r['known_tokens']+=attempt['known_tokens_lower_bound'];r['unknown_cost_attempts']+=value is None;r['native_timeouts']+=attempt['native_timeout'];r['grader_timeouts']+=attempt['grader_timeout']
 tasks=sorted({t for t,a in groups});pairs=[(a,b) for a in arms for b in ('none','K') if a!=b];rng=random.Random({'B':2026101212,'C':2026101213}[part]);samples={a+'/'+b:[] for a,b in pairs}
 def ratio(weights,a,b):
  ac=bc=sa=sb=0
  if not weights:return None
  for t,n in weights.items():
   if (t,a) not in groups or (t,b) not in groups:return None
   x=groups[t,a];y=groups[t,b]
   if x['unknown'] or y['unknown']:return None
   ac+=n*x['cost'];bc+=n*y['cost'];sa+=n*x['solves'];sb+=n*y['solves']
  return ac*sb/(bc*sa) if sa and sb and bc else None
 for _ in range(20000):
  weights=collections.Counter(rng.choices(tasks,k=len(tasks))) if tasks else {}
  for a,b in pairs:samples[a+'/'+b].append(ratio(weights,a,b))
 return arm_rows,samples

def check(source,analysis,output):
 cells=json.loads(pathlib.Path(source).read_text())['cells'];primary=json.loads(pathlib.Path(analysis).read_text());errors=[];parts={}
 for part in ('B','C'):
  metrics,draws=independent(part,cells);original=primary['parts'][part]
  for arm,row in metrics.items():
   for field,value in row.items():
    if original['arms'][arm][field]!=value:errors.append(part+'/'+arm+'/'+field)
  for name,values in draws.items():
   expected=original['comparisons'][name]['draws']
   if len(values)!=len(expected) or any((x is None)!=(y is None) or x is not None and not math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12) for x,y in zip(values,expected)):errors.append(part+'/'+name+'/draws')
  parts[part]=dict(arms=metrics,paired_draws=draws,seed=original['seed'],draws=20000)
 save(output,dict(input_sha256=sha(source),primary_analysis_sha256=sha(analysis),independent_source_sha256=sha(__file__),parts=parts,errors=errors,verified=not errors,model_calls=0,not_a_goal_completion_audit=True));return errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('analysis');p.add_argument('output');a=p.parse_args();errors=check(a.input,a.analysis,a.output);print('Independent20k draw/metric discrepancies:',errors)
 if errors:raise SystemExit(1)
