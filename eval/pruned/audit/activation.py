#!/usr/bin/env python3
"""Intention-to-treat assignment stays fixed; distinguish tool success and direct body reads."""
import json
from pathlib import Path
def inspect(path):
    calls={};loaded=set();read=set();failed=0;errors=0;first={};index=0
    for line in path.read_text().splitlines():
        try:d=json.loads(line)
        except ValueError:continue
        if d.get('type')=='assistant':
            index+=1
            for c in d.get('message',{}).get('content',[]):
                if c.get('type')=='tool_use':calls[c['id']]=(c,index)
        elif d.get('type')=='user':
            for c in d.get('message',{}).get('content',[]):
                if c.get('type')!='tool_result':continue
                call,idx=calls.get(c.get('tool_use_id'),({},0));inp=call.get('input',{});err=c.get('is_error',False) or '<tool_use_error>' in str(c.get('content',''));errors+=bool(err)
                if call.get('name')=='Skill':
                    if err:failed+=1
                    else:
                        skill=inp.get('skill',inp.get('command'));loaded.add(skill);first.setdefault(skill,idx)
                if call.get('name')=='Read' and not err:
                    p=inp.get('file_path','');body=str(c.get('content',''))
                    if '/.claude/skills/' in p and p.endswith('/SKILL.md') and len(body)>200:
                        skill=p.split('/.claude/skills/')[1].split('/')[0];read.add(skill);first.setdefault(skill,idx)
    return {'successful_skill_tool':sorted(s for s in loaded if s),'successful_direct_skill_body_read':sorted(read),'body_exposed_union':sorted(s for s in loaded|read if s),'first_body_exposure_request':first,'failed_skill_calls':failed,'tool_error_results':errors}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('campaign',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[]
    for result in sorted(a.campaign.glob('dev/*/runs/stress/*/*/r*/result.json')):
        r=json.loads(result.read_text());rows.append({'run':str(result.parent),'label':result.parents[5].name,'case':r['case'],'seed':r['round'],**inspect(result.parent/'stream.jsonl')})
    a.output.write_text(json.dumps(rows,indent=2)+'\n');print(a.output)
