"""Lossless UTF8-readable Git binary representation of a captured-only delta.
Uniform all-path representation; no lossy transcoding, source edits, models,
actors, grader calls, or unsafe-path options. Independently apply to baseline
and compare the complete Git delta bytes with the captured candidate.
"""
import hashlib,json,os,pathlib,shutil,subprocess

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def git(root,*args):
 env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null')
 return subprocess.run(['git','-C',str(root),*args],env=env,check=True,capture_output=True,timeout=120).stdout

def represent(baseline,projection,destination):
 baseline=pathlib.Path(baseline);projection=pathlib.Path(projection);destination=pathlib.Path(destination);old=json.loads((projection/'projection-proof.json').read_text());assert sha(projection/'model.patch')==old['patch_sha256'];manifest=json.loads((baseline/'manifest.json').read_text());assert manifest['snapshot_commit']==old['snapshot_commit'];assert old['data_filter_preserved'] and old['model_calls']==0 and old['actor_reruns']==0
 destination.mkdir(mode=0o700);candidate=destination/'candidate';applied=destination/'applied';shutil.copytree(projection/'captured',candidate,symlinks=True);shutil.copytree(baseline/'workspace',applied,symlinks=True)
 for root in (candidate,applied):
  assert git(root,'rev-parse','HEAD').decode().strip()==manifest['snapshot_commit']
  (root/'.git/info/attributes').write_text('* -diff\n')
 # Highest-precedence private Git attributes change representation only.
 # No candidate/baseline source bytes or original metadata are modified.
 patch=git(candidate,'diff','--binary','HEAD');patch.decode('utf-8');(destination/'model.patch').write_bytes(patch)
 git(applied,'apply','--binary','--whitespace=nowarn',str(destination/'model.patch'))
 new=old['new_intent_added_paths']
 if new:git(applied,'add','-N','--force','--',*new)
 replay=git(applied,'diff','--binary','HEAD')
 if replay!=patch:raise RuntimeError('Complete applied/candidate Git deltas differ')
 paths=git(candidate,'diff','--name-only','-z','HEAD').decode().split('\0');byte_proofs=[]
 for name in filter(None,paths):
  a=candidate/name;b=applied/name
  if a.is_symlink():
   if not b.is_symlink() or a.readlink()!=b.readlink():raise RuntimeError('symlink delta differs')
   byte_proofs.append(dict(path=name,type='symlink',target=str(a.readlink())))
  elif a.is_file():
   if not b.is_file() or sha(a)!=sha(b) or bool(a.stat().st_mode&0o111)!=bool(b.stat().st_mode&0o111):raise RuntimeError('file bytes/executable mode differ')
   byte_proofs.append(dict(path=name,type='file',sha256=sha(a),executable=bool(a.stat().st_mode&0o111)))
  elif os.path.lexists(b):raise RuntimeError('deletion differs')
  else:byte_proofs.append(dict(path=name,type='deletion'))
 proof=dict(original_patch_sha256=sha(projection/'model.patch'),original_projection_proof_sha256=sha(projection/'projection-proof.json'),patch_sha256=sha(destination/'model.patch'),captured_tar_sha256=old['captured_tar_sha256'],snapshot_commit=manifest['snapshot_commit'],representation='uniform all-path private * -diff plus Git diff --binary; no source edits or transcoding',complete_git_delta_replay_equal=True,changed_path_byte_mode_proofs=byte_proofs,utf8_readable=True,no_unsafe_path_option=True,model_calls=0,actor_reruns=0,grader_calls=0,runner_sha256=sha(__file__))
 (destination/'binary-proof.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
