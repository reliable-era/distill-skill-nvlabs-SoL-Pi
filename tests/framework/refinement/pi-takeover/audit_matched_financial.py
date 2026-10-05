"""Read-only financial cell/final audit;no new inference/grade/repair."""
import hashlib,json,pathlib,subprocess
from financial_output import verify
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_events(p):
 out=[]
 for l in p.read_text().splitlines():
  try:out.append(json.loads(l))
  except ValueError:pass
 return out
if __name__=='__main__':
 digest=sha(R/'matched-financial-plan.json');plan=json.loads((R/'matched-financial-plan.json').read_text());root=pathlib.Path('/tmp/solpi-mf-'+digest[:20]);record=None;terminal=False
 for filename in ['matched-financial-result.json','matched-financial-progress.json']:
  path=R/filename
  if path.exists():
   x=json.loads(path.read_text())
   if x['plan_sha256']==digest:record=x;terminal=filename.endswith('result.json');break
 if record is None:raise ValueError('no completedcurrentcells;stalepreviousresultsnotcurrent')
 assert all(sha(R/n)==h for n,h in plan['prospective_module_hashes'].items());source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/financial-document-processor');assert all(sha(source/n)==h for n,h in plan['task_source_manifest'].items());runtime=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime';assert all(sha(runtime/n)==h for n,h in plan['runtime_hashes'].items());assert sha(R/'public-financial-tools-draft.json')==plan['public_tools_manifest_sha256'];assert plan['memory_mb']==4096 and plan['per_actor_POST_cap']==16 and plan['actor_seconds']==600
 ledger=json.loads((root/'transport/ledger.json').read_text());journal=json.loads((root/'transport/prospective-ledger.json').read_text());views={v['request']:v for v in journal['records']};rows=[];pins={}
 for row in record['rows']:
  arm=row['arm'];requests=[r for r in ledger['records'] if r['actor']==arm];assert len(requests)==row['provider_POST'];costs=[];corrected=[]
  for raw in requests:
   n=raw['request'];v=views[n];c=v['accounting_view']['derived_cost'];assert c['provider_cost_complete'] and raw['provider_status']==200 and raw['stream_eof'] and raw['error'] is None and raw['provider_backend']=='127.0.0.1:18001';costs.append(c);a=root/'transport'/f'response-{n}.sse';b=root/'transport'/f'derived-response-{n}.sse';assert sha(a)==v['raw_sha256'] and sha(b)==v['derived_sha256'];pins[str(a.relative_to(root))]=sha(a);pins[str(b.relative_to(root))]=sha(b)
   if v['accounting_view']['correction_applied']:
    def sse(p):return [json.loads(l[6:]) for l in p.read_bytes().splitlines() if l.startswith(b'data: ') and l[6:]!=b'[DONE]']
    aa,bb=sse(a),sse(b);ta=next(e for e in aa if e['type']=='response.completed');tb=next(e for e in bb if e['type']=='response.completed');before=ta['response']['usage']['output_tokens_details']['reasoning_tokens'];after=tb['response']['usage']['output_tokens_details']['reasoning_tokens'];assert 1<=before-after<=7 and after==ta['response']['usage']['output_tokens'] and v['accounting_view']['raw_cost']['error']=='invalid_reasoning_subset';ta['response']['usage']['output_tokens_details']['reasoning_tokens']=after;assert aa==bb;corrected.append(n)
   else:assert a.read_bytes()==b.read_bytes()
  gross=sum(c['gross_tokens'] for c in costs);assert gross==row['provider_tokens_lower_bound'] and row['cost_complete'];native=read_events(root/arm/'native.jsonl');turns=[e for e in native if e.get('type')=='turn.completed'];reconciled=False
  if turns:
   for nk,ck in [('input_tokens','input_tokens_inclusive'),('output_tokens','output_tokens_inclusive'),('reasoning_output_tokens','reasoning_tokens_reported')]:assert sum(t['usage'][nk] for t in turns)==sum(c[ck] for c in costs)
   reconciled=True
  cap=verify(root/arm/'captured',plan['actor_image_id']);assert row['replay']['replay_complete'] and not row['replay']['rebuild_performed'];assert set(row['replay']['absent_paths_preserved'])=={p for p,r in cap['artifacts'].items() if r['state']=='absent'};setup=row['dependency_setup'];assert setup['test_network_disconnected'] and setup['pandas']=='2.3.2';assert sha(root/arm/'trusted-setup.log')==setup['setup_log_sha256'];tests=json.loads((root/arm/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(root/arm/'logs/verifier/reward.txt').read_text().strip();assert reward==row['reward'] and len(tests)==row['test_events']==7;solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved'];prompt=(root/arm/'prompt.txt').read_text();from uniform_budget_notice import NOTICE;assert prompt.count(NOTICE)==1
  for f in [root/arm/'prompt.txt',root/arm/'native.jsonl',root/arm/'captured/capture.json',root/arm/'logs/verifier/ctrf.json',root/arm/'logs/verifier/reward.txt',root/arm/'trusted-setup.log']:pins[str(f.relative_to(root))]=sha(f)
  rows.append({'arm':arm,'solved':solved,'official_reward':reward,'passed_tests':sum(t['status']=='passed' for t in tests),'POST':len(requests),'gross_tokens':gross,'provider_cost_complete':True,'native_provider_reconciled':reconciled,'native_terminal':[e['type'] for e in native if e.get('type') in ['turn.completed','turn.failed']],'directory_states':{p:r['state'] for p,r in cap['artifacts'].items()},'corrections':corrected,'actor_seconds':row['actor_seconds'],'setup_seconds':setup['seconds']})
 complete=terminal and len(rows)==4 and not record.get('errors');cleanup=None
 if complete:
  assert ledger['provider_POST']==len(ledger['records'])==sum(r['POST'] for r in rows)==record['POST'];assert ledger['native_starts']==record['starts']==4;assert record['proxy_journal']['journal_collected'];assert sha(root/'proxy-bundle/journal/proxy.json')==record['proxy_journal']['sha256'];cleanup={}
  for kind,args in [('containers',['docker','ps','-a','--filter','name=solpi-tfp','--format','{{.Names}}']),('networks',['docker','network','ls','--filter','name=solpi-tfp','--format','{{.Name}}'])]:cleanup[kind]=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10).stdout.splitlines()
  assert cleanup=={'containers':[],'networks':[]}
 audit={'plan_sha256':digest,'stage_complete':complete,'rows':rows,'starts':ledger['native_starts'],'POST':ledger['provider_POST'],'receipts':len(ledger['records']),'complete_cell_gross_tokens':sum(r['gross_tokens'] for r in rows),'cleanup':cleanup,'candidate_promotion':False,'representative_confirmation':False,'goal_complete':False,'artifact_hashes':pins};(R/'matched-financial-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
