"""Official run_instance with immutable cached image, resource checks and owned cleanup."""
import json,pathlib,sys,os,uuid,hashlib
import docker
from grade_validation import validate_report
from swebench.harness.run_evaluation import run_instance
from swebench.harness.utils import make_test_spec
from swebench.harness.grading import get_logs_eval
from swebench.harness.constants import APPLY_PATCH_FAIL,APPLY_PATCH_PASS,LOG_INSTANCE,LOG_TEST_OUTPUT
root=pathlib.Path(sys.argv[1]);task=json.loads(sys.argv[2]);out=root/'grade';os.chdir(out)
rows=json.loads(pathlib.Path(task['dataset']).read_text());row=next(x for x in rows if x['instance_id']=='pallets__flask-5014');row['image']=task['grader_image_id']
if row.get('image_assets'):raise RuntimeError('external official assets unsupported')
real=docker.from_env(timeout=5);owned=[];proofs=[];errors=[];coverage={};runid=task['grader_run_id']
class Images:
 def get(self,name):
  if name!=task['grader_image_id']:raise RuntimeError('unfrozen grader image')
  image=real.images.get(name)
  if image.id!=name:raise RuntimeError('image mismatch')
  return image
 def pull(self,*a,**k):raise RuntimeError('pull forbidden')
 def build(self,*a,**k):raise RuntimeError('build forbidden')
class Containers:
 def get(self,name):
  if name not in owned:raise docker.errors.NotFound('unowned object cannot be removed')
  return real.containers.get(name)
 def create(self,*a,**kw):
  name=kw.get('name')
  if not name or not name.startswith('sweb.eval.pallets__flask-5014.'+runid):raise RuntimeError('grader ownership')
  if owned:raise RuntimeError('second grader start forbidden')
  owned.append(name);kw.update(network_mode='none',nano_cpus=1000000000,mem_limit='2g',pids_limit=128,cap_add=[],cap_drop=['ALL'],security_opt=['no-new-privileges'])
  c=real.containers.create(*a,**kw);c.reload();h=c.attrs['HostConfig']
  if h['NetworkMode']!='none' or h['Memory']!=2147483648 or h['NanoCpus']!=1000000000 or h['PidsLimit']!=128:raise RuntimeError('official grader resource mismatch')
  proofs.append({'name':name,'image_id':c.attrs['Image'],'network':h['NetworkMode'],'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'pids':h['PidsLimit']});return c
class Client:
 images=Images();containers=Containers()
 api=real.api
try:
 pred={'instance_id':row['instance_id'],'model_name_or_path':'codex-local-qwen-development','model_patch':(root/'model.patch').read_text()}
 (out/'prediction.json').write_text(json.dumps(pred));spec=make_test_spec(row);empty_patch=not bool(pred['model_patch'].strip());result=run_instance(spec,pred,Client(),runid,timeout=180,skip_patch=empty_patch)
 reports=list(out.rglob('report.json'))
 if len(reports)!=1:
  logs=list(out.rglob(LOG_INSTANCE))
  if len(logs)==1 and APPLY_PATCH_FAIL in logs[0].read_text() and not empty_patch:
   (out/'functional-patch-rejection.json').write_text(json.dumps({'solved':False,'classification':'official_patch_application_failed'}))
   solved=False;raise ValueError('functional_patch_rejection')
  raise RuntimeError('official report missing or ambiguous')
 report=json.loads(reports[0].read_text());entry=report.get(row['instance_id'])
 if not isinstance(entry,dict) or type(entry.get('resolved')) is not bool:raise RuntimeError('official resolved missing')
 testlogs=list(out.rglob(LOG_TEST_OUTPUT))
 if len(testlogs)!=1:raise RuntimeError('official test log missing')
 parsed,found=get_logs_eval(spec,str(testlogs[0]));logs=list(out.rglob(LOG_INSTANCE))
 applied=empty_patch or len(logs)==1 and APPLY_PATCH_PASS in logs[0].read_text()
 coverage=validate_report(entry,{'FAIL_TO_PASS':spec.FAIL_TO_PASS,'PASS_TO_PASS':spec.PASS_TO_PASS},parsed,found,empty_patch,applied)
 solved=False if empty_patch else entry['resolved']
except BaseException as e:
 if str(e)=='functional_patch_rejection':solved=False
 else:errors.append({'type':type(e).__name__,'reason':str(e)[:200]});solved=None
finally:
 for name in owned:
  try:real.containers.get(name).remove(force=True)
  except docker.errors.NotFound:pass
  except Exception:errors.append('cleanup_remove')
  try:real.containers.get(name);errors.append('cleanup_remaining')
  except docker.errors.NotFound:proofs.append({'name':name,'absence_verified':True})
  except Exception:errors.append('cleanup_ambiguous')
 artifacts={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
 (out/'result.json').write_text(json.dumps({'solved':solved,'infrastructure_error':errors or None,'test_coverage':coverage,'resource_and_cleanup_proofs':proofs,'artifacts':artifacts},indent=2))
