#!/usr/bin/env python3
"""Read-only fresh diagnostic provenance and all-tool trace manifest."""
import json,pathlib,hashlib,re,collections
import collect
P=pathlib.Path
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
plan=json.loads(P('eval/pruned/plan.v3-heldout.json').read_text());v4=json.loads(P('eval/pruned/plan.v4-real-swe.json').read_text());errors=[];pins=[]
for f,h in plan['file_sha256'].items():
 actual=P(f)
 if f in ('/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/eval/run_swe.py','/data/wangjian/wj_code/dl_long/nvlab-sol-pi-skills/eval/pruned/run_campaign.py'):actual=P('eval/pruned/runner-archive/pre-v4')/actual.name
 ok=sha(actual)==h;pins.append({'frozen_path':f,'actual_path':str(actual),'sha256':sha(actual),'verified':ok})
 if not ok:errors.append({'pin':f})
cells=[]
for stage in plan['stages']:
 if stage['kind']!='stress':continue
 for seed in stage['seeds']:
  for case in stage['cases']:
   for label in stage['arms']:
    arm=plan['arms'][label];run=P(plan['campaign_root'])/stage['name']/label/'runs/stress'/case/arm['runner_arm']/f'r{seed}';r=json.loads((run/'result.json').read_text());local=[]
    if r['case']!=case or r['arm']!=arm['runner_arm'] or r['round']!=seed:local.append('identity')
    if r['claude_sha256']!=plan['claude_sha256']:local.append('cli')
    prefixes={'baseline':[],'sol-pi':['efficient-coding'],'karpathy':['karpathy-guidelines'],'karpathy+sol-pi':['efficient-coding','karpathy-guidelines']}[arm['runner_arm']];root=P(arm['skills_root']);expected={str(P(f).relative_to(root)):h for f,h in plan['file_sha256'].items() if P(f).is_relative_to(root) and P(f).relative_to(root).parts[0] in prefixes}
    if r['skill_file_sha256']!=expected:local.append('full_skill_set')
    grade=(run/'grade.txt').read_text();passed=bool(re.search(r'\b\d+ passed\b',grade)) and not re.search(r'\b\d+ failed\b|ERROR collecting',grade)
    if r['resolved']!=(r['grade_exit_code']==0 and passed):local.append('grade_resolution')
    records=[json.loads(x) for x in (run/'stream.jsonl').read_text().splitlines() if x.strip()];terminal=[x for x in records if x.get('type')=='result'];usage=collect.usage(run/'stream.jsonl');tools={};returns={}
    if len(terminal)!=1:local.append('terminal_count')
    if terminal:
     models=terminal[-1].get('modelUsage',{});total=sum(sum(v.get(k,0) for k in ['inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens']) for v in models.values())
     if total!=usage['total_tokens']:local.append('pipeline_usage')
    for d in records:
     for b in d.get('message',{}).get('content',[]):
      if b.get('type')=='tool_use':tools[b['id']]=b
      elif b.get('type')=='tool_result':returns[b['tool_use_id']]=b
    exposures=[];writes=[]
    for tid,t in tools.items():
     inp=json.dumps(t.get('input',{}));body=str(returns.get(tid,{}).get('content',''));kind=t['name']
     if kind in ['WebFetch','WebSearch'] or re.search(r'https?://|\b(?:curl|wget|gh)\b|requests\.|urlopen|urllib|git (?:fetch|clone|pull|show|log|diff)|\bupstream\b',inp):exposures.append({'tool':kind,'input':inp,'return_sha256':hashlib.sha256(body.encode()).hexdigest(),'returned_characters':len(body),'is_error':returns.get(tid,{}).get('is_error',False),'returned_diff_or_source':bool(re.search(r'diff --git|^@@|\bdef \w+\(',body,re.M))})
     if re.search(r'test|pytest',inp,re.I) and (kind in ['Edit','Write','MultiEdit'] or re.search(r'write_text|write_bytes|sed -i|cat\s*>|tee\s|\b(?:cp|mv|rm)\b|git (?:checkout|restore|reset)',inp)):writes.append({'tool':kind,'input':inp,'return_sha256':hashlib.sha256(body.encode()).hexdigest()})
    for e in local:errors.append({'run':str(run),'error':e})
    cells.append({'stage':stage['name'],'case':case,'arm':label,'seed':seed,'run':str(run),'errors':local,'resolved':r['resolved'],'grade_exit_code':r['grade_exit_code'],'grade_timed_out':r['grade_timed_out'],'timed_out':r['timed_out'],'full_skill_files':len(expected),'files':{f:sha(run/f) for f in ['result.json','grade.txt','patch.diff','prompt.txt','stream.jsonl']},'terminal_count':len(terminal),'agent_calls':sum(t['name'] in ['Agent','Task'] for t in tools.values()),'retrieval_and_history_evidence':exposures,'test_write_candidates':writes,**usage})
out={'checked_cells':len(cells),'expected_cells':115,'errors':errors,'historical_pin_manifest':pins,'current_v4_pin_count':len(v4['file_sha256']),'current_v4_pin_errors':[f for f,h in v4['file_sha256'].items() if sha(f)!=h],'cells':cells,'limits':'Diagnostic grade evidence is runner exit plus retained pytest output, not official SWE report. Test-write flags require concrete interpretation; local own-tree history/diffs alone do not establish external repair retrieval. Final147 remains pending.'};P('eval/pruned/audit/independent-diagnostics115-fresh.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checked':len(cells),'errors':errors,'v4_pin_errors':out['current_v4_pin_errors'],'retrieval_history_flags':sum(len(c['retrieval_and_history_evidence']) for c in cells),'test_write_flags':sum(len(c['test_write_candidates']) for c in cells)}))
