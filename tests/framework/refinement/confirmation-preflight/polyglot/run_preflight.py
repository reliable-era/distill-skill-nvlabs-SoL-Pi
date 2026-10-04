"""Private gold/pristine controls only, never actor calls or solution export."""
import json,pathlib,subprocess,hashlib,importlib.util,uuid
ROOT=pathlib.Path(__file__).resolve().parents[5];SOURCE=pathlib.Path('/tmp/solpi-polyglot-grader-source');IMAGE='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
spec=importlib.util.spec_from_file_location('polyglot',ROOT/'tests/framework/benchmarks/polyglot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
selection=ROOT/'tests/framework/refinement/confirmation-selection.json';tasks=[t['id'] for t in json.loads(selection.read_text())['selected_tasks'] if t['benchmark']=='aider-polyglot'];private=pathlib.Path('/tmp')/('solpi-sealed-polyglot-preflight-v2-'+uuid.uuid4().hex[:8]);private.mkdir();rows=[]
for task in tasks:
 image=IMAGE if task.startswith('go/') else subprocess.check_output(['docker','image','inspect','--format','{{.Id}}','sol-pi-eval-polyglot-java-login:2026-10-04' if task.startswith('java/') else 'sol-pi-simplecipher-cache:2026-10-04' if task.startswith('rust/') else 'sol-pi-eval-polyglot-multilingual-login:2026-10-04'],text=True).strip()
 out=private/task.split('/')[0];manifest=m.prepare(SOURCE,task,out);row={'task':task,'private_preparation':str(out),'image_id':image,'manifest':manifest,'manifest_sha256':m.digest(out/'manifest.json'),'actor_file_hashes':{str(p.relative_to(out/'workspace')):m.digest(p) for p in sorted((out/'workspace').rglob('*')) if p.is_file()},'controls':{}}
 controls = [('unchanged',out/'workspace'),('reference',out/'reference')]
 if manifest.get('reference_auxiliary_files'): controls.append(('reference_without_auxiliary_overlay',out/'reference'))
 for mode,workspace in controls:
  cmd=['docker','run','--rm','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--user','0','--read-only','--tmpfs','/tmp:rw,exec,size=1g','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','--entrypoint','python3','-v',str(workspace)+':/workspace:ro','-v',str(out/'grader')+':/grader:ro',image,'/grader/grade.py']
  if mode=='reference':cmd.append('--reference-control')
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=300);log=pathlib.Path(__file__).parent/(task.split('/')[0]+'-'+mode+'.log');log.write_text(r.stdout+r.stderr);row['controls'][mode]={'exit_code':r.returncode,'log_sha256':m.digest(log),'docker_command':cmd,'classification':'pass' if r.returncode==0 else 'quality_rejection' if r.returncode==1 else 'infrastructure_error'}
 rows.append(row)
report={'private_root':str(private),'selected_metadata_sha256':m.digest(selection),'image_id':IMAGE,'source_revision':m.REVISION,'harness_revision':m.HARNESS_REVISION,'source_hashes':{f:m.digest(ROOT/'tests/framework/benchmarks'/f) for f in ['polyglot.py','polyglot_grade.py','polyglot_cpp_test.sh']},'protocol':'Native single attempt, withheld tests, offline official grading; private gold control overlays auxiliary reference sources explicitly. Default grading never overlays private helper sources. No actor/model calls or canonical edits.','rows':rows}
(pathlib.Path(__file__).parent/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'task':r['task'],'controls':r['controls']} for r in rows]))
