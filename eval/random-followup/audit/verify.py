"""Fresh verifier independent of actor/grade decisions; no model calls or mutations."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

parser=argparse.ArgumentParser();parser.add_argument('plan',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
plan=json.loads(args.plan.read_text());root=Path(plan['campaign_root']);errors=[];cells=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(ok,message):
 if not ok:errors.append(message)
for path,expected in plan['file_sha256'].items():check(sha(path)==expected,'Pin changed: '+path)
check(sha(plan['claude_bin'])==plan['claude_sha256'],'CLI pin changed')
data={d['instance_id']:d for d in map(json.loads,Path(plan['grade_dataset']).read_text().splitlines())}
evaldir=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('collector',evaldir/'pruned/audit/collect.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
network=re.compile(r'WebFetch|WebSearch|https?://|\bcurl\b|\bwget\b|requests\.(get|post)|urlopen|git\s+(clone|fetch|pull)',re.I)
history=re.compile(r'\bgit\s+(?:[^\n;]*\s)?(show|log|diff)\b|\.patch\b|\.diff\b',re.I)
for stage in plan['stages']:
 for seed in stage['seeds']:
  for case in stage['cases']:
   for label in stage['arms']:
    arm=plan['arms'][label];run=root/stage['name']/label/'runs/swebench'/case/arm['runner_arm']/f'r{seed}'
    if not (run/'graded.json').exists():continue
    key=f'{case}/{label}/{seed}';result=json.loads((run/'result.json').read_text());grade=json.loads((run/'graded.json').read_text());base=json.loads((run/'initial-checkout.json').read_text())
    check(base['head']==data[case]['base_commit'] and not base['status_porcelain'].strip(),key+' nonclean base')
    check(result['claude_sha256']==plan['claude_sha256'],key+' CLI differs')
    names={'baseline':[],'sol-pi':['efficient-coding'],'karpathy':['karpathy-guidelines'],'karpathy+sol-pi':['karpathy-guidelines','efficient-coding']}[arm['runner_arm']]
    skills=Path(arm['skills_root']);expected={str(p.relative_to(skills)):sha(p) for name in names for p in sorted((skills/name).rglob('*')) if p.is_file()}
    check(result['skill_file_sha256']==expected,key+' activated skill set differs')
    check(grade['dataset_sha256']==sha(plan['grade_dataset']),key+' grade dataset differs')
    work=root/'grading'/stage['name']/label/f'{case}-{seed}';prediction=work/'prediction.jsonl';pred=json.loads(prediction.read_text())
    check(sha(prediction)==grade['prediction_sha256'],key+' prediction hash differs')
    check(pred['instance_id']==case and pred['model_patch']==(run/'patch.diff').read_text(),key+' prediction differs from final patch')
    report_hash=None;test_output_hash=None;test_counts=None
    if grade['grade_status']=='official_report':
     report=Path(grade['report_path']);r=json.loads(report.read_text())[case];check(r['patch_successfully_applied'] and r['resolved']==grade['resolved'],key+' official mismatch');report_hash=sha(report)
     output=report.parent/'test_output.txt';check(output.exists(),key+' missing test output');test_output_hash=sha(output) if output.exists() else None
     test_counts={k:{'pass':len(v['success']),'fail':len(v['failure'])} for k,v in r['tests_status'].items()}
    elif grade['grade_status']=='empty_patch':check(not pred['model_patch'].strip() and grade['resolved'] is False,key+' invalid empty grade')
    else:check(False,key+' infrastructure grade')
    records=[]
    for number,line in enumerate((run/'stream.jsonl').read_text().splitlines(),1):
     try:records.append((number,json.loads(line)))
     except ValueError:continue
    uses={};returns={}
    for number,d in records:
     content=(d.get('message') or {}).get('content',[])
     if not isinstance(content,list):continue
     for c in content:
      if c.get('type')=='tool_use':uses[c['id']]={'line':number,'name':c['name'],'input':c.get('input',{})}
      elif c.get('type')=='tool_result':returns[c['tool_use_id']]={'line':number,'is_error':c.get('is_error',False),'content':c.get('content')}
    flags=[];agent_calls=[];test_writes=[]
    for tid,u in uses.items():
     text=json.dumps(u['input']);name=u['name'];ret=returns.get(tid,{})
     if network.search(name+' '+text) or history.search(text):flags.append({'tool_id':tid,**u,'result_line':ret.get('line'),'result_is_error':ret.get('is_error'),'result_chars':len(str(ret.get('content',''))),'flag':'network_or_history_review'})
     if name in ['Agent','Task']:agent_calls.append(tid)
     if name in ['Edit','Write','MultiEdit'] and re.search(r'tests?[/_]|test_',text):test_writes.append({'tool_id':tid,**u})
    cells.append({'case':case,'arm':label,'seed':seed,'resolved':grade['resolved'],'grade_status':grade['grade_status'],'model_timeout':result['timed_out'],'model_exit':result['exit_code'],'wall_s':result['wall_s'],'patch_bytes':result['patch_bytes'],'usage':collector.usage(run/'stream.jsonl'),'prediction_sha256':sha(prediction),'report_sha256':report_hash,'test_output_sha256':test_output_hash,'test_counts':test_counts,'stream_sha256':sha(run/'stream.jsonl'),'tool_count':len(uses),'network_history_review':flags,'test_write_tool_review':test_writes,'agent_call_ids':agent_calls})
out={'checked_cells':len(cells),'planned_cells':16,'errors':errors,'plan_sha256':sha(args.plan),'pins_checked':len(plan['file_sha256']),'verification_author':'root-run standalone verifier; independent agent review available for prelaunch and first cell only unless separately resumed','cells':cells,'limits':['Flagged network/history calls require manual returned-content review; tool absence alone is not a complete exposure claim.','Incomplete token usage remains lower bounds, not zero output or measured savings.','Two easy distinct-repo tasks; no broad superiority inference.']}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print('Verified',len(cells),'cells; errors:',errors)
