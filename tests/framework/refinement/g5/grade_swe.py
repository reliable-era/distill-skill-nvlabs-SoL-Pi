"""G5 original official SWE grading of a captured patch, no agent/model calls.
Same source/images/base/cache/resources as prospective C controls. Unmodified
run_instance; retain original report/logs, explicit unknowns and owned cleanup.
"""
import hashlib,json,os,pathlib,sys,uuid
H=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2)+'\n')
def grade(root,iid,patch_file,plan):
 root=pathlib.Path(root);root.mkdir(mode=0o700);patch_file=pathlib.Path(patch_file)
 if patch_file.is_symlink() or not patch_file.is_file():raise RuntimeError('Regular captured patch required')
 for p,d in plan['official_source_hashes'].items():
  if sha(p)!=d:raise RuntimeError('Original official grader changed')
 for name,d in plan['wheel_sha256'].items():
  if sha(pathlib.Path(plan['wheelhouse'])/name)!=d:raise RuntimeError('Frozen offline wheel changed')
 if sha(plan['private_dataset'])!=plan['private_dataset_sha256']:raise RuntimeError('Frozen task dataset changed')
 task=next(r for r in json.loads(pathlib.Path(plan['private_dataset']).read_text()) if r['instance_id']==iid);image=plan['images'][iid];task=dict(task,image=image);sys.path.insert(0,plan['official_source'])
 import docker
 from swebench.harness.utils import make_test_spec
 from swebench.harness.run_evaluation import run_instance,LOG_INSTANCE,LOG_TEST_OUTPUT,APPLY_PATCH_FAIL
 from swebench.harness.grading import get_logs_eval,_resolve_case
 spec=make_test_spec(task);real=docker.from_env(timeout=20);owned=[];proofs=[];runid='g5-grade-'+uuid.uuid4().hex[:12];result=dict(task=iid,solved=None,grade_valid=False,model_calls=0,patch_sha256=sha(patch_file),image_id=image,errors=[]);cwd=pathlib.Path.cwd();os.chdir(root)
 class Proxy:
  def __init__(self,c):self.inner=c
  def __getattr__(self,k):return getattr(self.inner,k)
  def start(self):
   self.inner.start()
   for command in (['git','-C','/testbed','checkout','--detach',task['base_commit']],['git','-C','/testbed','reset','--hard',task['base_commit']]):
    r=self.inner.exec_run(command)
    if r.exit_code:raise RuntimeError('Original base restoration failed')
   r=self.inner.exec_run(['git','-C','/testbed','rev-parse','HEAD'])
   if r.exit_code or r.output.decode().strip()!=task['base_commit']:raise RuntimeError('Original base identity failed')
   proofs.append(dict(base_commit_verified=task['base_commit']))
 class Images:
  def get(self,name):
   if name!=image:raise RuntimeError('Unfrozen image')
   img=real.images.get(name)
   if img.id!=image:raise RuntimeError('Image identity failed')
   return img
  def pull(self,*a,**k):raise RuntimeError('Implicit image pull prohibited')
  def build(self,*a,**k):raise RuntimeError('Implicit image build prohibited')
 class Containers:
  def get(self,name):
   if name not in owned:raise RuntimeError('Unowned container access prohibited')
   return real.containers.get(name)
  def create(self,*a,**kw):
   name=kw.get('name')
   if not name or not name.startswith('sweb.eval.'+iid.lower()+'.'+runid) or owned:raise RuntimeError('Grader ownership failed')
   owned.append(name);save(root/'owned.json',dict(names=owned,run_id=runid));kw.update(network_mode='none',network_disabled=False,nano_cpus=1000000000,mem_limit='8g',pids_limit=512,security_opt=['no-new-privileges'],environment={'PIP_NO_INDEX':'1','PIP_FIND_LINKS':'/wheelhouse'},volumes={plan['wheelhouse']:{'bind':'/wheelhouse','mode':'ro'}});c=real.containers.create(*a,**kw);c.reload();h=c.attrs['HostConfig']
   if h['NetworkMode']!='none' or h['Memory']!=8*1024**3 or h['NanoCpus']!=1000000000 or h['PidsLimit']!=512 or h['Privileged'] or h.get('DeviceRequests'):raise RuntimeError('Grader resource mismatch')
   if not any(m.get('Source')==plan['wheelhouse'] and m.get('Destination')=='/wheelhouse' and m.get('RW') is False for m in c.attrs['Mounts']):raise RuntimeError('Readonly public cache missing')
   save(root/'container-inspect.json',c.attrs);proofs.append(dict(name=name,inspect_sha256=sha(root/'container-inspect.json')));return Proxy(c)
 class Client:
  images=Images();containers=Containers();api=real.api
 try:
  patch=patch_file.read_text();prediction=dict(instance_id=iid,model_name_or_path='g5-captured',model_patch=patch);run_instance(spec,prediction,Client(),runid,timeout=600,skip_patch=not bool(patch.strip()));reports=list(root.rglob('report.json'));instance_logs=list(root.rglob(LOG_INSTANCE))
  if len(reports)!=1:
   if patch.strip() and len(instance_logs)==1 and APPLY_PATCH_FAIL in instance_logs[0].read_text():result.update(solved=False,grade_valid=True,classification='original_official_patch_application_failure')
   else:raise RuntimeError('Original official report missing/ambiguous')
  else:
   entry=json.loads(reports[0].read_text())[iid];result['original_report']=entry;result['original_report_sha256']=sha(reports[0]);test_log=reports[0].parent/LOG_TEST_OUTPUT;statuses,found=get_logs_eval(spec,str(test_log));coverage={}
   for category,expected in [('FAIL_TO_PASS',spec.FAIL_TO_PASS),('PASS_TO_PASS',spec.PASS_TO_PASS)]:
    detail=entry['tests_status'][category];reported=detail['success']+detail['failure']
    # Per-test coverage is retained as information; official outcome governs.
    keys=[_resolve_case(t,statuses) for t in expected];coverage[category]=dict(expected=len(expected),parsed_expected=sum(k is not None for k in keys),success=len(detail['success']),failure=len(detail['failure']))
   result['coverage']=coverage;result['test_output_found']=found
   if type(entry.get('resolved')) is not bool or entry.get('infra_failure') is not False:raise RuntimeError('Original report uncertain/infrastructure failure')
   # Do not add our own per-test solve/eligibility requirements.
   result.update(solved=entry['resolved'],grade_valid=True,classification='original_official_report')
 except Exception as e:result['errors'].append(dict(type=type(e).__name__,message=str(e)[:500]))
 finally:
  for name in owned:
   try:real.containers.get(name).remove(force=True)
   except docker.errors.NotFound:pass
   except Exception as e:result['errors'].append(dict(type=type(e).__name__,message='owned cleanup removal failed'))
   try:real.containers.get(name);result['errors'].append(dict(message='owned grader remains'))
   except docker.errors.NotFound:proofs.append(dict(name=name,absence_verified=True))
   except Exception as e:result['errors'].append(dict(type=type(e).__name__,message='owned cleanup absence uncertain'))
  result['proofs']=proofs;result['owned_containers_absent']=all(name in {p.get('name') for p in proofs if p.get('absence_verified')} for name in owned);result['artifacts']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};save(root/'grade-result.json',result);os.chdir(cwd);real.close()
 return result
if __name__=='__main__':
 root=pathlib.Path(sys.argv[1]).resolve();iid=sys.argv[2];patch=pathlib.Path(sys.argv[3]).resolve();plan=json.loads(pathlib.Path(sys.argv[4]).read_text());grade(root,iid,patch,plan)
