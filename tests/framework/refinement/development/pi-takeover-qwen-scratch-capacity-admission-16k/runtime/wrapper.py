"""Private fixture preparation and independent verifier adapters; no implicit launches."""
import signal
import pathlib,json,subprocess,hashlib,shutil,os,uuid,importlib.util
R=pathlib.Path(__file__).resolve().parent.parent
MODEL='Qwen3.8-27B-FP8'
ARMS={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def files(root):
 root=pathlib.Path(root)
 return {str(p.relative_to(root)):({'symlink_target':os.readlink(p)} if p.is_symlink() else sha(p)) for p in sorted(root.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}
def validate_inputs(plan):
 if len(plan['schedule'])!=12 or {x['family'] for x in plan['schedule']}!=set(plan['tasks']):raise RuntimeError('fixed schedule')
 for family in plan['tasks']:
  if sorted(x['arm'] for x in plan['schedule'] if x['family']==family)!=sorted(ARMS):raise RuntimeError('matched arms')
 for path,pins in plan['external_trees'].items():
  if files(path)!=pins:raise RuntimeError('external full tree changed: '+path)
 for path,h in plan['external_files'].items():
  if sha(path)!=h:raise RuntimeError('external source changed')
def prepare(private,port,task,arm):
 root=pathlib.Path(private);root.mkdir(mode=0o700,exist_ok=False)
 shutil.copytree(task['baseline'],root/'work',symlinks=True)
 (root/'home'/'.codex').mkdir(parents=True);(root/'skills').mkdir()
 for key in ARMS[arm]:shutil.copytree(R/'frozen'/key,root/'skills'/key)
 prompt=pathlib.Path(task['prompt']).read_text()+'\n\nWork only in this repository. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
 for key in ARMS[arm]:prompt+='\n'+(R/'frozen'/key/'SKILL.md').read_text()
 (root/'prompt.txt').write_text(prompt);(root/'initial-files.json').write_text(json.dumps(files(root/'work'),sort_keys=True))
 return root
def argv(harness,port,private):
 cfg={'model_provider':'local','model':MODEL,'model_providers.local.name':'local-development','model_providers.local.base_url':f'http://provider.example:{port}/v1','model_providers.local.env_key':'MOCK_KEY','model_providers.local.wire_api':'responses','model_providers.local.requires_openai_auth':False,'model_providers.local.supports_websockets':False,'model_providers.local.request_max_retries':0,'model_providers.local.stream_max_retries':0,'web_search':'disabled',**{'features.'+k:False for k in ['multi_agent','multi_agent_v2','apps','workspace_dependencies','plugins','remote_plugin','browser_use','browser_use_external','computer_use','image_generation','unbounded_connection_retries']}}
 result=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--dangerously-bypass-approvals-and-sandbox']
 for k,v in cfg.items():result+=['-c',k+'='+json.dumps(v)]
 return result+[pathlib.Path(private,'prompt.txt').read_text()]
def shell(argv):
 binary='/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex'
 expected='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
 return ['/bin/sh','-c','mkdir -p "$CODEX_HOME" && echo "'+expected+'  '+binary+'" | sha256sum -c - >/dev/null && exec "$@"','development',*argv]
def capture(private,task):
 (private/'final-files.json').write_text(json.dumps(files(private/'work'),sort_keys=True))
 if task['family']=='swe':
  spec=importlib.util.spec_from_file_location('patcher',R/'runtime/swe_patch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  (private/'model.patch').write_text(m.snapshot_patch(pathlib.Path(task['baseline']),private/'work'))
def grade(private,task):
 grade=private/'grade';grade.mkdir(mode=0o700);name='solpi-qwendev-grade-'+uuid.uuid4().hex[:12];z=None;error=None
 if task['family']=='swe':
  runid='qwendev-'+uuid.uuid4().hex
  payload=dict(task,grader_run_id=runid)
  with (grade/'stdout').open('wb') as out,(grade/'stderr').open('wb') as err:
   process=subprocess.Popen([task['python'],str(R/'runtime/swe_grade.py'),str(private),json.dumps(payload)],stdout=out,stderr=err,start_new_session=True)
   try:process.wait(timeout=300)
   except subprocess.TimeoutExpired:
    os.killpg(process.pid,signal.SIGTERM)
    try:process.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=3)
    # The sole permitted name is known before the official worker starts.
    name='sweb.eval.pallets__flask-5014.'+runid
    subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=5)
    probe=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
    absent=probe.returncode!=0 and probe.stderr.strip() in ('Error: No such object: '+name,'Error response from daemon: No such container: '+name)
    result={'solved':None,'infrastructure_error':'official worker deadline','worker_group_terminal':process.poll() is not None,'grader_absence_verified':absent}
    (grade/'result.json').write_text(json.dumps(result));return result
  result=json.loads((grade/'result.json').read_text()) if (grade/'result.json').exists() else {'solved':None,'infrastructure_error':'official worker missing report'}
  return result
 command=['docker','create','--pull=never','--name',name,'--network','none','--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','/bin/sh']
 if task['family']=='go':command+=['-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','-e','GOPROXY=off','-e','GOSUMDB=off','-e','GOTOOLCHAIN=local','-v',str(private/'work')+':/workspace:ro','-v',str(R/'frozen/go-grader')+':/grade:ro',task['image_id'],'-c','python3 /grade/grade.py']
 else:command+=['-e','HOME=/tmp/grade-home','-v',str(private/'work')+':/app/dclm','-v',task['tests']+':/tests:ro','-v',str(grade)+':/logs/verifier','-w','/app/dclm',task['image_id'],'-c','mkdir -p "$HOME" && python -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA']
 try:
  subprocess.run(command,check=True,capture_output=True,timeout=10)
  q=json.loads(subprocess.check_output(['docker','inspect',name],timeout=5))[0];h=q['HostConfig']
  if q['Config'].get('User')!=str(os.getuid())+':'+str(os.getgid()) or h['NetworkMode']!='none' or h['Memory']!=2147483648 or h['NanoCpus']!=1000000000 or h['PidsLimit']!=128:raise RuntimeError('grader limits')
  (grade/'resource-inspect.json').write_text(json.dumps(q))
  with (grade/'stdout').open('wb') as out,(grade/'stderr').open('wb') as err:z=subprocess.run(['docker','start','-a',name],stdout=out,stderr=err,timeout=240)
 except Exception as e:error=type(e).__name__
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=5)
  q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
  if q.returncode==0 or q.stderr.strip() not in ('Error: No such object: '+name,'Error response from daemon: No such container: '+name):error='grader cleanup uncertain'
 terminal_validation=None
 if task['family']=='terminal':
  from grade_validation import validate_terminal_result
  try:terminal_validation=validate_terminal_result(grade,z.returncode if z is not None else None,task['expected_test_events'])
  except Exception as e:error=str(e)
 if task['family']=='go' and z is not None and z.returncode==2:error=error or 'grader exit2'
 result={'terminal_test_validation':terminal_validation,'solved':z.returncode==0 if z is not None and not error else None,'exit':z.returncode if z else None,'infrastructure_error':error or ('grader exit2' if task['family']=='go' and z is not None and z.returncode==2 else None),'artifacts':files(grade)}
 (grade/'result.json').write_text(json.dumps(result));return result

def reconcile_native(events,requests):
 terminal=[e.get('usage') for e in events if e.get('type')=='turn.completed']
 if len(terminal)!=1 or not isinstance(terminal[0],dict):return {'complete':False,'reason':'native_terminal_missing_or_duplicate'}
 usage=terminal[0];normalized=[r.get('usage_audit',{}) for r in requests]
 if not requests or not all(u.get('gross_usage_complete') for u in normalized):return {'complete':False,'reason':'provider_request_usage_incomplete'}
 expected={'input_tokens':sum(u['input_tokens_inclusive'] for u in normalized),'output_tokens':sum(u['output_tokens_inclusive'] for u in normalized)}
 if any(type(usage.get(k)) is not int or usage[k]!=v for k,v in expected.items()):return {'complete':False,'reason':'native_provider_mismatch','native_usage':usage,'provider_expected':expected}
 return {'complete':True,'native_usage':usage,'provider_expected':expected,'scope':'this actor forwarded Responses traffic only; cache billing and unobserved helper traffic not certified'}

def trace_metrics(events):
 """Descriptive event counts; read-like shell syntax is a heuristic, not causation."""
 import re
 completed={};missing_ids=0;duplicates=0
 for index,event in enumerate(events):
  if event.get('type')!='item.completed' or not isinstance(event.get('item'),dict):continue
  item=event['item'];key=item.get('id')
  if not key:missing_ids+=1;key=('unidentified_event',index)
  if key in completed:duplicates+=1
  completed[key]=item
 commands=[x for x in completed.values() if x.get('type')=='command_execution']
 read_pattern=re.compile(r'\b(?:cat|sed|head|tail|rg|grep|read_text|read_bytes)\b')
 readlike=[x for x in commands if read_pattern.search(str(x.get('command','')))]
 return {'completed_tool_items':sum(x.get('type') not in ('agent_message','reasoning') for x in completed.values()),'completed_command_calls':len(commands),'read_like_command_calls':len(readlike),'command_return_bytes':sum(len(str(x.get('aggregated_output','')).encode()) for x in commands),'read_like_return_bytes':sum(len(str(x.get('aggregated_output','')).encode()) for x in readlike),'nonzero_command_exits':sum(type(x.get('exit_code')) is int and x['exit_code']!=0 for x in commands),'missing_item_ids':missing_ids,'duplicate_completed_ids':duplicates,'scope':'Last completed item per native ID; missing IDs counted separately. Read-like regex includes searches and compound shell commands, not proof of independent reads; truncated logs undercount. Descriptive only, separate from solve and gross-token metrics.'}
