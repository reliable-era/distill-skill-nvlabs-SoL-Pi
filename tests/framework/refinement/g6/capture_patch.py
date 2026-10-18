"""Uniform G4C-safe captures plus lossless UTF8 Git-binary representation.
No unsafe filter or source edits; originals retained, apply/full-delta equality.
"""
import json,os,pathlib,shutil,tarfile
from common import command,sha,save
from recover_ignored_capture_links import project
from source_patch import project as source_project,artifact

def git(root,*args):
 return command(['git','-C',str(root),*args],env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null')).stdout

def capture(archive,baseline,root):
 archive=pathlib.Path(archive);baseline=pathlib.Path(baseline);root=pathlib.Path(root);manifest=json.loads((baseline/'manifest.json').read_text());work=root/'captured';work.mkdir();original_error=None;projection=None
 try:
  with tarfile.open(archive) as tar:tar.extractall(work,filter='data')
 except tarfile.AbsoluteLinkError as e:
  original_error=dict(type=type(e).__name__,message=str(e));projection=project(archive,baseline,root/'capture-projection');work=root/'capture-projection/captured'
 trusted=work/'.git'
 if trusted.is_symlink() or trusted.is_file():trusted.unlink()
 elif trusted.exists():shutil.rmtree(trusted)
 shutil.copytree(baseline/'workspace/.git',trusted)
 new=[str(p.relative_to(work)) for p in work.rglob('*') if p.is_file() and '.git' not in p.relative_to(work).parts and str(p.relative_to(work)) not in manifest['source_tree']]
 if new:git(work,'add','-N','--force','--',*new)
 # Private highest-precedence representation, not a content transformation.
 (trusted/'info/attributes').write_text('* -diff\n');raw_patch=git(work,'diff','--binary','HEAD');(root/'model.raw.patch').write_bytes(raw_patch);patch,source_projection=source_project(raw_patch);patch.decode('utf-8');(root/'model.patch').write_bytes(patch);applied=root/'delta-replay';shutil.copytree(baseline/'workspace',applied,symlinks=True);(applied/'.git/info/attributes').write_text('* -diff\n')
 if patch:git(applied,'apply','--binary','--whitespace=nowarn',str(root/'model.patch'))
 source_new=[p for p in new if not artifact(p)]
 if source_new:git(applied,'add','-N','--force','--',*source_new)
 assert git(applied,'diff','--binary','HEAD')==patch,'Complete captured/applied deltas differ';proofs=[]
 for name in filter(None,git(work,'diff','--name-only','-z','HEAD').decode().split('\0')):
  if artifact(name):continue
  a=work/name;b=applied/name
  if a.is_symlink():assert b.is_symlink() and a.readlink()==b.readlink();proofs.append(dict(path=name,type='symlink',target=str(a.readlink())))
  elif a.is_file():assert b.is_file() and sha(a)==sha(b) and bool(a.stat().st_mode&0o111)==bool(b.stat().st_mode&0o111);proofs.append(dict(path=name,type='file',sha256=sha(a),executable=bool(a.stat().st_mode&0o111)))
  else:assert not os.path.lexists(b);proofs.append(dict(path=name,type='deletion'))
 r=dict(captured_tar_sha256=sha(archive),snapshot_commit=manifest['snapshot_commit'],patch_sha256=sha(root/'model.patch'),raw_patch_sha256=sha(root/'model.raw.patch'),source_projection=source_projection,comparison_scope='source-only projection;raw tar/patch retained',data_filter_preserved=True,original_capture_error=original_error,ignored_link_projection=projection,complete_git_delta_replay_equal=True,changed_byte_mode_proofs=proofs,utf8_readable=True,model_calls=0,actor_reruns=0);save(root/'capture-proof.json',r);return r
