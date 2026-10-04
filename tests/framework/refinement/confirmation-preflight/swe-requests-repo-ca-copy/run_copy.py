import pathlib,json,hashlib,sys,subprocess,io,tarfile
OUT=pathlib.Path('/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/distill-skill-nvlabs-SoL-Pi/tests/framework/refinement/confirmation-preflight/swe-requests-repo-ca-copy')
ROOT=pathlib.Path('/tmp/solpi-requests-repo-ca-copy')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')
def worker():
 import docker
 p=json.loads((OUT/'plan.json').read_text());c=docker.from_env(timeout=2)
 try:
  i=c.images.get(p['image']);assert i.id==p['image_id'] and p['image'] in i.attrs['RepoDigests'];info=c.info();assert info['ID']==p['daemon_id']
  name='solpi-requests-repo-ca-copy'
  try:c.containers.get(name)
  except docker.errors.NotFound:pass
  else:raise RuntimeError('owned name present')
  container=c.containers.create(p['image'],name=name,entrypoint='sh',command=['-c','true'],network_mode='none',network_disabled=False,read_only=True,mem_limit=536870912,nano_cpus=1000000000)
  dump(ROOT/'container.json',{'id':container.id});container.reload();a=container.attrs;h=a['HostConfig'];proof={'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network_mode':h['NetworkMode'],'network_disabled':a['Config'].get('NetworkDisabled',False),'readonly':h['ReadonlyRootfs'],'state':a['State'],'mounts':a['Mounts']};dump(ROOT/'actual-config.json',proof)
  assert proof['memory']==536870912 and proof['nano_cpus']==1000000000 and proof['network_mode']=='none' and proof['network_disabled'] is False and proof['readonly'] is True and a['State']['Status']=='created' and not a['Mounts'] and not h.get('PortBindings')
  records=[];raw_total=0;content_total=0
  for path in p['paths']:
   stream,stat=container.get_archive(path);raw=bytearray()
   for chunk in stream:
    raw_total+=len(chunk)
    if raw_total>1048576:raise RuntimeError('archive byte cap')
    raw.extend(chunk)
   if hasattr(stream,'close'):stream.close()
   with tarfile.open(fileobj=io.BytesIO(raw),mode='r:*') as t:
    files=t.getmembers();assert len(files)==1;member=files[0];assert member.isfile() and member.name==pathlib.PurePosixPath(path).name and not member.issym() and not member.islnk()
    assert 0<member.size<=1048576-content_total;content=t.extractfile(member).read(member.size+1);assert len(content)==member.size;content_total+=len(content)
   f=ROOT/pathlib.PurePosixPath(path).name;f.write_bytes(content);f.chmod(0o600);records.append({'path':path,'sha256':sha(f),'bytes':len(content),'PEM_certificates':content.count(b'-----BEGIN CERTIFICATE-----')})
  dump(ROOT/'copy-result.json',{'records':records,'content_total_bytes':content_total,'archive_total_bytes':raw_total,'container_started':False})
 finally:c.close()
def launch():
 ROOT.mkdir(mode=0o700,exist_ok=True)
 with (ROOT/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'plan.json')},f)
 error=None;cleanup={}
 try:
  with (ROOT/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,__file__,'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=10)
  if r.returncode:error='copy_worker_failed'
 except Exception as e:error=type(e).__name__
 finally:
  if (ROOT/'container.json').exists():
   ident=json.loads((ROOT/'container.json').read_text())['id']
   try:
    subprocess.run(['docker','container','rm','-f',ident],capture_output=True,timeout=30)
    r=subprocess.run(['docker','container','inspect',ident],capture_output=True,timeout=10);cleanup={'id':ident,'absence_verified':r.returncode!=0 and r.stderr.decode().strip()=='Error response from daemon: No such container: '+ident};dump(ROOT/'cleanup.json',cleanup)
    if cleanup['absence_verified'] is not True:error=error or 'cleanup_unverified'
   except Exception as e:error=error or 'cleanup_'+type(e).__name__
  dump(OUT/'result.json',{'status':'stopped' if error else 'readonly_repository_files_copied','error_type':error,'copy':json.loads((ROOT/'copy-result.json').read_text()) if (ROOT/'copy-result.json').exists() else None,'cleanup':cleanup,'starts':0,'HTTP_requests':0,'models':0,'graders':0,'pulls':0,'builds':0})
 if error:raise RuntimeError('stop without retry')
if '--worker' in sys.argv:worker()
else:launch()
