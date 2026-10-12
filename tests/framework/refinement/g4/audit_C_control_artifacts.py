"""Original AND uniform offline C controls: immutable logs/resources/absence.
No reruns/calls; failures/exclusions are preserved, never treated as valid tests.
For valid controls, independently check original reported test-set coverage.
"""
import json,pathlib,subprocess
from native import H,sha
from transport import save

def main():
 plan=json.loads((H/'C-controls-plan.json').read_text());dataset=pathlib.Path(plan['private_dataset']);assert sha(dataset)==plan['private_dataset_sha256'];tasks={t['instance_id']:t for t in json.loads(dataset.read_text())};proofs=[];errors=[];eligible=json.loads((H/'C-eligibility.json').read_text())['rows'];eligibility={r['task']:r['eligible'] for r in eligible}
 for path,digest in plan['official_source_hashes'].items():assert sha(path)==digest
 for campaign,filename in [('original','C-controls-result.json'),('uniform_offline','C-controls-offline-result.json')]:
  summary=json.loads((H/filename).read_text());assert len(summary['rows'])==30 and {r['task'] for r in summary['rows']}==set(plan['tasks'])
  for row in summary['rows']:
   bad=[];task=tasks[row['task']]
   if row['model_calls']!=0 or row['image_id']!=plan['images'][row['task']]:bad.append('source image/model-free identity')
   if len(row['controls'])!=2 or {c['kind'] for c in row['controls']}!={'nop','gold'}:bad.append('paired original controls missing')
   if row['valid_pair']!=all(c['valid'] for c in row['controls']):bad.append('pair eligibility mismatch')
   if campaign=='uniform_offline' and eligibility[row['task']]!=row['valid_pair']:bad.append('failed-control-only exclusion mismatch')
   for c in row['controls']:
    directory=pathlib.Path(c['private_root']);owned=json.loads((directory/'owned.json').read_text())['names'];ins=json.loads((directory/'container-inspect.json').read_text());host=ins['HostConfig']
    if not (ins['Image']==row['image_id'] and host['NetworkMode']=='none' and host['Memory']==8*1024**3 and host['NanoCpus']==1000000000 and host['PidsLimit']==512 and not host['Privileged'] and not host.get('DeviceRequests')):bad.append('original control resource regime')
    for relative,digest in c['artifacts'].items():
     if sha(directory/relative)!=digest:bad.append('original control artifact changed:'+relative)
    if campaign=='uniform_offline' and not any(m['Destination']=='/wheelhouse' and not m['RW'] for m in ins['Mounts']):bad.append('uniform readonly wheel environment')
    for name in owned:
     if not name.startswith('sweb.eval.'+row['task'].lower()+'.g4-'):bad.append('unowned control name');continue
     gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20)
     if gone.returncode==0 or 'No such' not in gone.stderr:bad.append('actual owned control absence')
    if c['valid']:
     reports=list(directory.rglob('report.json'))
     if len(reports)!=1:bad.append('original report unavailable');continue
     report=json.loads(reports[0].read_text())[row['task']]
     for category in ('FAIL_TO_PASS','PASS_TO_PASS'):
      expected=task[category];expected=json.loads(expected) if isinstance(expected,str) else expected;detail=report['tests_status'][category];actual=detail['success']+detail['failure'];coverage=c['coverage'][category]
      if len(actual)!=len(expected) or set(actual)!=set(expected) or coverage['expected']!=len(expected) or coverage['passed']+coverage['failed']!=len(expected):bad.append('full original expected-test coverage')
     if c['kind']=='gold' and (not report['resolved'] or not report['patch_successfully_applied'] or c['coverage']['FAIL_TO_PASS']['failed']):bad.append('original gold resolve')
     if c['kind']=='nop' and (report['resolved'] or not c['coverage']['FAIL_TO_PASS']['failed']):bad.append('original no-op failure')
     if c['coverage']['PASS_TO_PASS']['failed']:bad.append('original P2P regression')
   if bad:errors.append(dict(campaign=campaign,task=row['task'],checks=bad))
   proofs.append(dict(campaign=campaign,task=row['task'],valid_pair=row['valid_pair'],control_validity={c['kind']:c['valid'] for c in row['controls']},original_failures={c['kind']:c.get('error') for c in row['controls'] if not c['valid']},owned_containers=sum(len(json.loads((pathlib.Path(c['private_root'])/'owned.json').read_text())['names']) for c in row['controls']),all_checks_passed=not bad))
 result=dict(proofs=proofs,errors=errors,all_original_control_evidence_verified=not errors,eligible_tasks=sum(eligibility.values()),excluded_tasks=30-sum(eligibility.values()),model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/'C-control-artifact-audit.json',result);print('Original/offline control pairs',len(proofs),'owned containers',sum(r['owned_containers'] for r in proofs),'errors',errors)
if __name__=='__main__':main()
