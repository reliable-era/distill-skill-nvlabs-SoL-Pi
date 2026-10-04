#!/usr/bin/env python3
"""Reconstruct every saved tracked diff from pinned baseline; official verifier rerun."""
import importlib.util,json,shutil,subprocess,tempfile,hashlib,tarfile,re,uuid
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('screen',OUT/'run_screen.py');screen=importlib.util.module_from_spec(spec);spec.loader.exec_module(screen)
def restore_patch(published, baseline):
 """Resolve digest markers using only public pinned baseline bytes."""
 candidates={}
 for path in baseline.rglob('*'):
  if path.is_file() and '.git' not in path.relative_to(baseline).parts:
   for match in re.finditer(rb'hf_[A-Za-z0-9]{20,}',path.read_bytes()):
    value=match.group();candidates[hashlib.sha256(value).hexdigest().encode()]=value
 def replacement(match):
  digest=match.group(1)
  if digest not in candidates:raise ValueError('Redacted patch token digest absent from pinned public baseline')
  return candidates[digest]
 restored=re.sub(rb'\[REDACTED_HF_TOKEN_([a-f0-9]{64})\]',replacement,published)
 if b'[REDACTED_HF_TOKEN' in restored:raise ValueError('Unresolved patch redaction marker')
 return restored

def main():
 plan=json.loads((OUT/'plan.json').read_text())
 image=subprocess.check_output(['docker','image','inspect',screen.IMAGE,'--format','{{.Id}}'],text=True).strip();assert image==plan['image_id']
 fresh=tempfile.TemporaryDirectory(prefix='terminal-pinned-replay-baseline-')
 base=Path(fresh.name)/'baseline';base.mkdir()
 container='terminal-replay-baseline-'+uuid.uuid4().hex[:12]
 subprocess.run(['docker','create','--name',container,image],check=True,capture_output=True)
 try:subprocess.run(['docker','cp',container+':/app/dclm/.',str(base)],check=True,capture_output=True)
 finally:subprocess.run(['docker','rm',container],check=True,capture_output=True)
 baseline=json.loads((OUT/'baseline-files.json').read_text());actual_base={str(p.relative_to(base)):screen.sha(p) for p in base.rglob('*') if p.is_file()}
 assert {k:v for k,v in actual_base.items() if k!='.git/index'}=={k:v for k,v in baseline.items() if k!='.git/index'}
 staged_before=subprocess.check_output(['git','-c',f'safe.directory={base}','-C',str(base),'ls-files','--stage'])
 with tarfile.open(OUT/'baseline-preparation-delta.tar.gz') as tar:
  assert tar.getnames()==['.git/index']
  tar.extractall(base,filter='data')
 staged_after=subprocess.check_output(['git','-c',f'safe.directory={base}','-C',str(base),'ls-files','--stage']);assert staged_before==staged_after
 actual_base={str(p.relative_to(base)):screen.sha(p) for p in base.rglob('*') if p.is_file()};assert actual_base==baseline
 redactions=json.loads((OUT.parent/'publication-redaction-audit.json').read_text())
 publication={entry['path']:entry for entry in redactions['changes']}
 results=json.loads((OUT/'results.json').read_text());assert len(results)==12
 audits=[];errors=[]
 for r in results:
  dest=OUT/r['harness']/r['arm'];patch=dest/'workspace.patch'
  if not patch.exists():continue
  restored_patch=restore_patch(patch.read_bytes(),base)
  original_patch_sha256=hashlib.sha256(restored_patch).hexdigest()
  assert original_patch_sha256==r['patch_sha256'],f'Original patch hash mismatch {r["harness"]}/{r["arm"]}'
  for artifact in (patch,dest/'stdout.jsonl'):
   key=str(artifact.relative_to(OUT.parent));entry=publication.get(key)
   original_expected=r['patch_sha256' if artifact==patch else 'transcript_sha256']
   if entry:
    assert entry['original_sha256']==original_expected and screen.sha(artifact)==entry['published_sha256']
   else:assert screen.sha(artifact)==original_expected
  with tempfile.TemporaryDirectory(prefix='terminal-regrade-') as td:
   work=Path(td)/'workspace';shutil.copytree(base,work)
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
    restored_path=Path(td)/'restored.patch';restored_path.write_bytes(restored_patch)
    apply=subprocess.run(['git','-C',str(work),'apply',str(restored_path)],capture_output=True)
    if apply.returncode:errors.append({'harness':r['harness'],'arm':r['arm'],'error':'Patch failed to apply'});continue
   output=dest/'replay-verifier';code=screen.grade(work,output)
   if code!=r['grade_exit_code']:errors.append({'harness':r['harness'],'arm':r['arm'],'error':'Official grader disagreement','original':r['grade_exit_code'],'replayed':code})
   audits.append({'harness':r['harness'],'arm':r['arm'],'reconstruction':method,'grade_exit_code':code,'original_patch_sha256':original_patch_sha256,'published_patch_sha256':screen.sha(patch),'original_transcript_sha256':r['transcript_sha256'],'published_transcript_sha256':screen.sha(dest/'stdout.jsonl'),'replay_grade_sha256':screen.sha(output/'grade.txt')})
 (OUT/'replay-audit.json').write_text(json.dumps({'baseline_preparation':'Fresh pinned image differs only in Git index stat-cache. Archived preparation index restores frozen baseline hash; staged entries verified identical before/after.', 'publication_replay':'Digest markers restored only from freshly copied pinned baseline content; original patch SHA256 checked before application. Published transcript hashes checked against redaction audit; original transcript hashes retained as provenance, not reconstructed.', 'attempts':len(results),'replayed':len(audits),'errors':errors,'records':audits,'scope':'Independent full-filesystem delta reconstruction where captured, otherwise tracked-diff replay with Git/untracked completeness unverified; same official tests, no actors/model calls or credentials'},indent=2)+'\n')
 fresh.cleanup()
 assert not errors,errors
if __name__=='__main__':main()
