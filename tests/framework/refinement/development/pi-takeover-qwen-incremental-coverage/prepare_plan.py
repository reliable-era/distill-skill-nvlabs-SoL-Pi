"""Freeze one incremental-coverage hypothesis, historical Ours and LB provenance."""
import hashlib,json,pathlib,random,shutil,subprocess
R=pathlib.Path(__file__).resolve().parent;origin=R.with_name('pi-takeover-qwen-patch-first');public=R.parent.parent/'pi-takeover';audit=public/'patch-first-audit.json';lb=public/'qwen-load-balancer'
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
if (R/'execution-authorization.json').exists():raise SystemExit('Already authorized;no refreeze')
previous=json.loads(audit.read_text());assert previous['status']=='PASS' and previous['complete']
shutil.copyfile(audit,R/'frozen-prior-audit.json');p=json.loads((origin/'plan.json').read_text())
p.update(status='prepared_incremental_coverage_LB',maximum_native_starts=5,maximum_provider_POST_total=80,combined_maximum_native_starts=23,combined_maximum_provider_POST_total=301,order_seed=20261008,cohort='New matched five-arm development: incremental coverage + frozen historical Ours,uniform load-balanced Qwen',native_starts=0,provider_POST=0)
p['arms']['original']=['original'];p['candidate_sha256']=sha(R/'frozen/candidate/SKILL.md');p['original_sha256']=sha(R/'frozen/original/SKILL.md')
p['prior_consumed_attempts'].update(native_starts=18,provider_POST=221,audit_path=str(R/'frozen-prior-audit.json'),audit_sha256=sha(R/'frozen-prior-audit.json'))
p['prior_consumed_attempts']['cohorts'].append({'plan_sha256':previous['plan_sha256'],'starts':4,'POST':57,'pooling':False})
arms=list(p['arms']);random.Random(p['order_seed']).shuffle(arms);p['schedule']=[{'id':'terminal-'+a,'family':'terminal','arm':a,'round':1} for a in arms]
p['timing']='5actors/600s including10s reserve;16POST each/80total;240s passive completion-only grace;2s frontend writes;6idle gates300s/61GET each (<=1800s);grader240s each;no retries'
p['runtime_origin']['adaptation']='One first-bullet prerequisite changed versus scope-coverage;old next-call bullet restored. Add historical whole original Ours via caller arm map,unchanged certified wrapper/graders. Only new transport behavior is recording verified Nginx upstream headers. No old control reuse.'
p['decision_basis']='Both prior scope/patch-first candidates made zero final worktree changes. Incremental coverage removes global inventory-before-edit prerequisite without weakening final coverage or testing. No fixture-specific answers or history exclusions. Historical Ours provides the missing refinement comparator.'
p['load_balancer']={'base_url':'http://127.0.0.1:8000/v1','allowed_upstreams':['127.0.0.1:18001','127.0.0.1:18002'],'header':'X-Solpi-Upstream','require_every_provider_receipt':True,'idle_scope':'/get_load aggregates both peers,fails closed','pool_with_direct_route':False,'backend_stratification_required':True}
for name in ['nginx.conf','route.json','load_status.py','migration.json','port8000-verification.json']:p['external_files'][str(lb/name)]=sha(lb/name)
snapshots=[]
for name in ['ykw-qwen38-dflash2-tp2','jev-pi-qwen38-replica-20261004-nccl-only']:
 x=json.loads(subprocess.check_output(['docker','inspect',name]))[0];snapshots.append({'name':name,'container_id':x['Id'],'image_id':x['Image'],'cmd':x['Config']['Cmd'],'GPU_visibility':[e for e in x['Config']['Env'] if e.startswith(('NVIDIA_VISIBLE_DEVICES=','CUDA_VISIBLE_DEVICES='))]})
p['server_snapshots']=snapshots
for f,h in p['grading_reuse']['adapter_source_hashes'].items():assert sha(R/f)==h,'Certified adapter changed:'+f
p['source_hashes']={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name not in ['plan.json','README.md','execution-authorization.json']}
(R/'plan.json').write_text(json.dumps(p,indent=2)+'\n');print(sha(R/'plan.json'))
