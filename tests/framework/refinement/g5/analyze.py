"""G5-only paired issue-cluster analysis; no cost/grade imputation.
Primary cost ratio is tokens per verified solve; total-token ratio is also
reported. All-attempt costs, last-attempt quality,20k shared paired draws.
Undefined draws stay private and counted; intervals conditional if any nulls.
"""
import collections,json,math,pathlib,random
from common import H,private_root,save,sha
ARMS=('none','K','ours','Both')
PAIRS=(('ours','none'),('ours','K'),('Both','none'),('Both','K'))

def panel(rows,eligible):
 by={};eligible=set(eligible)
 for r in rows:
  key=(r['task'],r['arm']);assert key not in by and r['task'] in eligible and r['arm'] in ARMS
  a=r['attempt_rows'];assert 1<=len(a)<=2 and [x['attempt'] for x in a]==list(range(1,len(a)+1));assert r['scored_attempt']==a[-1]['attempt'];assert r['solved']==(a[-1]['solved'] if a[-1]['grade_valid'] else None)
  for k in ('requests','known_tokens_lower_bound'):assert r[k]==sum(x[k] for x in a)
  assert r['cost_complete']==all(x['cost_complete'] for x in a)
  assert all(x['task']==r['task'] and x['arm']==r['arm'] for x in a)
  by[key]=r
 assert set(by)=={(t,a) for t in eligible for a in ARMS},'Incomplete/extra four-arm panel'
 return sorted(eligible),by

def aggregate(tasks,by):
 out={}
 for arm in ARMS:
  rs=[by[t,arm] for t in tasks];known=sum(r['known_tokens_lower_bound'] for r in rs);solves=sum(r['solved'] is True for r in rs);missing=sum(r['solved'] is None for r in rs);complete=all(r['cost_complete'] for r in rs)
  out[arm]=dict(cells=len(rs),solves=solves,unavailable_grades=missing,attempts=sum(len(r['attempt_rows']) for r in rs),requests=sum(r['requests'] for r in rs),known_tokens_lower_bound=known,total_tokens=known if complete else None,cost_complete=complete,unknown_cost_cells=sum(not r['cost_complete'] for r in rs),tokens_per_verified_solve=known/solves if complete and solves and not missing else None,known_tokens_per_observed_verified_solve=known/solves if solves else None,native_timeouts=sum(r.get('native_timeouts',sum(x['timeout'] for x in r['attempt_rows'])) for r in rs),grader_timeouts=sum(r.get('grader_timeouts',sum(x['grader_timeout'] for x in r['attempt_rows'])) for r in rs))
 return out

def ratios(stats,a,b):
 x,y=stats[a],stats[b]
 if not x['cost_complete'] or not y['cost_complete']:return dict(total_tokens=None,tokens_per_verified_solve=None,null_reason='unknown_cost')
 total=x['total_tokens']/y['total_tokens'] if y['total_tokens'] else None
 if x['unavailable_grades'] or y['unavailable_grades']:return dict(total_tokens=total,tokens_per_verified_solve=None,null_reason='unavailable_grade')
 tps=x['tokens_per_verified_solve']/y['tokens_per_verified_solve'] if x['tokens_per_verified_solve'] is not None and y['tokens_per_verified_solve'] else None
 return dict(total_tokens=total,tokens_per_verified_solve=tps,null_reason=None if tps is not None else 'zero_solve_or_zero_denominator')

def percentile(values,q):
 values=sorted(values);assert values;position=(len(values)-1)*q;lo=math.floor(position);hi=math.ceil(position);return values[lo]+(values[hi]-values[lo])*(position-lo)

def interval(values):
 defined=[x for x in values if x is not None];return dict(defined_draws=len(defined),undefined_draws=len(values)-len(defined),percentile_95=[percentile(defined,.025),percentile(defined,.975)] if defined else None,coverage='conditional_on_defined_draws' if len(defined)!=len(values) else 'all_draws_defined',undefined_draws_not_imputed=True)

def bootstrap(rows,eligible,seed=2026101402,draws=20000,private_draw_file=None):
 tasks,by=panel(rows,eligible);stats=aggregate(tasks,by);rng=random.Random(seed);values={a+'/'+b:dict(total_tokens=[],tokens_per_verified_solve=[],null_reasons=collections.Counter()) for a,b in PAIRS};out=open(private_draw_file,'x') if private_draw_file else None
 try:
  for n in range(draws):
   sample=[tasks[rng.randrange(len(tasks))] for _ in tasks] if tasks else [];s=aggregate(sample,by);draw={}
   for a,b in PAIRS:
    key=a+'/'+b;r=ratios(s,a,b);draw[key]=r
    for metric in ('total_tokens','tokens_per_verified_solve'):values[key][metric].append(r[metric])
    if r['null_reason']:values[key]['null_reasons'][r['null_reason']]+=1
   if out:out.write(json.dumps(dict(draw=n,task_multiplicities=dict(collections.Counter(sample)),ratios=draw),separators=(',',':'))+'\n')
 finally:
  if out:out.close()
 comparisons={a+'/'+b:dict(point=ratios(stats,a,b),total_token_ratio=interval(values[a+'/'+b]['total_tokens']),tokens_per_verified_solve_ratio=interval(values[a+'/'+b]['tokens_per_verified_solve']),null_reasons=dict(values[a+'/'+b]['null_reasons'])) for a,b in PAIRS}
 return dict(benchmark='G5 only; not pooled',eligible_issues=len(tasks),arms=stats,comparisons=comparisons,bootstrap=dict(seed=seed,draws=draws,unit='issue retaining four arms and all attempts',algorithm='sorted eligible IDs; Python Random.randrange(n),n draws with replacement per replicate; identical multiplicities for all arms/comparisons',interval='linear percentile2.5/97.5; conditional if nulls',private_draws_sha256=sha(private_draw_file) if private_draw_file else None),interpretation='Descriptive only; unknown costs/grades not imputed; no inferred savings from ratios of lower bounds')

def main():
 root=private_root();c=json.loads((root/'controls-complete.json').read_text());done=json.loads((root/'models-complete.json').read_text());rows=json.loads((root/'model-summary.json').read_text());assert done['cells']==len(rows)==4*len(c['eligible_tasks']);drawfile=root/'analysis-draws.jsonl';result=bootstrap(rows,c['eligible_tasks'],private_draw_file=drawfile);result['input_sha256']=sha(root/'model-summary.json');save(root/'analysis.json',result);save(H/'analysis-summary.json',result)
if __name__=='__main__':main()
