#!/usr/bin/env python3
"""Reconstruct every saved tracked diff from pinned baseline; official verifier rerun."""
import importlib.util,json,shutil,subprocess,tempfile,hashlib,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('screen',OUT/'run_screen.py');screen=importlib.util.module_from_spec(spec);spec.loader.exec_module(screen)
def main():
 plan=json.loads((OUT/'plan.json').read_text())
 image=subprocess.check_output(['docker','image','inspect',screen.IMAGE,'--format','{{.Id}}'],text=True).strip();assert image==plan['image_id']
 baseline=json.loads((OUT/'baseline-files.json').read_text());actual_base={str(p.relative_to(Path('/tmp/solpi-terminal-baseline'))):screen.sha(p) for p in Path('/tmp/solpi-terminal-baseline').rglob('*') if p.is_file()};assert actual_base==baseline
 results=json.loads((OUT/'results.json').read_text());assert len(results)==12
 audits=[];errors=[]
 for r in results:
  dest=OUT/r['harness']/r['arm'];patch=dest/'workspace.patch'
  if not patch.exists():continue
  with tempfile.TemporaryDirectory(prefix='terminal-regrade-') as td:
   work=Path(td)/'workspace';shutil.copytree('/tmp/solpi-terminal-baseline',work)
   manifest=dest/'final-state-manifest.json'
   method='full-filesystem-delta' if manifest.exists() else 'tracked-diff-only'
   if manifest.exists():
    m=json.loads(manifest.read_text())
    if m.get('missing_captured_files'):method='full-history-filesystem-delta-with-index-uncaptured'
    for path in m['deleted_files']:
     f=work/path
     if f.exists():f.unlink()
    with tarfile.open(dest/'final-state-delta.tar.gz') as tar:tar.extractall(work,filter='data')
    actual={str(p.relative_to(work)):screen.sha(p) for p in work.rglob('*') if p.is_file()}
    actual={k:v for k,v in actual.items() if k not in m.get('missing_captured_files',[])}
    assert actual==m['files_sha256'],f'Filesystem hash mismatch {r["harness"]}/{r["arm"]}'
   elif patch.stat().st_size:
    apply=subprocess.run(['git','-C',str(work),'apply',str(patch.resolve())],capture_output=True)
    if apply.returncode:errors.append({'harness':r['harness'],'arm':r['arm'],'error':'Patch failed to apply'});continue
   output=dest/'replay-verifier';code=screen.grade(work,output)
   if code!=r['grade_exit_code']:errors.append({'harness':r['harness'],'arm':r['arm'],'error':'Official grader disagreement','original':r['grade_exit_code'],'replayed':code})
   audits.append({'harness':r['harness'],'arm':r['arm'],'reconstruction':method,'grade_exit_code':code,'patch_sha256':screen.sha(patch),'transcript_sha256':screen.sha(dest/'stdout.jsonl'),'replay_grade_sha256':screen.sha(output/'grade.txt')})
 (OUT/'replay-audit.json').write_text(json.dumps({'attempts':len(results),'replayed':len(audits),'errors':errors,'records':audits,'scope':'Independent full-filesystem delta reconstruction where captured, otherwise tracked-diff replay with Git/untracked completeness unverified; same official tests, no actors/model calls or credentials'},indent=2)+'\n')
 assert not errors,errors
if __name__=='__main__':main()
