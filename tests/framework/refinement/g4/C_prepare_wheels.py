"""Download pinned public pure-Python build wheels to an owned private cache.
Zero model calls. No host install, benchmark/test/official-harness edits, or
network widening for graders. Original control failures remain immutable.
This is preparation only; a new committed paired control recheck is required.
"""
import datetime,hashlib,json,os,pathlib,subprocess,sys,uuid
H=pathlib.Path(__file__).resolve().parent
PACKAGES=['setuptools==67.8.0','wheel==0.41.3','certifi==2024.8.30','setuptools_scm==7.1.0','packaging==23.2','tomli==2.0.1','typing_extensions==4.7.1']
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 if (H/'C-wheel-launch.json').exists():raise RuntimeError('Existing preparation handle; reconcile, never automatic restart')
 root=pathlib.Path('/tmp/solpi-g4-C-wheelhouse-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);command=[sys.executable,'-m','pip','download','--only-binary=:all:','--no-deps','--dest',str(root),*PACKAGES];launch=dict(pid=os.getpid(),root=str(root),command=command,packages=PACKAGES,model_calls=0,runner_sha256=sha(__file__),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(H/'C-wheel-launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 log=root/'download.private.log'
 try:
  with log.open('xb') as out:os.chmod(log,0o600);p=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,timeout=300)
  result=dict(exit_code=p.returncode,wheels={p.name:sha(p) for p in root.glob('*.whl')},model_calls=0,root=str(root),log_sha256=sha(log),benchmark_edits=0,host_installs=0)
 except subprocess.TimeoutExpired:result=dict(timeout=True,model_calls=0,root=str(root),log_sha256=sha(log),no_automatic_retry=True)
 (H/'C-wheel-preparation.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
