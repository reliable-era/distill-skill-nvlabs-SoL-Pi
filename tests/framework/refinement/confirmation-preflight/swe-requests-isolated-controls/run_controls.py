#!/usr/bin/env python3
"""Prepared-only unless --launch; official grading untouched, resources intercepted."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, time, importlib.util, signal
OUT=pathlib.Path(__file__).resolve().parent
PRIVATE=pathlib.Path('/tmp/solpi-confirmation-requests-isolated-controls')
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
    expected={'pull_seconds':300,'test_seconds':600,'outer_seconds':900,'memory':MEM,'nano_cpus':4_000_000_000,'network':'isolated-internal-grader-fixture','max_logical_image_size_growth_bytes':GROWTH,'min_free_disk_bytes':FREE,'serial':True,'retries':0}
    if plan['limits']!=expected or plan['maximum_controls']!=2 or plan['maximum_pulls']!=0 or plan['maximum_builds']!=0:raise RuntimeError('hard limits mismatch')
    if plan['combined_budget']['preserved_prior_control_attempts']!=11 or plan['combined_budget']['new_maximum_control_attempts']!=2 or plan['combined_budget']['combined_maximum_control_attempts']!=13:raise RuntimeError('combined attempt budget mismatch')
    if plan['maximum_fixture_starts']!=1 or plan['maximum_models']!=0 or plan['phase_worker_outer_seconds']!=1900 or plan['maximum_total_seconds']!=2150:raise RuntimeError('fixture/phase budget mismatch')
    cs=plan['controls']
    expected=[('psf__requests-1921','unchanged'),('psf__requests-1921','gold')]
    if [(c['instance_id'],c['kind']) for c in cs]!=expected:raise RuntimeError('fixed remaining control order mismatch')
    pairs={(c['instance_id'],c['kind']) for c in cs}
    if len(cs)!=2 or len(pairs)!=2 or len({c['run_id'] for c in cs})!=2 or len(set(plan['images']))!=2:raise RuntimeError('unique budget mismatch')
    ids={c['instance_id'] for c in cs}
    if len(ids)!=1 or pairs!={(tid,k) for tid in ids for k in ['unchanged','gold']}:raise RuntimeError('control pairs mismatch')
    if len(plan['pull_images'])!=0 or len(plan['cached_images'])!=2 or set(plan['pull_images']+plan['cached_images'])!=set(plan['images']):raise RuntimeError('combined pull budget mismatch')
    if {c['image'] for c in cs}!={plan['images'][0]} or any('@sha256:' not in i for i in plan['images']):raise RuntimeError('image binding mismatch')
def claim_worker(path,index,plan_hash):
    with pathlib.Path(path).open('x') as f:json.dump({'index':index,'plan_sha256':plan_hash,'time':time.time()},f)
def verified_cleanup(container_id,record):
    removal=subprocess.run(['docker','rm','-f',container_id],capture_output=True,timeout=30)
    inspection=subprocess.run(['docker','container','inspect',container_id],capture_output=True,timeout=10)
    absent=inspection.returncode!=0 and inspection.stderr.decode().strip()=='Error response from daemon: No such container: '+container_id
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
class TrustedContainer:
    def __init__(self,inner,record):self.inner=inner;self.record=record
    def __getattr__(self,n):return getattr(self.inner,n)
    def start(self,*a,**k):
        result=self.inner.start(*a,**k)
        plan=load(OUT/'execution-plan.json');metadata=load(PRIVATE/'fixture.json')
        import docker
        client=docker.from_env(timeout=10)
        try:
            service=client.containers.get(metadata['service_id']);service.reload();dump(pathlib.Path(self.record).with_name('fixture-state-before-test.json'),service.attrs['State']);assert service.status=='running'
            net=client.networks.get(metadata['network_id']);net.reload();attrs=net.attrs
            dump(pathlib.Path(self.record).with_name('network-state-before-test.json'),attrs)
            assert attrs['Internal'] is True and attrs['EnableIPv6'] is False and attrs['Options'].get('com.docker.network.bridge.gateway_mode_ipv4')=='isolated'
            assert all(not x.get('Gateway') for x in attrs.get('IPAM',{}).get('Config',[])) and set(attrs['Containers'])=={metadata['service_id'],self.inner.id}
        finally:client.close()
        proof=load(self.record);proof['verified_before_test']=True;proof['exact_membership_verified']=True;dump(self.record,proof)
        return result
class ContainerGuard:
    def __init__(self,inner,record):self.inner=inner;self.record=record;self.created=[];self.calls=0
    def get(self,*a,**k):return self.inner.get(*a,**k)
    def create(self,*a,**k):
        self.calls+=1
        if self.calls>1:raise RuntimeError('container retry prohibited')
        plan=load(OUT/'execution-plan.json');fixture=load(PRIVATE/'fixture.json');ca=str(pathlib.Path(plan['fixture']['certificate_root'])/'ca.pem')
        if k.get('image')!=plan['images'][0]:raise RuntimeError('unexpected grader image')
        if k.get('environment') or k.get('volumes'):raise RuntimeError('unexpected official environment/mounts; stop rather than replace')
        k.update(mem_limit=MEM,nano_cpus=4_000_000_000,network_disabled=False,network_mode=fixture['network_name'],environment=plan['trusted_CA_environment'],volumes={ca:{'bind':'/certs/ca.pem','mode':'ro'}})
        c=self.inner.create(*a,**k);self.created.append(c);dump(self.record,{'container_id':c.id,'verified_before_test':False});c.reload();h=c.attrs['HostConfig'];conf=c.attrs['Config']
        mounts=[(m['Source'],m['Destination'],m['RW']) for m in c.attrs['Mounts']]
        proof={'container_id':c.id,'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network':h['NetworkMode'],'config_network_disabled':conf.get('NetworkDisabled',False),'mounts':mounts,'CA_environment_verified':'REQUESTS_CA_BUNDLE=/certs/ca.pem' in conf.get('Env',[]),'verified_before_test':False};dump(self.record,proof)
        assert h['Memory']==MEM and h['NanoCpus']==4_000_000_000 and h['NetworkMode']==fixture['network_name'] and conf.get('NetworkDisabled',False) is False and not h.get('PortBindings')
        assert mounts==[(ca,'/certs/ca.pem',False)] and proof['CA_environment_verified']
        assert not any(any(m in e.split('=',1)[0] for m in ['TOKEN','PASSWORD','SECRET','API_KEY']) for e in conf.get('Env',[]))
        return TrustedContainer(c,self.record)
    def cleanup(self):
        for c in self.created:verified_cleanup(c.id,pathlib.Path(self.record).with_name('cleanup.json'))
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
    if reference not in image.attrs.get('RepoDigests',[]) or image.id!=load(OUT/'execution-plan.json')['image_ids'][reference]:raise RuntimeError('cached immutable digest/ID missing')
def image_bytes():
    import docker
    binding=load(OUT/'execution-plan.json')['docker_sdk_images_source'];inventory_source_guard(binding)
    client=docker.from_env(timeout=20)
    try:return snapshot_bytes({'Images':client.api.images(all=True)})
    finally:client.close()
def process_start(pid):
    try:return pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
    except FileNotFoundError:return None

def group_members(pgid):
    listing=subprocess.run(['ps','-eo','pid=,pgid=,sid=,stat='],capture_output=True,text=True,check=True,timeout=3)
    rows=[]
    for line in listing.stdout.splitlines():
        pid,group,session,state=line.split()
        if int(group)==pgid:rows.append({'pid':int(pid),'pgid':int(group),'sid':int(session),'state':state})
    return rows

def terminal_group(record,proof_path):
    pgid=record['pgid'];assert pgid==record['pid'] and pgid>1 and pgid!=os.getpgrp()
    current_start=process_start(record['pid'])
    if current_start is not None and current_start!=record['starttime']:
        dump(proof_path,{'pid':record['pid'],'pgid':pgid,'terminal':False,'error':'PID starttime mismatch; no signal sent'});raise RuntimeError('owned PID reused; refuse signal')
    actions=[]
    for sig,seconds in [(signal.SIGTERM,3),(signal.SIGKILL,3)]:
        rows=group_members(pgid);assert all(x['sid']==record['sid']==pgid for x in rows)
        live=[x for x in rows if not x['state'].startswith('Z')]
        if not live:break
        try:os.killpg(pgid,sig);actions.append(sig.name)
        except ProcessLookupError:pass
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            rows=group_members(pgid)
            if not any(not x['state'].startswith('Z') for x in rows):break
            time.sleep(.05)
    rows=group_members(pgid);assert all(x['sid']==pgid for x in rows)
    terminal=not any(not x['state'].startswith('Z') for x in rows)
    dump(proof_path,{'pid':record['pid'],'pgid':pgid,'sid':record['sid'],'terminal':terminal,'remaining_members':rows,'signals':actions})
    if not terminal:raise RuntimeError('owned process group remains live; no Docker cleanup')

def owned_run(command,log,seconds,record_path):
    with pathlib.Path(log).open('wb') as output:
        process=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        record={'pid':process.pid,'pgid':process.pid,'sid':process.pid,'command_source':str(OUT/'run_controls.py'),'starttime':process_start(process.pid)};assert record['starttime'] is not None;dump(record_path,record)
        try:code=process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            bounded_terminal(record_path);process.wait(timeout=2);raise
        bounded_terminal(record_path)
        return type('ProcessResult',(),{'returncode':code})()

def bounded_terminal(record_path):
    subprocess.run([sys.executable,str(OUT/'run_controls.py'),'--terminate-group',str(record_path)],check=True,timeout=20,capture_output=True)

def drain_recorded_groups():
    # Stop the phase first so it cannot launch another control while draining.
    for record_path in [PRIVATE/'phase-process.json']+[PRIVATE/c['run_id']/'worker-process.json' for c in load(OUT/'execution-plan.json')['controls']]:
        if record_path.exists():bounded_terminal(record_path)

def worker(index):
    ownership=pathlib.Path.cwd()/'worker-process.json';deadline=time.monotonic()+5
    while not ownership.exists():
        if time.monotonic()>=deadline:raise RuntimeError('unrecorded worker cannot grade')
        time.sleep(.05)
    assert load(ownership)['pid']==os.getpid() and load(ownership)['pgid']==os.getpgrp()
    plan=load(OUT/'execution-plan.json');assert 0<=index<2;assert sha(__file__)==plan['runner_sha256'];authorized(plan);validate_plan(plan);assert load(PRIVATE/'launch-start.json')['plan_sha256']==sha(OUT/'execution-plan.json');c=plan['controls'][index];assert pathlib.Path.cwd()==PRIVATE/c['run_id'];assert load(pathlib.Path.cwd()/'control-start.json')['index']==index;assert load(pathlib.Path.cwd()/'control-start.json')['plan_sha256']==sha(OUT/'execution-plan.json');claim_worker(pathlib.Path.cwd()/'worker-start.json',index,sha(OUT/'execution-plan.json'));source=plan['clean_source'];sys.path.insert(0,source)
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
def parity_helper(plan):
    file=plan['parity_runner_source'];assert sha(file)==plan['source_hashes'][file]
    spec=importlib.util.spec_from_file_location('trusted_parity',file);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);return helper

def start_fixture(plan):
    with (PRIVATE/'fixture-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'execution-plan.json')},f)
    import docker
    client=docker.from_env(timeout=10);fixture=plan['fixture'];helper=parity_helper(plan)
    try:
        image=client.images.get(fixture['image']);assert image.id==fixture['image_id'] and fixture['image'] in image.attrs['RepoDigests']
        assert not client.networks.list(names=['solpi-requests-fixture-internal'])
        try:client.containers.get('solpi-requests-fixture-service')
        except docker.errors.NotFound:pass
        else:raise RuntimeError('owned service name present')
        net=client.networks.create('solpi-requests-fixture-internal',driver='bridge',internal=True,enable_ipv6=False,options={'com.docker.network.bridge.gateway_mode_ipv4':'isolated'})
        metadata={'network_id':net.id,'network_name':net.name};dump(PRIVATE/'fixture.json',metadata);net.reload();dump(PRIVATE/'network-state-created.json',net.attrs)
        assert net.attrs['Internal'] is True and net.attrs['EnableIPv6'] is False and net.attrs['Options'].get('com.docker.network.bridge.gateway_mode_ipv4')=='isolated' and all(not x.get('Gateway') for x in net.attrs['IPAM']['Config'])
        cert=pathlib.Path(fixture['certificate_root']);mounts={fixture['source_mount']:('/fixture/httpbin',False),fixture['listener_source']:('/listener.sh',False),str(cert/'server.pem'):('/certs/server.pem',False),str(cert/'server.key'):('/certs/server.key',False)}
        c=client.containers.create(fixture['image'],name='solpi-requests-fixture-service',entrypoint='sh',command=['/listener.sh'],network=net.name,mem_limit=536870912,nano_cpus=1_000_000_000,environment={'PYTHONPATH':'/fixture'},log_config=docker.types.LogConfig(type='json-file',config={'max-size':'64k','max-file':'1'}),volumes={src:{'bind':dest,'mode':'ro'} for src,(dest,rw) in mounts.items()})
        metadata['service_id']=c.id;dump(PRIVATE/'fixture.json',metadata);net.disconnect(c);net.connect(c,aliases=['httpbin.org'])
        proof=helper.verify(c,fixture['caps'],mounts,net.name);assert c.attrs['HostConfig']['LogConfig']==fixture['service_log_config'];dump(PRIVATE/'fixture-actual-config.json',proof)
        c.start();time.sleep(2);c.reload();dump(PRIVATE/'fixture-state-after-start.json',c.attrs['State']);assert c.status=='running'
    finally:client.close()

def capture_fixture():
    plan=load(OUT/'execution-plan.json');authorized(plan);metadata=load(PRIVATE/'fixture.json');f=plan['fixture']['diagnostic_capture_source'];assert sha(f)==plan['fixture']['diagnostic_capture_sha256']
    spec=importlib.util.spec_from_file_location('listener_capture',f);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    import docker
    c=docker.from_env(timeout=2);work=PRIVATE/'fixture-evidence';work.mkdir(mode=0o700,exist_ok=True)
    try:record=helper.capture(c.containers.get(metadata['service_id']),work)
    finally:c.close()
    if record.get('status')!='captured':raise RuntimeError('listener evidence unverified')

def cleanup_fixture():
    metadata_path=PRIVATE/'fixture.json'
    if not metadata_path.exists():return
    plan=load(OUT/'execution-plan.json');helper=parity_helper(plan);metadata=load(metadata_path);error=None;records=[]
    evidence=PRIVATE/'fixture-evidence/pre-cleanup-evidence.json'
    if metadata.get('service_id') and (not evidence.exists() or load(evidence).get('status')!='captured'):
        try:
            with (PRIVATE/'private-fixture-capture.log').open('wb') as f:subprocess.run([sys.executable,str(OUT/'run_controls.py'),'--capture-fixture'],stdout=f,stderr=subprocess.STDOUT,timeout=5,check=True)
        except Exception as e:error='capture_'+type(e).__name__
    deadline=time.monotonic()+35
    for kind,key in [('container','service_id'),('network','network_id')]:
        if key not in metadata:continue
        ident=metadata[key]
        try:
            remain=deadline-time.monotonic()
            if remain<=0:raise RuntimeError('fixture cleanup deadline')
            inspection=subprocess.run(['docker',kind,'inspect',ident],capture_output=True,timeout=min(5,remain))
            if helper.absence(inspection,kind,ident):records.append({'id':ident,'absence_verified':True})
            else:records.append(helper.remove(None,kind,ident,deadline))
        except Exception as e:records.append({'id':ident,'absence_verified':False,'error_type':type(e).__name__});error=error or 'cleanup_unverified'
    dump(PRIVATE/'fixture-cleanup.json',{'records':records,'error':error})
    if error:raise RuntimeError('fixture evidence/cleanup failed')

def launch_worker():
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
    start_fixture(plan)
    controls=[]
    for index,c in enumerate(plan['controls']):
        disk_checks(plan,initial);work=PRIVATE/c['run_id'];work.mkdir(mode=0o700)
        dump(work/'control-start.json',{'index':index,'kind':c['kind'],'instance_id':c['instance_id'],'plan_sha256':sha(OUT/'execution-plan.json')});start=time.monotonic()
        try:
            previous=pathlib.Path.cwd()
            try:
                os.chdir(work);p=owned_run([sys.executable,str(OUT/'run_controls.py'),'--worker',str(index)],work/'private-harness.log',900,work/'worker-process.json')
            finally:os.chdir(previous)
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
def launch():
    plan=load(OUT/'execution-plan.json');validate_plan(plan);authorized(plan)
    for f,h in plan['source_hashes'].items():assert sha(f)==h
    PRIVATE.mkdir(mode=0o700,exist_ok=True)
    with (PRIVATE/'phase-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'execution-plan.json')},f)
    error=None
    try:
        r=owned_run([sys.executable,str(OUT/'run_controls.py'),'--phase-worker'],PRIVATE/'private-phase.log',1900,PRIVATE/'phase-process.json')
        if r.returncode:error='phase_worker_failed'
    except Exception as e:error=type(e).__name__
    finally:
        try:drain_recorded_groups()
        except Exception as e:
            dump(OUT/'phase-result.json',{'status':'process_groups_unverified_no_Docker_cleanup','error_type':type(e).__name__,'models':0});raise
        # At most two already-created grader IDs; never infer an unrecorded ID.
        for control in plan['controls']:
            work=PRIVATE/control['run_id'];limits=work/'container-limits.json'
            if limits.exists():
                try:verified_cleanup(load(limits)['container_id'],work/'outer-cleanup.json')
                except Exception as e:error=error or 'grader_cleanup_'+type(e).__name__
        try:cleanup_fixture()
        except Exception as e:error=error or 'fixture_cleanup_'+type(e).__name__
        dump(OUT/'phase-result.json',{'status':'stopped' if error else 'intended_controls_finished','error_type':error,'maximum_controls':2,'combined_attempt_cap':13,'models':0,'pulls':0,'builds':0,'retries':0})
    if error:raise RuntimeError('stop without retry')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--launch',action='store_true');p.add_argument('--worker',type=int);p.add_argument('--phase-worker',action='store_true');p.add_argument('--capture-fixture',action='store_true');p.add_argument('--terminate-group');a=p.parse_args()
    if a.terminate_group:
        plan=load(OUT/'execution-plan.json');authorized(plan);record_path=pathlib.Path(a.terminate_group).resolve();allowed={(PRIVATE/'phase-process.json').resolve()}|{(PRIVATE/c['run_id']/'worker-process.json').resolve() for c in plan['controls']};assert record_path in allowed
        terminal_group(load(record_path),record_path.with_name('process-group-terminal.json'))
    elif a.capture_fixture:capture_fixture()
    elif a.worker is not None:worker(a.worker)
    elif a.phase_worker:
        ownership=PRIVATE/'phase-process.json';deadline=time.monotonic()+5
        while not ownership.exists():
            if time.monotonic()>=deadline:raise RuntimeError('unrecorded phase cannot create fixture')
            time.sleep(.05)
        assert load(ownership)['pid']==os.getpid() and load(ownership)['pgid']==os.getpgrp()
        plan=load(OUT/'execution-plan.json');authorized(plan);assert load(PRIVATE/'phase-start.json')['plan_sha256']==sha(OUT/'execution-plan.json')
        with (PRIVATE/'phase-worker-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'execution-plan.json')},f)
        launch_worker()
    elif a.launch:
        try:launch()
        except Exception as e:
            dump(OUT/'execution-error.json',{'error_type':type(e).__name__,'message':'bounded execution stopped; private logs retained; no retry','model_calls':0});raise
    else:print('prepared only; no controls/fixture')
