"""Freeze four-cell takeover smoke; no model, Docker, or grading calls."""
import hashlib,json,pathlib,random
R=pathlib.Path(__file__).resolve().parent
origin=R.with_name('local-qwen-scope-coverage')
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
if (R/'execution-authorization.json').exists():
 raise SystemExit('Already authorized; do not refreeze an execution plan')
p=json.loads((origin/'plan.json').read_text())
p.update(status='prepared_four_cell_takeover_smoke',maximum_native_starts=4,
 maximum_provider_POST_total=64,combined_maximum_native_starts=10,
 combined_maximum_provider_POST_total=116,order_seed=20261004,
 cohort='Pi coordination/Codex harness/local Qwen/scope-coverage/Go development smoke',
 purpose='Operational and candidate development only; not a 10-percent benchmark or confirmation',
 scope='One harness, one model, one reused development task, four matched arms; no historical pooling',
 retries=0,native_starts=0,provider_POST=0)
p['tasks']={'go':p['tasks']['go']}
# Retain existing external verifier bindings and certificate. Extra bindings do
# not expose verifier material to actors; only prepare() selects actor mounts.
arms=list(p['arms']);random.Random(p['order_seed']).shuffle(arms)
p['schedule']=[{'id':'go-'+arm,'family':'go','arm':arm,'round':1} for arm in arms]
p['local_budget_policy']['global_POST_cap']=64
p['timing']='4 actors maximum,600s each,16POST each/64 total; initial and each actor idle grace300s/61GET; at most1500s aggregate idle grace; graders240s each plus bounded setup/cleanup. No retries.'
p['selection']={'task':'go/food-chain','rule':'Single existing Go fixture with passing cached controls; chosen before new outcomes as cheap operational smoke. Not a representative benchmark sample.', 'confirmation_separate':True}
p['runtime_origin']['adaptation']='Copy of unstarted scope-coverage protocol;4/64 caps; four-cell input validation; own deadline-before-headers classification. Certified grading adapter files unchanged.'
p['scope_constraints']={'model':'Qwen3.8-27B-FP8','model_fallback':False,'harness':'codex0.160.0','benchmark_subset':'Separate Terminal-Bench metadata allocation; no confirmation inference authorized here','canonical_skill_unchanged':True}
for name,h in p['grading_reuse']['adapter_source_hashes'].items():
 assert sha(R/name)==h,'Certified grading adapter changed: '+name
p['source_hashes']={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name not in ['plan.json','README.md','execution-authorization.json']}
(R/'plan.json').write_text(json.dumps(p,indent=2)+'\n')
print(sha(R/'plan.json'))
