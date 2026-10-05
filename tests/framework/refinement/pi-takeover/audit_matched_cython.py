"""Independent read-only partial/final audit;native failures not inferred as zero."""
import hashlib,json,pathlib,subprocess
from task_replay import verify_payload
from cython_partial_output import verify_partial
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def events(path):
 out=[]
 for line in path.read_text().splitlines():
  try:out.append(json.loads(line))
  except ValueError:pass
 return out
if __name__=='__main__':
 digest=sha(R/'matched-cython-plan.json');plan=json.loads((R/'matched-cython-plan.json').read_text());root=pathlib.Path('/tmp/solpi-mc-'+digest[:20]);final=R/'matched-cython-result.json';f=final if final.exists() else R/'matched-cython-progress.json';result=json.loads(f.read_text());assert result['plan_sha256']==digest;assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items());ledger=json.loads((root/'transport/ledger.json').read_text());journal=json.loads((root/'transport/prospective-ledger.json').read_text());views={x['request']:x for x in journal['records']};assert len(views)==len(journal['records']);rows=[];pins={}
 for row in result['rows']:
  arm=row['arm'];requests=[r for r in ledger['records'] if r['actor']==arm];assert len(requests)==row['provider_POST'];costs=[];corrected=[]
  for raw in requests:
   n=raw['request'];view=views[n];cost=view['accounting_view']['derived_cost'];assert raw['stream_eof'] and raw['provider_status']==200 and raw['error'] is None and raw['provider_backend']=='127.0.0.1:18001' and cost['provider_cost_complete'];costs.append(cost)
   a=root/'transport'/f'response-{n}.sse';b=root/'transport'/f'derived-response-{n}.sse';assert sha(a)==view['raw_sha256'] and sha(b)==view['derived_sha256'];pins[str(a.relative_to(root))]=sha(a);pins[str(b.relative_to(root))]=sha(b)
   if view['accounting_view']['correction_applied']:
    def sse(path):return [json.loads(line[6:]) for line in path.read_bytes().splitlines() if line.startswith(b'data: ') and line[6:]!=b'[DONE]']
    aa,bb=sse(a),sse(b);ta=next(e for e in aa if e['type']=='response.completed');tb=next(e for e in bb if e['type']=='response.completed');before=ta['response']['usage']['output_tokens_details']['reasoning_tokens'];after=tb['response']['usage']['output_tokens_details']['reasoning_tokens'];assert view['accounting_view']['raw_cost']['error']=='invalid_reasoning_subset' and 1<=before-after<=7 and after==ta['response']['usage']['output_tokens'];ta['response']['usage']['output_tokens_details']['reasoning_tokens']=after;assert aa==bb;corrected.append(n)
   else:assert a.read_bytes()==b.read_bytes()
  gross=sum(c['gross_tokens'] for c in costs);assert gross==row['provider_tokens_lower_bound'];native=events(root/arm/'native.jsonl');turns=[e for e in native if e.get('type')=='turn.completed'];reconciled=False
  if turns:
   assert sum(t['usage']['input_tokens'] for t in turns)==sum(c['input_tokens_inclusive'] for c in costs);assert sum(t['usage']['output_tokens'] for t in turns)==sum(c['output_tokens_inclusive'] for c in costs);assert sum(t['usage']['reasoning_output_tokens'] for t in turns)==sum(c['reasoning_tokens_reported'] for c in costs);reconciled=True
  tests=json.loads((root/arm/'logs/verifier/ctrf.json').read_text())['results']['tests'];reward=(root/arm/'logs/verifier/reward.txt').read_text().strip();assert reward==row['reward'] and len(tests)==row['test_events']==11;solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved'];cap=root/arm/'captured';manifest=json.loads((cap/'capture.json').read_text())
  if row['output_present']:
   assert manifest['capture_complete'] and manifest['stopped_actor_verified'] and manifest['image_id']==plan['image_id']
   from task_artifacts import descriptor
   expected=descriptor('build-cython-ext',row['output_classification']['dynamic']);assert set(manifest['artifacts'])=={i['path'] for i in expected}
   for i in expected:
    rec=manifest['artifacts'][i['path']];assert all(rec[k]==v for k,v in i.items());verify_payload(cap/rec['local_payload'],rec)
  else:verify_partial(cap,plan['image_id']);assert row['replay']['missing_installation_preserved']
  assert row['replay']['replay_complete'] and not row['replay']['rebuild_performed'];assert row['dependency_setup']['target_builds']==row['dependency_setup']['target_installs']==0
  for p in [root/arm/'native.jsonl',root/arm/'logs/verifier/ctrf.json',root/arm/'logs/verifier/reward.txt',cap/'capture.json']:pins[str(p.relative_to(root))]=sha(p)
  rows.append({'arm':arm,'solved':solved,'reward':reward,'test_events':len(tests),'passed_tests':sum(t['status']=='passed' for t in tests),'POST':len(requests),'gross_tokens':gross,'provider_cost_complete':True,'native_provider_reconciled':reconciled,'native_terminal':[e.get('type') for e in native if e.get('type') in ['turn.failed','turn.completed']],'corrected_requests':corrected,'installation_present':row['output_present'],'source_capture_verified':True})
 complete=final.exists() and len(rows)==4 and not result.get('errors');cleanup=None
 if complete:
  assert ledger['provider_POST']==len(ledger['records'])==sum(r['POST'] for r in rows)==result['POST'];assert ledger['native_starts']==result['starts']==4;cleanup={}
  for kind in ['container','network']:
   args=['docker','ps','-a','--filter','name=solpi-tcp','--format','{{.Names}}'] if kind=='container' else ['docker','network','ls','--filter','name=solpi-tcp','--format','{{.Name}}'];p=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10);cleanup[kind]=p.stdout.splitlines()
  assert cleanup=={'container':[],'network':[]}
 audit={'plan_sha256':digest,'rows':rows,'stage_complete':complete,'starts':ledger['native_starts'],'POST':ledger['provider_POST'],'receipts':len(ledger['records']),'completed_cell_gross_tokens':sum(r['gross_tokens'] for r in rows),'cleanup':cleanup,'actor_prerequisite_gap':'pytest unavailable in frozen actor software cache;public repository tests explicitly permitted;do not change active panel','economic_eligibility':False,'representative_confirmation':False,'goal_complete':False,'artifact_hashes':pins};(R/'matched-cython-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
