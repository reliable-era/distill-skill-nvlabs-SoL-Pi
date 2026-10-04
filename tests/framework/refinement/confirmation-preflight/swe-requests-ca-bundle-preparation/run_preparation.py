import pathlib,json,hashlib,sys,subprocess,time,importlib.util
OUT=pathlib.Path(__file__).resolve().parent
NAME='solpi-requests-ca-metadata'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')
def setup():
 p=json.loads((OUT/'plan.json').read_text());assert p['maximum_metadata_probe_starts']==1 and p['probe_seconds']==10 and p['cleanup_seconds']==40 and p['maximum_private_extracted_bytes']==1048576
 assert all(p[k]==0 for k in ['maximum_HTTP_requests','maximum_graders','maximum_models','maximum_pulls','maximum_builds','maximum_retries'])
 a=json.loads((OUT/'execution-authorization.json').read_text());assert a.get('authorized') is True and a['plan_sha256']==sha(OUT/'plan.json')
 for f,h in {**p['source_hashes'],**p['preserved_consumed_phase']}.items():assert sha(f)==h
 return p

def metadata_gate(metadata):
 expected={'send_defaults_to_self_verify':True,'send_merges_CA_environment':False,'request_merges_CA_environment':True,'adapter_uses_default_CA':True}
 if metadata.get('facts')!=expected:raise RuntimeError('installed Requests trust facts mismatch')
 if metadata.get('requests_version')!='2.3.0' or type(metadata.get('extracted_bytes')) is not int or not 0<metadata['extracted_bytes']<=1048576:raise RuntimeError('version/byte-cap mismatch')
 records=metadata.get('records',{});bundle=records.get('default_CA',{})
 if set(records)!={'sessions','adapters','certs','default_CA'} or bundle.get('PEM_certificate_count',0)<1 or not pathlib.Path(bundle.get('path','')).is_absolute():raise RuntimeError('incomplete source/default CA metadata')
 for record in records.values():
  if not pathlib.Path(record.get('path','')).is_absolute() or len(record.get('sha256',''))!=64 or type(record.get('bytes')) is not int or record['bytes']<=0:raise RuntimeError('invalid provenance record')

def worker():
 p=setup();work=pathlib.Path(p['private_root']);assert json.loads((work/'phase-start.json').read_text())['plan_sha256']==sha(OUT/'plan.json')
 with (work/'worker-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 import docker
 c=docker.from_env(timeout=2);container=None
 try:
  info=c.info();assert info['ID']==p['daemon_id'] and info['DockerRootDir']==p['docker_root_dir'];image=c.images.get(p['image']);assert image.id==p['image_id'] and p['image'] in image.attrs['RepoDigests']
  try:c.containers.get(NAME)
  except docker.errors.NotFound:pass
  else:raise RuntimeError('owned name already present')
  output=work/'output';output.mkdir(mode=0o700);mounts={str(OUT/'probe.py'):{'bind':'/probe.py','mode':'ro'},str(output):{'bind':'/output','mode':'rw'}}
  container=c.containers.create(p['image'],name=NAME,entrypoint='sh',command=['-c',p['interpreter']+' /probe.py > /output/private-probe.log 2>&1'],network_mode='none',network_disabled=False,read_only=True,mem_limit=536870912,nano_cpus=1000000000,environment={'PYTHONDONTWRITEBYTECODE':'1'},volumes=mounts,log_config=docker.types.LogConfig(type='json-file',config={'max-size':'64k','max-file':'1'}))
  dump(work/'container.json',{'id':container.id});container.reload();a=container.attrs;h=a['HostConfig'];actual=[(m['Source'],m['Destination'],m['RW']) for m in a['Mounts']];expected=[(src,v['bind'],v['mode']=='rw') for src,v in mounts.items()]
  proof={'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network_mode':h['NetworkMode'],'network_disabled':a['Config'].get('NetworkDisabled',False),'read_only':h['ReadonlyRootfs'],'mounts':actual,'verified_before_execution':False};dump(work/'actual-config.json',proof)
  assert {k:proof[k] for k in p['caps']}==p['caps'] and len(actual)==len(expected) and set(actual)==set(expected) and not h.get('PortBindings')
  assert not any(any(x in e.split('=',1)[0] for x in ['API_KEY','TOKEN','SECRET','PASSWORD']) for e in a['Config'].get('Env',[]));proof['verified_before_execution']=True;dump(work/'actual-config.json',proof)
  container.start();status=container.wait(timeout=5);container.reload();dump(work/'state-before-cleanup.json',container.attrs['State']);dump(work/'worker-result.json',{'exit_code':status['StatusCode']});assert status['StatusCode']==0
 finally:
  if container:
   try:container.reload();dump(work/'state-before-cleanup.json',container.attrs['State'])
   except Exception as e:dump(work/'state-capture-error.json',{'error_type':type(e).__name__})
  c.close()

def launch():
 p=setup();work=pathlib.Path(p['private_root']);work.mkdir(mode=0o700,exist_ok=True)
 with (work/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 error=None;cleanup={};metadata=None
 try:
  with (work/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,str(OUT/'run_preparation.py'),'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=10)
  if r.returncode:error='worker_failed'
 except Exception as e:error=type(e).__name__
 finally:
  if (work/'container.json').exists():
   ident=json.loads((work/'container.json').read_text())['id']
   try:
    if not (work/'state-before-cleanup.json').exists():
     try:
      state=subprocess.run(['docker','container','inspect','--format','{{json .State}}',ident],capture_output=True,timeout=5,check=True);dump(work/'state-before-cleanup.json',json.loads(state.stdout))
     except Exception as e:
      dump(work/'state-capture-error.json',{'error_type':type(e).__name__});error=error or 'state_capture_unverified'
    removal=subprocess.run(['docker','container','rm','-f',ident],capture_output=True,timeout=25)
    inspection=subprocess.run(['docker','container','inspect',ident],capture_output=True,timeout=10)
    cleanup={'id':ident,'absence_verified':inspection.returncode!=0 and inspection.stderr.decode().strip()=='Error response from daemon: No such container: '+ident};dump(work/'cleanup.json',cleanup)
    if cleanup['absence_verified'] is not True:error=error or 'cleanup_unverified'
   except Exception as e:error=error or 'cleanup_'+type(e).__name__
  else:error=error or 'no_container_record'
  f=work/'output/metadata.json'
  if f.exists():
   metadata=json.loads(f.read_text())
   try:metadata_gate(metadata)
   except Exception as e:error=error or 'metadata_gate_'+type(e).__name__
  else:error=error or 'metadata_missing'
  dump(OUT/'result.json',{'status':'stopped' if error else 'cached_image_CA_provenance_verified','error_type':error,'metadata':metadata,'cleanup':cleanup,'HTTP_requests':0,'graders':0,'models':0,'pulls':0,'builds':0})
 if error:raise RuntimeError('stop without retry')
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 elif '--launch' in sys.argv:launch()
 else:print('prepared only; no probes')
