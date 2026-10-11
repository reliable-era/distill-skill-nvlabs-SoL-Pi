"""One G3 attempt, immutable input/isolated actor/receipt and exact artifact grade.
No scheduling or automatic retry here. Scheduler alone authorizes admitted start.
"""
import datetime,hashlib,json,os,pathlib,re,shutil,subprocess,threading,time,uuid
from transport import Broker,MODEL,save,metadata
H=pathlib.Path(__file__).resolve().parent
BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')
BINARY_SHA='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def tree(root):return {str(p.relative_to(root)):({'symlink':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(pathlib.Path(root).rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}
def docker(*args):return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.PIPE,timeout=30).strip()
def absent(name):
 z=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15);return z.returncode!=0 and 'No such' in z.stderr

def argv(prompt):
 cfg={'model_provider':'local','model':MODEL,'model_providers.local.name':'G3-direct9012','model_providers.local.base_url':'http://127.0.0.1:8080/v1','model_providers.local.env_key':'MOCK_KEY','model_providers.local.wire_api':'responses','model_providers.local.requires_openai_auth':False,'model_providers.local.supports_websockets':False,'model_providers.local.request_max_retries':0,'model_providers.local.stream_max_retries':0,'model_context_window':262144,'web_search':'disabled',**{'features.'+k:False for k in ('multi_agent','multi_agent_v2','apps','workspace_dependencies','plugins','remote_plugin','browser_use','browser_use_external','computer_use','image_generation','unbounded_connection_retries')}}
 result=['/opt/solpi/codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--dangerously-bypass-approvals-and-sandbox']
 for k,v in cfg.items():result+=['-c',k+'='+json.dumps(v)]
 return result+[prompt]

def prepare(cell,root,plan):
 root=pathlib.Path(root);root.mkdir(mode=0o700);(root/'skills').mkdir();task=cell['task'];baseline=pathlib.Path(plan['prepared_tasks'][task]);assert tree(baseline/'grader')==plan['grader_trees'][task];assert tree(baseline/'workspace')==plan['starter_trees'][task];assert sha(baseline/'prompt.txt')==plan['prompt_sha256'][task]
 shutil.copytree(baseline/'workspace',root/'starter');shutil.copytree(baseline/'grader',root/'grader');manifest=json.loads((baseline/'manifest.json').read_text());save(root/'manifest.json',manifest)
 prompt=(baseline/'prompt.txt').read_text()+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
 for skill in plan['arm_skills'][cell['arm']]:
  source=pathlib.Path(plan['skills'][skill]['path']);assert tree(source)==plan['skills'][skill]['tree'];shutil.copytree(source,root/'skills'/skill);prompt+='\n'+(source/'SKILL.md').read_text()
 if not plan['arm_skills'][cell['arm']]:prompt+='\nNo skill is supplied.\n'
 (root/'prompt.txt').write_text(prompt);return prompt

def attempt(cell,number,root,plan,admission,start_callback):
 """start_callback serializes slot/admission authorization immediately before start."""
 root=pathlib.Path(root);prompt=prepare(cell,root,plan);ident=cell['cell_id']+'-attempt'+str(number);name='solpi-'+ident+'-'+uuid.uuid4().hex[:8];grade=name+'-grade';row=dict(cell_id=cell['cell_id'],task=cell['task'],round=cell['round'],arm=cell['arm'],attempt=number,root=str(root),actor=name,grade_container=grade,solved=None,grade_valid=False,native_started=False,timeout=False,prompt_sha256=sha(root/'prompt.txt'),error=None);broker=None;stop=threading.Event();sampler=None;process=None;started=None
 try:
  assert sha(BINARY)==BINARY_SHA;image=plan['images'][cell['task'].split('/')[0]]
  broker=Broker(root/'transport',time.monotonic()+7200);broker.start()
  cmd=['create','--pull=never','--name',name,'--user','0','--network','none','--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(root/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-v',str(H/'relay.py')+':/opt/solpi/relay.py:ro','-v',str(root/'transport/socket')+':/broker:ro','-e','HOME=/root/solpi-home','-e','CODEX_HOME=/root/solpi-home/.codex','-e','MOCK_KEY=dummy-not-secret','-e','HTTP_PROXY=','-e','HTTPS_PROXY=','-e','ALL_PROXY=','-e','http_proxy=','-e','https_proxy=','-e','all_proxy=','-e','NO_PROXY=127.0.0.1','-e','no_proxy=127.0.0.1','-w','/app','--entrypoint','/bin/sh',image,'-c','mkdir -p "$CODEX_HOME"; python3 /opt/solpi/relay.py & relay=$!; trap "kill $relay 2>/dev/null || true" EXIT; sleep 0.2; "$@"','g3',*argv(prompt)]
  docker(*cmd);inspect=json.loads(docker('inspect',name))[0];hc=inspect['HostConfig'];assert hc['NetworkMode']=='none' and hc['NanoCpus']==1000000000 and hc['Memory']==2147483648 and inspect['Image']==image;save(root/'actor-inspect.json',inspect);docker('cp',str(root/'starter')+'/.',name+':/app')
  admission=start_callback(ident,admission);save(root/'admission.json',admission);started=time.monotonic();broker.deadline=started+7200;row.update(native_started=True,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(root/'attempt-progress.json',row)
  samples=[dict(kind='start',observation=admission)];save(root/'load-samples.json',samples)
  def sample():
   while not stop.wait(30):
    try:v=metadata('/get_load')
    except Exception as e:v={'error':type(e).__name__,'message':str(e)}
    samples.append(dict(kind='periodic',observation=v));save(root/'load-samples.json',samples)
  sampler=threading.Thread(target=sample,daemon=True);sampler.start()
  with (root/'native.jsonl').open('xb') as out:
   process=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT)
   try:process.wait(timeout=max(.1,broker.deadline-time.monotonic()-10))
   except subprocess.TimeoutExpired:row['timeout']=True
   docker('stop','-t','0',name);process.wait(timeout=15)
  row.update(native_exit=process.returncode,wall_seconds=time.monotonic()-started,native_sha256=sha(root/'native.jsonl'));stop.set();sampler.join(timeout=15);broker.close();broker=None
  work=root/'final-work';work.mkdir();docker('cp',name+':/app/.',str(work));row['final_work_hashes']=tree(work)
  cmd=['run','--rm','--name',grade,'--network','none','--cpus','1','--memory','2g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,exec,size=1g','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','--entrypoint','python3','-v',str(work)+':/workspace:ro','-v',str(root/'grader')+':/grader:ro']
  if cell['task'].startswith('javascript/'):cmd+=['-v','/tmp/solpi-g1-js-deps:/npm-install:ro']
  with (root/'verifier.log').open('xb') as out:z=subprocess.run(['docker',*cmd,image,'/grader/grade.py'],stdout=out,stderr=subprocess.STDOUT,timeout=300)
  text=(root/'verifier.log').read_text(errors='replace');count=re.search(r'Executed accepted tests:\s*(\d+)',text);row.update(verifier_exit=z.returncode,verifier_sha256=sha(root/'verifier.log'),tests=int(count.group(1)) if count else 0);row['grade_valid']=z.returncode in (0,1) and (z.returncode==1 or row['tests']>0);row['solved']=z.returncode==0 if row['grade_valid'] else None
 except Exception as e:row['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  stop.set()
  if sampler:sampler.join(timeout=15)
  cleanup=[]
  for owned in (grade,name):
   subprocess.run(['docker','rm','-f',owned],capture_output=True,timeout=30)
   if not absent(owned):cleanup.append(owned)
  if process and process.poll() is None:
   try:process.wait(timeout=15)
   except subprocess.TimeoutExpired:cleanup.append('docker-start-process')
  if broker:
   try:broker.close()
   except Exception as e:cleanup.append(str(e))
  row['cleanup_errors']=cleanup;row['owned_containers_absent']=not cleanup
  ledger=json.loads((root/'transport/ledger.json').read_text()) if (root/'transport/ledger.json').exists() else {'provider_POST':0,'records':[]};records=ledger['records'];row.update(requests=ledger['provider_POST'],recorded_receipts=len(records),tokens_lower_bound=sum(r['tokens_lower_bound'] for r in records),cost_complete=len(records)==ledger['provider_POST'] and all(r['cost_complete'] for r in records),connection_infra_failure=any(r.get('connection_infra_failure') for r in records),backend='127.0.0.1:9012')
  row['infra_retry_eligible']=not cleanup and row['requests']<60 and (row['requests']==0 or row['connection_infra_failure']) and not row['timeout'] and not any(r['provider_status'] not in (None,200) for r in records)
  if started and 'wall_seconds' not in row:row['wall_seconds']=time.monotonic()-started
  save(root/'attempt-result.json',row)
 return row
