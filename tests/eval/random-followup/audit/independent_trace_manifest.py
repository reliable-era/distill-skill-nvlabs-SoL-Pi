#!/usr/bin/env python3
"""All-tool backward trace manifest; read-only sources, audit output only."""
import json,pathlib,re,hashlib,collections
P=pathlib.Path
p=json.loads(P('eval/random-followup/audit/independent16.json').read_text());cells=[]
for c in p['cells']:
 run=P(c['run']);tools={};rets={}
 for line in (run/'stream.jsonl').read_text().splitlines():
  d=json.loads(line)
  for b in d.get('message',{}).get('content',[]):
   if b.get('type')=='tool_use':tools[b['id']]=b
   elif b.get('type')=='tool_result':rets[b['tool_use_id']]=b
 entries=[]
 for tid,t in tools.items():
  inp=json.dumps(t.get('input',{}));r=rets.get(tid,{});body=str(r.get('content',''));flags=[]
  if t['name'] in ['WebFetch','WebSearch'] or re.search(r'https?://|\b(?:curl|wget|gh)\b|requests\.|urlopen|urllib|git(?:\s+-\S+(?:\s+\S+)?)*\s+(?:fetch|clone|pull)',inp):flags.append('network_or_web')
  if re.search(r'git(?:\s+-\S+(?:\s+\S+)?)*\s+(?:show|log|diff)|\b(?:diff|cat|sed|grep|head|Read)\b|upstream|v290',inp):flags.append('history_or_read_or_comparison')
  if re.search(r'\b(?:test|tests)[/_-]|test_|pytest',inp) and (t['name'] in ['Edit','Write','MultiEdit'] or re.search(r'write_text|write_bytes|sed -i|cat\s*>|tee\s|\b(?:cp|mv|rm)\b|git(?:\s+-\S+(?:\s+\S+)?)*\s+(?:checkout|restore|reset)',inp)):flags.append('test_write_candidate')
  entries.append({'id':tid,'tool':t['name'],'input':t.get('input',{}),'flags':flags,'return_present':tid in rets,'return_sha256':hashlib.sha256(body.encode()).hexdigest(),'returned_characters':len(body),'is_error':r.get('is_error',False),'returned_diff_or_source':bool(re.search(r'diff --git|^@@|^\d+[acd]\d+|\bdef \w+\(',body,re.M)),'return_excerpt':body[:500] if flags else ''})
 grade=json.loads((run/'graded.json').read_text());rep=P(grade['report_path']);files={f:hashlib.sha256((run/f).read_bytes()).hexdigest() for f in ['result.json','graded.json','initial-checkout.json','stream.jsonl','patch.diff','prompt.txt']};files['prediction']=grade['prediction_sha256']
 if rep.exists():files['official_report']=hashlib.sha256(rep.read_bytes()).hexdigest()
 test=rep.parent/'test_output.txt'
 if test.exists():files['official_test_output']=hashlib.sha256(test.read_bytes()).hexdigest()
 cells.append({'case':c['case'],'arm':c['arm'],'seed':c['seed'],'run':str(run),'files':files,'tools_by_name':dict(collections.Counter(t['name'] for t in tools.values())),'tools':entries,'final_test_files':c['test_files_modified']})
P('eval/random-followup/audit/independent16-trace-manifest.json').write_text(json.dumps({'checked':len(cells),'cells':cells,'interpretation':'All actual tool IDs retained. History/read flags are broad evidence to review; own-tree diffs and base logs do not establish upstream retrieval. Correlate successful returned content with preceding fetch/clone and subsequent local reads. No raw gold dataset content included.'},indent=2)+'\n')
print(json.dumps({'checked':len(cells),'output':'independent-swe32-trace-manifest.json'}))
