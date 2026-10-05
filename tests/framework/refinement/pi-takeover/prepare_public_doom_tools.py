"""Public cross-toolchain prerequisite cache;no Doom target build or tests."""
import json,pathlib,subprocess,uuid
from prepare_public_pmars_source import R,sha,docker
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-public-doom-tools-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);archives=root/'archives';archives.mkdir(mode=0o755);name=root.name+'-prepare';image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']=='make-doom-for-mips');report={'task':'make-doom-for-mips','image_id':image,'private_root':str(root),'requested_packages':['gcc-mipsel-linux-gnu'],'selection_rule':'public task requires MIPS ELF;little-endian public VM input;generic crosscompiler,not target build flags','repository_policy':'unchanged original-image configured signed repositories;metadata refresh matches existing environment repair;freeze downloaded artifact versions/hashes','model_POSTs':0,'native_actor_starts':0,'target_builds':0,'scope':'public compiler prerequisites only;no Doom oracle/test/build'}
 try:
  docker('create','--name',name,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128','--security-opt','no-new-privileges','-v',str(archives)+':/var/cache/apt/archives','--entrypoint','/bin/sh',image,'-c','sleep infinity');docker('start',name)
  for label,args,seconds in [('metadata',['apt-get','-o','Acquire::Retries=0','-o','Acquire::http::Timeout=15','update'],120),('download',['apt-get','-o','Acquire::Retries=0','-o','Acquire::http::Timeout=15','--download-only','-y','install','gcc-mipsel-linux-gnu'],180)]:
   with (root/(label+'.log')).open('wb') as out:p=subprocess.run(['docker','exec',name,*args],stdout=out,stderr=subprocess.STDOUT,timeout=seconds)
   report[label+'_exit']=p.returncode
   if p.returncode:raise RuntimeError(label+' failed;no retry')
  files=sorted(archives.glob('*.deb'));assert files;report['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files};report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr
  partial=archives/'partial'
  if report.get('prepared') and partial.exists():partial.rmdir()
  report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-doom-tools-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},indent=2));print('deb count',len(report.get('artifacts',{})))
