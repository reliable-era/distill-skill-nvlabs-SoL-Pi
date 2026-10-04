#!/usr/bin/env python3
"""Prepared-only unless --launch; official grading untouched, resources intercepted."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, time
OUT=pathlib.Path(__file__).resolve().parent
PRIVATE=pathlib.Path('/tmp/solpi-confirmation-swe-controls')
MEM=8*1024**3; GROWTH=80*1024**3; FREE=100*1024**3

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(pathlib.Path(p).read_text())
def dump(p,d): pathlib.Path(p).write_text(json.dumps(d,indent=2)+'\n')
def disk_guard(initial,current,free):
    if current-initial>GROWTH or free<FREE: raise RuntimeError('disk limit')
class ImageGuard:
    def __init__(self,inner): self.inner=inner
    def get(self,*a,**k): return self.inner.get(*a,**k)
    def pull(self,*a,**k): raise RuntimeError('implicit image pull prohibited')
class ContainerGuard:
    def __init__(self,inner,record): self.inner=inner;self.record=record;self.created=[];self.calls=0
    def get(self,*a,**k): return self.inner.get(*a,**k)
    def create(self,*a,**k):
        self.calls+=1
        if self.calls>1: raise RuntimeError('container retry prohibited')
        k.update(mem_limit=MEM,nano_cpus=4_000_000_000,network_disabled=True)
        c=self.inner.create(*a,**k);self.created.append(c)
        c.reload();host=c.attrs['HostConfig']
        if host['Memory']!=MEM or host['NanoCpus']!=4_000_000_000 or c.attrs['HostConfig']['NetworkMode']!='none':
            c.remove(force=True);raise RuntimeError('container resource verification failed')
        dump(self.record,{'container_id':c.id,'memory':host['Memory'],'nano_cpus':host['NanoCpus'],'network':'none','verified_before_test':True});return c
    def cleanup(self):
        for c in self.created:
            try:c.remove(force=True)
            except Exception:pass
class ClientGuard:
    def __init__(self,inner,record): self.inner=inner;self.images=ImageGuard(inner.images);self.containers=ContainerGuard(inner.containers,record)
    def __getattr__(self,n):return getattr(self.inner,n)
def image_bytes():
    p=subprocess.run(['docker','image','ls','-q','--no-trunc'],capture_output=True,text=True,check=True)
    ids=sorted(set(p.stdout.split()));return sum(json.loads(subprocess.check_output(['docker','image','inspect',i]))[0]['Size'] for i in ids)
def worker(index):
    plan=load(OUT/'execution-plan.json');assert 0<=index<8;assert sha(__file__)==plan['runner_sha256'];assert load(OUT/'execution-authorization.json')['plan_sha256']==sha(OUT/'execution-plan.json');assert (PRIVATE/'launch-start.json').exists();c=plan['controls'][index];assert pathlib.Path.cwd()==PRIVATE/c['run_id'];assert load(pathlib.Path.cwd()/'control-start.json')['index']==index;source=plan['clean_source'];sys.path.insert(0,source)
    import docker
    from swebench.task.repo import load_task_repo
    from swebench.harness.utils import make_test_spec
    from swebench.harness.run_evaluation import run_instance
    row=load_task_repo(plan['private_task_root'],[c['instance_id']])[0];row['image']=c['image'];spec=make_test_spec(row)
    patch=row['patch'] if c['kind']=='gold' else 'diff --git a/solpi-control-marker.txt b/solpi-control-marker.txt\nnew file mode 100644\n--- /dev/null\n+++ b/solpi-control-marker.txt\n@@ -0,0 +1 @@\n+unchanged baseline marker\n'
    pred={'instance_id':c['instance_id'],'model_name_or_path':'private-control','model_patch':patch};client=ClientGuard(docker.from_env(),pathlib.Path.cwd()/'container-limits.json')
    try:
        result=run_instance(spec,pred,client,c['run_id'],600,False,False,plan['private_task_root'])
        dump(pathlib.Path.cwd()/'worker-result.json',{'result_present':result is not None})
    finally:client.containers.cleanup()
def launch():
    plan=load(OUT/'execution-plan.json');assert sha(__file__)==plan['runner_sha256']
    for path,h in plan['source_hashes'].items():assert sha(path)==h
    assert len(plan['controls'])==8 and len(plan['images'])==4
    assert load(OUT/'execution-authorization.json')['plan_sha256']==sha(OUT/'execution-plan.json')
    PRIVATE.mkdir(mode=0o700,exist_ok=True);os.chmod(PRIVATE,0o700)
    with (PRIVATE/'launch-start.json').open('x') as f:json.dump({'time':time.time(),'plan_sha256':sha(OUT/'execution-plan.json')},f)
    initial=image_bytes();records=[]
    for index,image in enumerate(plan['images']):
        disk_guard(initial,image_bytes(),shutil.disk_usage('/tmp').free)
        start=time.monotonic();log=PRIVATE/f'pull-{index}.log'
        with log.open('wb') as f:
            p=subprocess.run(['docker','pull','--platform','linux/amd64',image],stdout=f,stderr=subprocess.STDOUT,timeout=300)
        records.append({'pull':index,'image':image,'exit_code':p.returncode,'elapsed':time.monotonic()-start,'log_sha256':sha(log)});dump(OUT/'progress.json',{'pulls':records,'controls':[]})
        disk_guard(initial,image_bytes(),shutil.disk_usage('/tmp').free)
        if p.returncode:raise RuntimeError('pull failed; no retry')
    controls=[]
    for index,c in enumerate(plan['controls']):
        disk_guard(initial,image_bytes(),shutil.disk_usage('/tmp').free);work=PRIVATE/c['run_id'];work.mkdir(mode=0o700)
        dump(work/'control-start.json',{'index':index,'kind':c['kind'],'instance_id':c['instance_id']});start=time.monotonic()
        try:
            with (work/'private-harness.log').open('wb') as f:p=subprocess.run([sys.executable,str(OUT/'run_controls.py'),'--worker',str(index)],cwd=work,stdout=f,stderr=subprocess.STDOUT,timeout=900)
        except subprocess.TimeoutExpired:
            subprocess.run(['docker','rm','-f',f"sweb.eval.{c['instance_id'].lower()}.{c['run_id']}"],capture_output=True);raise RuntimeError('control timeout; stop without retry')
        reports=list(work.glob('logs/run_evaluation/**/report.json'));grade=None
        if len(reports)==1:
            report=load(reports[0]);grade=report[c['instance_id']]['resolved']
        record={'index':index,'instance_id':c['instance_id'],'kind':c['kind'],'exit_code':p.returncode,'elapsed':time.monotonic()-start,'resolved':grade,'report_sha256':sha(reports[0]) if len(reports)==1 else None};controls.append(record);dump(OUT/'progress.json',{'pulls':records,'controls':controls})
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
