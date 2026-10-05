"""Independent artifact/receipt audit; never launches model, grader or cleanup.
Raw task files, commands and responses are not included in the public report.
"""
import argparse,hashlib,json,pathlib,re,subprocess
R=pathlib.Path(__file__).resolve().parent
SMOKE=R.parent/'development/pi-takeover-qwen-smoke'
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
def check_absent(kind,name):
 command=['docker','inspect',name] if kind=='container' else ['docker','network','inspect',name]
 z=subprocess.run(command,capture_output=True,text=True,timeout=5)
 messages=('Error: No such object: '+name,'Error response from daemon: No such container: '+name) if kind=='container' else ('Error: No such network: '+name,'Error response from daemon: network '+name+' not found')
 return z.returncode!=0 and z.stderr.strip() in messages

def audit(stage='smoke'):
 SMOKE=R.parent/('development/pi-takeover-qwen-'+stage)
 p=json.loads((SMOKE/'plan.json').read_text());digest=sha(SMOKE/'plan.json');private=pathlib.Path('/tmp')/('solpi-qwendev-'+digest)
 family=next(iter(p['tasks']));expected=5 if stage=='incremental-coverage' else 4;post_cap=80 if expected==5 else 64
 errors=[];checks=[]
 def require(condition,message):
  checks.append({'check':message,'pass':bool(condition)})
  if not condition:errors.append(message)
 auth=json.loads((SMOKE/'execution-authorization.json').read_text())
 require(auth['plan_sha256']==digest and auth['maximum_starts']==expected,'exact start authorization')
 require(len(p['tasks'])==1 and len(p['schedule'])==expected and p['scope_constraints']['model']=='Qwen3.8-27B-FP8' and not p['scope_constraints']['model_fallback'],'one task/model and matched arms')
 if stage=='incremental-coverage':
  require(set(p['arms'])=={'none','K','candidate','Both','original'} and p['arms']['Both']==['karpathy','candidate'] and p['arms']['original']==['original'],'historical Ours separate from Both')
  for f,h in p['external_files'].items():require(sha(f)==h,'external binding '+f)
 for f,h in p['source_hashes'].items():require(sha(SMOKE/f)==h,'source binding '+f)
 for f,h in p['grading_reuse']['adapter_source_hashes'].items():require(sha(SMOKE/f)==h,'unchanged certified grader '+f)
 for z in p['shared_inference_locks']:
  st=pathlib.Path(z['path']).stat();require((st.st_dev,st.st_ino)==(z['device'],z['inode']),'lock identity '+z['path'])
 ledger=json.loads((private/'transport/ledger.json').read_text()) if (private/'transport/ledger.json').exists() else {}
 final_path=private/'final-evidence.json'
 if not final_path.exists():return {'status':'in_progress','plan_sha256':digest,'starts':ledger.get('native_starts',0),'POST':ledger.get('provider_POST',0),'checks':checks,'errors':errors,'complete':False}
 final=json.loads(final_path.read_text());actors=final['actors'];records=ledger.get('records',[])
 require(final['plan_sha256']==digest,'final plan identity')
 require(final['errors']==[],'runner no infrastructure errors')
 require(final['native_starts']==expected and len(actors)==expected,'all matched cells captured')
 require(final['provider_POST']<=post_cap and len(records)==final['provider_POST'] and len({r['request'] for r in records})==len(records),'all POST receipts covered within cap')
 require(not final['containers_remaining'] and not final['networks_remaining'],'owned remaining lists empty')
 cleanup=final['actual_proofs']['cleanup'];require(cleanup['server_workers']==0 and cleanup['socket_absent'] is True,'broker worker/socket cleanup')
 for key,kind in [('containers','container'),('networks','network')]:
  for z in cleanup[key]:require(z['absence_verified'] is True and check_absent(kind,z['name']),'actual absence '+z['name'])
 topology=final['actual_proofs']['topology']
 require(topology['internal'] is True and topology['ipv6'] is False and topology['gateway_mode']=='isolated' and all(not g for g in topology['gateways']),'recorded isolated topology')
 inspections=final['actual_proofs']['actors']
 require(len(inspections)==len(actors),'prestart inspection coverage')
 for z in inspections:
  require(z['nano_cpus']==1000000000 and z['memory']==536870912 and z['pids']==64 and z['prestart_verified'] is True,'recorded uniform actor resource limits '+z['harness'])
  require(len(z['mounts'])==3 and next(m for m in z['mounts'] if m['destination']=='/skills')['RW'] is False,'recorded readonly skills and no verifier mount '+z['harness'])
 panels=[]
 for a in actors:
  root=private/a['id'];request_rows=[r for r in records if r['actor']==a['id']];cost=0;cost_complete=bool(request_rows);protocol_valid=True
  require(a['arm'] in p['arms'] and a['family']==family,'declared arm/family '+a['id'])
  initial=json.loads((root/'initial-files.json').read_text())
  require(initial==p['external_trees'][p['tasks'][family]['baseline']],'exact initial development workspace '+a['id'])
  require(a['prestart_inspection_verified'] and a['upstream_drained_before_grade'] and a['actor_removed_verified'],'actor prestart and stopped-state safety '+a['id'])
  if stage in ('patch-first','incremental-coverage'):
   harvest=a['completion_harvest']
   require(harvest['maximum_seconds']==240 and harvest['workers_remaining']==0 and harvest['waited_seconds']<=244,'bounded backend harvest '+a['id'])
   require(all(r.get('completion_grace_seconds')==240 for r in request_rows),'declared receipt grace '+a['id'])
  require(len(request_rows)==ledger['per_actor'][a['id']]<=16,'per-actor request coverage '+a['id'])
  for record in request_rows:
   if stage=='incremental-coverage':require(record.get('provider_backend') in {'127.0.0.1:18001','127.0.0.1:18002'},'known load-balanced backend '+str(record['request']))
   n=record['request'];request=private/'transport'/f'request-{n}.json';forwarded=private/'transport'/f'forwarded-request-{n}.json'
   require(sha(request)==record['request_sha256'],'request hash '+str(n))
   original=json.loads(request.read_text());sent=json.loads(forwarded.read_text());cap=sent.pop('max_output_tokens',None);original.pop('max_output_tokens',None)
   require(sent==original and cap==8192 and sent['model']=='Qwen3.8-27B-FP8' and sent['stream'] is True,'single model and uniform one-field output policy '+str(n))
   stream=private/'transport'/f'response-{n}.sse'
   if not stream.exists():cost_complete=False;continue
   require(sha(stream)==record['sha256'],'response hash '+str(n))
   events=[]
   for line in stream.read_bytes().splitlines():
    if line.startswith(b'data: '):
     try:events.append(json.loads(line[6:]))
     except ValueError:pass
   terminals=[e for e in events if isinstance(e,dict) and e.get('type')=='response.completed']
   valid=record['stream_eof'] is True and record['provider_status']==200 and record['error'] is None and len(terminals)==1
   if valid:
    response=terminals[0].get('response',{});u=response.get('usage',{});status=response.get('status')
    valid=status=='completed' or (status=='incomplete' and response.get('incomplete_details')=={'reason':'max_output_tokens'} and response.get('max_output_tokens')==8192)
    valid=valid and all(type(u.get(k)) is int and u[k]>=0 for k in ['input_tokens','output_tokens','total_tokens'])
    valid=valid and u['input_tokens']+u['output_tokens']==u['total_tokens'] and u['total_tokens']>0
    if valid:
     cost+=u['total_tokens'];protocol_valid=protocol_valid and u['output_tokens']<=8192
     require(u['total_tokens']==record['usage_audit']['gross_tokens'],'independent terminal cost '+str(n))
   cost_complete=cost_complete and valid
  require(cost==a['observed_gross_tokens_lower_bound'],'independent actor token sum '+a['id'])
  require(cost_complete==a['provider_cost_complete'],'cost completeness agrees '+a['id'])
  grade=json.loads((root/'grade/result.json').read_text())
  require(grade==a['grade'] and grade['infrastructure_error'] is None,'independent grading record '+a['id'])
  for f,h in grade.get('artifacts',{}).items():require(sha(root/'grade'/f)==h,'grade artifact '+a['id']+'/'+f)
  if family=='go' and grade['solved']:
   text=(root/'grade/stdout').read_text();tests=re.findall(r'Executed accepted tests: (\d+)',text)
   require(len(tests)==1 and int(tests[0])>0,'passing grade executed substantive tests '+a['id'])
  if family=='terminal':
   events=json.loads((root/'grade/ctrf.json').read_text())['results']['tests']
   statuses=[e['status'] for e in events]
   require(len(events)==p['tasks'][family]['expected_test_events'] and all(s in ('passed','failed') for s in statuses),'original Terminal tests collected without skips '+a['id'])
   require(grade['solved']==all(s=='passed' for s in statuses),'Terminal solved matches actual test statuses '+a['id'])
  require(sha(root/'native.jsonl')==a['native_log_sha256'],'native transcript hash '+a['id'])
  for key in p['arms'][a['arm']]:
   for f in (SMOKE/'frozen'/key).rglob('*'):
    if f.is_file():require(sha(f)==sha(root/'skills'/key/f.relative_to(SMOKE/'frozen'/key)),'activated resource '+a['id']+'/'+key+'/'+str(f.relative_to(SMOKE/'frozen'/key)))
  denials=[d for d in ledger.get('local_budget_denials',[]) if d['actor']==a['id']]
  budget_exhaustion=a['actor_budget_exhaustion'] or any(d['reason'] in ('global_POST_cap','per_actor_POST_cap','actor_deadline_reserve') for d in denials)
  panels.append({'arm':a['arm'],'solved':grade['solved'],'cost_complete':cost_complete,'observed_tokens':cost,'protocol_valid':protocol_valid,'native_reconciled':a['native_reconciled'],'budget_exhaustion':budget_exhaustion,'budget_exhaustion_reported':a['actor_budget_exhaustion'],'budget_denial_reasons':sorted({d['reason'] for d in denials}),'native_seconds':a['native_phase_seconds'],'backend_request_counts':{b:sum(r.get('provider_backend')==b for r in request_rows) for b in sorted({r.get('provider_backend') for r in request_rows if r.get('provider_backend')})}})
 eligible=len(panels)==expected and not errors and all(z['cost_complete'] and z['protocol_valid'] for z in panels)
 return {'status':'PASS' if not errors else 'FAIL','complete':len(actors)==expected and not errors,'plan_sha256':digest,'checks':checks,'errors':errors,'panels':panels,'economic_comparison_eligible':eligible,'scope':'One reused '+family+' development fixture/one round; no confidence or majority-harness win. Provider-reported traffic only; no dollars. Historical cohorts excluded.'}

def main():
 a=argparse.ArgumentParser();a.add_argument('--stage',choices=['smoke','terminal','patch-first','incremental-coverage'],default='smoke');a.add_argument('--output',type=pathlib.Path);x=a.parse_args();result=audit(x.stage);output=x.output or R/(x.stage+'-audit.json');output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
 if result['errors']:raise SystemExit(1)
if __name__=='__main__':main()
