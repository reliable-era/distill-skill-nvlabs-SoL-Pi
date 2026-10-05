"""Offline install of cached dependencies;assert target package remains absent."""
import json,pathlib,subprocess,uuid
from prepare_public_cython_wheels import R,sha
from public_artifact_cache import verify_artifact_directory
if __name__=='__main__':
 cache=json.loads((R/'public-cython-wheels-cache.json').read_text());assert cache['prepared'];root=pathlib.Path(cache['private_root']);verified=verify_artifact_directory(root/'wheels',cache['artifacts']);name='solpi-public-cython-probe-'+uuid.uuid4().hex[:10];report={'network':'none','cap_drop':'ALL','image_id':cache['image_id'],'cache_sha256':sha(R/'public-cython-wheels-cache.json'),'verified_cache':verified,'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'target_installs':0,'scope':'offline dependency/import infrastructure probe;not target/skill performance'}
 try:
  program="import importlib.metadata as m,importlib.util,json,numpy,Cython,planarity,scipy;assert numpy.__version__=='2.3.0';assert importlib.util.find_spec('pyknotid') is None;print(json.dumps({'python_packages':{k:m.version(k) for k in ['numpy','Cython','setuptools','wheel','planarity']},'target_absent':True}))"
  command='pip install --disable-pip-version-check --no-index --find-links=/public-wheels -r /opt/public-requirements.txt && python -I -c '+__import__('shlex').quote(program)
  subprocess.run(['docker','create','--name',name,'--pull=never','--network','none','--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(root/'wheels')+':/public-wheels:ro','-v',str(root/'requirements.txt')+':/opt/public-requirements.txt:ro','--entrypoint','/bin/sh',cache['image_id'],'-c',command],capture_output=True,check=True,timeout=20)
  with (root/'offline-probe.log').open('wb') as log:p=subprocess.run(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,timeout=180)
  report['exit']=p.returncode
  for line in (root/'offline-probe.log').read_text().splitlines():
   if line.startswith('{'):report['import_witness']=json.loads(line)
 except Exception as e:report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['cache_unchanged']=verify_artifact_directory(root/'wheels',cache['artifacts'])==verified;report['log_sha256']=sha(root/'offline-probe.log') if (root/'offline-probe.log').exists() else None;report['runner_sha256']=sha(pathlib.Path(__file__));report['passed']=report.get('exit')==0 and report.get('import_witness',{}).get('target_absent') is True and report['cleanup_verified'] and report['cache_unchanged'];(R/'public-cython-wheels-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
