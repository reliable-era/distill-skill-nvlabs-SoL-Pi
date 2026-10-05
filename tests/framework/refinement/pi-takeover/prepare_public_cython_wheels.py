"""Build/cache public dependencies only in original Python ABI;never target pyknotid."""
import datetime,hashlib,json,pathlib,subprocess,urllib.request,uuid
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-public-cython-wheels-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);wheels=root/'wheels';wheels.mkdir(mode=0o755);name=root.name+'-prepare';image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']=='build-cython-ext');lock=R/'environment-inputs/cython-trusted-dependencies.txt';report={'task':'build-cython-ext','image_id':image,'private_root':str(root),'lock_sha256':sha(lock),'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'target_installs':0,'scope':'public dependency wheels only;not target compilation or scoring readiness'}
 try:
  # Outcome-independent epoch selection;package versions must be parseable by packaging.
  from packaging.version import Version,InvalidVersion
  chosen={};epoch=datetime.datetime(2025,11,1,tzinfo=datetime.timezone.utc)
  for package in ['Cython','setuptools','wheel']:
   with urllib.request.urlopen('https://pypi.org/pypi/'+package+'/json',timeout=20) as response:data=response.read(8388609)
   if len(data)>8388608:raise RuntimeError('public metadata byte cap')
   (root/(package+'-metadata.json')).write_bytes(data);rows=json.loads(data)['releases'];eligible=[]
   for version,files in rows.items():
    try:v=Version(version)
    except InvalidVersion:continue
    if v.is_prerelease or v.is_devrelease:continue
    timestamps=[datetime.datetime.fromisoformat(f['upload_time_iso_8601'].replace('Z','+00:00')) for f in files if not f.get('yanked')]
    if timestamps and min(timestamps)<epoch:eligible.append(v)
   chosen[package]=str(max(eligible))
  public_lock=lock.read_text();names={line.split('==')[0].lower() for line in public_lock.splitlines()}
  extras=''.join(k+'=='+v+'\n' for k,v in chosen.items() if k.lower() not in names);(root/'requirements.txt').write_text(public_lock+extras);report['build_tool_versions']=chosen;report['build_tool_selection']='latest stable public release before declared image date20251031;not target outcomes';report['requirements_sha256']=sha(root/'requirements.txt')
  args=['docker','create','--name',name,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','256','--security-opt','no-new-privileges','-v',str(wheels)+':/public-wheels','-v',str(root/'requirements.txt')+':/opt/public-requirements.txt:ro','--entrypoint','/bin/sh',image,'-c','pip wheel --disable-pip-version-check --retries 0 --timeout 20 --wheel-dir /public-wheels -r /opt/public-requirements.txt']
  subprocess.run(args,capture_output=True,check=True,timeout=20)
  with (root/'prepare.log').open('wb') as log:p=subprocess.run(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,timeout=600)
  report['exit']=p.returncode
  if p.returncode:raise RuntimeError('dependency wheel build failed;no retry')
  files=sorted(wheels.iterdir())
  if not files or any(not p.is_file() or p.is_symlink() or p.suffix!='.whl' or p.name.lower().startswith('pyknotid') for p in files):raise RuntimeError('unsafe or target wheel in public cache')
  report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files};report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-cython-wheels-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},indent=2));print('wheel count',len(report.get('artifacts',{})))
