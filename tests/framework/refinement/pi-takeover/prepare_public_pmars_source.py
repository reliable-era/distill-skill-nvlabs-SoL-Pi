"""Download public Debian source only;no target build/install or benchmark tests."""
import hashlib,json,pathlib,subprocess,uuid
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def docker(*args,timeout=20):return subprocess.check_output(['docker',*args],stderr=subprocess.PIPE,text=True,timeout=timeout).strip()
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-public-pmars-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);downloads=root/'downloads';downloads.mkdir(mode=0o755);name=root.name+'-fetch';image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']=='build-pmars')
 sources=(R/'environment-inputs/pmars-debian.sources').read_text();assert sources.count('Types: deb\n')==2;sources=sources.replace('Types: deb\n','Types: deb deb-src\n');(root/'debian.sources').write_text(sources)
 report={'task':'build-pmars','snapshot':'20251031T000000Z','snapshot_selection':'existing public image-date repair;no outcome/version search','image_id':image,'private_root':str(root),'base_sources_sha256':sha(R/'environment-inputs/pmars-debian.sources'),'source_enabled_sources_sha256':sha(root/'debian.sources'),'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'oracle_or_tests_mounted':False,'scope':'download original public Debian source;not build,grade or scoring readiness'}
 try:
  docker('create','--name',name,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128','--security-opt','no-new-privileges','-v',str(downloads)+':/public-downloads','-v',str(R/'environment-inputs/public-ca.crt')+':/etc/ssl/certs/ca-certificates.crt:ro','--entrypoint','/bin/sh',image,'-c','sleep infinity');docker('start',name);docker('cp',str(root/'debian.sources'),name+':/etc/apt/sources.list.d/debian.sources')
  for label,args,seconds in [('metadata',['apt-get','-o','Acquire::Retries=0','-o','Acquire::https::Timeout=15','update'],120),('download',['apt-get','-o','Acquire::Retries=0','-o','Acquire::https::Timeout=15','--download-only','source','pmars'],120)]:
   with (root/(label+'.log')).open('wb') as out:p=subprocess.run(['docker','exec','-w','/public-downloads',name,*args],stdout=out,stderr=subprocess.STDOUT,timeout=seconds)
   report[label+'_exit']=p.returncode
   if p.returncode:raise RuntimeError(label+' failed;no retry')
  paths=sorted(downloads.iterdir());dsc=[p for p in paths if p.suffix=='.dsc']
  if len(dsc)!=1 or any(not p.is_file() or p.is_symlink() for p in paths):raise RuntimeError('unsupported source download layout')
  report['dsc']=dsc[0].name;report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths};report['download_prepared']=True
 except Exception as e:report['download_prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:250]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-pmars-source-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
