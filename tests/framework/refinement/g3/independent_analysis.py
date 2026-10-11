"""Supplemental independent verification, never a replacement analysis or gate.
Use only complete analyzed rosters after the actual round-boundary certificate.
Counter-weighted integer task vectors independently reproduce every point and
20,000 paired task-cluster intervals, including retained undefined draws.
"""
import argparse,collections,hashlib,json,math,pathlib,random
ARMS=('none','K','candidate','Both')
PAIRS=(('candidate','none'),('Both','K'),('candidate','K'),('candidate','Both'),('K','none'),('Both','none'))
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def check(audit,analysis,plan,boundary):
 assert boundary['rounds']==analysis['rounds'] and boundary['status']=='COMPLETE_ROUND_BOUNDARY_NOT_ACCEPTANCE'
 assert all(boundary[k] for k in ('full2352_schedule_reproduced','first_admissions_exact_frozen_order','rounds_not_interleaved','all_attempts_accounted','all_prior_workers_owned_containers_absent','no_partial_gate'))
 rows=[r for r in audit['rows'] if r['round'] in analysis['rounds']];tasks=plan['tasks'];rounds=analysis['rounds']
 keys=[(r['task'],r['round'],r['arm']) for r in rows]
 assert boundary['exact_cells']==len(rows)
 assert len(keys)==len(set(keys)) and set(keys)=={(t,n,a) for t in tasks for n in rounds for a in ARMS}
 assert analysis['tasks']==tasks and all(r['grade_valid'] and type(r['solved']) is bool and type(r['tokens_lower_bound']) is int and r['tokens_lower_bound']>=0 for r in rows)
 vectors={t:{a:[0,0] for a in ARMS} for t in tasks};totals={a:[0,0] for a in ARMS}
 for r in rows:
  a=r['arm'];cost=r['tokens_lower_bound'];solve=int(r['solved']);vectors[r['task']][a][0]+=cost;vectors[r['task']][a][1]+=solve;totals[a][0]+=cost;totals[a][1]+=solve
 for a in ARMS:
  rr=[r for r in rows if r['arm']==a];v=analysis['aggregates'][a];assert totals[a]==[v['tokens_lower_bound'],v['solves']];assert v['cells']==len(rr) and v['attempts']==sum(r['attempts'] for r in rr) and v['timeouts']==sum(r['timeout'] for r in rr) and v['cost_complete']==all(r['cost_complete'] for r in rr)
  for n in rounds:assert v['rounds'][str(n)]==dict(solves=sum(r['solved'] for r in rr if r['round']==n),tokens_lower_bound=sum(r['tokens_lower_bound'] for r in rr if r['round']==n))
 def quotient(v,p):
  x,y=p;tx,sx=v[x];ty,sy=v[y]
  return (tx/sx)/(ty/sy) if sx and sy and ty else math.inf
 rng=random.Random(plan['bootstrap_seed']);distributions={p:[] for p in PAIRS};repetitions=analysis['bootstrap']['repetitions'];assert repetitions==20000 and analysis['bootstrap']['seed']==plan['bootstrap_seed']
 for _ in range(repetitions):
  weights=collections.Counter(rng.choices(tasks,k=len(tasks)));sample={a:[0,0] for a in ARMS}
  for t,w in weights.items():
   for a in ARMS:
    sample[a][0]+=w*vectors[t][a][0];sample[a][1]+=w*vectors[t][a][1]
  for p in PAIRS:distributions[p].append(quotient(sample,p))
 comparisons={}
 for p in PAIRS:
  x,y=p;v=analysis['comparisons'][x+'/'+y];q=quotient(totals,p);assert v['surrogate_ratio']==(q if math.isfinite(q) else None);d=sorted(distributions[p]);ci=[d[math.ceil(repetitions*f)-1] for f in (.025,.975)];ci=[z if math.isfinite(z) else None for z in ci];assert v['surrogate_bootstrap_95']==ci and v['undefined_replicates']==sum(not math.isfinite(z) for z in d)
  upper=all(r['cost_complete'] for r in rows if r['arm']==x);denominator_known=all(r['cost_complete'] for r in rows if r['arm']==y);assert v['conservative_upper_eligible']==upper and v['interval_is_exact_cost_ratio']==(upper and denominator_known);assert v['true_ratio_relation']==('=' if upper and denominator_known else '<=' if upper else '>=' if denominator_known else 'unknown');tx,sx=totals[x];ty,sy=totals[y];point=upper and math.isfinite(q) and tx*sy*100<=ty*sx*95;quality=sx>=sy;interval=upper and ci[1] is not None and ci[1]<1
  assert v['point_5_percent_met']==point and v['no_fewer_solves']==quality and v['interval_below_1']==interval and v['passes']==(point and quality and interval)
  comparisons[x+'/'+y]=dict(integer_5_percent_met=point,no_fewer_solves=quality,ratio=q if math.isfinite(q) else None,paired_bootstrap_95=ci,undefined_replicates=v['undefined_replicates'])
 decidable=all(r['cost_complete'] for r in rows if r['arm']=='candidate') and all(comparisons['candidate/'+a]['ratio'] is not None for a in ('none','K'));assert analysis['round1_futility_decidable']==decidable
 futility=rounds==[1] and (any(not comparisons['candidate/'+a]['no_fewer_solves'] for a in ('none','K')) or decidable and any(not comparisons['candidate/'+a]['integer_5_percent_met'] for a in ('none','K')))
 assert analysis['round1_negative_stop']==futility
 assert analysis['round1_survived']==(rounds==[1] and all(comparisons['candidate/'+a]['no_fewer_solves'] and comparisons['candidate/'+a]['integer_5_percent_met'] for a in ('none','K')))
 assert analysis['family_accepted']==(rounds==[1,2,3] and all(analysis['comparisons'][x+'/'+y]['passes'] for x,y in PAIRS[:3]))
 return dict(status='INDEPENDENT_INTEGER_AND_PAIRED_BOOTSTRAP_REPRODUCED_NOT_COMPLETION',cells=len(rows),rounds=rounds,repetitions=repetitions,comparisons=comparisons,round1_negative_stop=futility,family_accepted=analysis['family_accepted'],costs_complete=all(r['cost_complete'] for r in rows),original_grade_timeout_projections=audit.get('grade_timeout_repairs',[]))
def main():
 p=argparse.ArgumentParser();p.add_argument('audit',type=pathlib.Path);p.add_argument('analysis',type=pathlib.Path);p.add_argument('boundary',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();H=pathlib.Path(__file__).parent;load=lambda f:json.loads(f.read_text());b=load(a.boundary);assert b['audit_sha256']==digest(a.audit) and b['plan_sha256']==digest(H/'plan.json');v=check(load(a.audit),load(a.analysis),load(H/'plan.json'),b);v['inputs_sha256']={str(f):digest(f) for f in (a.audit,a.analysis,a.boundary,H/'plan.json',pathlib.Path(__file__))};a.output.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v[k] for k in ('status','cells','rounds','round1_negative_stop','family_accepted')}))
if __name__=='__main__':main()
