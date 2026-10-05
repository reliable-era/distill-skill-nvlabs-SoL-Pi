"""Read-only independent receipt/native/grading audit;partial stages stay partial."""
import hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def events(path):
 out=[]
 for line in path.read_text().splitlines():
  try:out.append(json.loads(line))
  except ValueError:pass
 return out
if __name__=='__main__':
 plan=json.loads((R/'matched-html-plan.json').read_text());digest=sha(R/'matched-html-plan.json');root=pathlib.Path('/tmp/solpi-mh-'+digest[:20]);final=R/'matched-html-resumed-result.json';progress=final if final.exists() else R/'matched-html-resumed-progress.json';record=json.loads(progress.read_text());assert record['plan_sha256']==digest
 rows=[];pins={};all_requests=[];posted=started=received=0
 for name in ['matched-html-plan.json','matched-html-result.json','matched-html-resumed-result.json','matched-html-resume-protocol.json','resume_matched_html_panel.py','matched-html-candidate-harvest-audit.json']:
  path=R/name
  if path.exists():pins['evidence/'+name]=sha(path)
 assert all(sha(R/n)==v for n,v in plan['prospective_module_hashes'].items())
 for segment in ['transport','transport-resume-v1']:
  ledger=json.loads((root/segment/'ledger.json').read_text());journal=json.loads((root/segment/'prospective-ledger.json').read_text());assert ledger['provider_POST']>=len(ledger['records']);posted+=ledger['provider_POST'];started+=ledger['native_starts'];received+=len(ledger['records']);views={x['request']:x for x in journal['records']}
  assert len(views)==len(journal['records'])
  for p in [root/segment/'ledger.json',root/segment/'prospective-ledger.json']:pins[str(p.relative_to(root))]=sha(p)
  for raw in ledger['records']:
   if raw['request'] not in views:continue # Inflight/unfinished never inferred as zero.
   view=views[raw['request']];all_requests.append((segment,raw,view))
 for row in record['rows']:
  arm=row['arm'];requests=[x for x in all_requests if x[1]['actor']==arm];assert len(requests)==row['provider_POST'];costs=[];corrections=[]
  for segment,raw,view in requests:
   n=raw['request'];original=root/segment/f'response-{n}.sse';derived=root/segment/f'derived-response-{n}.sse';assert sha(original)==view['raw_sha256'] and sha(derived)==view['derived_sha256'];assert raw['stream_eof'] is True and raw['provider_status']==200 and raw['error'] is None and raw['provider_backend']=='127.0.0.1:18001';cost=view['accounting_view']['derived_cost'];assert cost['provider_cost_complete'];costs.append(cost)
   def sse(path):return [json.loads(line[6:]) for line in path.read_bytes().splitlines() if line.startswith(b'data: ') and line[6:]!=b'[DONE]']
   a,b=sse(original),sse(derived)
   if view['accounting_view']['correction_applied']:
    assert view['accounting_view']['raw_cost']['error']=='invalid_reasoning_subset';ta=next(e for e in a if e['type']=='response.completed');tb=next(e for e in b if e['type']=='response.completed');before=ta['response']['usage']['output_tokens_details']['reasoning_tokens'];after=tb['response']['usage']['output_tokens_details']['reasoning_tokens'];assert 1<=before-after<=7;assert after==ta['response']['usage']['output_tokens'];ta['response']['usage']['output_tokens_details']['reasoning_tokens']=after;assert a==b;corrections.append({'segment':segment,'request':n,'raw_reasoning':before,'derived_reasoning':after,'raw_failure_preserved':True})
   else:assert original.read_bytes()==derived.read_bytes()
   for p in [original,derived]:pins[str(p.relative_to(root))]=sha(p)
  native=events(root/arm/'native.jsonl');turns=[e for e in native if e.get('type')=='turn.completed'];native_reconciled=False
  if turns:
   usage={k:sum(t['usage'].get(k,0) for t in turns) for k in ['input_tokens','output_tokens','reasoning_output_tokens','cached_input_tokens']};assert usage['input_tokens']==sum(c['input_tokens_inclusive'] for c in costs);assert usage['output_tokens']==sum(c['output_tokens_inclusive'] for c in costs);assert usage['reasoning_output_tokens']==sum(c['reasoning_tokens_reported'] for c in costs);native_reconciled=True
  reward=(root/arm/'logs/verifier/reward.txt').read_text().strip();tests=json.loads((root/arm/'logs/verifier/ctrf.json').read_text())['results']['tests'];assert reward==row['reward'] and len(tests)==row['test_events']==1;solved=reward=='1' and all(t['status']=='passed' for t in tests);assert solved==row['solved'];gross=sum(c['gross_tokens'] for c in costs);assert gross==row['provider_tokens_lower_bound']
  if row['output_present']:
   cap=json.loads((root/arm/'captured/capture.json').read_text());payload=root/arm/'captured'/cap['artifacts']['/app/out.html']['local_payload'];assert sha(payload)==row['graded_output_sha256']
  for p in [root/arm/'native.jsonl',root/arm/'logs/verifier/reward.txt',root/arm/'logs/verifier/ctrf.json']:pins[str(p.relative_to(root))]=sha(p)
  rows.append({'arm':arm,'solved':solved,'official_reward':reward,'POSTs':len(requests),'gross_tokens':gross,'native_provider_reconciled':native_reconciled,'corrections':corrections,'output_present':row['output_present'],'cost_complete':True})
 complete=final.exists() and len(rows)==4 and not record.get('errors')
 cleanup=None
 if complete:
  assert posted==received==sum(r['POSTs'] for r in rows)==record['POST'] and started==record['starts']==4
  cleanup={}
  for kind in ['container','network']:
   args=['docker','ps','-a','--filter','name=solpi-tbp','--format','{{.Names}}'] if kind=='container' else ['docker','network','ls','--filter','name=solpi-tbp','--format','{{.Name}}']
   p=subprocess.run(args,capture_output=True,text=True,check=True,timeout=10);cleanup[kind+'_names']=p.stdout.splitlines()
  assert cleanup=={'container_names':[],'network_names':[]}
 audit={'plan_sha256':digest,'rows':rows,'stage_complete':complete,'native_starts':started,'provider_POST':posted,'received_requests':received,'independent_cleanup':cleanup,'all_arms_complete':len(rows)==4,'artifact_hashes':pins,'failure_inclusive_gross_tokens_for_completed_cells':sum(r['gross_tokens'] for r in rows),'no_partial_as_zero':True,'representative_confirmation':False,'candidate_promotion':False,'goal_complete':False};(R/'matched-html-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='artifact_hashes'},indent=2))
