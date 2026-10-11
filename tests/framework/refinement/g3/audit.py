"""Independent G3 attempt/provider/prompt/resource/grade reconciliation; no POST."""
import argparse,datetime,json,pathlib,re,hashlib
from run_cell import H,sha,tree
from transport import usage_from_sse,MODEL,PEER

def audit(round_number):
 plan=json.loads((H/'plan.json').read_text());expected={c['cell_id']:c for c in plan['schedule'] if c['round']<=round_number};attempts=[];waves=[]
 from implementation_policy import verify
 amendment=verify(plan)
 import importlib.util,copy
 spec=importlib.util.spec_from_file_location('g3_legacy_transport',H/'frozen-v1/transport.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
 repairs=[]
 for file in sorted(H.glob('waves/*/progress.json')):
  launch=json.loads(file.with_name('launch.json').read_text());assert launch['plan_sha256']==sha(H/'plan.json');w=launch['window'];assert datetime.datetime.fromisoformat(w['end'])-datetime.datetime.fromisoformat(w['start'])==datetime.timedelta(hours=4);assert datetime.datetime.fromisoformat(w['latest'])-datetime.datetime.fromisoformat(w['start'])==datetime.timedelta(hours=2)
  value=json.loads(file.read_text());assert value['maximum_active_slots']<=18
  for row in value['attempts']:
   if row['round']>round_number:continue
   assert row['cell_id'] in expected;c=expected[row['cell_id']];assert all(row[k]==c[k] for k in ('task','arm','round'));d=pathlib.Path(row['root']);assert row==json.loads((d/'attempt-result.json').read_text());assert row['owned_containers_absent'] and not row['cleanup_errors'];assert row['attempt'] in (1,2)
   assert sha(d/'prompt.txt')==row['prompt_sha256'];baseline=pathlib.Path(plan['prepared_tasks'][c['task']]);prompt=(baseline/'prompt.txt').read_text()+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
   for skill in plan['arm_skills'][c['arm']]:assert tree(d/'skills'/skill)==plan['skills'][skill]['tree'];prompt+='\n'+(d/'skills'/skill/'SKILL.md').read_text()
   if not plan['arm_skills'][c['arm']]:prompt+='\nNo skill is supplied.\n'
   assert prompt==(d/'prompt.txt').read_text();assert sorted(p.name for p in (d/'skills').iterdir())==sorted(plan['arm_skills'][c['arm']]);assert tree(d/'grader')==plan['grader_trees'][c['task']];assert tree(d/'starter')==plan['starter_trees'][c['task']]
   if row['native_started']:
    ins=json.loads((d/'actor-inspect.json').read_text());hc=ins['HostConfig'];assert hc['NetworkMode']=='none' and hc['Memory']==2147483648 and hc['NanoCpus']==1000000000 and hc['PidsLimit']==128 and ins['Config']['User']=='0';assert ins['Image']==plan['images'][c['task'].split('/')[0]]
    assert ins['Config']['Cmd'][-1]==prompt
    ad=json.loads((d/'admission.json').read_text());assert ad['backend']==PEER and all(v['num_waiting_reqs']==0 for v in ad['body']);assert datetime.datetime.fromisoformat(w['start'])<=datetime.datetime.fromisoformat(row['started_utc'])<=datetime.datetime.fromisoformat(w['latest'])
    assert sha(d/'native.jsonl')==row['native_sha256'] if 'native_sha256' in row else row['error'] is not None
   ledger=json.loads((d/'transport/ledger.json').read_text()) if (d/'transport/ledger.json').exists() else {'provider_POST':0,'records':[]};records=ledger['records'];assert len(records)==ledger['provider_POST']==row['requests']<=60
   for receipt in records:
    n=receipt['request'];original=(d/f'transport/request-{n}.json').read_bytes();forwarded=(d/f'transport/forwarded-request-{n}.json').read_bytes();assert sha(d/f'transport/request-{n}.json')==receipt['original_sha256'];assert hashlib.sha256(forwarded).hexdigest()==receipt['forwarded_sha256'];a=json.loads(original);b=json.loads(forwarded);assert b['max_output_tokens']==16384 and b['model']==MODEL and b['stream'] is True;assert {k:v for k,v in a.items() if k!='max_output_tokens'}=={k:v for k,v in b.items() if k!='max_output_tokens'};assert receipt['backend']==PEER
    response=d/f'transport/response-{n}.sse';raw=response.read_bytes() if response.exists() else b'';assert hashlib.sha256(raw).hexdigest()==receipt['response_sha256'];cost=(legacy.usage_from_sse if file.parent.name=='r1-w01' else usage_from_sse)(raw,receipt['stream_eof'])
    if receipt.get('proven_zero_model_refusal'):assert receipt['error']=='ConnectionRefusedError' and receipt['provider_status'] is None and not raw;assert receipt['tokens_lower_bound']==0 and receipt['cost_complete']
    else:assert cost['tokens_lower_bound']==receipt['tokens_lower_bound'];assert (cost['cost_complete'] and receipt['error'] is None and receipt['provider_status']==200)==receipt['cost_complete']
   assert row['tokens_lower_bound']==sum(r['tokens_lower_bound'] for r in records);assert row['cost_complete']==all(r['cost_complete'] for r in records)
   if row['grade_valid']:
    assert sha(d/'verifier.log')==row['verifier_sha256'];assert tree(d/'final-work')==row['final_work_hashes'];text=(d/'verifier.log').read_text(errors='replace');count=re.search(r'Executed accepted tests:\s*(\d+)',text);assert row['solved']==(row['verifier_exit']==0) and row['verifier_exit'] in (0,1);assert row['verifier_exit']==1 or count and int(count.group(1))>0
   if file.parent.name=='r1-w01':
    assert amendment and amendment['legacy_window']=='r1-w01'
    original=row;row=copy.deepcopy(row);projected=[]
    for receipt in records:
     response=d/f"transport/response-{receipt['request']}.sse";raw=response.read_bytes() if response.exists() else b'';cost=usage_from_sse(raw,receipt['stream_eof']);known=bool(cost['cost_complete'] and receipt['error'] is None and receipt['provider_status']==200)
     if receipt.get('proven_zero_model_refusal'):cost['tokens_lower_bound']=0;known=True
     projected.append(dict(request=receipt['request'],tokens=cost['tokens_lower_bound'],cost_complete=known,response_sha256=receipt['response_sha256']))
    row['tokens_lower_bound']=sum(c['tokens'] for c in projected);row['cost_complete']=all(c['cost_complete'] for c in projected)
    repairs.append(dict(cell_id=row['cell_id'],original_attempt_result_sha256=sha(d/'attempt-result.json'),original_tokens_lower_bound=original['tokens_lower_bound'],original_cost_complete=original['cost_complete'],projected_tokens_lower_bound=row['tokens_lower_bound'],projected_cost_complete=row['cost_complete'],exact_captured_receipts=projected,model_calls_added=0))
   attempts.append(row)
  waves.append(dict(wave=file.parent.name,progress_sha256=sha(file),terminal=file.with_name('result.json').exists(),maximum_slots=value['maximum_active_slots']))
 keys=[(r['cell_id'],r['attempt']) for r in attempts];assert len(keys)==len(set(keys));rows=[];missing=[]
 for ident,c in expected.items():
  rr=sorted([r for r in attempts if r['cell_id']==ident],key=lambda r:r['attempt'])
  if not rr or len(rr)==1 and rr[0]['infra_retry_eligible']:missing.append(ident);continue
  assert rr[0]['attempt']==1 and (len(rr)==1 or len(rr)==2 and rr[0]['infra_retry_eligible'] and rr[1]['attempt']==2)
  last=rr[-1];rows.append(dict(cell_id=ident,task=c['task'],round=c['round'],arm=c['arm'],solved=last['solved'],grade_valid=last['grade_valid'],tokens_lower_bound=sum(r['tokens_lower_bound'] for r in rr),cost_complete=all(r['cost_complete'] for r in rr),timeout=any(r['timeout'] for r in rr),attempts=len(rr),wall_seconds=sum(r.get('wall_seconds',0) for r in rr),requests=sum(r['requests'] for r in rr),attempt_result_sha256=[sha(pathlib.Path(r['root'])/'attempt-result.json') for r in rr]))
 result=dict(rows=rows,accounting_repairs=repairs,legacy_ownership_failures_retained_no_retry=True,attempts=len(attempts),missing_cells=missing,all_observed_grades_valid=all(r['grade_valid'] for r in rows),all_observed_costs_complete=all(r['cost_complete'] for r in rows),plan_sha256=sha(H/'plan.json'),waves=waves,rounds_through=round_number,acceptance_established=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(H/'audits').mkdir(exist_ok=True);save=__import__('transport').save;save(H/'audits'/f'round{round_number}.json',result);print(json.dumps(dict(cells=len(rows),attempts=len(attempts),missing=len(missing),all_grades_valid=result['all_observed_grades_valid'],all_costs_complete=result['all_observed_costs_complete'])))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--round',required=True,type=int,choices=(1,2,3));a=p.parse_args();audit(a.round)
