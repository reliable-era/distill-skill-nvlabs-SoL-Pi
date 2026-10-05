"""Freeze a second reused development family; no execution."""
import hashlib,json,pathlib,random,shutil
R=pathlib.Path(__file__).resolve().parent
origin=R.with_name('local-qwen-scope-coverage');smoke=R.with_name('pi-takeover-qwen-smoke');audit=R.parent.parent/'pi-takeover/smoke-audit.json'
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
if (R/'execution-authorization.json').exists():raise SystemExit('Already authorized; do not refreeze')
previous=json.loads(audit.read_text())
if previous['status']!='PASS' or not previous['complete'] or not previous['economic_comparison_eligible']:raise SystemExit('Completed valid smoke required')
if not next(x for x in previous['panels'] if x['arm']=='candidate')['solved']:raise SystemExit('Candidate did not pass development smoke')
shutil.copyfile(audit,R/'frozen-prior-audit.json')
p=json.loads((origin/'plan.json').read_text())
p.update(status='prepared_four_cell_terminal_development',maximum_native_starts=4,maximum_provider_POST_total=64,combined_maximum_native_starts=14,combined_maximum_provider_POST_total=166,order_seed=20261005,cohort='Pi coordination/Codex/local Qwen/unchanged scope-coverage/Terminal development',purpose='Second reused development family; not fresh representative confirmation',scope='One model/harness and two development families across stages; no historical outcome pooling',retries=0,native_starts=0,provider_POST=0)
p['tasks']={'terminal':p['tasks']['terminal']}
arms=list(p['arms']);random.Random(p['order_seed']).shuffle(arms)
p['schedule']=[{'id':'terminal-'+arm,'family':'terminal','arm':arm,'round':1} for arm in arms]
p['prior_consumed_attempts'].update(native_starts=10,provider_POST=102,audit_path=str(R/'frozen-prior-audit.json'),audit_sha256=sha(R/'frozen-prior-audit.json'))
p['prior_consumed_attempts']['cohorts'].append({'plan_sha256':previous['plan_sha256'],'starts':4,'POST':50,'pooling':False})
p['local_budget_policy']['global_POST_cap']=64
p['timing']='4actors/600s each;16POST each/64total;initial+eachactor300s/61GET idle grace,total1500s;independent Terminal grader240s each plus bounded setup/cleanup;no retries'
p['selection']={'task':'sanitize-git-repo','rule':'Existing reused Terminal fixture in the prior fixed development allocation, with exact passing controls. Not selected from fresh nine-task sample or by task-specific candidate success.','confirmation_separate':True}
p['scope_constraints']={'model':'Qwen3.8-27B-FP8','model_fallback':False,'harness':'codex0.160.0','benchmark_subset':'Frozen nine-task Terminal allocation remains separate/unstarted','canonical_skill_unchanged':True}
p['runtime_origin']['adaptation']='Copy of completed Go smoke transport and caps;Terminal-only four-cell validation;prior ledger updated;exact grading adapters unchanged'
p['decision_basis']='Exploratory development: candidate solved Go while all controls failed with complete costs; additional family probes whether signal transfers. No superiority claim or candidate change.'
for name,h in p['grading_reuse']['adapter_source_hashes'].items():assert sha(R/name)==h,'Certified grading adapter changed: '+name
p['source_hashes']={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name not in ['plan.json','README.md','execution-authorization.json']}
(R/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print(sha(R/'plan.json'))
