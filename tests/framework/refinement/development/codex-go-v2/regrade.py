#!/usr/bin/env python3
"""Repair grader-launch infrastructure only; never rerun an actor."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
rows=[]
for p in sorted((HERE/'results').glob('*/result.json')):
 out=p.parent/'regrade.log'
 if out.exists(): raise SystemExit('Existing regrade output; no implicit repeat')
 argv=['docker','run','--rm','--init','--network','none','--cpus','2','--memory','2g','--mount',f'type=bind,src={p.parent / "workspace"},dst=/workspace,readonly','--mount','type=bind,src=/tmp/solpi-polyglot-go-smoke-v2/grader,dst=/grade,readonly','--env','HOME=/tmp','--env','GOCACHE=/tmp/go-cache',IMAGE,'python3','/grade/grade.py']
 r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=190)
 out.write_bytes(r.stdout)
 rows.append({'result':str(p.relative_to(ROOT)),'result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'grader_exit_code':r.returncode,'solved':r.returncode==0 if r.returncode in (0,1) else None,'log_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'argv':argv})
(HERE/'regrade.json').write_text(json.dumps({'reason':'Frozen launch wrapper omitted __file__; original exit 1 was infrastructure NameError, not test rejection. Actor attempts retained unchanged. Direct trusted script launch repairs grader only.','attempts':rows},indent=2)+'\n')
