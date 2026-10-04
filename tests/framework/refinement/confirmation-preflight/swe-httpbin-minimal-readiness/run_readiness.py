import pathlib,json,hashlib,subprocess,sys,time,shlex,importlib.util,shutil
OUT=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(p,x):pathlib.Path(p).write_text(json.dumps(x,indent=2)+'\n')
def budget_guard(p):
 assert p['maximum_pulls']==1 and p['pull_seconds']==300 and p['metadata_gate_cap']==1 and p['metadata_gate_seconds']==15 and p['cleanup_seconds']==40
 assert all(p[k]==0 for k in ['maximum_Docker_builds','maximum_fixtures','maximum_graders','maximum_models','maximum_retries'])
 assert p['caps']=={'memory':536870912,'nano_cpus':1000000000,'network_mode':'none','network_disabled':False}
def result_gate(record,p):
 if record.get('worker-result',{}).get('exit_code')!=0 or record.get('caps')!=p['caps'] or record.get('cleanup',{}).get('absence_verified') is not True:raise RuntimeError('exit/caps/cleanup gate failed')
 proof=record.get('mount-environment',{})
 if not all(proof.get(k) is True for k in ['readonly_source_verified','pythonpath_verified','sensitive_env_keys_absent','verified_before_execution']):raise RuntimeError('mount/environment gate failed')
 rows=record.get('metadata',[]);app=next((x for x in rows if x.get('stage')=='app'),None)
 if not app or not app.get('python','').startswith('3.6.') or app.get('gunicorn')!='19.9.0' or app.get('app_source')!='/fixture/httpbin/core.py' or app.get('core_sha256')!=p['core_source_sha256'] or app.get('ssl_settings_present') is not True:raise RuntimeError('missing/invalid authentic import metadata')
def setup():
 p=load(OUT/'plan.json');budget_guard(p);a=load(OUT/'execution-authorization.json');assert a.get('authorized') is True and a['plan_sha256']==sha(OUT/'plan.json');assert sha(__file__)==p['runner_sha256']
 for f,h in p['source_hashes'].items():assert sha(f)==h
 assert sha(p['helper_source'])==p['helper_sha256'];s=importlib.util.spec_from_file_location('guards',p['helper_source']);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return p,m
def worker():
 p,m=setup();work=pathlib.Path(p['artifact_root']);assert (work/'phase-start.json').exists()
 with (work/'metadata-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 import docker
 c=docker.from_env(timeout=10);container=None
 try:
  image=c.images.get(p['image']);assert p['image'] in image.attrs.get('RepoDigests',[])
  command=['-c',shlex.join(p['metadata_entrypoint'])+' > /output/private-metadata.log 2>&1']
  try:c.containers.get('solpi-httpbin-metadata-1')
  except docker.errors.NotFound:pass
  else:raise RuntimeError('owned container name already present')
  container=c.containers.create(image=p['image'],name='solpi-httpbin-metadata-1',entrypoint='sh',command=command,network_mode='none',network_disabled=False,mem_limit=536870912,nano_cpus=1000000000,environment={'PYTHONPATH':'/fixture'},volumes={p['source_mount']:{'bind':'/fixture/httpbin','mode':'ro'},str(work):{'bind':'/output','mode':'rw'}})
  dump(work/'container.json',{'container_id':container.id});container.reload();h=container.attrs['HostConfig'];conf=container.attrs['Config'];caps={'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network_mode':h['NetworkMode'],'network_disabled':conf.get('NetworkDisabled',False)};dump(work/'caps.json',caps);assert caps==p['caps'];assert not any(any(marker in x.split('=',1)[0] for marker in ['BUGSNAG_API_KEY','TOKEN','SECRET','PASSWORD','API_KEY']) for x in conf['Env']);assert 'PYTHONPATH=/fixture' in conf['Env'];assert any(x['Destination']=='/fixture/httpbin' and x['RW'] is False for x in container.attrs['Mounts'])
  dump(work/'mount-environment.json',{'readonly_source_verified':True,'pythonpath_verified':True,'sensitive_env_keys_absent':True,'verified_before_execution':True})
  container.start();r=container.wait(timeout=10);dump(work/'worker-result.json',{'exit_code':r['StatusCode']})
 finally:
  if container:m.verified_cleanup(container.id,work/'cleanup.json')
  c.close()
def launch():
 p,m=setup();work=pathlib.Path(p['artifact_root']);work.mkdir(mode=0o700,exist_ok=True)
 with (work/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 import docker
 c=docker.from_env(timeout=10);info=c.info();c.close();assert info['ID']==p['daemon_id'] and info['DockerRootDir']==p['docker_root_dir'];assert subprocess.check_output(['docker','info','--format','{{.ID}}'],timeout=20,text=True).strip()==p['daemon_id']
 def free():
  assert all(shutil.disk_usage(x).free>=p['min_free_disk_bytes'] for x in [p['docker_root_dir'],str(work)])
 free();initial=m.image_bytes()
 dump(work/'pull-start.json',{'attempt':1,'image':p['image'],'plan_sha256':sha(OUT/'plan.json')})
 with (work/'private-pull.log').open('wb') as f:r=subprocess.run(['docker','pull','--platform','linux/amd64',p['image']],stdout=f,stderr=subprocess.STDOUT,timeout=300)
 dump(OUT/'pull-result.json',{'exit_code':r.returncode,'private_log_sha256':sha(work/'private-pull.log')});assert r.returncode==0;free();assert m.image_bytes()-initial<=p['max_logical_expanded_growth_bytes']
 error=None;start=time.monotonic()
 try:
  with (work/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,str(OUT/'run_readiness.py'),'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=15)
  if r.returncode:raise RuntimeError('metadata worker failed')
 except Exception as e:
  error=type(e).__name__
  if (work/'container.json').exists():m.verified_cleanup(load(work/'container.json')['container_id'],work/'cleanup.json')
 record={'status':'failed' if error else 'process_finished','error_type':error,'elapsed_seconds':time.monotonic()-start,'models':0,'fixtures':0,'graders':0,'builds':0,'retries':0}
 for name in ['caps','cleanup','worker-result','mount-environment']:
  if (work/(name+'.json')).exists():record[name]=load(work/(name+'.json'))
 log=work/'private-metadata.log';record['metadata_log_sha256']=sha(log) if log.exists() else None
 record['metadata']=[json.loads(line) for line in log.read_text().splitlines() if line.startswith('{')] if log.exists() else []
 if not error:
  try:result_gate(record,p);record['status']='validated_import_readiness'
  except Exception as e:record['status']='failed';record['gate_error_type']=type(e).__name__
 dump(OUT/'result.json',record)
 if record['status']!='validated_import_readiness':raise RuntimeError('readiness failed; no retry')
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 elif '--launch' in sys.argv:
  try:launch()
  except Exception as e:
   dump(OUT/'execution-error.json',{'status':'stopped','error_type':type(e).__name__,'models':0,'fixtures':0,'graders':0,'builds':0,'retries':0,'partial_logs_retained':True});raise
 else:print('prepared only')
