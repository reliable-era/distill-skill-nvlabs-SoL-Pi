"""Private fixture preparation and independent verifier adapters; no implicit launches."""
import signal
import pathlib,json,subprocess,hashlib,shutil,os,uuid,importlib.util
R=pathlib.Path('/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/distill-skill-nvlabs-SoL-Pi/tests/framework/refinement/development/local-qwen-independent-reads')
FR=pathlib.Path('/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/distill-skill-nvlabs-SoL-Pi/tests/framework/refinement/development/local-qwen-independent-reads/frozen')
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
 agent=root/'home'/'.pi'/'agent';agent.mkdir(parents=True)
 (agent/'models.json').write_text(json.dumps({'providers':{'local-development':{'baseUrl':f'http://provider.example:{port}/v1','api':'openai-completions','apiKey':'dummy-not-a-real-secret','models':[{'id':MODEL,'reasoning':False,'input':['text'],'contextWindow':262144,'maxTokens':8192}]}}}))
 (agent/'settings.json').write_text(json.dumps({'compaction':{'enabled':False},'retry':{'enabled':False,'maxRetries':0,'provider':{'maxRetries':0,'timeoutMs':180000}},'cacheWarming':{'enabled':False}}));(root/'skills').mkdir()
 for key in ARMS[arm]:shutil.copytree(FR/key,root/'skills'/key)
 prompt=pathlib.Path(task['prompt']).read_text()+'\n\nWork only in this repository. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
 for key in ARMS[arm]:prompt+='\n'+(FR/key/'SKILL.md').read_text()
 (root/'prompt.txt').write_text(prompt);(root/'initial-files.json').write_text(json.dumps(files(root/'work'),sort_keys=True))
 return root
def argv(harness,port,private):
 if harness!='pi':raise ValueError('Pi-onlyscreen')
 return ['/opt/eval-node','--use-env-proxy','/opt/eval-pi/dist/bundle/cli.js','--mode','json','--provider','local-development','--model',MODEL,'--thinking','off','--no-session','--no-extensions','--no-skills','--no-prompt-templates','--no-themes','--tools','read,bash,edit,write',pathlib.Path(private,'prompt.txt').read_text()]
def shell(argv):
 expected='e0e46d3a1c0667117303412647cafcbcefb1be7612493015ec8fd6b7440162a4'
 return ['/bin/sh','-c','mkdir -p "$HOME/.pi/agent" && echo "'+expected+'  /opt/eval-node" | sha256sum -c - >/dev/null && exec "$@"','Pi-development',*argv]
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
 # Deduplicate by native assistantmessage id where present; otherwise exact event hash.
 messages={};duplicates=0
 for event in events:
  if event.get('type')!='message_end' or event.get('message',{}).get('role')!='assistant':continue
  message=event['message'];key=message.get('id') or hashlib.sha256(json.dumps(message,sort_keys=True).encode()).hexdigest()
  if key in messages:duplicates+=1
  messages[key]=message
 normalized=[r.get('usage_audit',{}) for r in requests]
 if not requests or not all(u.get('gross_usage_complete') for u in normalized) or len(messages)!=len(requests) or not any(e.get('type')=='agent_end' for e in events):return {'complete':False,'reason':'provider/native_terminal_missing','duplicates':duplicates}
 totals=[m.get('usage',{}).get('totalTokens') for m in messages.values()]
 if any(type(t) is not int or t<=0 for t in totals) or any(m.get('stopReason') in ['error','aborted'] for m in messages.values()):return {'complete':False,'reason':'native_usage_or_stop_invalid'}
 gross=sum(u['gross_tokens'] for u in normalized)
 if sum(totals)!=gross:return {'complete':False,'reason':'native_provider_mismatch'}
 return {'complete':True,'gross_tokens':gross,'duplicates':duplicates,'cache_components_complete':False,'actual_dollars':None,'scope':'thisactor forwarded chattraffic andobservednativeevents only; no universalhelpercertification'}
def trace_metrics(events):
 calls={};ends={};duplicates=0
 for event in events:
  key=event.get('toolCallId')
  if event.get('type')=='tool_execution_start' and key:calls[key]=event
  if event.get('type')=='tool_execution_end' and key:
   if key in ends:duplicates+=1
   ends[key]=event
 names={k:e.get('toolName') for k,e in calls.items()}
 sizes={k:sum(len(str(c.get('text','')).encode()) for c in e.get('result',{}).get('content',[]) if c.get('type')=='text') for k,e in ends.items()}
 return {'tool_calls':len(calls),'completed_calls':len(ends),'read_calls':sum(n=='read' for n in names.values()),'read_output_bytes':sum(sizes.get(k,0) for k,n in names.items() if n=='read'),'tool_output_bytes':sum(sizes.values()),'duplicate_tool_ends':duplicates,'scope':'deduplicated pinnedPi tool IDs; outputs contain onlyobservednative result text, not sourcefile reconstruction'}
