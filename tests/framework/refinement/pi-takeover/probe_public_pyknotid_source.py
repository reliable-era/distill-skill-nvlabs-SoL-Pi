"""No-network clone of exact public-instruction source using read-only mirror."""
import hashlib,json,pathlib,subprocess,uuid
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 cache=json.loads((R/'public-pyknotid-source-cache.json').read_text());assert cache['prepared'];repo=pathlib.Path(cache['private_root'])/'pyknotid.git';before={p.relative_to(repo).as_posix():sha(p) for p in sorted(repo.rglob('*')) if p.is_file()};assert before==cache['cache_hashes']
 config=pathlib.Path(cache['private_root'])/'clone.gitconfig';config.write_text('[safe]\n\tdirectory = /opt/public-sources/pyknotid.git\n[url "file:///opt/public-sources/pyknotid.git"]\n\tinsteadOf = https://github.com/SPOCKnots/pyknotid.git\n');config.chmod(0o644)
 env={'GIT_CONFIG_GLOBAL':'/opt/public-sources/clone.gitconfig'}
 image=next(t['image']['image_id'] for t in json.loads((R/'terminal-selected-image-cache.json').read_text())['tasks'] if t['task']=='build-cython-ext');name='solpi-public-source-probe-'+uuid.uuid4().hex[:10];root=pathlib.Path(cache['private_root']);report={'source_cache_sha256':sha(R/'public-pyknotid-source-cache.json'),'image_id':image,'model_POSTs':0,'native_actor_starts':0,'target_builds':0,'package_tests_run':0,'network':'none','readonly_source_mount':True,'git_config_env':env,'git_config_sha256':sha(config),'prior_failure':'public-pyknotid-source-probe-v1-failure.json','scope':'original unpatched public source availability only;not wheel/install/scoring readiness'}
 try:
  args=['docker','create','--name',name,'--pull=never','--network','none','--cpus','1','--memory','2048m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',cache['readonly_actor_mount'],'-v',str(config)+':/opt/public-sources/clone.gitconfig:ro','--entrypoint','/bin/sh']
  for k,v in env.items():args+=['-e',k+'='+v]
  command='git clone --depth 1 --branch 0.5.3 https://github.com/SPOCKnots/pyknotid.git /app/pyknotid && git -C /app/pyknotid rev-parse HEAD && git -C /app/pyknotid rev-parse HEAD^{tree} && test -z "$(git -C /app/pyknotid status --porcelain)"'
  subprocess.run([*args,image,'-c',command],capture_output=True,check=True,timeout=15)
  inspect=json.loads(subprocess.check_output(['docker','inspect',name],text=True,timeout=10))[0];assert inspect['HostConfig']['NetworkMode']=='none' and len(inspect['Mounts'])==2 and all(m['RW'] is False for m in inspect['Mounts']) and {m['Destination'] for m in inspect['Mounts']}=={'/opt/public-sources/pyknotid.git','/opt/public-sources/clone.gitconfig'}
  with (root/'isolated-clone-probe.log').open('wb') as out:result=subprocess.run(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,timeout=60)
  lines=(root/'isolated-clone-probe.log').read_text().splitlines();report.update(exit=result.returncode,commit_present=cache['commit'] in lines,tree_present=cache['tree'] in lines)
 except Exception as e:report['error']={'type':type(e).__name__,'message':str(e)[:200]}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20);p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);report['cleanup_verified']=p.returncode!=0 and 'No such' in p.stderr;report['cache_unchanged']={p.relative_to(repo).as_posix():sha(p) for p in sorted(repo.rglob('*')) if p.is_file()}==before;report['probe_log_sha256']=sha(root/'isolated-clone-probe.log') if (root/'isolated-clone-probe.log').exists() else None;report['runner_sha256']=sha(pathlib.Path(__file__));report['passed']=report.get('exit')==0 and report.get('commit_present') and report.get('tree_present') and report['cleanup_verified'] and report['cache_unchanged'];(R/'public-pyknotid-source-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
