"""G3 preregistration math: all attempt costs, final cell grade, task clusters.
Rows are one per planned cell, reconciling every retained attempt cost. Never
pool G1/G2. Unknown numerator costs forbid upper-bound acceptance; unknown
only in denominator permits G2-style conservative upper surrogate.
"""
import argparse,json,math,pathlib,random
ARMS=('none','K','candidate','Both')
PAIRS=(('candidate','none'),('Both','K'),('candidate','K'),('candidate','Both'),('K','none'),('Both','none'))
GATES=PAIRS[:3]
def ratio(a,b):
 return (a['tokens_lower_bound']/a['solves'])/(b['tokens_lower_bound']/b['solves']) if a['solves'] and b['solves'] and b['tokens_lower_bound'] else None
def percentile(values,p):
 v=sorted(values)[max(0,math.ceil(len(values)*p)-1)];return v if math.isfinite(v) else None
def analyze(rows,tasks,rounds,seed,repetitions=20000):
 ids=[(r['task'],r['round'],r['arm']) for r in rows];expected={(t,n,a) for t in tasks for n in rounds for a in ARMS}
 if len(ids)!=len(set(ids)) or set(ids)!=expected:raise ValueError('Exact unique complete planned roster required')
 if not tasks:raise ValueError('No control-valid tasks')
 if any(type(r['tokens_lower_bound']) is not int or r['tokens_lower_bound']<0 for r in rows):raise ValueError('Invalid cost lower bound')
 valid=all(r['grade_valid'] and r['solved'] in (True,False) for r in rows)
 totals={}
 for a in ARMS:
  rr=[r for r in rows if r['arm']==a];n=len(rr);solves=sum(r['grade_valid'] and r['solved'] is True for r in rr);tokens=sum(r['tokens_lower_bound'] for r in rr);known=all(r['cost_complete'] for r in rr);p=solves/n;z=1.959963984540054;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
  totals[a]=dict(cells=n,solves=solves,tokens_lower_bound=tokens,cost_complete=known,tokens_per_solve=tokens/solves if solves and known else None,tokens_per_solve_lower_bound=tokens/solves if solves else None,timeouts=sum(r.get('timeout',False) for r in rr),attempts=sum(r.get('attempts',1) for r in rr),wall_seconds=sum(r.get('wall_seconds',0) for r in rr),descriptive_wilson_95=[c-h,c+h],rounds={str(n):dict(solves=sum(r['solved'] is True and r['grade_valid'] for r in rr if r['round']==n),tokens_lower_bound=sum(r['tokens_lower_bound'] for r in rr if r['round']==n)) for n in rounds})
 bins={t:{a:dict(tokens_lower_bound=sum(r['tokens_lower_bound'] for r in rows if r['task']==t and r['arm']==a),solves=sum(r['grade_valid'] and r['solved'] is True for r in rows if r['task']==t and r['arm']==a)) for a in ARMS} for t in tasks}
 draws={pair:[] for pair in PAIRS};rng=random.Random(seed)
 if valid:
  for _ in range(repetitions):
   picked=rng.choices(tasks,k=len(tasks));v={a:dict(tokens_lower_bound=sum(bins[t][a]['tokens_lower_bound'] for t in picked),solves=sum(bins[t][a]['solves'] for t in picked)) for a in ARMS}
   for pair in PAIRS:
    q=ratio(v[pair[0]],v[pair[1]]);draws[pair].append(q if q is not None else math.inf)
 comparisons={}
 for x,y in PAIRS:
  a,b=totals[x],totals[y];q=ratio(a,b) if valid else None;s=draws[x,y];ci=[percentile(s,.025),percentile(s,.975)] if s else [None,None];upper_valid=valid and a['cost_complete'];relation='=' if a['cost_complete'] and b['cost_complete'] else '<=' if a['cost_complete'] else '>=' if b['cost_complete'] else 'unknown'
  quality=valid and a['solves']>=b['solves'];point=upper_valid and q is not None and a['tokens_lower_bound']*b['solves']*100<=b['tokens_lower_bound']*a['solves']*95;interval=upper_valid and ci[1] is not None and ci[1]<1
  comparisons[x+'/'+y]=dict(surrogate_ratio=q,true_ratio_relation=relation,surrogate_bootstrap_95=ci,interval_is_exact_cost_ratio=a['cost_complete'] and b['cost_complete'],conservative_upper_eligible=upper_valid,undefined_replicates=sum(not math.isfinite(v) for v in s),no_fewer_solves=quality,point_5_percent_met=point,interval_below_1=interval,gate=(x,y) in GATES,passes=point and interval and quality)
 futility=[comparisons['candidate/'+a] for a in ('none','K')]
 # Incomplete/invalid numerator evidence is inconclusive, not cost failure.
 futility_decidable=valid and all(c['conservative_upper_eligible'] and c['surrogate_ratio'] is not None for c in futility)
 negative=rounds==[1] and valid and (any(not c['no_fewer_solves'] for c in futility) or futility_decidable and any(not c['point_5_percent_met'] for c in futility))
 return dict(tasks=tasks,rounds=rounds,all_grades_valid=valid,raw_costs_complete=all(r['cost_complete'] for r in rows),aggregates=totals,comparisons=comparisons,round1_futility_decidable=futility_decidable,round1_negative_stop=negative,round1_survived=rounds==[1] and valid and all(c['no_fewer_solves'] and c['point_5_percent_met'] for c in futility),family_accepted=rounds==[1,2,3] and all(comparisons[x+'/'+y]['passes'] for x,y in GATES),bootstrap=dict(seed=seed,repetitions=repetitions,unit='task retaining all arms/rounds',undefined='+inf retained; null endpoint nonfinite',percentiles='nearest rank .025/.975'),quality_note='Wilson descriptive only; task repeats not independent population draws',cost_note='All retained attempt costs included; unknown costs not imputed. Surrogate intervals not exact intervals for unknown true ratios. Failed upper bounds do not prove true-ratio failure.')
def main():
 p=argparse.ArgumentParser();p.add_argument('audit',type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);p.add_argument('--rounds',type=int,required=True);a=p.parse_args();H=pathlib.Path(__file__).parent;plan=json.loads((H/'plan.json').read_text());v=json.loads(a.audit.read_text());rounds=list(range(1,a.rounds+1));result=analyze([r for r in v['rows'] if r['round'] in rounds],plan['tasks'],rounds,plan['bootstrap_seed']);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
