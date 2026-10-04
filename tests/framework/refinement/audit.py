#!/usr/bin/env python3
"""Count terminal/start events once; categories are observed strings, not intent."""
import collections, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
TRIALS = ROOT / 'tests/framework/trials'
OUT = Path(__file__).resolve().parent

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def events(p):
    for line in p.read_text().splitlines():
        try: yield json.loads(line)
        except json.JSONDecodeError: continue

def calls(p, harness):
    seen=set()
    for e in events(p):
        name=args=output=None; key=None
        if harness=='pi' and e.get('type')=='tool_execution_start':
            key=e['toolCallId']; name=e['toolName']; args=e['args']
        elif harness=='codex' and e.get('type')=='item.completed':
            d=e['item']; key=d['id']; name=d['type']; args=d.get('command',d.get('changes',{})); output=d.get('aggregated_output')
            if name not in ('command_execution','file_change','mcp_tool_call','web_search'): continue
        elif harness=='copilot' and e.get('type')=='tool.execution_start':
            d=e['data']; key=d['toolCallId'];name=d['toolName'];args=d.get('arguments',{})
        elif harness=='agy' and e.get('event')=='step_update':
            d=e['step_update']
            if d.get('step_type')!='tool' or d['state']!='DONE': continue
            key=d['step_index']; name=d.get('tool_name');args=d.get('tool_info',{}).get('parameters',{});output=d.get('tool_info',{}).get('output')
        elif harness=='cursor' and e.get('type')=='tool_call' and e.get('subtype')=='completed':
            key=e['call_id'];d=e['tool_call'];
            for k,v in d.items():
                if k.endswith('ToolCall') and isinstance(v,dict): name=k;args=v.get('args',{});output=v.get('result');break
        if name and key not in seen:
            seen.add(key);yield {'name':name,'args':args,'output':output}

def main():
    records=[]
    for a in json.loads((TRIALS/'collection.json').read_text())['attempts']:
        parent=(TRIALS/a['source']).parent
        p=parent/('agent.log' if a['harness'] in ('codex','copilot') else 'stdout.jsonl')
        cs=list(calls(p,a['harness'])); counters=collections.Counter()
        # Start events count calls; terminal outputs are collected separately once.
        terminal_outputs=[]; output_ids=set()
        if a['harness'] in ('pi','copilot'):
            for e in events(p):
                if a['harness']=='pi' and e.get('type')=='tool_execution_end':
                    key=e['toolCallId']; value=e.get('result',{}).get('content',[])
                    value=''.join(c.get('text','') for c in value if isinstance(c,dict))
                elif a['harness']=='copilot' and e.get('type')=='tool.execution_complete':
                    d=e['data']; key=d['toolCallId']; value=d.get('result',{}).get('content')
                else: continue
                if key not in output_ids and isinstance(value,str):
                    output_ids.add(key);terminal_outputs.append(value)
        for c in cs:
            s=json.dumps(c['args']);name=c['name'].lower()
            counters['calls']+=1
            counters['explicit_read_calls']+=int(name in ('read','readtoolcall','view','view_file') or bool(re.search(r'\b(cat|sed|head|tail)\b',s)))
            counters['test_command_calls']+=int(bool(re.search(r'\b(pytest|unittest|npm test|cargo test|go test)\b',s)))
            counters['skill_path_calls']+=int('/skills/' in s or '/opt/eval-skill' in s)
            counters['tool_output_chars']+=len(c['output']) if isinstance(c['output'],str) else 0
        # Output unavailable in a start-only schema remains unknown, not zero.
        if a['harness'] in ('pi','copilot'): counters['tool_output_chars']=sum(map(len,terminal_outputs)) if terminal_outputs else None
        if a['harness']=='cursor': counters['tool_output_chars']=None
        records.append({k:a[k] for k in ('harness','arm','task','solved','reported_total_tokens')}|dict(counters)|{'transcript':str(p.relative_to(ROOT)),'sha256':digest(p),'tool_names':dict(collections.Counter(c['name'] for c in cs))})
    controls={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'skills/efficient-coding/SKILL.md', ROOT/'tests/eval/pruned/frozen/latest/karpathy-guidelines/SKILL.md']}
    data={'method':'One observed call event per native tool id/step. Read/test flags match explicit tool names/argument strings and can overlap. They are not a full semantic classification. AGY output often reports a byte/line summary, not actual returned text. Unknown output is null. No token overhead attribution or causality inferred.','controls':controls,'records':records}
    (OUT/'trace-audit.json').write_text(json.dumps(data,indent=2)+'\n')
    rows=['# Native trace audit','',data['method'],'','| Harness | Arm | Calls | Explicit reads | Test commands | Skill-path calls |','|---|---|---:|---:|---:|---:|']
    for h in ('pi','codex','copilot','agy','cursor'):
        for arm in ('none','karpathy','ours','both'):
            rs=[r for r in records if r['harness']==h and r['arm']==arm]
            vals=[sum(r.get(k,0) for r in rs) for k in ('calls','explicit_read_calls','test_command_calls','skill_path_calls')]
            rows.append('| '+h+' | '+arm+' | '+' | '.join(map(str,vals))+' |')
    rows+=['','Counts sum two reused synthetic tasks, one round. Paired per-task records and transcript hashes are in trace-audit.json. Complete token totals remain the trial collector’s responsibility.','', 'The candidate is a development hypothesis only: shorten always-loaded guidance, avoid unnecessary process/output, and retain verification. These traces cannot prove any instruction caused the observed token gap. Do not promote or call it a winner before fresh public benchmark confirmation.']
    (OUT/'README.md').write_text('\n'.join(rows)+'\n')
if __name__=='__main__':main()
