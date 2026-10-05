"""Build only public fastText software wheels;never train target model/read dataset."""
import datetime,json,pathlib,subprocess,urllib.request,uuid
from packaging.version import Version,InvalidVersion
from prepare_public_pmars_source import R,sha,docker
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-public-fasttext-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);wheels=root/'wheels';wheels.mkdir(mode=0o755);name=root.name+'-prepare';image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']=='train-fasttext');report={'task':'train-fasttext','image_id':image,'private_root':str(root),'model_POSTs':0,'native_actor_starts':0,'models_trained':0,'dataset_read':False,'scope':'public training-software wheel only;not model training or grading'}
 try:
  versions={};epoch=datetime.datetime(2025,11,1,tzinfo=datetime.timezone.utc)
  for package in ['fasttext','pybind11','setuptools','wheel']:
   with urllib.request.urlopen('https://pypi.org/pypi/'+package+'/json',timeout=20) as response:data=response.read(8388609)
   if len(data)>8388608:raise RuntimeError('metadata byte cap')
   (root/(package+'-metadata.json')).write_bytes(data);eligible=[]
   for version,files in json.loads(data)['releases'].items():
    try:v=Version(version)
    except InvalidVersion:continue
    if v.is_prerelease or v.is_devrelease:continue
    times=[datetime.datetime.fromisoformat(f['upload_time_iso_8601'].replace('Z','+00:00')) for f in files if not f.get('yanked')]
    if times and min(times)<epoch:eligible.append(v)
   versions[package]=str(max(eligible))
  docker('create','--name',name,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','256','--security-opt','no-new-privileges','-v',str(wheels)+':/public-wheels','--entrypoint','/bin/sh',image,'-c','sleep infinity');docker('start',name);versions['numpy']=docker('exec',name,'python','-c','import importlib.metadata as m;print(m.version("numpy"))');requirements=''.join(k+'=='+v+'\n' for k,v in versions.items());(root/'requirements.txt').write_text(requirements);docker('cp',str(root/'requirements.txt'),name+':/opt/public-requirements.txt');report['versions']=versions;report['version_selection']='latest stable before image-date20251031;NumPy preserved from original image'
  for label,args,seconds in [('metadata',['apt-get','-o','Acquire::Retries=0','update'],120),('compiler',['apt-get','-o','Acquire::Retries=0','-y','install','g++'],180),('wheels',['pip','wheel','--disable-pip-version-check','--retries','0','--timeout','20','-w','/public-wheels','-r','/opt/public-requirements.txt'],600)]:
   with (root/(label+'.log')).open('wb') as out:p=subprocess.run(['docker','exec','-e','PIP_CONSTRAINT=/opt/public-requirements.txt',name,*args],stdout=out,stderr=subprocess.STDOUT,timeout=seconds)
   report[label+'_exit']=p.returncode
   if p.returncode:raise RuntimeError(label+' failed;no retry')
  docker('exec',name,'/bin/sh','-c','test ! -e /app/model.bin');files=sorted(wheels.iterdir());assert files and all(p.suffix=='.whl' and p.is_file() and not p.is_symlink() for p in files);report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files};report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-fasttext-wheels-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},indent=2));print('wheel count',len(report.get('artifacts',{})))
