"""Offline source/tool access diagnostic under actor-like capabilities;never build pmars."""
import json,pathlib,subprocess,uuid
from prepare_public_pmars_source import R,sha,docker
if __name__=='__main__':
 source=json.loads((R/'public-pmars-source-cache.json').read_text());tools=json.loads((R/'public-pmars-tools-cache.json').read_text());assert source['download_prepared'] and tools['prepared'];root=pathlib.Path(source['private_root']);name='solpi-public-pmars-probe-'+uuid.uuid4().hex[:10]
 for dirname,manifest in [('downloads',source['artifacts']),('tool-archives',tools['artifacts'])]:
  for filename,record in manifest.items():assert sha(root/dirname/filename)==record['sha256']
 report={'task':'build-pmars','image_id':source['image_id'],'network':'none','cap_drop':'ALL','model_POSTs':0,'native_actor_starts':0,'target_builds':0,'source_cache_sha256':sha(R/'public-pmars-source-cache.json'),'tools_cache_sha256':sha(R/'public-pmars-tools-cache.json'),'prior_failure':'public-pmars-source-probe-v1-failure.json','scope':'offline public dependencies/extraction diagnostic only;not target build/skill result'}
 try:
  command='mkdir -p /tmp/public-apt-cache/partial /tmp/public-apt-lists/partial && apt-get -o Acquire::Retries=0 -o APT::Sandbox::User=root -o Dir::Cache::archives=/tmp/public-apt-cache -o Dir::State::lists=/tmp/public-apt-lists -y install /opt/public-debs/*.deb && dpkg-source -x /opt/public-source/'+source['dsc']+' /app/pmars-0.9.4 && test -f /app/pmars-0.9.4/src/Makefile && test ! -e /usr/local/bin/pmars && gcc --version && dpkg-query -W -f="${Version}\\n" dpkg-dev'
  docker('create','--name',name,'--pull=never','--network','none','--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(root/'downloads')+':/opt/public-source:ro','-v',str(root/'tool-archives')+':/opt/public-debs:ro','--entrypoint','/bin/sh',source['image_id'],'-c',command)
  with (root/'offline-access-probe.log').open('wb') as out:p=subprocess.run(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,timeout=180)
  report['exit']=p.returncode;report['source_extraction_verified']=p.returncode==0
 except Exception as e:report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['cache_unchanged']=all(sha(root/d/f)==record['sha256'] for d,m in [('downloads',source['artifacts']),('tool-archives',tools['artifacts'])] for f,record in m.items());report['log_sha256']=sha(root/'offline-access-probe.log') if (root/'offline-access-probe.log').exists() else None;report['runner_sha256']=sha(pathlib.Path(__file__));report['passed']=report.get('source_extraction_verified') and report['cleanup_verified'] and report['cache_unchanged'];(R/'public-pmars-source-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
