#!/usr/bin/env python3
"""Full-state official verifier replay; zero actor/model requests."""
import hashlib,importlib.util,json,shutil,tarfile,tempfile
from pathlib import Path
OUT=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
screen=load('terminal_locate_screen',OUT/'run_screen.py')
restore=load('terminal_publication_restore',OUT.parent/'terminal-sanitize/audit_replay.py')

def main():
 plan=json.loads((OUT/'plan.json').read_text());records=json.loads((OUT/'results.json').read_text());assert len(records)==4
 assert screen.sha(OUT/'baseline-files.json')==plan['baseline_manifest_sha256']
 assert screen.files(screen.TASK)==plan['task_sha256']
 publication=json.loads((OUT/'publication-redaction-audit.json').read_text());entries={r['path']:r for r in publication['changes']}
 outputs=[];errors=[];new_publications=[]
 with tempfile.TemporaryDirectory(prefix='terminal-locate-replay-baseline-') as td:
  base=Path(td)/'baseline';screen.fresh_baseline(base)
  assert screen.files(base)==json.loads((OUT/'baseline-files.json').read_text())
  for record in records:
   if not (OUT/'codex'/record['arm']/'final-state-manifest.json').exists():continue
   dest=OUT/'codex'/record['arm'];manifest=json.loads((dest/'final-state-manifest.json').read_text())
   patch=restore.restore_patch((dest/'workspace.patch').read_bytes(),base)
   assert hashlib.sha256(patch).hexdigest()==record['patch_sha256']
   for artifact,key in [('workspace.patch','patch_sha256'),('stdout.jsonl','transcript_sha256')]:
    path=dest/artifact;entry=entries[str(path.relative_to(OUT))]
    assert screen.sha(path)==entry['published_sha256'] and entry['original_sha256']==record[key]
   with tempfile.TemporaryDirectory(prefix='terminal-locate-replay-state-') as state:
    work=Path(state)/'workspace';shutil.copytree(base,work)
    for relative in manifest['deleted_files']:
     path=work/relative
     if path.exists():path.unlink()
    delta=dest/'final-state-delta.tar.gz';expected=manifest.get('published_delta_sha256',manifest['delta_sha256']);assert screen.sha(delta)==expected
    with tarfile.open(delta) as archive:archive.extractall(work,filter='data')
    for relative in manifest['changed_or_added_files']:
     path=work/relative;data=path.read_bytes()
     if b'[REDACTED_HF_TOKEN' in data:path.write_bytes(restore.restore_patch(data,base))
    assert screen.files(work)==manifest['files_sha256']
    code,published=screen.grade(work,dest/'replay-verifier');new_publications.append(published)
    if code!=record['grade_exit_code']:errors.append({'arm':record['arm'],'original':record['grade_exit_code'],'replayed':code})
    outputs.append({'arm':record['arm'],'replayed_grade_exit_code':code,'original_grade_exit_code':record['grade_exit_code'],'filesystem_byte_hashes_verified':True,'original_patch_sha256_verified':record['patch_sha256'],'published_transcript_sha256_verified':record['published_transcript_sha256']})
 publication['changes']=[entry for entry in publication['changes'] if not entry['path'].endswith('/replay-verifier/grade.txt')]+new_publications;screen.write(OUT/'publication-redaction-audit.json',publication)
 screen.write(OUT/'replay-audit.json',{'actors_launched':0,'original_records':len(records),'replayed':len(outputs),'records':outputs,'errors':errors,'method':'Fresh pinned native task image baseline; full Git/worktree/untracked deltas; digest markers restored only from pinned baseline; original patch and full filesystem hashes verified; unchanged official tests offline without credentials'})
 assert not errors,errors
if __name__=='__main__':main()
