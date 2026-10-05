"""Actual hashed provider requests: delivery/role persistence, not cognitive adherence."""
import pathlib,json,hashlib,re
from uniform_budget_notice import NOTICE
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-db16-703569da7d9b953094');D=R.parent/'development/pi-takeover-qwen-documented-baseline-admission-16k'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def texts(q):
 return [(x.get('role'),c['text']) for x in q['input'] if x.get('type')=='message' for c in x.get('content',[]) if isinstance(c,dict) and isinstance(c.get('text'),str)]
def main():
 plan=json.loads((R/'documented-baseline-fasttext-plan.json').read_text());ledger=json.loads((ROOT/'transport/ledger.json').read_text());rows=[];pins={};clause='For an existing tool or library, start from its documented idiomatic baseline; override defaults only to meet requirements or respond to observed evidence.'
 for arm in plan['schedule']:
  records=[x for x in ledger['records'] if x['actor']==arm];prompt=(ROOT/arm/'prompt.txt').read_text();keys=plan['arm_recipe'][arm];requests=[]
  for receipt in records:
   p=ROOT/'transport'/f"request-{receipt['request']}.json";h=sha(p);assert h==receipt['request_sha256'];pins[str(p.relative_to(ROOT))]=h;q=json.loads(p.read_text());ts=texts(q);assert sum(prompt in s for _,s in ts)==1;skill_roles={}
   for k in keys:
    s=(D/'frozen'/k/'SKILL.md').read_text();roles=[role for role,t in ts if s in t];assert roles==['user'];skill_roles[k]=roles
   requests.append({'request':receipt['request'],'full_prompt_exact_once':True,'skill_roles':skill_roles,'baseline_clause_present_in_prompt':clause in prompt,'higher_priority_stock_instructions_bytes':len(q['instructions'].encode()),'developer_message_bytes':sum(len(s.encode()) for role,s in ts if role=='developer'),'full_prompt_bytes':len(prompt.encode()),'explicit_CPU_memory_PID_limit_in_first_message_texts':bool(re.search(r'(?i)(?:1\s*CPU|CPU\s*[:=]\s*1|4096\s*MiB|pids?\s*[:=]\s*128)', '\n'.join(s for _,s in ts))) if receipt==records[0] else None,'uniform_time_POST_notice_present':NOTICE in prompt})
  native=(ROOT/arm/'native.jsonl').read_bytes();ev=[]
  for l in native.decode().splitlines():
   try:ev.append(json.loads(l))
   except ValueError:pass
  cmds=[e['item'].get('command','') for e in ev if e.get('type')=='item.started' and e.get('item',{}).get('type')=='command_execution'];pins[str((ROOT/arm/'native.jsonl').relative_to(ROOT))]=hashlib.sha256(native).hexdigest();rows.append({'arm':arm,'requests':requests,'matched_explicit_doc_help_source_command_indices':[i for i,c in enumerate(cmds) if re.search(r'__doc__|inspect\.|help\(|--help|FastText\.py',c)],'host_capacity_commands_observed':any('nproc' in c for c in cmds),'original_grade':0})
 assert sum(len(x['requests']) for x in rows)==63;assert all(x['requests'][0]['baseline_clause_present_in_prompt']==(x['arm'] in ['candidate','Both']) for x in rows)
 out={'terminal_metadata_readonly':True,'plan_sha256':sha(R/'documented-baseline-fasttext-plan.json'),'POST':63,'all_actual_request_body_hashes_verified':True,'full_prompt_and_skills_persisted_each_request':True,'skills_in_user_role_not_stock_developer_instructions':True,'uniform_notice_scope':'time/POST only; does not disclose selected CPU/memory/PID numbers','rows':rows,'limitations':['Byte counts are not Qwen token counts or causal overhead.','Higher-priority text volume does not prove a conflicting instruction or cognitive cause.','Actual delivery does not prove adherence; lexical help matching does not cover implicit knowledge.','First-message absence of explicit limits is not proof limits could not be discovered in the actor environment.','No inference that disclosure or parallelism changes will improve original quality.'],'artifact_hashes':pins,'new_model_POST':0,'new_actor_training_grading':0,'promotion':False,'goal_complete':False};(R/'provider-visible-skill-priority-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['rows','artifact_hashes']},indent=2));print([(x['arm'],len(x['requests']),x['matched_explicit_doc_help_source_command_indices'],x['requests'][0]['explicit_CPU_memory_PID_limit_in_first_message_texts']) for x in rows])
if __name__=='__main__':main()
