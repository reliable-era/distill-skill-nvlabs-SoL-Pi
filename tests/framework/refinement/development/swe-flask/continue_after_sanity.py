"""Explicit continuation after empty-patch control was skipped by official harness. No actor had run."""
import concurrent.futures,json
import run_screen as r
if any((r.OUT/h).exists() for h in ('pi','codex')): raise SystemExit('Actor directory exists; refuse any replay')
plan=json.loads((r.OUT/'plan.json').read_text())
control={'instance_id':'pallets__flask-5014','model_name_or_path':'swe-native-bridge-marker-noop','model_patch':'diff --git a/.solpi_noop_marker b/.solpi_noop_marker\nnew file mode 100644\n--- /dev/null\n+++ b/.solpi_noop_marker\n@@ -0,0 +1 @@\n+Grader sanity only.\n'}
code,reports=r.official([control],'solpi-swe-native-bridge-marker-noop-105')
if code!=0 or not reports: raise RuntimeError('Official marker control failed infrastructure')
report=json.loads(reports[0].read_text()); leaf=report.get('pallets__flask-5014',report)
assert leaf.get('resolved') is False,report
(r.OUT/'bridge-sanity-marker.json').write_text(json.dumps({'exit_code':code,'report':report,'official_report_sha256':r.sha(reports[0]),'correction':'Empty patches are reported as incomplete by swebench; harmless marker control obtains real task grading; zero actors ran before correction'},indent=2)+'\n')
def campaign(harness):
    records=[]
    for arm in plan['order']:
        try: records.append(r.attempt(harness,arm,(r.OUT/(arm+'-prompt.txt')).read_text()))
        except RuntimeError: break
    return records
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    records=sum([f.result() for f in [pool.submit(campaign,h) for h in ('pi','codex')]],[])
(r.OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
for record in records:
    h,a=record['harness'],record['arm']; dest=r.OUT/h/a
    code,reports=r.official([{'instance_id':'pallets__flask-5014','model_name_or_path':f'{h}-{a}','model_patch':(dest/'model.patch').read_text()}],f'solpi-swe-native-{h}-{a}-105')
    if reports:
        report=json.loads(reports[0].read_text()); leaf=report.get('pallets__flask-5014',report)
        record['solved']=leaf.get('resolved'); record['official_report']=str(reports[0].relative_to(r.OUT)); record['official_report_sha256']=r.sha(reports[0])
    elif not (dest/'model.patch').read_text(): record['solved']=False; record['official_empty_patch_rejection']=True
    record['official_harness_exit_code']=code
    (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    (r.OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(record),flush=True)
