#!/usr/bin/env python3
"""Read-only audit of finished SWE cells; writes only requested audit artifact."""
import argparse,collections,hashlib,json,re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"pruned/audit"))
import collect

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(plan_path,output):
 plan=json.loads(plan_path.read_text());root=Path(plan['campaign_root']);dataset=Path(plan['grade_dataset']);tasks={r['instance_id']:r for r in map(json.loads,dataset.read_text().splitlines())};stage=next(s for s in plan['stages'] if s['name']=='real_swe');errors=[];cells=[]
 for f,h in plan['file_sha256'].items():
  if sha(Path(f))!=h:errors.append({'path':f,'error':'frozen_pin'})
 for seed in stage['seeds']:
  for case in stage['cases']:
   for label in stage['arms']:
    ar=plan['arms'][label];run=root/'real_swe'/label/'runs/swebench'/case/ar['runner_arm']/f'r{seed}';gfile=run/'graded.json'
    if not gfile.exists():continue
    result=json.loads((run/'result.json').read_text());grade=json.loads(gfile.read_text());checkout=json.loads((run/'initial-checkout.json').read_text());local=[]
    if checkout['head']!=tasks[case]['base_commit'] or checkout['base_commit']!=tasks[case]['base_commit'] or checkout['status_porcelain'].strip():local.append('initial_checkout')
    if result['instance_id']!=case or result['arm']!=ar['runner_arm'] or result['round']!=seed:local.append('cell_identity')
    if result['claude_sha256']!=plan['claude_sha256']:local.append('claude_hash')
    skills=Path(ar['skills_root']);prefixes={'baseline':[],'sol-pi':['efficient-coding'],'karpathy':['karpathy-guidelines'],'karpathy+sol-pi':['efficient-coding','karpathy-guidelines']}[ar['runner_arm']]
    expected={str(Path(f).relative_to(skills)):h for f,h in plan['file_sha256'].items() if Path(f).is_relative_to(skills) and Path(f).relative_to(skills).parts[0] in prefixes}
    if result.get('skill_file_sha256',{})!=expected:local.append('full_skill_hash_set')
    if grade.get('dataset_name')!=str(dataset) or grade.get('dataset_sha256')!=sha(dataset):local.append('official_dataset')
    rep=Path(grade['report_path']);work=rep.parents[5];pred=work/'prediction.jsonl'
    if not pred.exists():local.append('prediction_missing')
    else:
     prediction=json.loads(pred.read_text())
     if sha(pred)!=grade['prediction_sha256'] or prediction['instance_id']!=case or prediction['model_patch']!=(run/'patch.diff').read_text():local.append('prediction_provenance')
    if grade['grade_status']=='official_report':
     if not rep.exists() or json.loads(rep.read_text())[case]['resolved']!=grade['resolved']:local.append('official_report')
    elif grade['grade_status']=='empty_patch':
     if (run/'patch.diff').read_text().strip() or grade['resolved'] is not False:local.append('empty_patch_classification')
    elif grade['grade_status']=='infrastructure_error':local.append('grade_infrastructure_error')
    else:local.append('unknown_grade_status')
    usage=collect.usage(run/'stream.jsonl');records=[];tools={};returns={}
    for line in (run/'stream.jsonl').read_text().splitlines():
     try:d=json.loads(line)
     except ValueError:continue
     records.append(d)
     if d.get('type')=='assistant':
      for c in d['message'].get('content',[]):
       if c.get('type')=='tool_use':tools[c['id']]=c
     if d.get('type')=='user':
      for c in d.get('message',{}).get('content',[]):
       if c.get('type')=='tool_result':returns[c.get('tool_use_id')]=c
    terminals=[d for d in records if d.get('type')=='result']
    if usage['usage_complete']:
     if len(terminals)!=1:local.append('terminal_count')
     else:
      mu=terminals[0].get('modelUsage',{});mt=sum(sum(v.get(k,0) for k in ['inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens']) for v in mu.values())
      if mt!=usage['total_tokens']:local.append('terminal_model_usage_mismatch')
    external=[{'tool':c['name'],'url':c['input'].get('url'),'query':c['input'].get('query'),'is_error':returns.get(c['id'],{}).get('is_error',False),'result_prefix':str(returns.get(c['id'],{}).get('content',''))[:180]} for c in tools.values() if c['name'] in ['WebFetch','WebSearch']]
    network=[]
    for c in tools.values():
     if c['name'] in ['WebFetch','WebSearch']:continue
     payload=json.dumps(c.get('input',{}));r=returns.get(c['id'],{});body=str(r.get('content',''))
     if re.search(r'https?://|\b(?:curl|wget|gh)\b|requests\.|urlopen|urllib|git (?:fetch|clone|pull)',payload):
      network.append({'tool':c['name'],'urls':re.findall(r'https?://[^\s\\"<>]+',payload),'input_excerpt':payload[:350],'is_error':r.get('is_error',False),'result_characters':len(body),'result_prefix':body[:650],'returned_source_or_diff_pattern':bool(re.search(r'\bdef \w+\(|^@@|^\d+[acd]\d+',body,re.M))})
    test_write_attempts=[]
    for c in tools.values():
     inp=c.get('input',{});file=inp.get('file_path','');cmd=inp.get('command','');payload=json.dumps(inp)
     direct=c['name'] in ['Edit','Write','MultiEdit'] and any(part in ['test','tests'] or part.startswith(('test_','unittest')) for part in Path(file).parts)
     shell=c['name']=='Bash' and re.search(r'(?:^|[/\s])(?:tests?[/_.-]|unittest)|\bpytest\b',cmd,re.I) and re.search(r'write_text|write_bytes|open\(|sed -i|cat\s*>|tee\s|\b(?:cp|mv|rm)\b|git (?:checkout|restore|reset)',cmd)
     if direct or shell:test_write_attempts.append({'tool':c['name'],'file_path':file,'input_excerpt':payload[:650],'result_is_error':returns.get(c['id'],{}).get('is_error',False),'interpretation':'Potential test-related mutation or regression script; inspect concrete command. This flag does not establish benchmark test alteration.'})
    patchfiles=re.findall(r'^diff --git a/(.*?) b/',(run/'patch.diff').read_text(),re.M);testfiles=[f for f in patchfiles if 'test' in f.split('/') or '/tests/' in '/'+f or Path(f).name.startswith('test')]
    for e in local:errors.append({'run':str(run),'error':e})
    cells.append({'stage':'real_swe','case':case,'arm':label,'seed':seed,'run':str(run),'resolved':grade['resolved'],'grade_status':grade['grade_status'],'timed_out':result['timed_out'],'grade_exit_code':grade['exit_code'],'initial_checkout_verified':'initial_checkout' not in local,'prediction_sha256':grade['prediction_sha256'],'patch_sha256':sha(run/'patch.diff'),'dataset_sha256':sha(dataset),'external_reference_attempts':external,'trace_test_write_attempts':test_write_attempts,'network_tool_attempts':network,'test_files_modified':testfiles,'patch_files':patchfiles,'agent_calls':sum(c['name'] in ['Agent','Task'] for c in tools.values()),'terminal_count':len(terminals),**usage})
 summaries={arm:collect.summary([c for c in cells if c['arm']==arm and isinstance(c['resolved'],bool)]) for arm in stage['arms']}
 report={'plan':str(plan_path),'checked_graded_cells':len(cells),'expected_cells':len(stage['cases'])*len(stage['seeds'])*len(stage['arms']),'errors':errors,'arms_unmatched_partial':summaries,'cells':cells,'cost_warning':'Fallback usage is recorded lower bound; missing terminal output is never fabricated. Partial summaries do not imply comparative efficiency.'};output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checked':len(cells),'errors':errors,'output':str(output)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.plan,a.output)
