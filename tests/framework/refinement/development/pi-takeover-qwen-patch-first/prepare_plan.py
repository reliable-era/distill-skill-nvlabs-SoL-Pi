"""Freeze patch-first development and uniform issued-request receipt grace."""
import hashlib,json,pathlib,random,shutil
R=pathlib.Path(__file__).resolve().parent;origin=R.with_name('pi-takeover-qwen-terminal');audit=R.parent.parent/'pi-takeover/terminal-audit.json'
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
if (R/'execution-authorization.json').exists():raise SystemExit('Already authorized; do not refreeze')
previous=json.loads(audit.read_text())
if previous['status']!='PASS' or not previous['complete']:raise SystemExit('Completed audited prior stage required')
shutil.copyfile(audit,R/'frozen-prior-audit.json');p=json.loads((origin/'plan.json').read_text())
p.update(status='prepared_patch_first_with_completion_grace',combined_maximum_native_starts=18,combined_maximum_provider_POST_total=228,order_seed=20261006,cohort='New matched Terminal development: patch-first candidate/uniform backend completion grace',completion_grace_seconds=240,frontend_write_timeout_seconds=2,native_starts=0,provider_POST=0)
p['candidate_sha256']=sha(R/'frozen/candidate/SKILL.md')
p['prior_consumed_attempts'].update(native_starts=14,provider_POST=164,audit_path=str(R/'frozen-prior-audit.json'),audit_sha256=sha(R/'frozen-prior-audit.json'))
p['prior_consumed_attempts']['cohorts'].append({'plan_sha256':previous['plan_sha256'],'starts':4,'POST':62,'pooling':False})
arms=list(p['arms']);random.Random(p['order_seed']).shuffle(arms);p['schedule']=[{'id':'terminal-'+a,'family':'terminal','arm':a,'round':1} for a in arms]
p['timing']='4actors/600s each including10s reserve;16POST each/64total;already committed requests have<=240s completion grace afteractorstop;2s frontend writes;5idle gates300s/61GET each;graders240s each;no retries'
p['profile']['completion_accounting']={'grace_seconds':240,'actor_continuation':False,'new_requests_during_grace':False,'charge_unconsumed_output':True,'missing_usage_remains_incomplete':True,'selection_basis':'110 completed development requests:max214.9s,p95 87.9s;240s finite margin,not a guarantee'}
p['runtime_origin']['adaptation']='Separate new cohort:single patch-first sequencing bullet;fixed actor caps;uniform passive backend receipt grace/client detach/bounded parent drain;certified grading adapters unchanged'
p['decision_basis']='Previous candidate made zero worktree changes and failed while controls passed. Patch-first is a development hypothesis; no history exclusions or fixture-specific answers. New grace protocol precludes old/new causal cost attribution or historical control reuse.'
p['maximum_recovery_panels']=1
p['stop_policy']='Grade captured stopped work after owned receipt drain. Missing usage remains incomplete. Provider failures before hard backend grace, uncertain cleanup, protocol violations, auxiliary events or exhausted scheduler grace stop. No retries or post-cutoff actor execution.'
for f,h in p['grading_reuse']['adapter_source_hashes'].items():assert sha(R/f)==h,'Certified grading adapter changed:'+f
p['source_hashes']={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name not in ['plan.json','README.md','execution-authorization.json']}
(R/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print(sha(R/'plan.json'))
