"""Cache basic source/build prerequisites from same signed snapshot;never install pmars."""
import hashlib,json,pathlib,subprocess,uuid
from prepare_public_pmars_source import docker,sha,R
if __name__=='__main__':
 source=json.loads((R/'public-pmars-source-cache.json').read_text());assert source['download_prepared'];root=pathlib.Path(source['private_root']);archives=root/'tool-archives';archives.mkdir(mode=0o755,exist_ok=False);name='solpi-public-pmars-tools-'+uuid.uuid4().hex[:10];report={'requested_packages':['build-essential','dpkg-dev','xz-utils'],'selection_rule':'generic C source build/extraction tools;no pmars binary or X11 build dependencies','model_POSTs':0,'native_actor_starts':0,'target_builds':0,'private_root':str(root),'scope':'public tool prerequisites only;no actor scoring'}
 try:
  docker('create','--name',name,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128','--security-opt','no-new-privileges','-v',str(archives)+':/var/cache/apt/archives','-v',str(R/'environment-inputs/public-ca.crt')+':/etc/ssl/certs/ca-certificates.crt:ro','--entrypoint','/bin/sh',source['image_id'],'-c','sleep infinity');docker('start',name);docker('cp',str(root/'debian.sources'),name+':/etc/apt/sources.list.d/debian.sources')
  for label,args,timeout in [('tool-metadata',['apt-get','-o','Acquire::Retries=0','-o','Acquire::https::Timeout=15','update'],120),('tool-download',['apt-get','-o','Acquire::Retries=0','-o','Acquire::https::Timeout=15','--download-only','-y','install','build-essential','dpkg-dev','xz-utils'],180)]:
   with (root/(label+'.log')).open('wb') as out:p=subprocess.run(['docker','exec',name,*args],stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
   report[label+'_exit']=p.returncode
   if p.returncode:raise RuntimeError(label+' failed;no retry')
  files=sorted(archives.glob('*.deb'));assert files;report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
  if any(p.name.startswith(('pmars_','libx11')) for p in files):raise RuntimeError('target/X11 package unexpectedly cached')
  report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-pmars-tools-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},indent=2));print('hashed deb count',len(report.get('artifacts',{})))
