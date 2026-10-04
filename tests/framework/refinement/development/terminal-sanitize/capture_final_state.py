import subprocess,time,json,shutil,tarfile,hashlib,os
from pathlib import Path
def copy_snapshot_file(src,dst):
 try:os.link(src,dst)
 except OSError:shutil.copy2(src,dst)
 return dst
OUT=Path(__file__).resolve().parent
SEEN={};DONE=set();END=time.monotonic()+1800
while time.monotonic()<END:
 names=subprocess.run(['docker','ps','--filter','name=solpi-terminal-','--format','{{.Names}}'],capture_output=True,text=True).stdout.splitlines()
 for name in names:
  if name in DONE or name in SEEN:continue
  r=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
  try:info=json.loads(r.stdout)[0]
  except Exception:continue
  work=next((Path(m['Source']) for m in info['Mounts'] if m['Destination']=='/app/dclm'),None)
  if work:SEEN[name]=work
 for name,work in list(SEEN.items()):
  if name in names:continue
  h,a=name.removeprefix('solpi-terminal-').split('-',1);dest=OUT/h/a;dest.mkdir(parents=True,exist_ok=True)
  try:
   # Store complete local snapshot outside Git, including original full history.
   saved=Path('/tmp/solpi-terminal-final-snapshots')/h/a;saved.parent.mkdir(parents=True,exist_ok=True)
   shutil.copytree(work,saved,copy_function=copy_snapshot_file)
   baseline=Path('/tmp/solpi-terminal-baseline');files={str(p.relative_to(saved)):hashlib.sha256(p.read_bytes()).hexdigest() for p in saved.rglob('*') if p.is_file()}
   base={str(p.relative_to(baseline)):hashlib.sha256(p.read_bytes()).hexdigest() for p in baseline.rglob('*') if p.is_file()}
   changed=[p for p,v in files.items() if base.get(p)!=v];deleted=sorted(set(base)-set(files))
   with tarfile.open(dest/'final-state-delta.tar.gz','w:gz') as tar:
    for path in changed:tar.add(saved/path,arcname=path,recursive=False)
   (dest/'final-state-manifest.json').write_text(json.dumps({'full_snapshot_path':str(saved),'snapshot_capture':'After actor container exited; actor absent at capture; verifier may be running','files_sha256':files,'changed_or_added_files':changed,'deleted_files':deleted,'delta_sha256':hashlib.sha256((dest/'final-state-delta.tar.gz').read_bytes()).hexdigest(),'baseline_image_id':json.loads((OUT/'plan.json').read_text())['image_id']},indent=2)+'\n')
   print('Snapshot',name,len(changed),len(deleted),flush=True)
  except Exception as e:print('Snapshot ERROR',name,type(e).__name__,str(e),flush=True)
  DONE.add(name);SEEN.pop(name)
 if (OUT/'results.json').exists() and len(json.loads((OUT/'results.json').read_text()))==12 and not SEEN:break
 time.sleep(.05)
