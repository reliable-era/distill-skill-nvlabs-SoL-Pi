"""Fetch only instruction-authorized original source;never compile/install/run its tests."""
import hashlib,json,pathlib,subprocess,uuid
R=pathlib.Path(__file__).resolve().parent
URL='https://github.com/SPOCKnots/pyknotid.git';TAG='0.5.3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-public-pyknotid-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);repo=root/'pyknotid.git';report={'source_url':URL,'source_tag':TAG,'private_root':str(root),'model_POSTs':0,'actor_starts':0,'target_builds':0,'source_selection':'exact public instruction URL/tag;not grader/oracle artifacts','scope':'public original-source cache only;not dependency/wheel or scoring readiness'}
 try:
  with (root/'fetch.log').open('wb') as log:subprocess.run(['git','clone','--bare','--depth','1','--branch',TAG,URL,str(repo)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
  def git(*args):return subprocess.check_output(['git','--git-dir='+str(repo),*args],text=True,stderr=subprocess.PIPE,timeout=15).strip()
  report['commit']=git('rev-parse',TAG+'^{commit}');report['tree']=git('rev-parse',TAG+'^{tree}');assert git('rev-parse','HEAD')==report['commit']
  names=git('ls-tree','-r','--name-only',TAG).splitlines();assert 'setup.py' in names
  if any(p.endswith(('.so','.whl')) for p in names):raise RuntimeError('unexpected built artifacts in public source tag')
  for p in repo.rglob('*'):
   if p.is_symlink():raise RuntimeError('linked public cache file')
   p.chmod(0o755 if p.is_dir() else 0o644)
  config=root/'clone.gitconfig';config.write_text('[safe]\n\tdirectory = /opt/public-sources/pyknotid.git\n[url "file:///opt/public-sources/pyknotid.git"]\n\tinsteadOf = https://github.com/SPOCKnots/pyknotid.git\n');config.chmod(0o644)
  report['cache_hashes']={p.relative_to(repo).as_posix():sha(p) for p in sorted(repo.rglob('*')) if p.is_file()};report['source_file_count']=len(names);report['git_config_env']={'GIT_CONFIG_GLOBAL':'/opt/public-sources/clone.gitconfig'};report['git_config_sha256']=sha(config);report['readonly_config_mount']=str(config)+':/opt/public-sources/clone.gitconfig:ro';report['readonly_actor_mount']=str(repo)+':/opt/public-sources/pyknotid.git:ro';report['prepared']=True
 except Exception as e:report['prepared']=False;report['error']={'type':type(e).__name__,'message':str(e)[:250]}
 report['runner_sha256']=sha(pathlib.Path(__file__));(R/'public-pyknotid-source-cache.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
