"""Read-onlydeliveryaudit:actualmountedskills+promptversusplanandgoal,no inference."""
import hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parent
EXPECTED={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['candidate','karpathy']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(plan_path,root):
 plan_path=pathlib.Path(plan_path);root=pathlib.Path(root);plan=json.loads(plan_path.read_text());frozen=plan['frozen_skills_manifest'];rows=[]
 for arm,keys in EXPECTED.items():
  folder=root/arm/'skills';assert not folder.is_symlink();actual={p.name for p in folder.iterdir()};assert actual==set(keys),(arm,actual,keys)
  prompt=(root/arm/'prompt.txt').read_text();pins={}
  for key in keys:
   for p in (folder/key).rglob('*'):
    assert not p.is_symlink(),'linkedactorresource'
    if p.is_file():
     relative=str(p.relative_to(folder));assert sha(p)==frozen[relative];pins[relative]=sha(p)
   assert {str(p.relative_to(folder)) for p in (folder/key).rglob('*') if p.is_file()}=={name for name in frozen if name.startswith(key+'/')},'deliveredresourceinventorymismatch'
   text=(folder/key/'SKILL.md').read_text();assert prompt.count(text)==1,'missing/repeatedskillprompt'
  for key in {'candidate','original','karpathy'}-set(keys):
   # OnlyclaimabsenceforSKILLblockswhosebytesarenotidenticaltoanallowedblock.
   f=frozen.get(key+'/SKILL.md');assert f is None or f not in pins.values(),'excludedskillduplicate'
  rows.append({'arm':arm,'delivered_skill_keys':sorted(actual),'hashes':pins,'prompt_sha256':sha(root/arm/'prompt.txt'),'goal_delivery_matches':True})
 declared=plan.get('comparator_Both_definition');goal_both='currentcandidate+frozenKarpathy';declaration_match=declared==goal_both
 return {'plan_sha256':sha(plan_path),'root':str(root),'declared_Both':declared,'actual_Both':goal_both,'goal_definition_matches_actual_delivery':True,'declaration_matches_actual_delivery':declaration_match,'protocol_declaration_consistent':declaration_match,'rows':rows,'no_model_calls':True,'historical_manifest_rewritten':False,'goal_complete':False}
if __name__=='__main__':
 panels={'source-backed-financial':('source-backed-financial-plan.json','/tmp/solpi-sbf-4cea54e5b8829ceddc'),'source-backed-doom':('source-backed-doom-plan.json','/tmp/solpi-sbd-20572b2ceffdd55541'),'matched-financial':('matched-financial-plan.json','/tmp/solpi-mf-5382dff1cfe9757893fa')}
 for name,(plan,root) in panels.items():
  value=audit(R/plan,root);(R/(name+'-delivery-audit.json')).write_text(json.dumps(value,indent=2)+'\n');print(name,value['declared_Both'],'ACTUAL',value['actual_Both'],'declaration_consistent',value['declaration_matches_actual_delivery'])
