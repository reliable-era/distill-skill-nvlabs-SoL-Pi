"""Read-onlyRegexaudit;no actor/model/grader/retry calls. Active cells != final win."""
import hashlib,json,pathlib,subprocess
from audit_16k_tex import events,native_events
from task_artifacts import descriptor
from task_replay import verify_payload
from uniform_budget_notice import NOTICE
from regex_actor_inputs import recipe
from cached_grader_setup import inputs
from prospective_output_budget import module
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def validate_response(raw,derived,request,view,derive=None):
 av=view['accounting_view'];cost=av['derived_cost'];assert av['framing_complete'] and cost['provider_cost_complete'] and cost['protocol_valid'];assert request['provider_status']==200 and request['error'] is None and request['stream_eof'] and request['provider_backend']=='127.0.0.1:18001' and request['payload_policy']['output_cap']==16384
 assert sha(raw)==view['raw_sha256'] and sha(derived)==view['derived_sha256'];aa=events(raw);bb=events(derived);terms=[e['response'] for e in aa if e.get('type')=='response.completed'];assert len(terms)==1;tr=terms[0];assert tr['model']=='Qwen3.8-27B-FP8' and tr['max_output_tokens']==16384
 if derive is not None:
  rebuilt=derive(aa,request['stream_eof'],view['provenance']);assert all(rebuilt[k]==av[k] for k in ['raw_cost','derived_cost','raw_provider_protocol_valid','correction_applied'])
 if av['correction_applied']:
  td=next(e['response'] for e in bb if e.get('type')=='response.completed');u=tr['usage'];before=u['output_tokens_details']['reasoning_tokens'];after=td['usage']['output_tokens_details']['reasoning_tokens'];assert tr['status']=='incomplete' and tr['incomplete_details']=={'reason':'max_output_tokens'} and 16382<=after<=16384 and after==u['output_tokens'] and 1<=before-after<=7;u['output_tokens_details']['reasoning_tokens']=after;assert aa==bb
 else:assert raw.read_bytes()==derived.read_bytes() and av['raw_provider_protocol_valid'] is True
 return cost,tr
if __name__=='__main__':
 planpath=R/'16k-regex-plan.json';digest=sha(planpath);plan=json.loads(planpath.read_text());root=pathlib.Path('/tmp/solpi-r16-'+digest[:18]);record=None;terminal=False
 for n in ['16k-regex-result.json','16k-regex-progress.json']:
  if (R/n).exists():
   v=json.loads((R/n).read_text())
   if v['plan_sha256']==digest:record=v;terminal=n.endswith('result.json');break
 if record is None:raise ValueError('no completedcells—notanoutcome')
 D=R.parent/'development/pi-takeover-qwen-source-backed-16k';source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/regex-log');assert all(sha(D/'runtime'/n)==h for n,h in plan['runtime_hashes'].items());assert all(sha(R/n)==h for n,h in plan['prospective_module_hashes'].items());assert all(sha(source/n)==h for n,h in plan['task_source_manifest'].items());assert all(sha(D/'frozen'/n)==h for n,h in plan['frozen_skills_manifest'].items());assert sha(D/'freeze-manifest.json')==plan['new_candidate_freeze_sha256'];assert sha(R/'regex-public-python-binding.json')==plan['public_python_binding_sha256'];assert recipe('regex-log')==plan['public_recipe'] and inputs()==plan['trusted_recipe']['cache_inputs'];assert plan['memory_mb']==2048 and plan['cpus']==1 and plan['configured_output_cap']==16384 and plan['actor_seconds']==600 and plan['per_actor_POST_cap']==16
 assert plan['arm_recipe']=={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']} and plan['comparator_Both_definition']=='currentcandidate+frozenKarpathy';assert json.loads((R/'terminal-10pct-selection.json').read_text())['selected_tasks'][6]['id']=='regex-log'
 strict=module('independent_regex_strict',(D/'runtime/usage_normalization.py').read_text());costmodule=module('independent_regex_cost',(D/'runtime/provider_cost.py').read_text().replace('from usage_normalization import normalize_request',''),{'normalize_request':strict.normalize_request});adapter=module('independent_regex_adapter',(D/'runtime/reasoning_adapter.py').read_text().replace('from provider_cost import normalize_cost',''),{'normalize_cost':costmodule.normalize_cost,'__file__':str(D/'runtime/reasoning_adapter.py')})
 ledger=json.loads((root/'transport/ledger.json').read_text());views={v['request']:v for v in json.loads((root/'transport/prospective-ledger.json').read_text())['records']};rows=[];pins={}
 for row in record['rows']:
  arm=row['arm'];d=root/arm;requests=[v for v in ledger['records'] if v['actor']==arm];assert len(requests)==row['provider_POST'];costs=[];corrections=[];statuses=[]
  for request in requests:
   n=request['request'];cost,tr=validate_response(root/'transport'/f'response-{n}.sse',root/'transport'/f'derived-response-{n}.sse',request,views[n],adapter.derive);costs.append(cost);statuses.append({'request':n,'status':tr['status'],'incomplete_details':tr.get('incomplete_details'),'output_tokens':tr['usage']['output_tokens'],'reasoning_tokens':tr['usage']['output_tokens_details']['reasoning_tokens'],'raw_reasoning_tokens':next(e['response']['usage']['output_tokens_details']['reasoning_tokens'] for e in events(root/'transport'/f'response-{n}.sse') if e.get('type')=='response.completed'),'raw_protocol_valid':views[n]['accounting_view']['raw_provider_protocol_valid']})
   if views[n]['accounting_view']['correction_applied']:corrections.append(n)
   for prefix in ['response-','derived-response-','request-','forwarded-request-']:
    p=root/'transport'/(prefix+str(n)+('.sse' if 'response' in prefix else '.json'));pins[str(p.relative_to(root))]=sha(p)
  gross=sum(c['gross_tokens'] for c in costs);assert row['cost_complete'] and gross==row['provider_tokens_lower_bound'];native=native_events(d/'native.jsonl');turns=[e for e in native if e.get('type')=='turn.completed'];reconciled=False
  if turns:
   for nk,ck in [('input_tokens','input_tokens_inclusive'),('output_tokens','output_tokens_inclusive'),('reasoning_output_tokens','reasoning_tokens_reported')]:assert sum(e['usage'][nk] for e in turns)==sum(c[ck] for c in costs)
   reconciled=True
  if row['output_present']:
   cap=json.loads((d/'captured/capture.json').read_text());assert cap==row['capture'] and cap['capture_complete'] and cap['stopped_actor_verified'] and cap['image_id']==plan['actor_image_id'];item=descriptor('regex-log')[0];assert set(cap['artifacts'])=={'/app/regex.txt'};rec=cap['artifacts'][item['path']];assert all(rec.get(k)==v for k,v in item.items()) and rec['local_payload']=='payload-0';verify_payload(d/'captured/payload-0',rec);assert row['replay']['replay_complete'] and row['replay']['restored_paths']==['/app/regex.txt'] and not row['replay']['rebuild_performed']
  else:assert row['capture']=={'capture_complete':False,'output_absent_verified':True,'not_unsupported_layout':True,'path':'/app/regex.txt','actor_image_id':plan['actor_image_id']} and row['replay']['verified_original_output_absence'] and not row['replay']['rebuild_performed'];assert not (d/'captured').exists()
  keys=plan['arm_recipe'][arm];actual={str(p.relative_to(d/'skills')):sha(p) for p in (d/'skills').rglob('*') if p.is_file()};assert actual=={n:h for n,h in plan['frozen_skills_manifest'].items() if n.split('/')[0] in keys};prompt=(d/'prompt.txt').read_text();assert prompt.count(NOTICE)==1 and all(prompt.count((D/'frozen'/k/'SKILL.md').read_text())==1 for k in keys)
  setup=row['dependency_setup'];assert setup['test_network_disconnected'] and setup['network']=='none' and setup['target_builds']==setup['target_installs']==0 and setup['cache_inputs']==plan['trusted_recipe']['cache_inputs'] and sha(d/'trusted-setup.log')==setup['setup_log_sha256'];tests=json.loads((d/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(d/'logs/verifier/reward.txt').read_text().strip();assert len(tests)==row['test_events']==1 and reward==row['reward'] and reward in ['0','1'];assert {t['name'] for t in tests}==set(json.loads((R/'regex-readiness-probe.json').read_text())['collected_original_tests']);solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved']
  for p in d.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:pins[str(p.relative_to(root))]=sha(p)
  rows.append({'arm':arm,'solved':solved,'reward':reward,'passed_tests':sum(t['status']=='passed' for t in tests),'POST':len(requests),'gross_tokens':gross,'provider_cost_complete':True,'native_usage_reconciled':reconciled,'native_terminal':[e['type'] for e in native if e.get('type') in ['turn.completed','turn.failed']],'statuses':statuses,'corrections':corrections,'output_present':row['output_present'],'actual_skill_delivery_verified':True,'actor_seconds':row['actor_seconds'],'setup_seconds':setup['seconds']})
 complete=terminal and len(rows)==4 and not record.get('errors');cleanup=None
 if complete:
  assert ledger['native_starts']==record['starts']==4 and ledger['provider_POST']==len(ledger['records'])==record['POST']==sum(r['POST'] for r in rows);assert record['proxy_journal']['journal_collected'] and sha(root/'proxy-bundle/journal/proxy.json')==record['proxy_journal']['sha256'];cleanup={}
  for k,args in [('containers',['docker','ps','-a','--filter','name=solpi-r16','--format','{{.Names}}']),('networks',['docker','network','ls','--filter','name=solpi-r16','--format','{{.Name}}'])]:cleanup[k]=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10).stdout.splitlines()
  assert cleanup=={'containers':[],'networks':[]}
 audit={'plan_sha256':digest,'stage_complete':complete,'rows':rows,'starts_snapshot':ledger['native_starts'],'POST_snapshot':ledger['provider_POST'],'receipts_snapshot':len(ledger['records']),'completed_cell_gross_tokens':sum(r['gross_tokens'] for r in rows),'cleanup':cleanup,'cost_independently_rederived_from_raw_SSE':True,'isolation_proof_scope':'hashedprestartverify_actor_inspectassertion+publicsoftwareproof;no independent retrospective raw actor inspect for removed actors','candidate_promotion':False,'representative_confirmation':False,'goal_complete':False,'artifact_hashes':pins};(R/'16k-regex-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
