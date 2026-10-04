#!/usr/bin/env python3
"""Replay captured states with official graders; never launch actors or models."""
import hashlib,importlib.util,json,shutil,subprocess,tarfile,tempfile
from pathlib import Path
OUT=Path(__file__).resolve().parent

def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
screen=load('acceptance_replay_screen',OUT/'run_screen.py')
restore=load('acceptance_restore',OUT.parent/'terminal-sanitize/audit_replay.py')
patcher=load('acceptance_replay_patch',screen.FAMILIES['go']['adapter'].parent/'frozen/runtime/swe_patch.py')
def main():
 records=json.loads((OUT/'results.json').read_text());assert (OUT/'completion.json').exists(),'Do not replay a live stage'
 assert screen.sha(OUT/'plan.json')==json.loads((OUT/'launch.json').read_text())['plan_sha256']
 outputs=[];errors=[]
 with tempfile.TemporaryDirectory(prefix='acceptance-replay-baselines-') as td:
  fresh=Path(td)/'terminal';old=load('acceptance_terminal_native',screen.FAMILIES['terminal']['adapter']);old.fresh_baseline(fresh)
  assert screen.files(fresh)==json.loads((OUT/'terminal/baseline-files.json').read_text())
  for record in records:
   f,arm=record['family'],record['arm'];dest=OUT/f/'codex'/arm;c=screen.FAMILIES[f];base=fresh if f=='terminal' else c['workspace']
   assert screen.files(base)==json.loads((OUT/f/'baseline-files.json').read_text())
   manifest=json.loads((dest/'final-state-manifest.json').read_text())
   original_patch=restore.restore_patch((dest/'workspace.patch').read_bytes(),base)
   assert hashlib.sha256(original_patch).hexdigest()==record['patch_sha256']
   raw=screen.PRIVATE/dest.relative_to(OUT)/'stdout.jsonl';assert screen.sha(raw)==record['transcript_sha256']
   delta=dest/'final-state-delta.tar.gz' if manifest['public_delta_available'] else screen.PRIVATE/dest.relative_to(OUT)/'final-state-delta.tar.gz'
   assert screen.sha(delta)==manifest['delta_sha256']
   with tempfile.TemporaryDirectory(prefix='acceptance-replay-state-') as sd:
    work=Path(sd)/'workspace';shutil.copytree(base,work)
    for rel in manifest['deleted_files']:
     p=work/rel
     if p.exists():p.unlink()
    with tarfile.open(delta) as archive:archive.extractall(work,filter='data')
    assert screen.files(work)==manifest['files_sha256']
    if f=='terminal':patch=subprocess.check_output(['git','-c',f'safe.directory={work}','-C',str(work),'diff','--binary','d6987af002b122fef54bc0be402062c76488a4d9'])
    else:patch=patcher.snapshot_patch(base,work).encode()
    assert hashlib.sha256(patch).hexdigest()==record['patch_sha256']
    code,solved,detail=screen.grade(f,work,dest/'replay',patch.decode(),'replay-'+f+'-'+arm)
    agrees=code==record['grade_exit_code'] and (record['solved'] is None or solved==record['solved'])
    if not agrees:errors.append({'family':f,'arm':arm,'code':code,'solved':solved})
    outputs.append({'family':f,'arm':arm,'original_solved':record['solved'],'replayed_solved':solved,'original_grade_exit_code':record['grade_exit_code'],'replayed_grade_exit_code':code,'original_patch_and_transcript_sha256_verified':True,'full_git_and_untracked_file_hashes_verified':True,'public_delta_available':manifest['public_delta_available'],'agrees':agrees,**detail})
    print(json.dumps({'family':f,'arm':arm,'replay_agrees':agrees}),flush=True)
 screen.write(OUT/'replay-audit.json',{'actors_launched':0,'records':outputs,'errors':errors,'source_policy':'Terminal baseline freshly extracted from exact pinned native image. Go/Flask reused pinned pristine baselines verified against frozen complete manifests. Full Git plus working/untracked bytes reconstructed from delta and all hashes verified. Digest patches restored only from baseline bytes; original patch/transcript hashes checked. Official graders without auth mounts; no models.'})
 assert not errors
if __name__=='__main__':main()
