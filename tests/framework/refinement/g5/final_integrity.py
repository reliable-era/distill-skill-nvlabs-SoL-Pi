"""Verify retained archives/manifest bindings without exporting private bytes.
Two checksum workers only;no model/grader calls,no reruns or Docker actions.
Archive manifests were byte/mode/link checked before original compression cleanup.
"""
import collections,concurrent.futures,json,pathlib
from common import H,private_root,save,sha

def audit(root):
 root=pathlib.Path(root);index={};archives=[];proof_hashes=[]
 for directory in sorted(root.glob('archives*')):
  for f in sorted(directory.glob('*.proof.json')):
   p=json.loads(f.read_text());assert p['all_regular_bytes_modes_links_verified'];archive=directory/p['archive_name'];assert archive.is_file();archives.append((archive,p['archive_sha256']));proof_hashes.append(sha(f))
   for rel,item in p['regular_file_and_link_manifest'].items():
    if item.get('type')=='file' and pathlib.Path(rel).name in ('native.jsonl','model.patch','capture-proof.json','grade-result.json'):
     key=str(root/p['removed_directory']/rel);assert key not in index or index[key]==item['sha256'];index[key]=item['sha256']
 def check_file(path,expected):
  path=pathlib.Path(path)
  if path.is_file():assert sha(path)==expected,(path,'live hash mismatch');return 'live'
  assert index.get(str(path))==expected,(path,'archive manifest binding mismatch');return 'archive_manifest'
 rows=json.loads((root/'model-summary.json').read_text());assert len(rows)==1776;counts=collections.Counter()
 for r in rows:
  a=r['attempt_rows'][-1];base=pathlib.Path(a['root'])
  for field,name in (('native_sha256','native.jsonl'),('patch_sha256','model.patch'),('capture_proof_sha256','capture-proof.json')):
   assert a.get(field),(r['cell_id'],field);counts[field+'_'+check_file(base/name,a[field])]+=1
  if a.get('report_adjudication_root'):
   f=pathlib.Path(a['report_adjudication_root'])/'adjudicated-grade-result.json';check_file(f,a['grader_sha256']);g=json.loads(f.read_text());assert g['original_report']['resolved'] is r['solved'];check_file(base/'grade/grade-result.json',a['original_grader_sha256']);counts['report_only_correction_grades']+=1
  elif a.get('deterministic_regrade_root'):
   f=pathlib.Path(a['deterministic_regrade_root'])/'grade-result.json';check_file(f,a['grader_sha256']);g=json.loads(f.read_text());assert g['grade_valid'] and g['solved'] is r['solved'];assert g['patch_sha256']==a['graded_patch_sha256'];check_file(base/'grade/grade-result.json',a['pre_source_regrade']['grader_sha256']);counts['source_or_empty_correction_grades']+=1
  else:counts['original_grades_'+check_file(base/'grade/grade-result.json',a['grader_sha256'])]+=1
  assert a['grade_valid'] and a['solved'] is r['solved']
 assert sum(counts[k] for k in counts if k.startswith('original_grades_') or k.endswith('correction_grades'))==1776
 def check_archive(item):
  path,expected=item;actual=sha(path);assert actual==expected,(path,'archive hash mismatch');return dict(archive=path.name,sha256=actual,bytes=path.stat().st_size)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:checked=list(pool.map(check_archive,archives))
 save(root/'final-integrity-private.json',dict(archive_checks=checked,proof_sha256=proof_hashes,latest_cell_binding_counts=dict(counts)));summary=dict(latest_cells=1776,latest_boolean_quality_and_grade_hash_bindings_verified=True,latest_native_patch_capture_hash_bindings_verified=True,latest_cell_binding_counts=dict(counts),archives_rehashed=len(checked),archive_bytes_rehashed=sum(x['bytes'] for x in checked),all_archives_match_creation_hashes=True,original_archive_byte_mode_link_verification_preserved=True,private_integrity_sha256=sha(root/'final-integrity-private.json'),model_calls=0,grader_reruns=0,note='Current archive hashes match hashes recorded after original bytewise manifest verification;latest grade hashes reconcile to manifests or explicit retained no-model corrections. No raw contents exported.');save(H/'final-integrity-summary.json',summary);return summary
if __name__=='__main__':print(json.dumps(audit(private_root()),indent=2),flush=True)
