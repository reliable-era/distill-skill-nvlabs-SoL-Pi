"""Replay four verified official decisions from retained reports only.
No model,grader,Docker or test execution. Original archived bytes stay unchanged.
Apply after the owned controller drains;save a retained-results resume snapshot.
"""
import datetime,json,pathlib
from common import H,private_root,save,sha
from report_outcome import adjudicate_report
TARGETS={'g5-037-K','g5-112-K','g5-112-Both','g5-171-K'}
def main():
 root=private_root();pid=json.loads((root/'model-resume-v3-handle.json').read_text())['pid'];p=pathlib.Path('/proc')/str(pid)
 if p.exists() and ') Z ' not in (p/'stat').read_text():raise RuntimeError('Wait for clean admission drain;do not overwrite live summary')
 directory=root/'report-adjudication-v1';inspection=json.loads((directory/'inspection.json').read_text());assert {x['cell_id'] for x in inspection}==TARGETS;before=json.loads((root/'model-summary.json').read_text());rows=json.loads(json.dumps(before));byid={x['cell_id']:x for x in rows};changes=[]
 for item in inspection:
  cid=item['cell_id'];d=directory/cid;raw=d/'original-report.json';oldfile=d/'original-grade-result.json';assert sha(raw)==item['official_report_sha256'] and sha(oldfile)==item['original_grade_sha256'];entry=json.loads(raw.read_text())[item['task']];assert entry['resolved'] is False and entry['infra_failure'] is False and 'tests_status' not in entry;original=json.loads(oldfile.read_text());assert entry==original['original_report'];assert original['owned_containers_absent'];row=byid[cid];last=row['attempt_rows'][-1];assert last['attempt']==item['attempt'] and last['grader_sha256']==item['original_grade_sha256'];assert row['solved'] is None and row['grade_valid'] is False
  grade=dict(original);old_errors=grade.get('errors',[]);grade.update(adjudicate_report(entry),errors=[],diagnostic_errors=old_errors,prior_grade_errors=old_errors,adjudication_model_calls=0,grader_reruns=0,source_official_report_sha256=sha(raw));target=d/'adjudicated-grade-result.json';save(target,grade);last.update(solved=grade['solved'],grade_valid=True,original_grader_sha256=last['grader_sha256'],grader_sha256=sha(target),report_adjudication_root=str(d),report_adjudication_model_calls=0,report_adjudication_grader_reruns=0);row.update(solved=grade['solved'],grade_valid=True);changes.append(dict(cell_id=cid,arm=row['arm'],attempt=item['attempt'],solved_before=None,solved_after=False,grade_valid_before=False,grade_valid_after=True,official_report_sha256=sha(raw),corrected_grade_sha256=sha(target)))
 assert [(x['cell_id'],x['requests'],x['known_tokens_lower_bound']) for x in before]==[(x['cell_id'],x['requests'],x['known_tokens_lower_bound']) for x in rows]
 base=json.loads((root/'source-regrade-recovery-v3.json').read_text());allrows={}
 for aa in base['prior_attempt_rows'].values():
  for a in aa:allrows[a['root']]=dict(a)
 for row in rows:
  for a in row['attempt_rows']:allrows[a['root']]=a
 for f in (root/'models-resume-v3').glob('*/g5-*-a*/attempt-result.json'):
  a=json.loads(f.read_text())
  if not a.get('native_started') and a.get('error'):a.update(harness_failure=True,harness_failure_reason='clean deployment drain before native admission')
  allrows.setdefault(a['root'],a)
 done={r['cell_id'] for r in rows};prior={};finished=[]
 for a in allrows.values():
  if a['cell_id'] not in done:prior.setdefault(a['cell_id'],[]).append(a)
  if a.get('native_started') and a.get('started_utc') and a.get('wall_seconds') is not None:
   finished.append(dict(epoch=datetime.datetime.fromisoformat(a['started_utc']).timestamp()+a['wall_seconds'],cell_id=a['cell_id'],attempt=a['attempt'],ended5xx=bool(a.get('ended_on_5xx'))))
 for aa in prior.values():aa.sort(key=lambda a:a['attempt'])
 save(root/'model-summary-before-report-adjudication.json',before);save(root/'model-summary.json',rows);save(root/'report-adjudication-recovery-v4.json',dict(retained_rows=rows,prior_attempt_rows=prior,last16_finished_attempts=sorted(finished,key=lambda x:x['epoch'])[-16:],no_model_calls=True,no_grader_or_test_reruns=True,known_model_costs_unchanged=True,original_archive_bytes_retained=True));save(directory/'corrections.json',changes);summary=dict(changes=changes,corrected_cells=4,same_report_shape_confirmed_for_all4=True,model_calls=0,grader_reruns=0,test_reruns=0,known_tokens_unchanged=True,retained_cells=len(rows),unknown_latest_outcomes_before=sum(x['solved'] is None for x in before),unknown_latest_outcomes_after=sum(x['solved'] is None for x in rows),solves_before=sum(x['solved'] is True for x in before),solves_after=sum(x['solved'] is True for x in rows));save(H/'report-adjudication-summary.json',summary);print('Retained-report adjudication complete',summary,flush=True)
if __name__=='__main__':main()
