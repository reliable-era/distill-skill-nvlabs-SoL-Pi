"""Separate saved-state diagnostic; never mutates the consumed native row."""
import argparse,hashlib,json,os,pathlib,signal,subprocess,sys,types,uuid,importlib.util,shutil
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def manifest(root):
 return {str(p.relative_to(root)):({'symlink':os.readlink(p)} if p.is_symlink() else sha(p)) for p in sorted(root.rglob('*')) if p.is_file() or p.is_symlink()}
def copy_snapshot(work,private,expected):
 shutil.copytree(work,private/"work",symlinks=True)
 if manifest(private/"work")!=expected:raise RuntimeError("private snapshot copy mismatch")
def load_wrapper(path):
 sys.path.insert(0,str(path.parent));s=importlib.util.spec_from_file_location('W',path);w=importlib.util.module_from_spec(s);s.loader.exec_module(w);return w
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-diagnostic',action='store_true');a.add_argument('--plan-sha256');a.add_argument('--worker');x=a.parse_args()
 p=json.loads((R/'plan.json').read_text())
 if x.worker:
  d=pathlib.Path(x.worker);w=load_wrapper(pathlib.Path(p['wrapper']));w.uuid.uuid4=lambda:types.SimpleNamespace(hex=d.name.split('-')[-1]);result=w.grade(d,p['task']);(d/'diagnostic-result.json').write_text(json.dumps(result));return
 if not x.execute_diagnostic or x.plan_sha256!=sha(R/'plan.json'):raise SystemExit('explicit reviewed plan required')
 auth=json.loads((R/'execution-authorization.json').read_text());assert auth['plan_sha256']==x.plan_sha256
 for f,h in p['source_hashes'].items():assert sha(f)==h
 work=pathlib.Path(p['saved_work']);assert manifest(work)==p['snapshot_manifest']
 marker=R/'consumed.marker';marker.open('x').close()
 private=pathlib.Path('/tmp/solpi-posthoc-'+uuid.uuid4().hex);private.mkdir(mode=0o700);copy_snapshot(work,private,p['snapshot_manifest'])
 name='solpi-qwendev-grade-'+private.name.split('-')[-1][:12]
 # Adapter uses first twelve uuid characters.
 z=subprocess.Popen([sys.executable,str(__file__),'--worker',str(private)],start_new_session=True)
 errors=[]
 try:z.wait(timeout=180)
 except subprocess.TimeoutExpired:
  os.killpg(z.pid,signal.SIGKILL);z.wait(timeout=3);errors.append('diagnostic deadline')
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=5)
  q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
  absent=q.returncode!=0 and q.stderr.strip() in ['Error: No such object: '+name,'Error response from daemon: No such container: '+name]
  assert absent
  evidence={'scope':'posthoc diagnostic only; original ungraded native row unchanged','cleanup_absent':absent,'errors':errors,'snapshot_unchanged':manifest(work)==p['snapshot_manifest'],'worker_exit':z.returncode,'worker_terminal':z.poll() is not None,'private_directory':str(private),'grade':json.loads((private/'diagnostic-result.json').read_text()) if (private/'diagnostic-result.json').exists() else None}
  (R/'diagnostic-audit.json').write_text(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
