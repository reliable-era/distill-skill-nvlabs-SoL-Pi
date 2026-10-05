"""Metadata-only 10% Terminal-Bench subset; no prompts/tests/solutions read.
Freeze before new actor outcomes. Finite-population strata: difficulty.
Within strata, seeded SHA256 ranking is outcome-independent and reproducible.
"""
import argparse,collections,hashlib,json,math,pathlib,subprocess,tomllib
REVISION='2fd12b88aafdd04a52c298e3940bcb189f9766d6'
SEED=20261004
EXPOSED={'sanitize-git-repo','code-from-image'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def select(source):
 head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 if head!=REVISION:raise ValueError('pinned source revision mismatch')
 rows=[]
 for f in sorted(source.glob('*/task.toml')):
  raw=f.read_bytes()
  if subprocess.check_output(['git','-C',str(source),'show',REVISION+':'+str(f.relative_to(source))])!=raw:raise ValueError('modified metadata: '+f.parent.name)
  m=tomllib.loads(raw.decode())['metadata']
  rows.append({'id':f.parent.name,'difficulty':m['difficulty'],'category':m['category'],'expert_time_estimate_min':m.get('expert_time_estimate_min'),'metadata_sha256':sha(raw),'previously_exposed':f.parent.name in EXPOSED})
 if len(rows)!=89:raise ValueError('population size changed')
 n=math.ceil(len(rows)*.10)
 eligible=[r for r in rows if not r['previously_exposed']]
 strata={k:[r for r in eligible if r['difficulty']==k] for k in sorted({r['difficulty'] for r in eligible})}
 # Reserve one per nonempty difficulty stratum, then apportion remaining slots
 # proportionally by largest remainder. Small easy stratum is intentionally
 # oversampled for coverage; declare design and sampling weights explicitly.
 quotas={k:1 for k in strata};remaining=n-len(strata)
 ideals={k:remaining*len(v)/len(eligible) for k,v in strata.items()}
 for k in quotas:quotas[k]+=math.floor(ideals[k])
 for k in sorted(strata,key=lambda k:(-(ideals[k]-math.floor(ideals[k])),k))[:n-sum(quotas.values())]:quotas[k]+=1
 picked=[]
 for k,group in strata.items():
  ranked=sorted(group,key=lambda r:sha(f'{SEED}:{REVISION}:{r["id"]}'.encode()))
  for r in ranked[:quotas[k]]:picked.append(dict(r,stratum_population=len(group),stratum_sample=quotas[k],design_weight=len(group)/quotas[k]))
 picked.sort(key=lambda r:r['id'])
 return {'schema_version':1,'benchmark':'terminal-bench-2','source_revision':REVISION,'seed':SEED,'full_population':len(rows),'eligible_population':len(eligible),'excluded_previously_exposed':sorted(EXPOSED),'fraction_rule':'ceil(0.10 * full release population)','selected_size':n,'fraction_of_full_population':n/len(rows),'fraction_of_eligible_population':n/len(eligible),'selection_rule':'minimum-one difficulty coverage + proportional largest-remainder remaining allocation + seeded SHA256 ranking within difficulty','stratum_counts':{k:len(v) for k,v in strata.items()},'stratum_quotas':quotas,'category_population':dict(sorted(collections.Counter(r['category'] for r in eligible).items())),'category_sample':dict(sorted(collections.Counter(r['category'] for r in picked).items())),'metadata_population_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),'selected_tasks':picked,'limits':['Metadata-stratified sample, not a guarantee of performance representativeness. Nine tasks cannot cover every category.','Excluded exposed tasks change inference target to the eligible release population.','Difficulty is stratified; categories and runtime distributions are descriptive, not balanced by outcome-selected resampling.','Unweighted task averages describe this panel; use declared stratum design weights for an eligible-population estimate and report uncertainty.','No task may be replaced due to model failure, environment cost, or unavailability. Blocked tasks remain planned/unrun.'],'status':'metadata allocation only; environment controls, candidate freeze, accounting and bounded inference authorization required','model':'Qwen3.8-27B-FP8','harness':'Codex primary; other harnesses require separate matched stages','read_surface':'task.toml metadata only, pinned Git metadata blobs; no task instructions, verifier assertions or solutions read'}
def main():
 a=argparse.ArgumentParser();a.add_argument('--source',type=pathlib.Path,default=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2'));a.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).with_name('terminal-10pct-selection.json'));x=a.parse_args()
 result=select(x.source);text=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if x.output.exists():
  if x.output.read_text()!=text:raise SystemExit('refuse to overwrite changed frozen selection')
 else:x.output.write_text(text)
 print(json.dumps({'selected':[r['id'] for r in result['selected_tasks']],'quotas':result['stratum_quotas'],'categories':result['category_sample'],'selection_sha256':sha(text.encode())},indent=2))
if __name__=='__main__':main()
