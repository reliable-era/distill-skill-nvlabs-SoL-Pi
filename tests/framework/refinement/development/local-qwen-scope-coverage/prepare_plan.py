"""Freeze prospective cohort only; never execute Docker or inference."""
import pathlib,json,random,hashlib
R=pathlib.Path(__file__).resolve().parent;old=R.with_name('local-qwen-independent-reads');sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
p=json.loads((old/'plan.json').read_text())
p.update(status='prepared_zero_starts_root_review_required',seconds_per_actor=600,combined_maximum_native_starts=18,combined_maximum_provider_POST_total=244,cohort='scope-coverage;600s;nativecontext262144;fixedbrokeroutput8192;separate prospective seed131 cohort',order_seed=131,native_starts=0,provider_POST=0)
p['idle_grace'].update(seconds=300,maximum_metadata_GETs=61)
p['candidate_sha256']=sha(R/'frozen/candidate/SKILL.md');p['karpathy_sha256']=sha(R/'frozen/karpathy/SKILL.md')
p['prior_consumed_attempts']={'native_starts':6,'provider_POST':52,'audit_path':str(old/'repaired-development-audit.json'),'audit_sha256':sha(old/'repaired-development-audit.json'),'cohorts':[{'plan_sha256':'c71b9ca2f36dbb0536d65cc8c39c175fc355bbddc2b1d564cf3ec0fc10878b53','starts':2,'POST':17},{'plan_sha256':'566371965b91c3966be683997917ffff47a1b23dcb5b62bce5f2e071646aa0f3','starts':4,'POST':35}],'pooling':False}
pi=R.with_name('pi-qwen-independent-reads')/'consumed-phase-2-audit.json'
p['other_harness_prior_ledger']={'harness':'Pi','native_starts':1,'provider_POST':8,'zero_start_busy_plan':'36a14253684ae886889ffad30c5ab2db186930dbb8e832f8df552d61500c34f5','consumed_plan':'b037a6a0f2a474a739d99b9d88208a811947e6bf343f926a41843723629bcca3','audit_path':str(pi),'audit_sha256':sha(pi),'scope':'Separate protocol/harness; seven complete requests116442 lowerbound, eighth incomplete; no pooling'}
p['require_protocol_valid']=True
p['profile']={'native_model_context_window':262144,'reasoning':'Native unchanged: observed payload summary=auto; effort omitted. No cross-harness reasoning equivalence claimed.','output_cap':{'field':'max_output_tokens','value':8192,'scope':'Declared provider adapter transform all four arms; matching8192 identity allowed, noninteger/conflicting field rejected before POST; original and forwarded payloads private with hash and exact one-field semantic proof'},'generation_status_separate_from_provider_cost':True}
p['timing']='600s per actor including create/inspect/start and10s cleanup reserve; remaining upstream deadline authoritative; proxy/broker<=600s. Initial+eachactor<=300s/61GET under both frozen locks. Independent official grading separate.'
p['local_budget_policy']={'per_actor_POST_cap':16,'global_POST_cap':192,'denial_receipt':'Persisted before typed LocalBudgetExhaustion, actor/count/reason/source/zero provider forward; does not consume POST','continuation':'Captured partial state independently graded; actor absence/upstream drain/request counter coverage required. Generic provider429 remains infrastructure stop.'}
p['stop_policy']='Fixed schedule continues on functional failure and actor_budget_exhaustion only after actor removal/upstream drain/independent grading. Non-budget provider or infrastructure errors, uncertain cleanup, auxiliary events or exhausted scheduler grace stop; preserve all actual attempts and partial costs; no retries.'
p['accounting']='Pinned SGLang unique final response.completed+EOF/full valid usage; completed or max_output_tokens8192 length-capped incomplete terminal permitted for provider cost, generation status separate. All actor POSTcounter equals records, all per-request valid costs, drain+removal proofs and no auxiliary events required. Native reconciliation separately reported; helper/account-wide/dollars TBD. Missing/partial cost blocks savings.'
p['runtime_origin']['adaptation']='Separate copy from consumed seed127 source;600s/300s grace/scope candidate/native context/output adapter/prospective cost status rule. Certified grader adapters unchanged.'
rng=random.Random(131);p['schedule']=[]
for family in p['tasks']:
 arms=list(p['arms']);rng.shuffle(arms)
 p['schedule'] += [{'id':family+'-'+arm,'family':family,'arm':arm,'round':1} for arm in arms]
for name,h in p['grading_reuse']['adapter_source_hashes'].items():assert sha(R/name)==h,'Certified adapter changed'
p['source_hashes']={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name not in ['plan.json','README.md','execution-authorization.json']}
(R/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print(sha(R/'plan.json'))
