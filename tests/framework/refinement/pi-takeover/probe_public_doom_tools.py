"""Offline crosscompiler availability only;do not compile target or fixture programs."""
import json,pathlib,subprocess,uuid
from prepare_public_pmars_source import R,sha,docker
from public_artifact_cache import verify_artifact_directory
if __name__=='__main__':
 cache=json.loads((R/'public-doom-tools-cache.json').read_text());assert cache['prepared'];root=pathlib.Path(cache['private_root']);verified=verify_artifact_directory(root/'archives',cache['artifacts'],True);name='solpi-public-doom-probe-'+uuid.uuid4().hex[:10];report={'network':'none','cap_drop':'ALL','image_id':cache['image_id'],'cache_sha256':sha(R/'public-doom-tools-cache.json'),'verified_cache':verified,'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'scope':'offline compiler availability only;not VM/target/official grade'}
 try:
  command='mkdir -p /tmp/public-apt-cache/partial /tmp/public-apt-lists/partial && apt-get -o Acquire::Retries=0 -o APT::Sandbox::User=root -o Dir::Cache::archives=/tmp/public-apt-cache -o Dir::State::lists=/tmp/public-apt-lists -y install /opt/public-debs/*.deb && mipsel-linux-gnu-gcc -dumpmachine && mipsel-linux-gnu-gcc --version && test ! -e /app/doomgeneric_mips'
  docker('create','--name',name,'--pull=never','--network','none','--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(root/'archives')+':/opt/public-debs:ro','--entrypoint','/bin/sh',cache['image_id'],'-c',command)
  with (root/'offline-probe.log').open('wb') as out:p=subprocess.run(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,timeout=180)
  report['exit']=p.returncode;report['mipsel_compiler_available']='mipsel-linux-gnu' in (root/'offline-probe.log').read_text().splitlines()
 except Exception as e:report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['cache_unchanged']=verify_artifact_directory(root/'archives',cache['artifacts'],True)==verified;report['log_sha256']=sha(root/'offline-probe.log') if (root/'offline-probe.log').exists() else None;report['runner_sha256']=sha(pathlib.Path(__file__));report['passed']=report.get('exit')==0 and report.get('mipsel_compiler_available') and report['cleanup_verified'] and report['cache_unchanged'];(R/'public-doom-tools-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
