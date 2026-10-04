#!/usr/bin/env python3
"""Root-gated official controls; no model agents, retries, builds or public gold logs."""
import argparse,hashlib,json,os,shutil,signal,subprocess,tempfile,time,tomllib,uuid
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
SOURCE=Path('/tmp/solpi-refinement-terminal-bench-2')
HARBOR=Path('/tmp/solpi-refinement-harbor-venv/bin/harbor')
STOP=False

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def tree_manifest(root):
 root=Path(root);rows=[]
 for f in sorted(root.rglob('*')):
  rel=str(f.relative_to(root))
  if f.is_symlink():rows.append([rel,'symlink',os.readlink(f)])
  elif f.is_file():rows.append([rel,'file',sha(f)])
  elif f.is_dir():rows.append([rel,'directory'])
 return {'sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),'entries':len(rows)}

def probe_failed(result,forbidden_dirs=False,gold_hash=False):
 return bool(result['exit_code']!=0 or result['stop_reason'] or forbidden_dirs or gold_hash)

def cap_check(plan,starts,pulls,builds):
 assert plan['maximum_official_controls']==8 and plan['maximum_model_calls']==0 and plan['automatic_retries']==0
 assert plan['time_caps']['image_pull_attempts']==4 and plan['time_caps']['per_pull_seconds']==300 and plan['time_caps']['maximum_builds']==0
 assert starts<=8 and pulls<=4 and builds==0
 assert plan['time_caps']['oracle_agent_seconds']==600 and plan['time_caps']['verifier_seconds']==600 and plan['time_caps']['baseline_control_outer_seconds']==900 and plan['time_caps']['oracle_control_outer_seconds']==1500 and plan['time_caps']['global_wall_seconds']==12000
 assert plan['disk_caps']['maximum_incremental_usage_bytes']==32*1024**3 and plan['disk_caps']['minimum_free_before_start_bytes']==40*1024**3
 assert plan['resource_limits']['cpus']==1 and plan['resource_limits']['memory_mb']==2048
 assert len(plan['controls'])==8 and all(c['attempts']==1 and c['agent'] in ('nop','oracle') for c in plan['controls'])
 assert [(c['task'],c['agent']) for c in plan['controls']]==[(t,a) for t in plan['task_order'] for a in ('nop','oracle')]

def verify():
 p=json.loads((OUT/'plan.json').read_text());cap_check(p,0,0,0)
 assert sha(ROOT/p['selection_path'])==p['selection_sha256']
 assert sha(Path(__file__))==p['runner_sha256'] and sha(OUT/'test_controls.py')==p['guard_tests_sha256']
 for rel,h in p['metadata_files_sha256'].items():assert sha(OUT/rel)==h,rel
 for rel,h in p['harbor_source_sha256'].items():assert sha(rel)==h,rel
 assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True,timeout=15).strip()==p['source_revision']
 for r in json.loads((OUT/'offline-inspection.json').read_text())['records']:
  for rel,h in r['private_content_file_hashes'].items():assert sha(SOURCE/r['task']/rel)==h
 assert not any(r['llm_or_provider_dependency_found'] for r in json.loads((OUT/'oracle-dependency-audit.json').read_text())['records'])
 assert subprocess.check_output(['docker','image','inspect',p['existing_agent_runtime_image_id'],'--format','{{.Id}}'],text=True,timeout=15).strip()==p['existing_agent_runtime_image_id']
 return p

def check_authorization(p):
 file=OUT/'execution-authorization.json'
 if not file.exists():raise RuntimeError('Root authorization missing: no pulls or controls')
 a=json.loads(file.read_text())
 if not (a.get('authorized') is True and a.get('plan_sha256')==sha(OUT/'plan.json') and a.get('max_official_controls')==8 and a.get('max_pulls')==4 and a.get('max_builds')==0 and a.get('max_model_calls')==0):raise RuntimeError('Root authorization mismatch')
 if (OUT/'launch.json').exists():raise RuntimeError('Already launched: no resume/retry')
 return file

def filesystem_samples(private,docker_root):
 rows={}
 for p in (private,docker_root):
  info=p.stat();rows[info.st_dev]={'path':str(p),'free':shutil.disk_usage(p).free}
 return rows

def disk_ok(before,after,max_growth,min_free):
 growth=sum(max(0,before[k]['free']-after[k]['free']) for k in before)
 return growth<=max_growth and all(v['free']>=min_free for v in after.values()),growth

def owned_containers(label):
 r=subprocess.run(['docker','ps','-aq','--filter','label=solpi.terminal.preflight='+label],capture_output=True,text=True,timeout=15,check=True)
 return r.stdout.split()

def cleanup(label):
 try:
  ids=owned_containers(label)
  if ids:
   r=subprocess.run(['docker','rm','-f',*ids],capture_output=True,timeout=15)
   if r.returncode!=0:return False
  return not owned_containers(label)
 except (subprocess.TimeoutExpired,subprocess.CalledProcessError):return False

def runtime_container_checks(label,seen,private):
 for cid in owned_containers(label):
  if cid in seen:continue
  result=subprocess.run(['docker','inspect',cid],capture_output=True,text=True,timeout=10)
  if result.returncode!=0:continue # --rm container may have exited between list/inspect
  row=json.loads(result.stdout)[0];cfg=row['HostConfig']
  cpu_ok=cfg.get('NanoCpus')==1000000000 or (cfg.get('CpuPeriod',0)>0 and cfg.get('CpuQuota',0)>0 and cfg['CpuQuota']==cfg['CpuPeriod'])
  if not cpu_ok or cfg.get('Memory')!=2147483648:raise RuntimeError('Docker CPU/memory enforcement mismatch')
  for mount in row.get('Mounts',[]):
   if mount['Type']=='bind' and not Path(mount['Source']).resolve().is_relative_to(private):raise RuntimeError('Unexpected external bind mount: controls cannot mount credentials')
  for entry in row['Config'].get('Env',[]):
   key,_,value=entry.partition('=')
   if value and key in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','CODEX_API_KEY','CODEX_ACCESS_TOKEN','GEMINI_API_KEY']:raise RuntimeError('Credential environment present')
  proof=OUT/'resource-inspections.json';observations=json.loads(proof.read_text()) if proof.exists() else []
  observations.append({'container_id':cid,'nano_cpus':cfg.get('NanoCpus'),'cpu_quota':cfg.get('CpuQuota'),'cpu_period':cfg.get('CpuPeriod'),'memory_limit_bytes':cfg.get('Memory'),'external_bind_mounts_rejected':True,'model_secret_env_rejected':True});write(proof,observations)
  seen.add(cid)

def kill_process(process):
 if process.poll() is not None:return
 os.killpg(process.pid,signal.SIGTERM)
 try:process.wait(timeout=5)
 except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)

def guarded_process(cmd,log,seconds,context,monitor_containers=False):
 global STOP
 start=time.monotonic();reason=None;seen=set();env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':str(context['private']/'home'),'LANG':'C.UTF-8','PYTHONNOUSERSITE':'1'}
 with log.open('wb') as stream:
  os.chmod(log,0o600)
  process=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=env)
  try:
   while process.poll() is None:
    if STOP:reason='external_stop';break
    if time.monotonic()-start>=seconds or time.monotonic()-context['start']>=context['plan']['time_caps']['global_wall_seconds']:reason='time_cap';break
    ok,growth=disk_ok(context['disk_before'],filesystem_samples(context['private'],context['docker_root']),context['plan']['disk_caps']['maximum_incremental_usage_bytes'],context['plan']['disk_caps']['minimum_free_before_start_bytes'])
    if not ok:reason='disk_cap_or_free_space';break
    if monitor_containers:runtime_container_checks(context['label'],seen,context['private'])
    time.sleep(1)
  except Exception:
   kill_process(process);cleanup(context['label']);raise
  if reason:kill_process(process)
  code=process.wait(timeout=10)
 return {'exit_code':code,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'resource_checked_containers':len(seen),'private_log_sha256':sha(log)}

def bind_private_task(task,image,private):
 source=SOURCE/task;copy=private/'tasks'/task;shutil.copytree(source,copy)
 text=(copy/'task.toml').read_text();original=tomllib.loads(text)['environment']['docker_image'];assert text.count('"'+original+'"')==1
 (copy/'task.toml').write_text(text.replace('"'+original+'"','"'+image+'"'))
 for area in ('tests','solution','environment'):
  for f in (source/area).rglob('*'):
   if f.is_file():assert sha(f)==sha(copy/f.relative_to(source))
 return copy

def cli_probe(image,cli,context,task):
 name='solpi-terminal-cli-'+context['label']+'-'+task
 cmd=['docker','run','--rm','--name',name,'--label','solpi.terminal.preflight='+context['label'],'--network','none','--cpus','1','--memory','2g','--read-only','--tmpfs','/tmp:rw,exec,size=64m','-e','HOME=/tmp','--mount',f'type=bind,src={cli},dst=/cli,readonly','--entrypoint','/bin/bash',image,'-c','set -e; /cli/node /cli/codex/bin/codex.js --version; /cli/node /cli/pi/dist/cli.js --version']
 return guarded_process(cmd,context['private']/(task+'-cli.raw'),60,context,True)

def execute():
 global STOP
 p=verify();authorization=check_authorization(p)
 label=uuid.uuid4().hex[:12];private=Path('/tmp/solpi-terminal-confirmation-controls-'+label);private.mkdir(mode=0o700);(private/'home').mkdir(mode=0o700)
 info=json.loads(subprocess.check_output(['docker','info','--format','{{json .}}'],timeout=15));docker_root=Path(info['DockerRootDir']);before=filesystem_samples(private,docker_root)
 assert all(v['free']>=p['disk_caps']['minimum_free_before_start_bytes'] for v in before.values())
 context={'private':private,'docker_root':docker_root,'disk_before':before,'plan':p,'label':label,'start':time.monotonic()}
 with (OUT/'launch.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json'),'authorization_sha256':sha(authorization),'private_artifacts':str(private),'label':label,'model_calls':0},f)
 signal.signal(signal.SIGTERM,lambda *_:globals().__setitem__('STOP',True));signal.signal(signal.SIGINT,lambda *_:globals().__setitem__('STOP',True))
 starts=pulls=0;rows=[];images={};stop=None;pull_rows=[]
 try:
  resolved=json.loads((OUT/'resolved-images.json').read_text())['records']
  for r in resolved:
   cap_check(p,starts,pulls+1,0);pulls+=1
   write(OUT/'pull-start-ledger.json',{'pulls':pulls,'maximum':4,'current_task':r['task'],'controls_started':starts,'builds':0})
   result=guarded_process(['docker','pull',r['immutable_reference']],private/(r['task']+'-pull.raw'),300,context)
   pull_rows.append({'task':r['task'],'immutable_reference':r['immutable_reference'],**result});write(OUT/'pull-results.json',pull_rows)
   if result['exit_code']!=0 or result['stop_reason']:stop='image_pull_failed_or_capped';break
   i=json.loads(subprocess.check_output(['docker','image','inspect',r['immutable_reference']],timeout=15))[0]
   if i['Id']!=r['config_digest'] or i.get('Architecture')!='amd64' or i.get('Os')!='linux':stop='image_digest_or_platform_mismatch';break
   if i['Size']>p['disk_caps']['maximum_single_image_size_bytes']:stop='image_size_cap';break
   images[r['task']]={'immutable_reference':r['immutable_reference'],'image_id':i['Id'],'size_bytes':i['Size']}
  write(OUT/'pulled-image-bindings.json',images)
  if not stop:
   # Extract public CLI packages from the pinned already-local source image only.
   cli=private/'cli';cli.mkdir();name='solpi-terminal-cli-source-'+label
   subprocess.run(['docker','create','--name',name,'--label','solpi.terminal.preflight='+label,'--cpus','1','--memory','2g',p['existing_agent_runtime_image_id']],capture_output=True,check=True,timeout=15)
   for source,dest in [('/usr/local/bin/node',cli/'node'),('/usr/local/lib/node_modules/@openai/codex',cli/'codex'),('/usr/local/lib/node_modules/@earendil-works/pi-coding-agent',cli/'pi')]:subprocess.run(['docker','cp',name+':'+source,str(dest)],capture_output=True,check=True,timeout=60)
   assert sha(cli/'node')==p['existing_agent_runtime_file_sha256']['/usr/local/bin/node']
   assert sha(cli/'codex/bin/codex.js')==p['existing_agent_runtime_file_sha256']['/usr/local/lib/node_modules/@openai/codex/bin/codex.js']
   assert sha(cli/'pi/dist/cli.js')==p['existing_agent_runtime_file_sha256']['/usr/local/lib/node_modules/@earendil-works/pi-coding-agent/dist/cli.js']
   for package,expected in p['existing_agent_runtime_package_trees'].items():assert tree_manifest(cli/package)==expected,'copied runtime package tree mismatch: '+package
   if not cleanup(label):raise RuntimeError('CLI source container cleanup not verified')
   native=[];isolation=[]
   for task in p['task_order']:
    isolation_log=private/(task+'-isolation.raw')
    isolation_command=['docker','run','--rm','--label','solpi.terminal.preflight='+label,'--network','none','--cpus','1','--memory','2g','--read-only','--entrypoint','/bin/sh',images[task]['image_id'],'-c',r'for p in /tests /solution; do if [ -e "$p" ]; then echo "$p"; fi; done; find / -xdev -type f \( -name test_outputs.py -o -name solve.sh \) -exec sha256sum {} \; 2>/dev/null']
    isolation_result=guarded_process(isolation_command,isolation_log,60,context,True)
    text=isolation_log.read_text(errors='replace');expected=json.loads((OUT/'offline-inspection.json').read_text())['records'];record=[r for r in expected if r['task']==task][0]
    gold_hashes=[h for rel,h in record['private_content_file_hashes'].items() if rel.startswith(('tests/','solution/'))]
    isolation.append({'task':task,**isolation_result,'forbidden_task_dirs_present':any(line in ['/tests','/solution'] for line in text.splitlines()),'official_test_or_solution_hash_present':any(h in text for h in gold_hashes),'gold_contents_published':False})
    if probe_failed(isolation_result,isolation[-1]['forbidden_task_dirs_present'],isolation[-1]['official_test_or_solution_hash_present']):stop='isolation_probe_failed_or_gold_present';break
    probe=cli_probe(images[task]['image_id'],cli,context,task);native.append({'task':task,**probe})
    if probe_failed(probe):stop='native_probe_failed_or_capped';break
   write(OUT/'actor-image-isolation.json',{'records':isolation,'models':0,'scope':'Fresh official images only, directory presence and official source file hashes, no gold contents emitted; failed isolation blocks future actors'})
   write(OUT/'native-compatibility.json',{'probes':native,'models':0,'auth_mounts':False,'scope':'Readonly existing CLI library mounts in exact official images, version only; any failed probe blocks future actors but does not rewrite official controls'})
   if not cleanup(label):raise RuntimeError('Native probe cleanup not verified')
   for c in p['controls']:
    if stop or STOP:stop=stop or 'external_stop';break
    cap_check(p,starts+1,pulls,0)
    image=images[c['task']];assert subprocess.check_output(['docker','image','inspect',image['immutable_reference'],'--format','{{.Id}}'],text=True,timeout=15).strip()==image['image_id']
    taskcopy=private/'tasks'/c['task']
    if not taskcopy.exists():taskcopy=bind_private_task(c['task'],image['immutable_reference'],private)
    conf=tomllib.loads((taskcopy/'task.toml').read_text());agent=c['agent'];job='terminal-preflight-'+label+'-'+c['task']+'-'+agent
    compose=private/'resource-override.json';write(compose,{'services':{'main':{'cpus':1.0,'mem_limit':2147483648,'pull_policy':'never','labels':{'solpi.terminal.preflight':label}}}})
    jobs=private/'jobs';outer=900 if agent=='nop' else 1500
    cmd=[str(HARBOR),'run','-p',str(taskcopy),'-a',agent,'--job-name',job,'-o',str(jobs),'--n-attempts','1','--n-concurrent','1','--max-retries','0','--quiet','--no-force-build','--delete','--cpus','limit','--memory','limit','--override-cpus','1','--override-memory-mb','2048','--extra-docker-compose',str(compose),'--agent-timeout-multiplier',str(600/conf['agent']['timeout_sec']),'--verifier-timeout-multiplier',str(600/conf['verifier']['timeout_sec'])]
    starts+=1;write(OUT/'control-start-ledger.json',{'starts':starts,'pulls':pulls,'builds':0,'current':c,'models':0})
    result=guarded_process(cmd,private/(job+'.raw'),outer,context,True)
    clean=cleanup(label);reward=None;trial_hashes=[];exception_types=[]
    for trial in (jobs/job).glob('*/result.json'):
     data=json.loads(trial.read_text());trial_hashes.append(sha(trial));exception=data.get('exception_info')
     if exception:exception_types.append(exception.get('exception_type','TBD'))
     rewards=(data.get('verifier_result') or {}).get('rewards') or {}
     if 'reward' in rewards:reward=rewards['reward']
    binding_ok=subprocess.check_output(['docker','image','inspect',image['immutable_reference'],'--format','{{.Id}}'],text=True,timeout=15).strip()==image['image_id']
    row={**c,**result,'image_binding_verified_after_control':binding_ok,'official_reward':reward,'private_trial_result_sha256':trial_hashes,'exception_types':exception_types,'cleanup_verified':clean,'image_id':image['image_id'],'model_calls':0,'test_oracle_contents_published':False}
    rows.append(row);write(OUT/'control-results.json',rows);print(json.dumps(row),flush=True)
    if not clean:stop='cleanup_unverified';break
    if not binding_ok:stop='image_binding_changed';break
    if result['stop_reason'] or result['exit_code']!=0 or exception_types or reward!=c['expected_official_reward']:stop='unexpected_official_control_or_infrastructure';break
    if not result['resource_checked_containers']:stop='resource_limits_not_observed';break
 except Exception as e:stop='runner_exception_'+type(e).__name__
 finally:
  clean=cleanup(label)
  for f in private.rglob('*'):
   if f.is_file():os.chmod(f,0o600)
  write(OUT/'completion.json',{'official_controls_started':starts,'unused_controls':8-starts,'pull_attempts':pulls,'builds':0,'model_calls':0,'stop_reason':stop,'cleanup_verified':clean,'elapsed_seconds':time.monotonic()-context['start'],'source_files_unchanged':all(sha(SOURCE/r['task']/rel)==h for r in json.loads((OUT/'offline-inspection.json').read_text())['records'] for rel,h in r['private_content_file_hashes'].items()),'disk_guard':'Measured32GiB growth +min40GiB free; no hard10GiB container quota claim','private_artifacts':str(private)})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['verify','execute']);args=a.parse_args()
 if args.action=='verify':verify();print('Pinned sources and zero-model controls verified; no pulls/controls')
 else:execute()
