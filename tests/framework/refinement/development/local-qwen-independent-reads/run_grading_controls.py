"""Separately authorized baseline/gold verifier controls. No model/actor entrypoint."""
import argparse,hashlib,json,pathlib,shutil,subprocess,sys,uuid,os,signal
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'runtime'));import wrapper as W
from grade_validation import validate_swe_control
sha=W.sha

def setup_terminal(root,task,solution):
 name='solpi-qwendev-oracle-'+uuid.uuid4().hex[:12];z=None;cleanup=False
 command=['docker','create','--pull=never','--name',name,'--network','none','--user',str(os.getuid())+':'+str(os.getgid()),'-e','HOME=/tmp/oracle-home','--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(root/'work')+':/app/dclm','-v',str(solution)+':/solution:ro','-w','/app/dclm','--entrypoint','/bin/bash',task['image_id'],'-c','mkdir -p "$HOME" && exec /bin/bash /solution/solve.sh']
 try:
  subprocess.run(command,capture_output=True,check=True,timeout=10)
  q=json.loads(subprocess.check_output(['docker','inspect',name],timeout=5))[0];h=q['HostConfig']
  if q['Config'].get('User')!=str(os.getuid())+':'+str(os.getgid()) or h['NetworkMode']!='none' or h['Memory']!=2147483648 or h['NanoCpus']!=1000000000 or h['PidsLimit']!=128:raise RuntimeError('oracle resources')
  (root/'oracle-resource-inspect.json').write_text(json.dumps(q))
  with (root/'oracle.stdout').open('wb') as out,(root/'oracle.stderr').open('wb') as err:z=subprocess.run(['docker','start','-a',name],stdout=out,stderr=err,timeout=60)
  if z.returncode!=0:raise RuntimeError('oracle setup failed')
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=5)
  q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
  cleanup=q.returncode!=0 and q.stderr.strip() in ('Error: No such object: '+name,'Error response from daemon: No such container: '+name)
  (root/'oracle-cleanup.json').write_text(json.dumps({'name':name,'absence_verified':cleanup}))
  if not cleanup:raise RuntimeError('oracle cleanup uncertain')
def validate(plan,digest):
 if plan.get('control_uid')!=os.getuid() or plan.get('control_gid')!=os.getgid() or plan.get('combined_maximum_official_verifiers')!=7 or plan.get('combined_maximum_oracle_setups')!=2:raise RuntimeError('combined control identity/caps')
 if plan['maximum_official_controls']!=6 or plan['maximum_oracle_setups']!=1 or plan['native_starts']!=0 or plan['provider_POST']!=0:raise RuntimeError('control caps')
 if sha(R/'plan.json')!=plan['screen_plan_sha256']:raise RuntimeError('screen plan changed')
 screen=json.loads((R/'plan.json').read_text());W.validate_inputs(screen)
 for name,h in plan['source_hashes'].items():
  if sha(R/name)!=h:raise RuntimeError('control source changed')
 for name,pins in plan['gold_source_hashes'].items():
  if W.files(name)!=pins:raise RuntimeError('trusted gold source changed')
 auth=json.loads((R/'grading-authorization.json').read_text())
 if auth.get('plan_sha256')!=digest or auth.get('maximum_controls')!=6:raise RuntimeError('grading authorization absent')
 return screen

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute-grading-controls',action='store_true');parser.add_argument('--plan-sha256',required=True);a=parser.parse_args();digest=sha(R/'grading-plan.json')
 if not a.execute_grading_controls or a.plan_sha256!=digest:raise SystemExit('exact control plan required')
 p=json.loads((R/'grading-plan.json').read_text());screen=validate(p,digest)
 root=pathlib.Path('/tmp')/('solpi-qwendev-controls-'+digest);root.mkdir(mode=0o700,exist_ok=False);(root/'launch.json').write_text(json.dumps({'plan':digest,'models':0}));results=[];errors=[]
 try:
  for family in ['terminal','go','swe']:
   task=screen['tasks'][family]
   for kind in ['baseline','gold']:
    cell=root/(family+'-'+kind);cell.mkdir(mode=0o700);shutil.copytree(task['baseline'],cell/'work',symlinks=True)
    if family=='swe':
     dataset=json.loads(pathlib.Path(task['dataset']).read_text());row=next(x for x in dataset if x['instance_id']==task['task']);(cell/'model.patch').write_text(row['patch'] if kind=='gold' else '')
    elif kind=='gold':
     if family=='terminal':setup_terminal(cell,task,p['terminal_gold'])
     else:
      manifest=json.loads((R/'frozen/go-grader/manifest.json').read_text())
      for name in manifest['solution_files']:shutil.copy2(pathlib.Path(p['go_gold'])/name,cell/'work'/name)
    row={'family':family,'kind':kind,'expected':kind=='gold','grade_started':True};results.append(row)
    (root/'partial-evidence.json').write_text(json.dumps({'controls':results,'errors':errors}))
    grade=W.grade(cell,task);row['grade']=grade
    if family=='swe':row['strict_original_test_control_validated']=validate_swe_control(grade,kind)
    row['expected_matched']=grade.get('solved') is row['expected'] and not grade.get('infrastructure_error')
    if not row['expected_matched']:raise RuntimeError('control outcome or infrastructure failure')
 except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e)[:200]})
 finally:
  evidence={'plan_sha256':digest,'controls':results,'errors':errors,'native_starts':0,'POST':0,'prior_infrastructure_attempts':p['prior_infrastructure_attempts'],'combined_official_verifiers':1+len(results),'combined_oracle_setups':2 if (root/'terminal-gold/oracle-resource-inspect.json').exists() else 1,'success':len(results)==6 and not errors and all(x.get('expected_matched') for x in results),'private':True}
  (root/'final-evidence.json').write_text(json.dumps(evidence,indent=2));print(json.dumps({'private_root':str(root),'completed':len(results),'success':evidence['success'],'errors':len(errors)}))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
