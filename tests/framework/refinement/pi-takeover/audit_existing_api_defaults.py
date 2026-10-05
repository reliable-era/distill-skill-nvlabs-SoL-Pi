"""Read-only lexical evidence; no training/config recommendation or causal inference."""
import ast,hashlib,json,pathlib,re,zipfile
R=pathlib.Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def events(data):
 out=[];bad=0
 for line in data.decode().splitlines():
  try:out.append(json.loads(line))
  except ValueError:bad+=1
 return out,bad
def main():
 wheel=pathlib.Path('/tmp/solpi-public-fasttext-39579ce22b/wheels/fasttext-0.9.3-cp313-cp313-linux_x86_64.whl')
 with zipfile.ZipFile(wheel) as z:
  names=[n for n in z.namelist() if n.endswith('/FastText.py')];assert len(names)==1;source=z.read(names[0])
 tree=ast.parse(source);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='train_supervised');updates=[n for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='update'];defaults=ast.literal_eval(updates[0].args[0]);assert 'lr' in defaults
 cases=[('feasible-first',a,'/tmp/solpi-ff16-cecf19ddfc86fa6902') for a in ['candidate','Both','none','K']]+[('measured-feasibility',a,'/tmp/solpi-mf16-7cd69b82b6a7aff8ad') for a in ['candidate','Both']]
 rows=[]
 for stage,arm,root in cases:
  d=pathlib.Path(root)/arm;data=(d/'native.jsonl').read_bytes();ev,bad=events(data);commands=[e['item'].get('command','') for e in ev if e.get('type')=='item.started' and e.get('item',{}).get('type')=='command_execution'];docs=[i for i,c in enumerate(commands) if re.search(r'__doc__|inspect\.|help\(|--help|FastText\.py',c)];decl=[]
  for i,c in enumerate(commands):
   if 'train_supervised' not in c:continue
   vals=re.findall(r'(?:\blr\s*=|[\"\x27]lr[\"\x27]\s*:)\s*([0-9]+(?:\.[0-9]+)?)',c)
   if vals:decl.append({'started_command_index':i,'explicit_declarations':len(vals),'all_match_public_api_default':all(float(v)==defaults['lr'] for v in vals),'any_match_public_api_default':any(float(v)==defaults['lr'] for v in vals)})
  row=json.loads((d/'partial-row.json').read_text());rows.append({'stage':stage,'arm':arm,'native_sha256':sha(data),'original_grade':int(row['reward']) if row.get('official_grade_available') else None,'explicit_source_help_patterns_started_command_indices':docs,'training_source_numeric_learning_rate_declaration_metadata':decl,'nonJSON_native_lines_skipped':bad})
 assert all(not x['explicit_source_help_patterns_started_command_indices'] for x in rows)
 output={'public_wheel_sha256':sha(wheel.read_bytes()),'original_software_source_sha256':sha(source),'source_member':names[0],'rows':rows,'coverage':'lexical explicit command/source declarations only; NOT every implicit doc read, executed config, reason for override, or hidden test accuracy','limitations':['Defaults may violate hard constraints and are not automatically safe.','Overrides may be justified; absence of matched help pattern does not establish absence of knowledge.','Source declarations do not establish all configs executed or submitted.','Historical successful Both is separate evidence, not a current control or reusable grade.','Observed default alignment and grades are association, not causal proof or a task parameter recommendation.'],'numeric_training_values_exported':False,'new_model_POST':0,'actor_training_grading_runs':0,'promotion':False,'goal_complete':False};(R/'existing-api-defaults-audit.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
