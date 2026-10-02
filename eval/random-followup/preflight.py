#!/usr/bin/env python3
import importlib.util,json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('campaign',ROOT/'eval/pruned/run_campaign.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
selection=json.loads((OUT/'selection.json').read_text());rows={r['instance_id']:r for r in map(json.loads,(OUT/'selected.jsonl').read_text().splitlines())};reports=[]
for task in selection['tasks']:
 iid=task['instance_id'];name='random-preflight-'+iid.replace('__','-')
 def run(cmd):return subprocess.run(cmd,text=True,capture_output=True,check=True)
 run(['docker','run','-d','--name',name,task['image'],'sleep','infinity'])
 try:
  envcmd=['docker','exec',name,'bash','-c','source /opt/miniconda3/bin/activate testbed && python -c "import sys; print(sys.executable); print(sys.version)"']
  before=run(envcmd).stdout;run(['docker','exec',name,'git','-C','/testbed','reset','--hard',task['base_commit']]);run(['docker','exec',name,'git','-C','/testbed','clean','-fd']);head=run(['docker','exec',name,'git','-C','/testbed','rev-parse','HEAD']).stdout.strip();status=run(['docker','exec',name,'git','-C','/testbed','status','--porcelain']).stdout;after=run(envcmd).stdout;assert head==task['base_commit'] and not status.strip() and before==after
  pristine={'head':head,'status':status,'activated_env_before':before,'activated_env_after':after}
 finally:subprocess.run(['docker','rm','-f',name],capture_output=True)
 gold=OUT/'preflight'/iid/'reference';gold.mkdir(parents=True,exist_ok=True);(gold/'result.json').write_text(json.dumps({'instance_id':iid}));(gold/'patch.diff').write_text(rows[iid]['patch']);print('GOLD START',iid,flush=True);m.grade(gold,OUT/'preflight'/iid/'grading',1800,str(OUT/'selected.jsonl'));graded=json.loads((gold/'graded.json').read_text());reports.append({'instance_id':iid,'pristine':pristine,'gold_grade':graded});(OUT/'preflight-summary.json').write_text(json.dumps(reports,indent=2)+'\n');print('GOLD DONE',iid,graded['resolved'],graded['grade_status'],flush=True)
 if graded.get('resolved') is not True or graded['grade_status']!='official_report':raise RuntimeError('Infrastructure eligibility failed; stop for audit, do not replace using model outcomes')
