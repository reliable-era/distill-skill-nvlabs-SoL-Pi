import pathlib,json,hashlib,time,sys,subprocess
OUT=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,x):pathlib.Path(p).write_text(json.dumps(x,indent=2)+'\n')
def guard(p):
 assert p['maximum_HTTP_requests']==12 and p['probe_seconds']==30 and p['cleanup_seconds']==40
 assert p['maximum_fixture_starts']==p['maximum_probe_starts']==1
 assert all(p[k]==0 for k in ['maximum_pulls','maximum_builds','maximum_graders','maximum_models','maximum_retries'])
 assert p['network']=={'driver':'bridge','internal':True,'enable_ipv6':False,'service_alias':'httpbin.org','published_ports':[],'actor_membership':False}
def mount_sets(p,work):
 service={p['source_mount']:('/fixture/httpbin',False),str(OUT/'listener.sh'):('/fixture-listener.sh',False),str(work/'server.pem'):('/certs/server.pem',False),str(work/'server.key'):('/certs/server.key',False)}
 probe={str(OUT/'probe.py'):('/probe.py',False),str(work/'ca.pem'):('/certs/ca.pem',False),str(work/'output'):('/output',True)}
 return service,probe
def verify(c,caps,mounts,network):
 c.reload();a=c.attrs;h=a['HostConfig']
 assert h['Memory']==caps['memory'] and h['NanoCpus']==caps['nano_cpus'] and not h.get('PortBindings')
 assert set(a['NetworkSettings']['Networks'])=={network}
 actual=[(m['Source'],m['Destination'],m['RW']) for m in a['Mounts']]
 expected=[(source,dest,rw) for source,(dest,rw) in mounts.items()]
 assert len(actual)==len(expected) and set(actual)==set(expected)
 assert not any(any(k in e.split('=',1)[0] for k in ['BUGSNAG_API_KEY','TOKEN','SECRET','PASSWORD','API_KEY']) for e in a['Config']['Env'])
 return {'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'mounts':actual,'network':network,'published_ports':False,'sensitive_env_absent':True}
def absence(result,kind,ident):
 if result.returncode==0:return False
 text=result.stderr.decode().strip()
 expected={'container':'Error response from daemon: No such container: '+ident,'network':'Error response from daemon: network '+ident+' not found'}
 return text==expected[kind]
def remove(c,kind,ident,deadline):
 remaining=deadline-time.monotonic()
 if remaining<=0:raise RuntimeError("cleanup deadline exceeded")
 command=['docker',kind,'rm']+(['-f'] if kind=='container' else [])+[ident]
 subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=min(30,remaining))
 remaining=deadline-time.monotonic()
 if remaining<=0:raise RuntimeError("cleanup inspection deadline exceeded")
 r=subprocess.run(['docker',kind,'inspect',ident],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=min(10,remaining))
 assert absence(r,kind,ident)
 return {'id':ident,'absence_verified':True}
def worker():
 p=json.loads((OUT/'plan.json').read_text());guard(p)
 a=json.loads((OUT/'execution-authorization.json').read_text());assert a.get('authorized') is True and a['plan_sha256']==sha(OUT/'plan.json')
 for f,h in p['source_hashes'].items():assert sha(f)==h
 work=pathlib.Path(p['private_root']);work.mkdir(mode=0o700,exist_ok=True)
 assert (work/'phase-start.json').exists()
 with (work/'worker-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 import docker
 c=docker.from_env(timeout=10);owned=[];proof={};error=None
 try:
  info=c.info();assert info['ID']==p['daemon_id'] and info['DockerRootDir']==p['docker_root_dir']
  image=c.images.get(p['image']);assert image.id==p['image_id'] and p['image'] in image.attrs['RepoDigests']
  probe_image=c.images.get(p['probe_image']);assert probe_image.id==p['probe_image_id'] and p['probe_image'] in probe_image.attrs['RepoDigests']
  output=work/'output';output.mkdir(mode=0o700,exist_ok=True);assert not any(output.iterdir());service_mounts,probe_mounts=mount_sets(p,work)
  assert sha(pathlib.Path(p['source_mount'])/'core.py')==p['source_sha256']
  for f,h in p['certificate_hashes'].items():assert sha(f)==h
  assert not c.networks.list(names=['solpi-httpbin-parity-internal'])
  for name in ['solpi-httpbin-parity-service','solpi-httpbin-parity-probe']:
   try:c.containers.get(name)
   except docker.errors.NotFound:pass
   else:raise RuntimeError('owned container name exists')
  net=c.networks.create('solpi-httpbin-parity-internal',driver='bridge',internal=True,enable_ipv6=False,options={'com.docker.network.bridge.gateway_mode_ipv4':'isolated'});owned.append(('network',net.id));dump(work/'owned.json',owned);net.reload();assert net.attrs['Internal'] is True and not net.attrs['EnableIPv6'];assert net.attrs['Options'].get('com.docker.network.bridge.gateway_mode_ipv4')=='isolated';assert all(not x.get('Gateway') for x in net.attrs.get('IPAM',{}).get('Config',[]))
  service=c.containers.create(p['image'],name='solpi-httpbin-parity-service',entrypoint='sh',command=['/fixture-listener.sh'],network=net.name,mem_limit=p['fixture_caps']['memory'],nano_cpus=p['fixture_caps']['nano_cpus'],environment={'PYTHONPATH':'/fixture'},volumes={p['source_mount']:{'bind':'/fixture/httpbin','mode':'ro'},str(OUT/'listener.sh'):{'bind':'/fixture-listener.sh','mode':'ro'},str(work/'server.pem'):{'bind':'/certs/server.pem','mode':'ro'},str(work/'server.key'):{'bind':'/certs/server.key','mode':'ro'}});owned.append(('container',service.id));dump(work/'owned.json',owned)
  net.disconnect(service);net.connect(service,aliases=['httpbin.org']);proof['service']=verify(service,p['fixture_caps'],service_mounts,net.name);dump(work/'pre-listener-limits.json',proof);service.start()
  # Readiness waits inspect local process state only; no hidden HTTP requests.
  time.sleep(2);service.reload();assert service.status=='running'
  probe=c.containers.create(p['probe_image'],name='solpi-httpbin-parity-probe',entrypoint='sh',command=['-c','/opt/miniconda3/envs/testbed/bin/python /probe.py > /output/private-probe.log 2>&1'],network=net.name,mem_limit=p['probe_caps']['memory'],nano_cpus=p['probe_caps']['nano_cpus'],volumes={str(OUT/'probe.py'):{'bind':'/probe.py','mode':'ro'},str(work/'ca.pem'):{'bind':'/certs/ca.pem','mode':'ro'},str(output):{'bind':'/output','mode':'rw'}});owned.append(('container',probe.id));dump(work/'owned.json',owned);proof['probe']=verify(probe,p['probe_caps'],probe_mounts,net.name)
  net.reload();assert set(net.attrs['Containers'])=={service.id,probe.id};proof['internal_network_members_only']=True;proof['network']={'internal':net.attrs['Internal'],'IPv6':net.attrs['EnableIPv6'],'gateway_mode_ipv4':net.attrs['Options']['com.docker.network.bridge.gateway_mode_ipv4'],'Gateway':[x.get('Gateway') for x in net.attrs.get('IPAM',{}).get('Config',[])],'members':sorted(net.attrs['Containers'])};dump(work/'actual-limits.json',proof)
  probe.start();r=probe.wait(timeout=30);assert r['StatusCode']==0
  result=json.loads((output/'protocol-result.json').read_text());assert result['status']=='passed' and result['http_requests']==12 and result['TLS_verification'] is True
 except Exception as e:error=type(e).__name__
 finally:
  cleanup=[];deadline=time.monotonic()+40
  for kind,ident in reversed(owned):
   try:cleanup.append(remove(c,kind,ident,deadline))
   except Exception as e:cleanup.append({'id':ident,'absence_verified':False,'error':type(e).__name__});error=error or 'cleanup_unverified'
  dump(work/'cleanup.json',cleanup);c.close()
 dump(OUT/'result.json',{'status':'failed' if error else 'validated_protocol_parity','error_type':error,'limits':proof,'cleanup':cleanup,'models':0,'graders':0,'pulls':0,'builds':0})
 if error:raise RuntimeError('stop; no retries')
def launch():
 p=json.loads((OUT/'plan.json').read_text());guard(p)
 a=json.loads((OUT/'execution-authorization.json').read_text());assert a.get('authorized') is True and a['plan_sha256']==sha(OUT/'plan.json')
 for f,h in p['source_hashes'].items():assert sha(f)==h
 work=pathlib.Path(p['private_root']);work.mkdir(mode=0o700,exist_ok=True)
 with (work/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 try:
  with (work/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,str(OUT/'run_parity.py'),'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=90)
  if r.returncode:raise RuntimeError('worker failed')
 except Exception as e:
  cleanup=[];deadline=time.monotonic()+40
  if (work/'owned.json').exists():
   for kind,ident in reversed(json.loads((work/'owned.json').read_text())):
    # An already removed owned object is success, not a second fixture attempt.
    try:
     inspection=subprocess.run(['docker',kind,'inspect',ident],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=max(.1,min(5,deadline-time.monotonic())))
     if absence(inspection,kind,ident):cleanup.append({'id':ident,'absence_verified':True})
     else:cleanup.append(remove(None,kind,ident,deadline))
    except Exception as ce:cleanup.append({'id':ident,'absence_verified':False,'error':type(ce).__name__})
  dump(OUT/'outer-error.json',{'status':'stopped','error_type':type(e).__name__,'cleanup':cleanup,'no_retries':True});raise
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 elif '--launch' in sys.argv:launch()
 else:print('prepared only; no fixture starts')
