"""Descriptive G4 analysis only: no acceptance/futility/promotion decisions.
Input: audited canonical cells {part,task,arm,round,attempts,verified_solved}.
Each attempt has exact_provider_tokens:int|null, known_tokens_lower_bound:int,
native_timeout/grader_timeout booleans. ALL attempts, including infra retries,
are charged. Historical A amounts must be ORIGINAL reported amounts, never
reconstructed from rounded tables or repriced. Empty attempts = unattempted.
Response model/usage/receipt evidence remains in the input provenance; no
variant grouping or model-share report. Analysis never makes provider calls.
"""
import argparse,collections,hashlib,json,math,pathlib,random
DRAWS=20000
SEEDS={'A':2026101211,'B':2026101212,'C':2026101213}
ARMS={'A':['none','K','ours','Both','solpi','solpi_K'],'B':['none','K','ours','Both'],'C':['none','K','ours','Both']}
def amount(value):
 if value is not None and (type(value) is not int or value<0):raise ValueError('Token amount must be exact nonnegative integer or null')
 return value

def task_totals(cells):
 totals={};seen=set()
 for cell in cells:
  key=(cell['task'],cell['arm'],cell['round'])
  if key in seen:raise ValueError('Duplicate canonical cell; retries belong inside attempts')
  seen.add(key);attempts=cell['attempts'];solved=cell['verified_solved']
  if solved is not None and type(solved) is not bool:raise ValueError('Verified solve must be boolean or explicit unknown')
  if not attempts:
   if solved is not None:raise ValueError('Unattempted cell cannot have a verified grade')
   continue
  target=totals.setdefault((cell['task'],cell['arm']),dict(cells=0,attempts=0,solves=0,failures=0,unknown_grades=0,known_tokens=0,unknown_cost_attempts=0,native_timeouts=0,grader_timeouts=0))
  target['cells']+=1;target['solves']+=solved is True;target['failures']+=solved is False;target['unknown_grades']+=solved is None
  for attempt in attempts:
   tokens=amount(attempt['exact_provider_tokens']);lower=amount(attempt.get('known_tokens_lower_bound',tokens if tokens is not None else 0))
   if lower is None:raise ValueError('Known lower bound must be an integer')
   if tokens is not None and lower!=tokens:raise ValueError('Exact amount and known amount disagree')
   target['attempts']+=1;target['known_tokens']+=lower;target['unknown_cost_attempts']+=tokens is None
   for field in ('native_timeout','grader_timeout'):
    flag=attempt.get(field,False)
    if type(flag) is not bool:raise ValueError('Timeout must be a recorded boolean')
    target[field+'s']+=flag
 return totals

def combine(rows):
 result={k:sum(r[k] for r in rows) for k in ('cells','attempts','solves','failures','unknown_grades','known_tokens','unknown_cost_attempts','native_timeouts','grader_timeouts')}
 exact=result['known_tokens'] if result['cells'] and not result['unknown_cost_attempts'] else None
 result['all_attempt_provider_tokens']=exact
 result['tokens_per_verified_solve']=exact/result['solves'] if exact is not None and result['solves'] else None
 return result

def ratio(a,b):
 # Ratio (tokens_a/solves_a)/(tokens_b/solves_b), undefined when any exact
 # amount/verified-solve denominator is unavailable or baseline cost is zero.
 if not a['cells'] or not b['cells'] or a['unknown_cost_attempts'] or b['unknown_cost_attempts'] or not a['solves'] or not b['solves'] or not b['known_tokens']:return None
 return (a['known_tokens']*b['solves'])/(b['known_tokens']*a['solves'])
def percentile(values,p):
 if not values:return None
 values=sorted(values);position=(len(values)-1)*p;lo=math.floor(position);hi=math.ceil(position)
 return values[lo]+(values[hi]-values[lo])*(position-lo)

def analyze_part(part,cells,draws=DRAWS):
 if part not in ARMS:raise ValueError('Unknown part')
 if any(c['part']!=part or c['arm'] not in ARMS[part] for c in cells):raise ValueError('Part/arm mismatch')
 totals=task_totals(cells);arms=ARMS[part];tables={a:combine([r for (t,arm),r in totals.items() if arm==a]) for a in arms};tasks=sorted({t for t,a in totals});pairs=[(a,b) for a in arms for b in ('none','K') if a!=b];samples={a+'/'+b:[] for a,b in pairs};rng=random.Random(SEEDS[part])
 # One common task-cluster resample per draw, retaining all rounds/attempts
 # and all arms together. Missing pair-arm clusters are undefined, NOT zero.
 for _ in range(draws):
  sampled=rng.choices(tasks,k=len(tasks)) if tasks else []
  weighted={a:combine([totals[t,a] for t in sampled if (t,a) in totals]) for a in arms}
  complete={a:all((t,a) in totals for t in sampled) and bool(sampled) for a in arms}
  for a,b in pairs:samples[a+'/'+b].append(ratio(weighted[a],weighted[b]) if complete[a] and complete[b] else None)
 comparisons={}
 for a,b in pairs:
  name=a+'/'+b;values=samples[name];defined=[v for v in values if v is not None];pair_complete=bool(tasks) and all((t,a) in totals and (t,b) in totals for t in tasks)
  comparisons[name]=dict(point=ratio(tables[a],tables[b]) if pair_complete else None,bootstrap95=[percentile(defined,.025),percentile(defined,.975)],defined_draws=len(defined),undefined_draws=len(values)-len(defined),draws=values,interval_conditional_on_defined_draws=bool(len(defined)!=len(values)),cross_harness_informational_only=part=='A' and a.startswith('solpi'),paired_panel_complete=pair_complete)
 return dict(part=part,descriptive_only=True,seed=SEEDS[part],bootstrap_draws=draws,cluster_unit='task; all rounds/all attempts retained together',task_clusters=len(tasks),arms=tables,comparisons=comparisons,no_imputation=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args();source=a.input.read_bytes();data=json.loads(source);cells=data['cells'];result=dict(input_sha256=hashlib.sha256(source).hexdigest(),analysis_source_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),parts={part:analyze_part(part,[c for c in cells if c['part']==part]) for part in ARMS});a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
