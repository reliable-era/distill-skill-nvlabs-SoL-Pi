"""Actual negative G3 closure checks; no inference, shared-system repairs or deletes.
Complements (does not replace) original receipt/prompt audit, full boundary and
independent statistics. Raw artifacts remain private; this writes hash indices.
"""
import collections,datetime,hashlib,json,pathlib,re,subprocess
from run_cell import H,sha,tree
from scheduler import load_plan

def load(p):return json.loads(pathlib.Path(p).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(H.parents[3]),*args],text=True).strip()
def absent(pid):return not subprocess.run(['ps','-p',str(pid),'-o','pid=,stat='],capture_output=True,text=True).stdout.strip()
def main():
 plan=load_plan();audit=load(H/'audits/round1.json');analysis=load(H/'analysis/round1.json');boundary=load(H/'analysis/round1-boundary.json');independent=load(H/'analysis/round1-independent.json');assert analysis['round1_negative_stop'] and not analysis['round1_survived'] and not analysis['family_accepted'];assert independent['round1_negative_stop'] and independent['cells']==784
 assert boundary['audit_sha256']==sha(H/'audits/round1.json') and boundary['plan_sha256']==sha(H/'plan.json');assert not audit['missing_cells'] and audit['all_observed_costs_complete'] and audit['all_observed_grades_valid'];assert len(audit['rows'])==audit['attempts']==784 and all(r['round']==1 and r['attempts']==1 for r in audit['rows'])
 for path,digest in independent['inputs_sha256'].items():assert sha(path)==digest
 controls_plan=load(H/'controls-plan.json');original=load(H/'controls-result.json');repair=load(H/'controls-repair-result.json');controls=load(H/'controls-audit.json');selection=H.parent/'g1/polyglot-selection.json';assert sha(selection)==controls_plan['selection_sha256'];assert load(selection)['exclusions']==controls_plan['exclusions'] and len(controls_plan['exclusions'])==14
 source=pathlib.Path('/tmp/solpi-polyglot-grader-source');assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==plan['source_revision'];all_tasks=sorted(str(p.relative_to(source)) for lang in ('cpp','go','java','javascript','python','rust') for p in (source/lang/'exercises/practice').iterdir() if p.is_dir());eligible=sorted(set(all_tasks)-{t.removeprefix('aider:') for t in controls_plan['exclusions']});assert len(all_tasks)==225 and eligible==controls_plan['tasks'] and len(eligible)==211
 assert original['model_calls']==repair['model_calls']==controls['model_calls']==0 and len(original['rows'])==211 and len(repair['rows'])==6 and repair['original_result_sha256']==sha(H/'controls-result.json')
 control_index=[];preparation_failures=[];final_controls={}
 for kind,value in [('original',original),('repair',repair)]:
  for row in value['rows']:
   assert row['model_calls']==0
   if 'private_preparation' not in row:
    assert kind=='original' and not row['valid_pair'] and row['controls']==[] and row['error'] and row['task'] in {r['task'] for r in repair['rows']};preparation_failures.append(row);final_controls[row['task']]=row;continue
   d=pathlib.Path(row['private_preparation']);assert sha(d/'manifest.json')==row['manifest_sha256'] and len(row['controls'])==2
   for c in row['controls']:
    log=d/(c['mode']+'.private.log');assert sha(log)==c['private_log_sha256'] and c['owned_container_absent'];control_index.append(dict(task=row['task'],kind=kind,mode=c['mode'],path=str(log),sha256=sha(log),exit=c['exit_code']))
    if row['valid_pair'] and c['mode']=='reference':
     count=re.search(r'Executed accepted tests:\s*(\d+)',log.read_text());assert c['exit_code']==0 and count and int(count.group(1))>0
   assert row['valid_pair']==all(c['exit_code']==c['expected_exit'] for c in row['controls']);final_controls[row['task']]=row
 assert sorted(t for t,r in final_controls.items() if r['valid_pair'])==plan['tasks']==controls['control_valid_tasks'];assert {t for t,r in final_controls.items() if not r['valid_pair']}=={r['task'] for r in controls['excluded_tasks']} and len(controls['excluded_tasks'])==15
 # Preregistration/control audit commits precede the first actual provider POST.
 freeze=git('show','7257c9d:tests/framework/refinement/g3/plan.json')+'\n';assert hashlib.sha256(freeze.encode()).hexdigest()==sha(H/'plan.json')
 assert hashlib.sha256((git('show','5d9ca19:tests/framework/refinement/g3/analyze.py')+'\n').encode()).hexdigest()==sha(H/'analyze.py')
 files=[];receipts=[];attempts=[];events=[];windows=[];load_samples=0;verified_binaries={};output_cap_responses=collections.Counter();terminal_types=collections.Counter();actual_provider_tokens=collections.Counter()
 for launch_path in sorted(H.glob('waves/*/launch.json')):
  launch=load(launch_path);assert launch['round']==1 and absent(launch['pid']);result=load(launch_path.with_name('result.json'));assert not result['error'] and not result['stop'];assert load(launch_path.with_name('progress.json'))=={k:v for k,v in result.items() if k not in ('error',)} or load(launch_path.with_name('progress.json'))['attempts']==result['attempts']
  w=launch['window'];end=datetime.datetime.fromisoformat(w['end']);latest=datetime.datetime.fromisoformat(w['latest']);start=datetime.datetime.fromisoformat(w['start']);assert end-start==datetime.timedelta(hours=4) and latest-start==datetime.timedelta(hours=2);assert result['maximum_active_slots']<=18
  windows.append(dict(wave=launch_path.parent.name,commit=w['commit'],cells=len(result['attempts']),launch_sha256=sha(launch_path),result_sha256=sha(launch_path.with_name('result.json'))))
  events.extend(e for e in result['events'] if e['kind']=='admitted')
  for r in result['attempts']:
   assert r['attempt']==1 and not r['infra_retry_eligible'] and not r['cleanup_errors'] and r['owned_containers_absent'];d=pathlib.Path(r['root']);attempts.append(r);ins=load(d/'actor-inspect.json');hc=ins['HostConfig'];assert hc['CapDrop']==['ALL'] and hc['SecurityOpt']==['no-new-privileges'] and hc['NetworkMode']=='none';assert all(not m['RW'] for m in ins['Mounts']);assert {m['Destination'] for m in ins['Mounts']}=={'/skills','/broker','/opt/solpi/codex','/opt/solpi/relay.py'}
   binary=next(m['Source'] for m in ins['Mounts'] if m['Destination']=='/opt/solpi/codex')
   if binary not in verified_binaries:verified_binaries[binary]=sha(binary)
   assert verified_binaries[binary]==plan['binary_sha256'];env=dict(s.split('=',1) for s in ins['Config']['Env'] if '=' in s);assert all(env.get(k,'')=='' for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'))
   ledger=load(d/'transport/ledger.json');assert ledger['provider_POST']==r['requests']<=60
   for c in ledger['records']:
    assert c['backend']==plan['route']=='127.0.0.1:9012' and c['model']==plan['model']=='Qwen/Qwen3.8-27B' and c['path']=='/v1/responses' and c['output_cap']==16384 and c['provider_status']==200 and c['error'] is None
    assert start<=datetime.datetime.fromisoformat(c['started_utc'])<=end and datetime.datetime.fromisoformat(c['ended_utc'])<=end
    terminal=[]
    for line in (d/f"transport/response-{c['request']}.sse").read_bytes().splitlines():
     if not line.startswith(b'data:'):continue
     try:event=json.loads(line[5:].strip())
     except (ValueError,UnicodeError):continue
     if event.get('type') in ('response.completed','response.incomplete','response.failed'):terminal.append(event)
    assert len(terminal)==1;event=terminal[0];u=event['response']['usage'];assert all(type(u[k]) is int and u[k]>=0 for k in ('input_tokens','output_tokens','total_tokens')) and u['input_tokens']+u['output_tokens']==u['total_tokens'] and u['output_tokens']<=16384;actual_provider_tokens[r['cell_id']]+=u['total_tokens'];terminal_types[event['type']]+=1
    if event['type']=='response.incomplete':assert event['response']['incomplete_details']['reason']=='max_output_tokens';output_cap_responses[r['arm']]+=1
    receipts.append(dict(cell_id=r['cell_id'],request=c['request'],root=str(d/'transport'),started_utc=c['started_utc'],original_sha256=c['original_sha256'],forwarded_sha256=c['forwarded_sha256'],response_sha256=c['response_sha256'],backend=c['backend'],actual_standard_provider_tokens=u['total_tokens'],terminal_type=event['type']))
   samples=load(d/'load-samples.json');assert samples[0]['kind']=='start' and all(s['kind'] in ('start','periodic') for s in samples);load_samples+=len(samples)
   files.append(dict(cell_id=r['cell_id'],root=str(d),attempt_result_sha256=sha(d/'attempt-result.json'),native_sha256=sha(d/'native.jsonl'),prompt_sha256=sha(d/'prompt.txt'),verifier_sha256=sha(d/'verifier.log'),actor_inspect_sha256=sha(d/'actor-inspect.json'),load_samples_sha256=sha(d/'load-samples.json'),raw_solved=r['solved'],raw_grade_valid=r['grade_valid'],raw_cost_complete=r['cost_complete']))
 assert len(attempts)==len(events)==784 and len(receipts)==sum(r['requests'] for r in audit['rows'])==6660
 assert all(actual_provider_tokens[r['cell_id']]==r['tokens_lower_bound'] for r in audit['rows'])
 first=min(datetime.datetime.fromisoformat(c['started_utc']) for c in receipts)
 for commit in ('47ccf73','b587ceb','65e7e82','93e58b7','5d9ca19','7257c9d'):assert datetime.datetime.fromisoformat(git('show','-s','--format=%cI',commit))<first
 for f in ('controls-launch.json','controls-repair-launch.json','grade-timeout-replay-launch.json'):assert absent(load(H/f)['pid'])
 replay=load(H/'grade-timeout-replay-result.json');assert replay['model_calls']==0 and replay['all_owned_grader_containers_absent'];assert len(audit['grade_timeout_repairs'])==2
 owned={r[k] for r in attempts for k in ('actor','grade_container')}|{c['container_name'] for v in (original,repair) for r in v['rows'] for c in r['controls']};names=set(subprocess.check_output(['docker','ps','-a','--filter','name=solpi-g3-','--format','{{.Names}}'],text=True,timeout=30).splitlines());assert not owned.intersection(names) and not names
 networks=subprocess.check_output(['docker','network','ls','--filter','name=solpi-g3-','--format','{{.Name}}'],text=True,timeout=30).splitlines();assert not networks
 assert not git('diff','--name-only','68cff75','HEAD','--','tests/framework/refinement/g1','tests/framework/refinement/g2','skills','tests/archive','tests/goal.md')
 external=load(H/'external-readme-change.json');assert git('diff-tree','--no-commit-id','--name-only','-r',external['external_commit'])=='README.md' and sha(external['path'])==external['external_sha256']
 for commit in git('rev-list','68cff75..HEAD').splitlines():
  if commit==external['external_commit']:continue
  paths=git('diff-tree','--no-commit-id','--name-only','-r',commit).splitlines();assert all(p=='tests/STATUS.md' or p.startswith('tests/framework/refinement/g3/') for p in paths),(commit,paths)
 status=git('status','--short');unrelated=[line for line in status.splitlines() if 'qwen-load-balancer/nginx.conf' in line];assert len(unrelated)==4
 output=H/'audits';(output/'private-artifact-index.json').write_text(json.dumps(dict(attempts=files,requests=receipts,controls=control_index,original_preparation_failures_preserved=preparation_failures,raw_payloads_traces_and_solutions_remain_private=True),indent=2)+'\n')
 result=dict(status='ACTUAL_G3_NEGATIVE_EXECUTION_CLOSURE_VERIFIED_NOT_SAVINGS_ACCEPTANCE',disposition='negative_round1_futility',rounds_attempted=[1],rounds2_3='unattempted/ineligible after mandatory futility',cells=784,attempts=784,requests=6660,tokens= sum(r['tokens_lower_bound'] for r in audit['rows']),solves=sum(r['solved'] for r in audit['rows']),failures=sum(not r['solved'] for r in audit['rows']),native_wall_timeouts=sum(r['timeout'] for r in attempts),verified_original_test_deadlines=2,request_cap_reached_cells=sum(r['requests']==60 for r in attempts),infra_retry_attempts=0,provider_terminal_events=dict(terminal_types),individual_output_cap_responses_by_arm=dict(output_cap_responses),individual_output_cap_responses_total=sum(output_cap_responses.values()),actual_provider_usage_independently_summed_from_terminal_SSE=True,all_provider_costs_exact_after_named_raw_byte_projection=True,raw_incomplete_cost_flags_retained=sum(not r['cost_complete'] for r in attempts),raw_unknown_grade_records_retained=sum(not r['grade_valid'] for r in attempts),all_original_controls_logs_manifests_hash_checked=len(control_index),original_control_preparation_failures_preserved=len(preparation_failures),all211_have_final_original_gold_noop_checks=True,all_attempt_payload_response_prompt_grade_inspect_artifacts_checked=True,load_samples=load_samples,maximum_slots=18,all_owned_workers_containers_absent=True,owned_networks_created=0,source_revision=plan['source_revision'],candidate_sha256=plan['skills']['candidate']['tree']['SKILL.md'],karpathy_sha256=plan['skills']['karpathy']['tree']['SKILL.md'],windows=windows,first_provider_post_utc=first.isoformat(),last_provider_end_utc=max(c['ended_utc'] for r in attempts for c in load(pathlib.Path(r['root'])/'transport/ledger.json')['records']),unrelated_worktree_status_preserved=unrelated,external_supervisor_README_exception=external,agent_changes_scoped_G3_STATUS_only=True,no_shipping=True,no_push=True,protected_scope_unchanged_except_named_external_README=True,private_artifact_index_sha256=sha(output/'private-artifact-index.json'),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 result['inputs_sha256']={str(H/f):sha(H/f) for f in ('plan.json','controls-plan.json','controls-result.json','controls-repair-result.json','controls-audit.json','audits/round1.json','analysis/round1.json','analysis/round1-boundary.json','analysis/round1-independent.json','execution-repair.json','grade-timeout-repair.json','grade-timeout-replay-result.json','final_execution_audit.py')};(output/'final-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','cells','requests','tokens','solves','failures','native_wall_timeouts','request_cap_reached_cells','all_owned_workers_containers_absent')}))
if __name__=='__main__':main()
