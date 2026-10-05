"""Read-onlyindependent16KTeXcompletedcell/finalaudit;no inference/grade/repair."""
import hashlib,json,pathlib,subprocess
from task_artifacts import descriptor,GUARDS
from task_replay import verify_payload
from protected_inputs import check_protected_inputs
from uniform_budget_notice import NOTICE
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def events(p):
 return [json.loads(l[6:]) for l in pathlib.Path(p).read_bytes().splitlines() if l.startswith(b'data: ') and l[6:]!=b'[DONE]']
def native_events(p):
 result=[]
 for l in pathlib.Path(p).read_text().splitlines():
  try:result.append(json.loads(l))
  except ValueError:pass
 return result
if __name__=='__main__':
 planpath=R/'16k-tex-r2-plan.json';digest=sha(planpath);plan=json.loads(planpath.read_text());root=pathlib.Path('/tmp/solpi-t16-'+digest[:18]);record=None;terminal=False
 for n in ['16k-tex-r2-result.json','16k-tex-r2-progress.json']:
  if (R/n).exists():
   x=json.loads((R/n).read_text())
   if x['plan_sha256']==digest:record=x;terminal=n.endswith('result.json');break
 if record is None:raise ValueError('no currentcompletedcells;notanoutcome')
 D=R.parent/'development/pi-takeover-qwen-source-backed-16k';source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/overfull-hbox');assert all(sha(D/'runtime'/n)==h for n,h in plan['runtime_hashes'].items());assert all(sha(R/n)==h for n,h in plan['prospective_module_hashes'].items());assert all(sha(source/n)==h for n,h in plan['task_source_manifest'].items());assert all(sha(D/'frozen'/n)==h for n,h in plan['frozen_skills_manifest'].items());assert sha(D/'freeze-manifest.json')==plan['new_candidate_freeze_sha256'];freeze=json.loads((D/'freeze-manifest.json').read_text());assert plan['arm_recipe']==freeze['arm_recipe']=={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']};assert plan['comparator_Both_definition']=='currentcandidate+frozenKarpathy';assert plan['configured_output_cap']==16384 and plan['actor_seconds']==600 and plan['per_actor_POST_cap']==16 and plan['memory_mb']==plan['public_recipe']['memory_mb']==4096
 ledger=json.loads((root/'transport/ledger.json').read_text());views={v['request']:v for v in json.loads((root/'transport/prospective-ledger.json').read_text())['records']};rows=[];pins={}
 for row in record['rows']:
  arm=row['arm'];d=root/arm;costs=[];corrections=[];requests=[v for v in ledger['records'] if v['actor']==arm];assert len(requests)==row['provider_POST']
  for request in requests:
   n=request['request'];view=views[n];av=view['accounting_view'];cost=av['derived_cost'];assert av['framing_complete'] and cost['provider_cost_complete'] and cost['protocol_valid'];assert request['provider_status']==200 and request['error'] is None and request['stream_eof'] and request['provider_backend']=='127.0.0.1:18001' and request['payload_policy']['output_cap']==16384
   raw=root/'transport'/f'response-{n}.sse';derived=root/'transport'/f'derived-response-{n}.sse';assert sha(raw)==view['raw_sha256'] and sha(derived)==view['derived_sha256'];aa=events(raw);bb=events(derived);tr=next(e['response'] for e in aa if e.get('type')=='response.completed');assert tr['model']=='Qwen3.8-27B-FP8' and tr['max_output_tokens']==16384
   if av['correction_applied']:
    td=next(e['response'] for e in bb if e.get('type')=='response.completed');u=tr['usage'];before=u['output_tokens_details']['reasoning_tokens'];after=td['usage']['output_tokens_details']['reasoning_tokens'];assert tr['status']=='incomplete' and tr['incomplete_details']=={'reason':'max_output_tokens'} and 16382<=after<=16384 and after==u['output_tokens'] and 1<=before-after<=7;u['output_tokens_details']['reasoning_tokens']=after;assert aa==bb;corrections.append(n)
   else:assert raw.read_bytes()==derived.read_bytes() and av['raw_provider_protocol_valid'] is True
   for p in [raw,derived]:pins[str(p.relative_to(root))]=sha(p)
   costs.append(cost)
  gross=sum(c['gross_tokens'] for c in costs);assert row['cost_complete'] and gross==row['provider_tokens_lower_bound'];native=native_events(d/'native.jsonl');turns=[e for e in native if e.get('type')=='turn.completed'];reconciled=False
  if turns:
   for nk,ck in [('input_tokens','input_tokens_inclusive'),('output_tokens','output_tokens_inclusive'),('reasoning_output_tokens','reasoning_tokens_reported')]:assert sum(e['usage'][nk] for e in turns)==sum(c[ck] for c in costs)
   reconciled=True
  baseline=json.loads((d/'before/baseline.json').read_text());assert baseline==row['protected_before'] and baseline['before_actor_start_verified'] and baseline['image_id']==plan['actor_image_id'];assert check_protected_inputs(plan['protected_inputs_original'],baseline['protected_baseline'],GUARDS['overfull-hbox'])['unchanged']
  for i,path in enumerate(GUARDS['overfull-hbox']):
   p=d/'before'/('input-'+str(i));rec=baseline['protected_baseline'][path];assert sha(p)==rec['sha256'] and p.stat().st_size==rec['bytes']
  cap=json.loads((d/'captured/capture.json').read_text());assert cap['capture_complete'] and cap['stopped_actor_verified'] and cap['image_id']==plan['actor_image_id'] and cap['protected_input_gate_passed'];items=descriptor('overfull-hbox');assert set(cap['artifacts'])=={i['path'] for i in items}
  for i,item in enumerate(items):
   rec=cap['artifacts'][item['path']];assert all(rec.get(k)==v for k,v in item.items()) and rec['local_payload']=='payload-'+str(i);verify_payload(d/'captured'/rec['local_payload'],rec)
  assert check_protected_inputs(baseline['protected_baseline'],{p:cap['artifacts'][p] for p in GUARDS['overfull-hbox']},GUARDS['overfull-hbox'])['unchanged'];assert row['replay']['replay_complete'] and not row['replay']['rebuild_performed'] and row['replay']['restored_paths']==['/app/input.tex'] and set(row['replay']['witness_paths_not_replayed'])==set(GUARDS['overfull-hbox'])
  keys=plan['arm_recipe'][arm];actual={str(p.relative_to(d/'skills')):sha(p) for p in (d/'skills').rglob('*') if p.is_file()};assert actual=={n:h for n,h in plan['frozen_skills_manifest'].items() if n.split('/')[0] in keys};prompt=(d/'prompt.txt').read_text();assert prompt.count(NOTICE)==1 and all(prompt.count((D/'frozen'/key/'SKILL.md').read_text())==1 for key in keys)
  setup=row['dependency_setup'];assert setup['test_network_disconnected'] and setup['python']=='3.13.7' and setup['pytest']=='8.4.1' and setup['pytest_json_ctrf']=='0.3.5' and sha(d/'trusted-setup.log')==setup['setup_log_sha256'];tests=json.loads((d/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(d/'logs/verifier/reward.txt').read_text().strip();assert len(tests)==row['test_events']==4 and reward==row['reward'];assert {t['name'] for t in tests}==set(json.loads((R/'tex-wiring-probe.json').read_text())['collected_original_tests']);solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved']
  for p in d.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:pins[str(p.relative_to(root))]=sha(p)
  rows.append({'arm':arm,'solved':solved,'reward':reward,'passed_tests':sum(t['status']=='passed' for t in tests),'POST':len(requests),'gross_tokens':gross,'provider_cost_complete':True,'native_usage_reconciled':reconciled,'native_terminal':[e['type'] for e in native if e.get('type') in ['turn.completed','turn.failed']],'last_provider_status':tr['status'],'last_incomplete_details':tr.get('incomplete_details'),'corrections':corrections,'protected_before_after_verified':True,'actual_skill_delivery_verified':True,'actor_seconds':row['actor_seconds'],'setup_seconds':setup['seconds']})
 complete=terminal and len(rows)==4 and not record.get('errors');cleanup=None
 if complete:
  assert ledger['native_starts']==record['starts']==4 and ledger['provider_POST']==len(ledger['records'])==record['POST']==sum(r['POST'] for r in rows);assert record['proxy_journal']['journal_collected'] and sha(root/'proxy-bundle/journal/proxy.json')==record['proxy_journal']['sha256'];cleanup={}
  for kind,args in [('containers',['docker','ps','-a','--filter','name=solpi-t16','--format','{{.Names}}']),('networks',['docker','network','ls','--filter','name=solpi-t16','--format','{{.Name}}'])]:cleanup[kind]=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10).stdout.splitlines()
  assert cleanup=={'containers':[],'networks':[]}
 audit={'plan_sha256':digest,'stage_complete':complete,'rows':rows,'starts':ledger['native_starts'],'POST':ledger['provider_POST'],'receipts':len(ledger['records']),'completed_cell_gross_tokens':sum(r['gross_tokens'] for r in rows),'cleanup':cleanup,'candidate_promotion':False,'representative_confirmation':False,'goal_complete':False,'artifact_hashes':pins};(R/'16k-tex-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
