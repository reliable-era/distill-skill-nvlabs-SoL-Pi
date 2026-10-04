import pathlib,json,hashlib,subprocess,time,sys
OUT=pathlib.Path(__file__).resolve().parent
NAME='solpi-httpbin-listener-diagnostic'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,x):pathlib.Path(p).write_text(json.dumps(x,indent=2)+'\n')
def setup():
 p=json.loads((OUT/'plan.json').read_text());assert p['maximum_listener_starts']==1 and p['listener_seconds']==10 and p['cleanup_seconds']==40 and p['maximum_log_bytes']==65536
 assert p['caps']=={'memory':536870912,'nano_cpus':1000000000,'network_mode':'none','network_disabled':False}
 assert p['log_config']=={'type':'json-file','config':{'max-size':'64k','max-file':'1'}}
 assert all(p[k]==0 for k in ['maximum_HTTP_requests','maximum_probes','maximum_graders','maximum_models','maximum_pulls','maximum_builds','maximum_retries'])
 a=json.loads((OUT/'execution-authorization.json').read_text());assert a.get('authorized') is True and a['plan_sha256']==sha(OUT/'plan.json')
 for f,h in {**p['source_hashes'],**p['preserved_consumed_phase'],**p['certificate_hashes']}.items():assert sha(f)==h
 return p

def capture(container,work):
 record={'status':'capture_failed'};stream=None
 try:
  container.reload();state=container.attrs['State'];record={'status':'captured','container_id':container.id,'state':{k:state.get(k) for k in ['Status','Running','ExitCode','OOMKilled','Error','StartedAt','FinishedAt']}}
  stream=container.logs(stdout=True,stderr=True,stream=True,follow=False,tail=200);total=0;truncated=False
  with (work/'private-listener.log').open('wb') as f:
   for chunk in stream:
    remain=65536-total;f.write(chunk[:remain]);total+=min(len(chunk),remain)
    if len(chunk)>=remain:truncated=True;break
  record.update(log_bytes=total,log_sha256=sha(work/'private-listener.log'),truncated_or_at_cap=truncated)
 except Exception as e:record['status']='capture_failed';record['error_type']=type(e).__name__
 finally:
  if hasattr(stream,'close'):stream.close()
  dump(work/'pre-cleanup-evidence.json',record)
 return record

def cleanup(ident,work):
 deadline=time.monotonic()+35
 subprocess.run(['docker','container','rm','-f',ident],check=True,capture_output=True,timeout=25)
 r=subprocess.run(['docker','container','inspect',ident],capture_output=True,timeout=max(.1,min(10,deadline-time.monotonic())))
 absent=r.returncode!=0 and r.stderr.decode().strip()=='Error response from daemon: No such container: '+ident
 dump(work/'cleanup.json',{'id':ident,'absence_verified':absent});assert absent

def worker():
 p=setup();work=pathlib.Path(p['private_root']);assert json.loads((work/'phase-start.json').read_text())['plan_sha256']==sha(OUT/'plan.json')
 with (work/'worker-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 import docker
 c=docker.from_env(timeout=2);container=None;error=None
 try:
  info=c.info();assert info['ID']==p['daemon_id'] and info['DockerRootDir']==p['docker_root_dir'];i=c.images.get(p['image']);assert i.id==p['image_id'] and p['image'] in i.attrs['RepoDigests']
  try:c.containers.get(NAME)
  except docker.errors.NotFound:pass
  else:raise RuntimeError('owned name already exists')
  cert=pathlib.Path(p['certificate_root']);volumes={p['source_mount']:{'bind':'/fixture/httpbin','mode':'ro'},str(OUT/'listener.sh'):{'bind':'/listener.sh','mode':'ro'},str(cert/'server.pem'):{'bind':'/certs/server.pem','mode':'ro'},str(cert/'server.key'):{'bind':'/certs/server.key','mode':'ro'}}
  container=c.containers.create(p['image'],name=NAME,entrypoint='sh',command=['/listener.sh'],network_mode='none',network_disabled=False,mem_limit=536870912,nano_cpus=1000000000,environment={'PYTHONPATH':'/fixture'},volumes=volumes,log_config=docker.types.LogConfig(type='json-file',config={'max-size':'64k','max-file':'1'}));dump(work/'container.json',{'id':container.id})
  container.reload();a=container.attrs;h=a['HostConfig'];actual={(m['Source'],m['Destination'],m['RW']) for m in a['Mounts']};expected={(s,v['bind'],False) for s,v in volumes.items()}
  proof={'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network_mode':h['NetworkMode'],'network_disabled':a['Config'].get('NetworkDisabled',False),'log_config':h['LogConfig'],'mounts':sorted(actual)};dump(work/'actual-config.json',proof)
  assert proof['memory']==536870912 and proof['nano_cpus']==1000000000 and proof['network_mode']=='none' and proof['network_disabled'] is False and proof['log_config']=={'Type':'json-file','Config':{'max-size':'64k','max-file':'1'}} and actual==expected and len(a['Mounts'])==len(expected)
  assert not h.get('PortBindings');assert not any(any(k in e.split('=',1)[0] for k in ['BUGSNAG_API_KEY','TOKEN','SECRET','PASSWORD','API_KEY']) for e in a['Config']['Env'])
  dump(work/'listener-start.json',{'plan_sha256':sha(OUT/'plan.json')});container.start();time.sleep(2)
 except Exception as e:error=type(e).__name__
 finally:
  if container:capture(container,work)
  c.close()
 dump(work/'worker-result.json',{'error_type':error})
 if error:raise RuntimeError('diagnostic stopped')

def launch():
 p=setup();work=pathlib.Path(p['private_root']);work.mkdir(mode=0o700,exist_ok=True)
 with (work/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 error=None;evidence={};clean={}
 try:
  with (work/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,str(OUT/'run_diagnostic.py'),'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=10)
  if r.returncode:error='worker_failed'
 except Exception as e:error=type(e).__name__
 finally:
  if (work/'container.json').exists():
   ident=json.loads((work/'container.json').read_text())['id']
   # Capture even after worker timeout, always before removal. Five seconds of
   # the aggregate forty-second cleanup envelope are reserved for capture.
   try:
    if not (work/'pre-cleanup-evidence.json').exists() or json.loads((work/'pre-cleanup-evidence.json').read_text()).get('status')!='captured':
     with (work/'private-capture.log').open('wb') as f:subprocess.run([sys.executable,str(OUT/'run_diagnostic.py'),'--capture'],stdout=f,stderr=subprocess.STDOUT,timeout=5,check=True)
   except Exception as e:error=error or 'capture_'+type(e).__name__
   try:cleanup(ident,work)
   except Exception as e:error=error or 'cleanup_'+type(e).__name__
  if (work/'pre-cleanup-evidence.json').exists():evidence=json.loads((work/'pre-cleanup-evidence.json').read_text())
  if (work/'cleanup.json').exists():clean=json.loads((work/'cleanup.json').read_text())
  if evidence.get('status')!='captured' or clean.get('absence_verified') is not True:error=error or 'evidence_or_cleanup_unverified'
  dump(OUT/'result.json',{'status':'diagnostic_evidence_retained' if not error else 'stopped','error_type':error,'evidence':evidence,'cleanup':clean,'HTTP_requests':0,'models':0,'graders':0,'probe_starts':0})
 if error:raise RuntimeError('stop; no retry')
if __name__=='__main__':
 if '--capture' in sys.argv:
  p=setup();work=pathlib.Path(p['private_root']);import docker
  c=docker.from_env(timeout=2)
  try:capture(c.containers.get(json.loads((work/'container.json').read_text())['id']),work)
  finally:c.close()
 elif '--worker' in sys.argv:worker()
 elif '--launch' in sys.argv:launch()
 else:print('prepared only')
