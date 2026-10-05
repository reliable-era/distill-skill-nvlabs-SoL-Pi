"""Independent read-only partial/final PMARS audit;no inference or replay."""
import hashlib,json,pathlib,subprocess
from task_replay import verify_payload
from pmars_partial_output import verify_partial
from task_artifacts import descriptor
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def native_events(p):
 out=[]
 for line in p.read_text().splitlines():
  try:out.append(json.loads(line))
  except ValueError:pass
 return out
if __name__=='__main__':
 digest=sha(R/'matched-pmars-plan.json');plan=json.loads((R/'matched-pmars-plan.json').read_text());root=pathlib.Path('/tmp/solpi-mp-'+digest[:20]);final=R/'matched-pmars-result.json';record=json.loads((final if final.exists() else R/'matched-pmars-progress.json').read_text());assert record['plan_sha256']==digest;assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items());runtime=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime';assert all(sha(runtime/n)==v for n,v in plan['runtime_hashes'].items());source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/build-pmars');assert all(sha(source/n)==v for n,v in plan['task_source_manifest'].items());ledger=json.loads((root/'transport/ledger.json').read_text());journal=json.loads((root/'transport/prospective-ledger.json').read_text());views={v['request']:v for v in journal['records']};assert len(views)==len(journal['records']);rows=[];pins={}
 for row in record['rows']:
  arm=row['arm'];requests=[r for r in ledger['records'] if r['actor']==arm];assert len(requests)==row['provider_POST'];costs=[];corrected=[]
  for raw in requests:
   n=raw['request'];view=views[n];cost=view['accounting_view']['derived_cost'];assert cost['provider_cost_complete'] and raw['provider_status']==200 and raw['stream_eof'] and raw['error'] is None and raw['provider_backend']=='127.0.0.1:18001';costs.append(cost);a=root/'transport'/f'response-{n}.sse';b=root/'transport'/f'derived-response-{n}.sse';assert sha(a)==view['raw_sha256'] and sha(b)==view['derived_sha256'];pins[str(a.relative_to(root))]=sha(a);pins[str(b.relative_to(root))]=sha(b)
   if view['accounting_view']['correction_applied']:
    def sse(p):return [json.loads(line[6:]) for line in p.read_bytes().splitlines() if line.startswith(b'data: ') and line[6:]!=b'[DONE]']
    aa,bb=sse(a),sse(b);ta=next(e for e in aa if e['type']=='response.completed');tb=next(e for e in bb if e['type']=='response.completed');before=ta['response']['usage']['output_tokens_details']['reasoning_tokens'];after=tb['response']['usage']['output_tokens_details']['reasoning_tokens'];assert view['accounting_view']['raw_cost']['error']=='invalid_reasoning_subset' and 1<=before-after<=7 and after==ta['response']['usage']['output_tokens'];ta['response']['usage']['output_tokens_details']['reasoning_tokens']=after;assert aa==bb;corrected.append(n)
   else:assert a.read_bytes()==b.read_bytes()
  gross=sum(c['gross_tokens'] for c in costs);assert gross==row['provider_tokens_lower_bound'];events=native_events(root/arm/'native.jsonl');turns=[e for e in events if e.get('type')=='turn.completed'];reconciled=False
  if turns:
   for native_key,cost_key in [('input_tokens','input_tokens_inclusive'),('output_tokens','output_tokens_inclusive'),('reasoning_output_tokens','reasoning_tokens_reported')]:assert sum(t['usage'][native_key] for t in turns)==sum(c[cost_key] for c in costs)
   reconciled=True
  caproot=root/arm/'captured';cap=json.loads((caproot/'capture.json').read_text())
  if row['output_present']:
   expected=descriptor('build-pmars',{'source_directory':row['output_classification']['source_directory']});assert cap['capture_complete'] and cap['stopped_actor_verified'] and cap['image_id']==plan['image_id'];assert set(cap['artifacts'])=={i['path'] for i in expected}
   for i in expected:
    rec=cap['artifacts'][i['path']];assert all(rec.get(k)==v for k,v in i.items());verify_payload(caproot/rec['local_payload'],rec)
  else:verify_partial(caproot,plan['image_id']);assert row['replay']['installed_binary_absence_preserved']
  assert row['replay']['replay_complete'] and not row['replay']['rebuild_performed'];setup=row['dependency_setup'];assert setup['test_network_disconnected'] and setup['target_builds']==setup['target_installs']==0 and setup['python']=='3.13.7' and setup['uv']=='0.9.5';assert sha(root/arm/'trusted-setup.log')==setup['setup_log_sha256']
  tests=json.loads((root/arm/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(root/arm/'logs/verifier/reward.txt').read_text().strip();assert reward==row['reward'] and len(tests)==row['test_events']==4;solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved']
  for p in [root/arm/'native.jsonl',caproot/'capture.json',root/arm/'logs/verifier/ctrf.json',root/arm/'logs/verifier/reward.txt',root/arm/'trusted-setup.log']:pins[str(p.relative_to(root))]=sha(p)
  rows.append({'arm':arm,'solved':solved,'official_reward':reward,'passed_tests':sum(t['status']=='passed' for t in tests),'POST':len(requests),'gross_tokens':gross,'provider_cost_complete':True,'native_provider_reconciled':reconciled,'native_terminal':[e['type'] for e in events if e.get('type') in ['turn.completed','turn.failed']],'installation_present':row['output_present'],'corrections':corrected,'actor_seconds':row['actor_seconds'],'setup_seconds':setup['seconds'],'grading_network_disconnected':True})
 complete=final.exists() and len(rows)==4 and not record.get('errors');cleanup=None
 if complete:
  assert ledger['provider_POST']==len(ledger['records'])==sum(r['POST'] for r in rows)==record['POST'];assert ledger['native_starts']==record['starts']==4;assert record['proxy_journal']['journal_collected'];proxy=json.loads((root/'proxy-bundle/journal/proxy.json').read_text());assert proxy['records']==record['proxy_journal']['records'];assert sha(root/'proxy-bundle/journal/proxy.json')==record['proxy_journal']['sha256'];cleanup={}
  for kind in ['container','network']:
   args=['docker','ps','-a','--filter','name=solpi-tpp','--format','{{.Names}}'] if kind=='container' else ['docker','network','ls','--filter','name=solpi-tpp','--format','{{.Name}}'];p=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10);cleanup[kind]=p.stdout.splitlines()
  assert cleanup=={'container':[],'network':[]}
 audit={'plan_sha256':digest,'rows':rows,'stage_complete':complete,'starts':ledger['native_starts'],'POST':ledger['provider_POST'],'receipts':len(ledger['records']),'complete_cell_gross_tokens':sum(r['gross_tokens'] for r in rows),'local_budget_denials':ledger['local_budget_denials'],'cleanup':cleanup,'representative_confirmation':False,'candidate_promotion':False,'goal_complete':False,'artifact_hashes':pins};(R/'matched-pmars-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
