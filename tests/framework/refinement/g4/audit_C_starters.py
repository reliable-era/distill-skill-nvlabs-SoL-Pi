"""Actual C starter archive equals trusted sanitized snapshot bytes/modes/links.
No extraction/actor calls/Git mutation. UID/GID0, exact paths, one Git snapshot
and actor-side recorded HEAD proof; not evidence of subsequent actor edits.
"""
import argparse,hashlib,json,pathlib,stat,subprocess,tarfile
from native import H,sha
from transport import save

def audit(window):
 plan=json.loads((H/'preregistration.json').read_text());q=json.loads((H/'queue-order.json').read_text());lookup={r['cell_id']:r for r in q['parts']['C']};root=pathlib.Path(json.loads((H/f'window-{window}-launch.json').read_text())['root']);proofs=[];pending=[];errors=[]
 for cell in json.loads((H/f'windows/{window}.json').read_text())['cells']:
  if cell not in lookup:continue
  dirs=sorted(p for p in root.glob(cell+'-a*') if p.is_dir())
  if not dirs:pending.append(cell);continue
  for directory in dirs:
   archive=directory/'starter.tar';record=directory/'source-proof.json'
   if not archive.exists() or not record.exists():pending.append(directory.name);continue
   source=pathlib.Path(plan['prepared_tasks'][lookup[cell]['task']]);workspace=source/'workspace';manifest=json.loads((source/'manifest.json').read_text());bad=[];expected={'testbed':workspace};expected.update({'testbed/'+str(p.relative_to(workspace)):p for p in workspace.rglob('*')});source_proof=json.loads(record.read_text());git=['git','--no-optional-locks','-C',str(workspace)]
   head=subprocess.check_output(git+['rev-parse','HEAD'],text=True,timeout=20).strip();count=subprocess.check_output(git+['rev-list','--all','--count'],text=True,timeout=20).strip()
   if head!=manifest['snapshot_commit'] or source_proof['snapshot_commit']!=head or count!='1' or source_proof['gold_in_actor'] is not False or source_proof['upstream_history_in_actor'] is not False:bad.append('sanitized single-snapshot/actor HEAD identity')
   with tarfile.open(archive) as tar:
    members=tar.getmembers();names=[m.name for m in members]
    if len(set(names))!=len(names) or set(names)!=set(expected):bad.append('unexpected/missing starter path')
    for m in members:
     if m.name not in expected:continue
     p=expected[m.name];s=p.lstat()
     if (m.uid,m.gid,m.uname,m.gname)!=(0,0,'root','root') or m.mode!=stat.S_IMODE(s.st_mode):bad.append('UID/GID/mode changed:'+m.name)
     if p.is_symlink():
      if not m.issym() or m.linkname!=str(p.readlink()):bad.append('symlink changed:'+m.name)
     elif p.is_dir():
      if not m.isdir():bad.append('directory changed:'+m.name)
     elif p.is_file():
      if not (m.isfile() or m.islnk()) or hashlib.sha256(tar.extractfile(m).read()).hexdigest()!=sha(p):bad.append('starter bytes changed:'+m.name)
     else:bad.append('unsupported starter type:'+m.name)
   if bad:errors.append(dict(attempt=directory.name,checks=bad))
   proofs.append(dict(cell_id=cell,attempt=directory.name,task=lookup[cell]['task'],snapshot_commit=head,git_commits=1,starter_paths=len(expected),starter_sha256=sha(archive),source_proof_sha256=sha(record),all_checks_passed=not bad))
 result=dict(window=window,proofs=proofs,pending=pending,errors=errors,all_sanitized_starters_verified=not pending and not errors,model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/f'window-{window}-C-starter-audit.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('window');a=p.parse_args();r=audit(a.window);print('Actual C starter proofs',len(r['proofs']),'pending',r['pending'],'errors',r['errors'])
