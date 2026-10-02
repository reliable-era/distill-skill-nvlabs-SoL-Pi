#!/usr/bin/env python3
"""Infrastructure preflight only. Gold patches never enter model run directories."""
import hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('campaign',E/'pruned/run_campaign.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows={r['instance_id']:r for r in map(json.loads,(E/'swebench_verified.jsonl').read_text().splitlines())}
selection=json.loads((Path(__file__).parent/'selection.json').read_text())
root=Path(__file__).parent/'grader-preflight';root.mkdir(exist_ok=True)
out=[]
for item in selection['tasks']:
    iid=item['instance_id'];run=root/iid/'reference';run.mkdir(parents=True,exist_ok=True)
    (run/'result.json').write_text(json.dumps({'instance_id':iid}))
    (run/'patch.diff').write_text(rows[iid]['patch'])
    print('START',iid,flush=True)
    m.grade(run,root/iid/'grading',1800)
    report=json.loads((run/'graded.json').read_text())
    out.append({'instance_id':iid,'patch_sha256':hashlib.sha256((run/'patch.diff').read_bytes()).hexdigest(),**report})
    (root/'summary.json').write_text(json.dumps({'purpose':'Official grader infrastructure preflight; reference results are not model performance. Empty predictions are skipped by official harness and counted unresolved; that alone is not a measured test execution on original source.','reference_runs':out},indent=2)+'\n')
    print('DONE',iid,report.get('resolved'),report.get('grade_status'),round(report.get('wall_s',0)),flush=True)
print('COMPLETE',str(root/'summary.json'),flush=True)
