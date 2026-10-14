"""User-approved G5 control eligibility: official outcomes only.
Original statuses/coverage remain informational. Missing reports, uncertain
cleanup, or official infrastructure/collection failures require infra retry.
"""
import json,pathlib,sys
from common import sha

def judge(directory,iid,official_source):
 directory=pathlib.Path(directory);sys.path.insert(0,official_source)
 from swebench.harness.run_evaluation import LOG_TEST_OUTPUT,LOG_INSTANCE
 from swebench.harness.infra_failure import classify_logs
 reports=list(directory.rglob('report.json'));grade=directory/'grade-result.json'
 if len(reports)!=1 or not grade.exists():return dict(valid_report=False,reason='result_unavailable')
 g=json.loads(grade.read_text())
 if g.get('owned_containers_absent') is not True:return dict(valid_report=False,reason='cleanup_unavailable')
 entry=json.loads(reports[0].read_text()).get(iid,{})
 if type(entry.get('resolved')) is not bool or entry.get('infra_failure') is not False or entry.get('infra_failure_reason'):return dict(valid_report=False,reason='official_infrastructure_failure')
 classification=classify_logs(reports[0].parent/LOG_TEST_OUTPUT,reports[0].parent/LOG_INSTANCE)
 if classification is not None:return dict(valid_report=False,reason='official_collection_or_infrastructure_failure')
 return dict(valid_report=True,resolved=entry['resolved'],report_sha256=sha(reports[0]),grade_artifact_sha256=sha(grade),per_test_requirements_informational_only=True)

def pair(directories,iid,official_source):
 decisions={k:judge(directories[k],iid,official_source) for k in ('nop','gold')};infra=any(not d['valid_report'] for d in decisions.values());eligible=not infra and decisions['gold']['resolved'] is True and decisions['nop']['resolved'] is False
 return dict(task=iid,valid_pair=eligible,category='infrastructure' if infra else ('eligible' if eligible else 'official_outcome_failure'),controls=[dict(kind=k,valid=decisions[k]['valid_report'] and decisions[k].get('resolved') is (k=='gold'),**decisions[k]) for k in ('nop','gold')],model_calls=0)
