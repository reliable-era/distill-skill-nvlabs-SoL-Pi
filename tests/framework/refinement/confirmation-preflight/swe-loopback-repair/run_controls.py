#!/usr/bin/env python3
"""Prepared-only unless --launch; official grading untouched, resources intercepted."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, time
OUT=pathlib.Path(__file__).resolve().parent
PRIVATE=pathlib.Path('/tmp/solpi-confirmation-swe-loopback-repair')
MEM=8*1024**3; GROWTH=80*1024**3; FREE=100*1024**3

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(pathlib.Path(p).read_text())
def dump(p,d): pathlib.Path(p).write_text(json.dumps(d,indent=2)+'\n')
def disk_guard(initial,current,free):
    if current-initial>GROWTH or free<FREE: raise RuntimeError('disk limit')
def authorized(plan):
    auth=load(OUT/'execution-authorization.json')
    if auth.get('authorized') is not True or auth.get('plan_sha256')!=sha(OUT/'execution-plan.json'):raise RuntimeError('authorization required')
def validate_plan(plan):
    expected={'pull_seconds':300,'test_seconds':600,'outer_seconds':900,'memory':MEM,'nano_cpus':4_000_000_000,'network':'none','max_logical_image_size_growth_bytes':GROWTH,'min_free_disk_bytes':FREE,'serial':True,'retries':0}
    if plan['limits']!=expected or plan['maximum_controls']!=8 or plan['maximum_pulls']!=0 or plan['maximum_builds']!=0:raise RuntimeError('hard limits mismatch')
    cs=plan['controls'];pairs={(c['instance_id'],c['kind']) for c in cs}
    if len(cs)!=8 or len(pairs)!=8 or len({c['run_id'] for c in cs})!=8 or len(set(plan['images']))!=4:raise RuntimeError('unique budget mismatch')
    ids={c['instance_id'] for c in cs}
    if len(ids)!=4 or pairs!={(tid,k) for tid in ids for k in ['unchanged','gold']}:raise RuntimeError('control pairs mismatch')
    if len(plan['pull_images'])!=0 or len(plan['cached_images'])!=4 or set(plan['pull_images']+plan['cached_images'])!=set(plan['images']):raise RuntimeError('combined pull budget mismatch')
    if {c['image'] for c in cs}!=set(plan['images']) or any('@sha256:' not in i for i in plan['images']):raise RuntimeError('image binding mismatch')
def claim_worker(path,index,plan_hash):
    with pathlib.Path(path).open('x') as f:json.dump({'index':index,'plan_sha256':plan_hash,'time':time.time()},f)
def verified_cleanup(container_id,record):
    removal=subprocess.run(['docker','rm','-f',container_id],capture_output=True,timeout=30)
    inspection=subprocess.run(['docker','container','inspect',container_id],capture_output=True,timeout=10)
    absent=inspection.returncode!=0 and (b'No such container' in inspection.stderr or b'No such object' in inspection.stderr)
    dump(record,{'container_id':container_id,'remove_exit':removal.returncode,'inspect_exit':inspection.returncode,'absence_verified':absent})
    if not absent:raise RuntimeError('cleanup absence unverified')
def disk_checks(plan,initial):
    current=image_bytes()
    for path in [plan['docker_root_dir'],plan['artifact_filesystem_path']]:disk_guard(initial,current,shutil.disk_usage(path).free)
class ImageGuard:
    def __init__(self,inner): self.inner=inner
    def get(self,*a,**k): return self.inner.get(*a,**k)
    def build(self,*a,**k): raise RuntimeError('implicit image build prohibited')
    def pull(self,*a,**k): raise RuntimeError('implicit image pull prohibited')
class ContainerGuard:
    def __init__(self,inner,record): self.inner=inner;self.record=record;self.created=[];self.calls=0
    def get(self,*a,**k): return self.inner.get(*a,**k)
    def create(self,*a,**k):
        self.calls+=1
        if self.calls>1: raise RuntimeError('container retry prohibited')
        k.update(mem_limit=MEM,nano_cpus=4_000_000_000,network_disabled=False,network_mode='none')
        c=self.inner.create(*a,**k);self.created.append(c);dump(self.record,{'container_id':c.id,'verified_before_test':False})
        c.reload();host=c.attrs['HostConfig'];config=c.attrs.get('Config',{})
        dump(self.record,{'container_id':c.id,'memory':host.get('Memory'),'nano_cpus':host.get('NanoCpus'),'network_mode':host.get('NetworkMode'),'config_network_disabled':config.get('NetworkDisabled',False),'verified_before_test':False})
        if host['Memory']!=MEM or host['NanoCpus']!=4_000_000_000 or c.attrs['HostConfig']['NetworkMode']!='none' or config.get('NetworkDisabled',False) is not False:
            verified_cleanup(c.id,pathlib.Path(self.record).with_name('cleanup.json'));raise RuntimeError('container resource verification failed')
        dump(self.record,{'container_id':c.id,'memory':host['Memory'],'nano_cpus':host['NanoCpus'],'network':'none','config_network_disabled':config.get('NetworkDisabled',False),'verified_before_test':True});return c
    def cleanup(self):
        for c in self.created:
            verified_cleanup(c.id,pathlib.Path(self.record).with_name('cleanup.json'))
class APIGuard:
    BLOCKED={'build','pull','import_image','load_image','commit','build_prune','prune_builds'}
    def __init__(self,inner):self.inner=inner
    def __getattr__(self,n):
        if n in self.BLOCKED:raise RuntimeError('implicit image build/pull prohibited')
        return getattr(self.inner,n)
class ClientGuard:
    def __init__(self,inner,record): self.inner=inner;self.images=ImageGuard(inner.images);self.containers=ContainerGuard(inner.containers,record);self.api=APIGuard(inner.api)
    def __getattr__(self,n):return getattr(self.inner,n)
def snapshot_bytes(snapshot):
    import re
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get('Images'),list):raise RuntimeError('invalid image-summary snapshot')
    images={}
    for image in snapshot['Images']:
        ident=image.get('Id');size=image.get('Size')
        if not isinstance(ident,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',ident) or type(size) is not int or size<0:raise RuntimeError('invalid image-summary image')
        if ident in images and images[ident]!=size:raise RuntimeError('conflicting image-summary duplicate')
        images[ident]=size
    return sum(images.values())
def inventory_source_guard(binding):
    if sha(binding['file'])!=binding['sha256']:raise RuntimeError('inventory SDK source mismatch')
def cached_digest_guard(image,reference):
    if reference not in image.attrs.get('RepoDigests',[]):raise RuntimeError('cached immutable digest missing')
def image_bytes():
    import docker
    binding=load(OUT/'execution-plan.json')['docker_sdk_images_source'];inventory_source_guard(binding)
    client=docker.from_env(timeout=20)
    try:return snapshot_bytes({'Images':client.api.images(all=True)})
    finally:client.close()
def worker(index):
    plan=load(OUT/'execution-plan.json');assert 0<=index<8;assert sha(__file__)==plan['runner_sha256'];authorized(plan);validate_plan(plan);assert (PRIVATE/'launch-start.json').exists();c=plan['controls'][index];assert pathlib.Path.cwd()==PRIVATE/c['run_id'];assert load(pathlib.Path.cwd()/'control-start.json')['index']==index;claim_worker(pathlib.Path.cwd()/'worker-start.json',index,sha(OUT/'execution-plan.json'));source=plan['clean_source'];sys.path.insert(0,source)
    for path,h in plan['source_hashes'].items():assert sha(path)==h
    import docker
    from swebench.task.repo import load_task_repo
    from swebench.harness.utils import make_test_spec
    from swebench.harness.run_evaluation import run_instance
    row=load_task_repo(plan['private_task_root'],[c['instance_id']])[0];row['image']=c['image'];spec=make_test_spec(row)
    patch=row['patch'] if c['kind']=='gold' else 'diff --git a/solpi-control-marker.txt b/solpi-control-marker.txt\nnew file mode 100644\n--- /dev/null\n+++ b/solpi-control-marker.txt\n@@ -0,0 +1 @@\n+unchanged baseline marker\n'
    pred={'instance_id':c['instance_id'],'model_name_or_path':'private-control','model_patch':patch};client=ClientGuard(docker.from_env(timeout=20),pathlib.Path.cwd()/'container-limits.json')
    try:
        result=run_instance(spec,pred,client,c['run_id'],600,False,False,plan['private_task_root'])
        dump(pathlib.Path.cwd()/'worker-result.json',{'result_present':result is not None})
    finally:client.containers.cleanup()
def infrastructure_gate(report,instance_id):
    if report[instance_id].get('infra_failure') is True:raise RuntimeError('official infrastructure failure; stop before next control')
def control_grade_gate(report,tid,kind,status_map,f2p,p2p,resolve,classification):
    row=report[tid]
    if classification is not None or row.get('infra_failure') is not False or row.get('infra_failure_reason'):raise RuntimeError('infrastructure or ambiguous failure')
    if row.get('patch_is_None') is not False or row.get('patch_exists') is not True or row.get('patch_successfully_applied') is not True or not isinstance(row.get('tests_status'),dict):raise RuntimeError('incomplete official report')
    for category,expected in [('FAIL_TO_PASS',f2p),('PASS_TO_PASS',p2p)]:
        group=row['tests_status'].get(category)
        if not isinstance(group,dict) or not isinstance(group.get('success'),list) or not isinstance(group.get('failure'),list):raise RuntimeError('invalid official test-report schema')
        ids=group['success']+group['failure']
        if len(ids)!=len(expected) or set(ids)!=set(expected):raise RuntimeError('incomplete official test IDs')
    def statuses(ids):
        keys=[resolve(x,status_map) for x in ids]
        if any(k is None for k in keys):raise RuntimeError('missing or ambiguous expected tests')
        return [status_map[k] for k in keys]
    f=statuses(f2p);p=statuses(p2p)
    if not f or any(x!='PASSED' for x in p):raise RuntimeError('invalid pass-to-pass control evidence')
    if kind=='unchanged':
        if not any(x=='FAILED' for x in f) or any(x not in ['PASSED','FAILED'] for x in f) or row.get('resolved') is not False:raise RuntimeError('no genuine fail-to-pass negative')
    elif any(x!='PASSED' for x in f) or row.get('resolved') is not True:raise RuntimeError('gold not fully resolved')
def validate_official_control(report,control,report_path,plan):
    from swebench.task.repo import load_task_repo
    from swebench.harness.utils import make_test_spec
    from swebench.harness.grading import get_logs_eval,_resolve_case
    from swebench.harness.infra_failure import classify_logs
    from swebench.harness.run_evaluation import LOG_TEST_OUTPUT,LOG_INSTANCE
    spec=make_test_spec(load_task_repo(plan['private_task_root'],[control['instance_id']])[0])
    test_log=report_path.parent/LOG_TEST_OUTPUT;instance_log=report_path.parent/LOG_INSTANCE
    statuses,found=get_logs_eval(spec,str(test_log))
    if not found:raise RuntimeError('no parseable official tests')
    control_grade_gate(report,control['instance_id'],control['kind'],statuses,spec.FAIL_TO_PASS,spec.PASS_TO_PASS,_resolve_case,classify_logs(test_log,instance_log))
def official_report_paths(work,plan):
    sys.path.insert(0,plan['clean_source'])
    from swebench.harness.run_evaluation import RUN_EVALUATION_LOG_DIR,LOG_REPORT
    return list((pathlib.Path(work)/RUN_EVALUATION_LOG_DIR).rglob(LOG_REPORT))
def launch():
    plan=load(OUT/'execution-plan.json');assert sha(__file__)==plan['runner_sha256']
    for path,h in plan['source_hashes'].items():assert sha(path)==h
    validate_plan(plan);authorized(plan)
    actual=subprocess.check_output(['docker','info','--format','{{.DockerRootDir}}'],timeout=20,text=True).strip()
    if str(pathlib.Path(actual).resolve())!=plan['docker_root_dir']:raise RuntimeError('Docker storage root changed')
    PRIVATE.mkdir(mode=0o700,exist_ok=True);os.chmod(PRIVATE,0o700)
    with (PRIVATE/'launch-start.json').open('x') as f:json.dump({'time':time.time(),'plan_sha256':sha(OUT/'execution-plan.json')},f)
    import docker
    client=docker.from_env(timeout=20)
    try:
        info=client.info()
        cli_id=subprocess.check_output(['docker','info','--format','{{.ID}}'],timeout=20,text=True).strip()
        if info['ID']!=plan['daemon_id'] or cli_id!=plan['daemon_id'] or str(pathlib.Path(info['DockerRootDir']).resolve())!=plan['docker_root_dir']:raise RuntimeError('daemon binding mismatch')
        for image in plan['cached_images']:cached_digest_guard(client.images.get(image),image)
    finally:client.close()
    initial=image_bytes();records=[]
    for index,image in enumerate(plan['pull_images']):
        disk_checks(plan,initial)
        start=time.monotonic();log=PRIVATE/f'pull-{index}.log'
        with log.open('wb') as f:
            p=subprocess.run(['docker','pull','--platform','linux/amd64',image],stdout=f,stderr=subprocess.STDOUT,timeout=300)
        records.append({'pull':index,'image':image,'exit_code':p.returncode,'elapsed':time.monotonic()-start,'log_sha256':sha(log)});dump(OUT/'progress.json',{'pulls':records,'controls':[]})
        disk_checks(plan,initial)
        if p.returncode:raise RuntimeError('pull failed; no retry')
    controls=[]
    for index,c in enumerate(plan['controls']):
        disk_checks(plan,initial);work=PRIVATE/c['run_id'];work.mkdir(mode=0o700)
        dump(work/'control-start.json',{'index':index,'kind':c['kind'],'instance_id':c['instance_id']});start=time.monotonic()
        try:
            with (work/'private-harness.log').open('wb') as f:p=subprocess.run([sys.executable,str(OUT/'run_controls.py'),'--worker',str(index)],cwd=work,stdout=f,stderr=subprocess.STDOUT,timeout=900)
        except subprocess.TimeoutExpired:
            limits=work/'container-limits.json';container_id=load(limits)['container_id'] if limits.exists() else f"sweb.eval.{c['instance_id'].lower()}.{c['run_id']}"
            controls.append({'index':index,'instance_id':c['instance_id'],'kind':c['kind'],'timeout':True,'elapsed':time.monotonic()-start});dump(OUT/'progress.json',{'pulls':records,'controls':controls})
            verified_cleanup(container_id,work/'outer-cleanup.json');raise RuntimeError('control timeout; stop without retry')
        disk_checks(plan,initial)
        reports=official_report_paths(work,plan);grade=None
        if len(reports)==1:
            report=load(reports[0]);grade=report[c['instance_id']]['resolved']
        record={'index':index,'instance_id':c['instance_id'],'kind':c['kind'],'exit_code':p.returncode,'elapsed':time.monotonic()-start,'resolved':grade,'report_sha256':sha(reports[0]) if len(reports)==1 else None,'infra_failure':report[c['instance_id']].get('infra_failure') if len(reports)==1 else None};controls.append(record);dump(OUT/'progress.json',{'pulls':records,'controls':controls})
        cleanup=work/'cleanup.json'
        if not cleanup.exists() or load(cleanup).get('absence_verified') is not True:raise RuntimeError('cleanup unverified; stop')
        if len(reports)==1:validate_official_control(report,c,reports[0],plan)
        if p.returncode or grade is None or grade!=(c['kind']=='gold'):raise RuntimeError('control failed or unexpected quality; stop without retry')
    dump(OUT/'completion.json',{'controls':controls,'pulls':records,'model_calls':0})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--launch',action='store_true');p.add_argument('--worker',type=int);a=p.parse_args()
    if a.worker is not None:worker(a.worker)
    elif a.launch:
        try:launch()
        except Exception as e:
            dump(OUT/'execution-error.json',{'error_type':type(e).__name__,'message':'bounded execution stopped; private logs retained; no retry','model_calls':0});raise
    else:print('prepared only; no pulls or controls')
