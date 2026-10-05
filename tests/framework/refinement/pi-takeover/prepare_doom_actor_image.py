"""Trusted pre-actor compiler installation only;source/base grader remain untouched."""
import json,pathlib,subprocess,uuid
from prepare_public_pmars_source import R,sha,docker
from public_artifact_cache import verify_artifact_directory
if __name__=='__main__':
 cache=json.loads((R/'public-doom-tools-cache.json').read_text());root=pathlib.Path(cache['private_root']);verify_artifact_directory(root/'archives',cache['artifacts'],True);name='solpi-doom-actor-prep-'+uuid.uuid4().hex[:10];report={'base_image_id':cache['image_id'],'cache_sha256':sha(R/'public-doom-tools-cache.json'),'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'trusted_setup_only':True,'actor_cap_drop_required':'ALL','grader_image_must_remain_original':True,'scope':'dependency-only actor image;not scoring or target installation'}
 def app_manifest():return docker('exec',name,'/bin/sh','-c','find /app -type f -exec sha256sum {} + | sort')
 try:
  docker('create','--name',name,'--pull=never','--network','none','--cpus','1','--memory','2048m','--pids-limit','128','--security-opt','no-new-privileges','-v',str(root/'archives')+':/opt/public-debs:ro','--entrypoint','/bin/sh',cache['image_id'],'-c','sleep infinity');docker('start',name);before=app_manifest();(root/'app-before.sha256').write_text(before)
  command='mkdir -p /tmp/public-apt-cache/partial /tmp/public-apt-lists/partial && apt-get -o Acquire::Retries=0 -o APT::Sandbox::User=root -o Dir::Cache::archives=/tmp/public-apt-cache -o Dir::State::lists=/tmp/public-apt-lists -y install /opt/public-debs/*.deb && mipsel-linux-gnu-gcc -dumpmachine && test ! -e /app/doomgeneric_mips'
  with (root/'trusted-install.log').open('wb') as out:p=subprocess.run(['docker','exec',name,'/bin/sh','-c',command],stdout=out,stderr=subprocess.STDOUT,timeout=180)
  if p.returncode:raise RuntimeError('trusted dependency installation failed')
  after=app_manifest();assert before==after;report['app_source_inputs_unchanged']=True;report['app_manifest_sha256']=sha(root/'app-before.sha256');report['target_binary_absent']=True
  docker('stop','-t','1',name);report['prepared_actor_image_id']=docker('commit',name);report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['runner_sha256']=sha(pathlib.Path(__file__));(R/'doom-dependency-actor-image.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
