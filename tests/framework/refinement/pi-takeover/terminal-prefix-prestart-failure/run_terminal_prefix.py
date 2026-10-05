"""Four-arm first-selected-task pilot,existing broker;not confirmation certificate."""
import contextlib,hashlib,importlib.util,json,os,pathlib,random,shutil,subprocess,sys,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage';sys.path.insert(0,str(D/'runtime'))
import session as S,server as B,wrapper as W,actor_profile as A
SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/break-filter-js-from-html');BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex');EXPECTED='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.PIPE,text=True,timeout=timeout).strip()
def idle(path):
 deadline=time.monotonic()+300
 while True:
  try:v=S.fetch_idle();path.write_text(json.dumps(v));return v
  except Exception:
   if time.monotonic()>=deadline:raise
   time.sleep(5)
def absent(name):
 p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);return p.returncode!=0 and name in p.stderr and 'No such' in p.stderr
if __name__=='__main__':
 controls=json.loads((R/'terminal-first-controls.json').read_text());assert controls['valid_baseline_gold_pair'];assert sha(BINARY)==EXPECTED
 transfer=json.loads((R/'terminal-output-transfer-control.json').read_text());assert transfer['passed'] and transfer['cleanup_done']
 cache=json.loads((R/'terminal-selected-image-cache.json').read_text());image=next(x['image']['image_id'] for x in cache['tasks'] if x['task']==SOURCE.name)
 prior=json.loads((D/'plan.json').read_text());arms=['none','K','candidate','Both'];random.Random(20261004).shuffle(arms)
 plan={'task':SOURCE.name,'selection_sha256':sha(R/'terminal-10pct-selection.json'),'controls_sha256':sha(R/'terminal-first-controls.json'),'image_id':image,'binary_sha256':EXPECTED,'candidate_sha256':sha(D/'frozen/candidate/SKILL.md'),'runtime_hashes':{p.name:sha(p) for p in (D/'runtime').glob('*.py')},'schedule':arms,'native_starts_cap':4,'provider_POST_cap':64,'per_actor_POST_cap':16,'actor_seconds':600,'completion_grace_seconds':240,'grader_seconds':600,'cpus':1,'memory_mb':2048,'retries':0,'route':'http://127.0.0.1:8000/v1','backend_policy':'unchanged uniform least_conn;record every peer;no causal claim or cross-cohort pooling','grading_policy':'Original trusted image/filter/test environment;only captured /app/out.html supplied;not actor image or modified executables','scope':'First fixed-selected task four-arm adapter/scoring pilot;not nine-task confirmation or population estimate'}
 plan.update(output_transfer_control_sha256=sha(R/'terminal-output-transfer-control.json'),orchestration_sha256=sha(pathlib.Path(__file__)),frozen_skills_manifest=W.files(D/'frozen'),task_source_manifest=W.files(SOURCE),nginx_config_sha256=sha(R/'qwen-load-balancer/nginx.conf'),prior_model_protocol_sha256=sha(D/'plan.json'))
 (R/'terminal-prefix-plan.json').write_text(json.dumps(plan,indent=2)+'\n');digest=sha(R/'terminal-prefix-plan.json');root=pathlib.Path('/tmp/solpi-terminal-prefix-'+digest);root.mkdir(mode=0o700,exist_ok=False);prefix='solpi-tbp-'+uuid.uuid4().hex[:10];owned=[];snapshots=[];net=prefix+'-net';server=None;session=None;rows=[];error=None
 try:
  with S.inference_locks(prior['shared_inference_locks']):
   for i in range(3):idle(root/('initial-idle-'+str(i)+'.json'));time.sleep(1)
   docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net)
   topology=json.loads(docker('network','inspect',net))[0];assert topology['Internal'] and not topology['EnableIPv6'] and all(not x.get('Gateway') for x in topology['IPAM']['Config'])
   sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock';session=S.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net});handler=type('PrefixHandler',(B.PostHandler,),{'session':session});server=B.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);threading.Thread(target=server.serve_forever,daemon=True).start()
   proxy=prefix+'-proxy';owned.append(proxy);docker('create','--pull=never','--name',proxy,'--network',net,'--network-alias','proxy','--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',str(D)+':/app:ro','--entrypoint','python3',S.IMAGE,'/app/runtime/stream_proxy.py');docker('start',proxy)
   for arm in arms:
    assert W.files(D/'frozen')==plan['frozen_skills_manifest'] and W.files(SOURCE)==plan['task_source_manifest'] and sha(BINARY)==EXPECTED
    assert all(sha(D/'runtime'/k)==v for k,v in plan['runtime_hashes'].items()) and sha(R/'qwen-load-balancer/nginx.conf')==plan['nginx_config_sha256']
    d=root/arm;d.mkdir();(d/'skills').mkdir();(d/'home').mkdir();(d/'home/.codex').mkdir();keys=W.ARMS[arm]
    for key in keys:shutil.copytree(D/'frozen'/key,d/'skills'/key)
    prompt=(SOURCE/'instruction.md').read_text()+'\n\nUse supplied skills in /skills. No subagents,compaction,web retrieval or external solutions. Work in /app.\n'+''.join('\n'+(D/'frozen'/k/'SKILL.md').read_text() for k in keys);(d/'prompt.txt').write_text(prompt)
    session.begin(arm,idle(d/'idle.json'));name=prefix+'-'+arm;owned.append(name);env=['HOME=/tmp/home','CODEX_HOME=/tmp/home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']
    args=['create','--pull=never','--name',name,'--network',net,'--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(d/'home')+':/tmp/home','-v',str(d/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/app','--entrypoint','/opt/solpi/codex']
    for e in env:args+=['-e',e]
    argv=A.argv('codex',8000,d);assert argv[0]=='codex';docker(*args,image,*argv[1:]);inspect=json.loads(docker('inspect',name))[0];assert set(inspect['NetworkSettings']['Networks'])=={net} and inspect['HostConfig']['Memory']==2147483648 and inspect['HostConfig']['NanoCpus']==1000000000 and len(inspect['Mounts'])==3 and not any(x['Destination'] in ['/tests','/solution','/broker'] for x in inspect['Mounts'])
    row={'arm':arm};start=time.monotonic()
    with (d/'native.jsonl').open('wb') as out:
     p=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT)
     try:p.wait(timeout=max(.1,session.deadline-time.monotonic()-10))
     except subprocess.TimeoutExpired:row['actor_deadline_interrupted']=True
     docker('stop','-t','0',name);p.wait(timeout=5)
    row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start)
    captured=d/'captured';captured.mkdir();docker('cp',name+':/app/.',str(captured),timeout=30);row['captured_app_manifest']=W.files(captured);docker('rm',name);owned.remove(name);assert absent(name)
    end=time.monotonic()+240
    while server.workers and time.monotonic()<end:time.sleep(.05)
    if server.workers:session.abort_owned_connections();time.sleep(3)
    assert not server.workers
    grade=prefix+'-grade-'+arm;owned.append(grade);logs=d/'logs';(logs/'verifier').mkdir(parents=True)
    grade_args=['create','--pull=never','--name',grade,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(SOURCE/'tests')+':/tests:ro','-v',str(logs)+':/logs']
    output=captured/'out.html'
    docker(*grade_args,'--entrypoint','/bin/bash',image,'/tests/test.sh')
    if output.is_file() and not output.is_symlink():
     row['graded_output_sha256']=sha(output);docker('cp',str(output),grade+':/app/out.html')
    with (d/'verifier.log').open('wb') as out:
     p=subprocess.run(['docker','start','-a',grade],stdout=out,stderr=subprocess.STDOUT,timeout=600)
    docker('rm',grade);owned.remove(grade);assert absent(grade)
    reward=logs/'verifier/reward.txt';ctrf=logs/'verifier/ctrf.json'
    # Read verifier artifacts through Docker-owned files without publishing content.
    row['reward']=reward.read_text().strip() if reward.exists() else None;events=json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else [];row['test_events']=len(events);row['solved']=row['reward']=='1' and bool(events) and all(x['status']=='passed' for x in events)
    requests=[x for x in session.records if x['actor']==arm];row.update(provider_POST=len(requests),provider_tokens=sum(x.get('usage_audit',{}).get('gross_tokens',0) for x in requests),cost_complete=bool(requests) and all(x.get('usage_complete') and not x.get('error') and x.get('provider_status')==200 for x in requests),backends=[x.get('provider_backend') for x in requests]);session.finish(True);rows.append(row);(R/'terminal-prefix-progress.json').write_text(json.dumps({'plan_sha256':digest,'rows':rows,'POST':session.posts,'starts':session.starts},indent=2)+'\n')
    if not events or row['reward'] not in ['0','1']:raise RuntimeError('official grading unavailable')
    if not row['cost_complete'] or any(x not in ['127.0.0.1:18001','127.0.0.1:18002'] for x in row['backends']):raise RuntimeError('accounting/routing incomplete')
 except Exception as e:error={'type':type(e).__name__,'message':str(e)[:180]}
 finally:
  for name in owned:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  if session:session.abort_owned_connections()
  if server:server.shutdown();server.server_close()
  subprocess.run(['docker','network','rm',net],capture_output=True,timeout=20)
  for image in snapshots:subprocess.run(['docker','image','rm',image],capture_output=True,timeout=20)
  out={'plan_sha256':digest,'rows':rows,'errors':[error] if error else [],'starts':session.starts if session else 0,'POST':session.posts if session else 0,'cleanup_containers_absent':all(absent(n) for n in owned),'scope':plan['scope']};(R/'terminal-prefix-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
