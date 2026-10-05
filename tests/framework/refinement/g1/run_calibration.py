"""G1 No-skill calibration only. No candidate selection or old stage entrypoint."""
import datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, threading, time, uuid
G = pathlib.Path(__file__).resolve().parent
R = G.parent / 'pi-takeover'
RT = G / 'runtime'
E = G / 'calibration-attempt-2'
E.mkdir(exist_ok=True)
sys.path[:0] = [str(RT), str(R), str(G), str(G.parent.parent / 'benchmarks')]
import session as S, wrapper as W, actor_profile as A
import queue_admission as Q
from budget_panel import PanelSession, PEER, PROVENANCE
from prospective_body_capacity import factory, session_factory
from private_rejection_journal import RejectionJournal
from owned_capacity_proxy import build as build_proxy, create_args as proxy_args, collect as collect_proxy
from actor_public_inputs import recipe, docker_options, verify_actor_inspect
from task_artifacts import capture_stopped_actor
from task_replay import replay_capture

BINARY = pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')
EXPECTED = '12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'

def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def save(path, value):
    path = pathlib.Path(path); tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n'); tmp.replace(path)
def docker(*args, timeout=30):
    return subprocess.check_output(['docker', *args], stderr=subprocess.PIPE, text=True, timeout=timeout).strip()
def absent(name):
    p = subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10)
    return p.returncode != 0 and 'No such' in p.stderr and name in p.stderr

def sources():
    # Inspect, but never change, the container actually serving port 18001.
    found = []
    for name in docker('ps','--format','{{.Names}}').splitlines():
        if not ('qwen38' in name): continue
        info = json.loads(docker('inspect', name))[0]; cmd = info['Config'].get('Cmd') or []
        text = ' '.join(cmd)
        if '--port 18001' not in text and '--port=18001' not in text: continue
        if info['HostConfig']['NetworkMode'] != 'host': continue
        root = '/sgl-workspace/sglang/python/sglang/'
        files = {'dflash_worker_sha256':root+'srt/speculative/dflash_worker_v2.py', 'dflash_utils_sha256':root+'srt/speculative/dflash_utils.py', 'schedule_batch_sha256':root+'srt/managers/schedule_batch.py', 'dflash_kernel_sha256':root+'kernels/ops/speculative/dflash.py', 'output_streamer_sha256':root+'srt/managers/scheduler_components/output_streamer.py'}
        raw = docker('exec', name, 'sha256sum', *files.values())
        pins = {key:line.split()[0] for key,line in zip(files,raw.splitlines())}
        if pins != {key:PROVENANCE[key] for key in files}: raise RuntimeError('Direct backend source differs from accounting adapter')
        if 'DFLASH' not in text or '--speculative-num-draft-tokens 8' not in text: raise RuntimeError('Direct backend speculative settings changed')
        found.append({'name':name,'id':info['Id'],'image':info['Image'],'cmd_sha256':hashlib.sha256(json.dumps(cmd).encode()).hexdigest(),'source_pins':pins,'peer':PEER})
    if len(found) != 1: raise RuntimeError('Cannot uniquely identify direct18001 backend')
    return found

class CalibrationSession(PanelSession):
    def forward(self, path, body, emit):
        before = self.posts
        observed = Q.snapshot(self.deadline - 10)
        save(self.root / ('queue-before-' + str(before + 1) + '.json'), observed)
        try: return super().forward(path, body, emit)
        finally:
            for row in self.raw_session.records:
                if row['request'] > before:
                    row['observed_queue_before_request'] = observed
            self.raw_session.persist()

# Task-specific capture/preload adapters previously validated on development controls.
def grader_spec(task):
    import cached_grader_setup as cached
    if task == 'build-cython-ext':
        import cython_grader_inputs as module
        return module, module.inputs(), 'none'
    if task == 'build-pmars':
        import pmars_grader_setup as module
        return module, {}, 'none'
    if task == 'sparql-university':
        import sparql_grader_setup as module
        return module, module.inputs(), 'none'
    if task == 'train-fasttext':
        import fasttext_grader_setup_r2 as module
        return module, module.inputs(), 'none'
    if task == 'financial-document-processor':
        import financial_grader_setup as module
        return module, {'mounts':['/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']}, 'bridge'
    if task == 'make-doom-for-mips':
        import doom_grader_setup as module
        return module, {'mounts':['/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro']}, 'bridge'
    return cached, cached.inputs(), 'none'

def terminal_grade(task, actor, spec, d, prefix, owned, row, baseline=None):
    image = spec['grader_image_id']; captured = d/'captured'; mode = 'full'; dynamic = None
    if task == 'build-cython-ext':
        from stopped_cython_output import classify_stopped
        state = classify_stopped(actor, spec['actor_image_id']); row['output_classification'] = state
        if state['output_state'] == 'present': dynamic = state['dynamic']
        else: mode = 'cython_partial'
    elif task == 'build-pmars':
        from discover_task_layout import discover_stopped_layout
        dynamic = discover_stopped_layout(task,actor,spec['actor_image_id'])
    elif task == 'financial-document-processor': mode = 'financial'
    elif task == 'make-doom-for-mips':
        from doom_output import classify_stopped
        state = classify_stopped(actor,spec['actor_image_id']); row['output_classification'] = state
        if state['output_state'] != 'present': mode = 'doom_missing'
    elif task in ('break-filter-js-from-html','regex-log','sparql-university','train-fasttext'):
        # Presence helpers retain double-identity Docker archive witnesses.
        import importlib
        name = {'break-filter-js-from-html':'matched_html_support','regex-log':'regex_output_presence','sparql-university':'sparql_output_presence','train-fasttext':'fasttext_output_presence'}[task]
        if not importlib.import_module(name).stopped_output_present(actor,spec['actor_image_id']): mode = 'absent'
    if mode == 'financial':
        import financial_output as output
        row['capture'] = output.capture_stopped(actor,spec['actor_image_id'],captured)
    elif mode == 'cython_partial':
        import cython_partial_output as output
        row['capture'] = output.capture_partial(actor,spec['actor_image_id'],captured)
    elif mode == 'doom_missing':
        import doom_output as output
        row['capture'] = output.capture_missing(actor,spec['actor_image_id'],captured)
    elif mode == 'absent': row['capture'] = {'output_absent_verified':True}
    else:
        row['capture'] = capture_stopped_actor(task,actor,spec['actor_image_id'],captured,dynamic=dynamic,protected_baseline=baseline)
        if task == 'overfull-hbox' and not row['capture']['protected_input_gate_passed']: raise RuntimeError('Protected TeX input changed')
    module, preload, network = grader_spec(task)
    grade = prefix+'-grade'; owned.append(grade); logs = d/'logs'; (logs/'verifier').mkdir(parents=True)
    args = ['create','--pull=never','--name',grade,'--network',network,'--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(pathlib.Path(row['source'])/'tests')+':/tests:ro','-v',str(logs)+':/logs']
    for mount in preload.get('mounts',[]): args += ['-v',mount]
    for key,value in preload.get('environment',{}).items(): args += ['-e',key+'='+value]
    docker(*args,'--entrypoint','/bin/sh',image,'-c','sleep infinity')
    if mode == 'financial': row['replay'] = output.replay(captured,grade,image,actor_image_id=spec['actor_image_id'])
    elif mode == 'cython_partial': row['replay'] = output.replay_partial(captured,grade,image)
    elif mode == 'doom_missing': row['replay'] = output.replay_missing(captured,grade,image,actor_image_id=spec['actor_image_id'])
    elif mode == 'absent': docker('start',grade); row['replay'] = {'verified_actor_output_absence':True,'fresh_original_baseline':True}
    else: row['replay'] = replay_capture(task,captured,grade,image,dynamic=dynamic,actor_image_id=spec['actor_image_id'])
    if task == 'build-cython-ext': row['dependency_setup'] = module.prepare(grade,image,installation_absent=mode=='cython_partial')
    else: row['dependency_setup'] = module.prepare(grade,image,d)
    command = module.grade_argv(grade) if hasattr(module,'grade_argv') else ['docker','exec','-w','/app','-e','UV_OFFLINE=1','-e','UV_PYTHON_DOWNLOADS=never',grade,'bash','/tests/test.sh']
    with (d/'verifier.log').open('wb') as out: z = subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,timeout=600)
    docker('stop','-t','0',grade); docker('rm',grade); owned.remove(grade)
    if not absent(grade): raise RuntimeError('Grader cleanup uncertain')
    reward = logs/'verifier/reward.txt'; ctrf = logs/'verifier/ctrf.json'
    row['reward'] = reward.read_text().strip() if reward.exists() else None
    tests = json.loads(ctrf.read_text())['results']['tests'] if ctrf.exists() else []
    row['test_events'] = len(tests); row['verifier_exit'] = z.returncode
    if not tests or row['reward'] not in ('0','1'): raise RuntimeError('Original grade unavailable')
    row['solved'] = row['reward']=='1' and all(t['status']=='passed' for t in tests)


def main():
    contract = json.loads((G/'calibration-contract.json').read_text())
    assert contract['arms'] == ['No skill'] and contract['model_endpoint']=='http://127.0.0.1:18001/v1'
    assert sha(BINARY)==EXPECTED and Q.PORTS==(18001,)
    assert not (E/'calibration-launch.json').exists(), 'No full-actor or stage retry'
    end = datetime.datetime.fromisoformat(contract['window_end']).timestamp()
    deadline = time.monotonic() + end - time.time()
    if deadline <= time.monotonic(): raise RuntimeError('Window expired; no automatic extension')
    pins = {p.name:sha(p) for p in RT.glob('*.py')}
    live = sources(); root = pathlib.Path('/tmp/solpi-g1-cal-'+uuid.uuid4().hex[:12]); root.mkdir(mode=0o700)
    prefix = root.name; net = prefix+'-net'; owned=[]; rows=[]; error=None; server=None; session=None; proxy_spec=None
    plan = {'contract_sha256':sha(G/'calibration-contract.json'),'runtime_hashes':pins,'orchestration_sha256':sha(__file__),'root':str(root),'prefix':prefix,'binary_sha256':EXPECTED,'backend':live,'native_starts':0,'model_POST':0,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'helper_hashes':{p.name:sha(p) for p in R.glob('*.py') if 'copilot_' not in p.name},'task_source_hashes':{t['id']:W.files(t['source']) for t in contract['development_pool']}}
    plan['launch_commit'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=G,text=True).strip()
    save(E/'calibration-launch.json',plan)
    try:
        docker('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',net)
        topology=json.loads(docker('network','inspect',net))[0]
        assert topology['Internal'] and not topology['EnableIPv6'] and all(not c.get('Gateway') for c in topology['IPAM']['Config'])
        sockdir=root/'broker';sockdir.mkdir(mode=0o700);sock=sockdir/'broker.sock'
        proxy_spec=build_proxy(root/'proxy-bundle',RT,pins);rejections=RejectionJournal(root/'broker-rejections.json')
        B=factory(RT/'server.py',pins['server.py'],rejections); C=session_factory(RT/'session.py',pins['session.py'])
        session=CalibrationSession(C.Session(root/'transport',{'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':net}))
        handler=type('G1Handler',(B.PostHandler,),{'session':session});server=B.OwnedUnixServer(str(sock),handler);sock.chmod(0o600);threading.Thread(target=server.serve_forever,daemon=True).start()
        proxy=prefix+'-proxy';owned.append(proxy);docker(*proxy_args(proxy_spec,proxy,net,S.IMAGE,sockdir,os.getuid(),os.getgid()));docker('start',proxy)
        ready=time.monotonic()+20
        while 'owned_capacity_proxy_ready' not in docker('logs',proxy):
            if time.monotonic()>ready:raise RuntimeError('Proxy startup expired')
            time.sleep(.1)
        for index, task in enumerate(contract['development_pool']):
            if time.monotonic()+7200>deadline:break
            ident=task['id'];d=root/str(index);d.mkdir();(d/'skills').mkdir();row={'task':ident,'source':task['source'],'arm':'No skill','family':task['family'],'solved':None}; rows.append(row)
            save(E/'calibration-progress.json',{'rows':rows,'starts':session.starts,'POST':session.posts,'current_task':ident})
            if sources()!=live or W.files(task['source'])!=plan['task_source_hashes'][ident]:raise RuntimeError('Source identity changed')
            if any(sha(RT/name)!=value for name,value in pins.items()) or any(sha(R/name)!=value for name,value in plan['helper_hashes'].items()):raise RuntimeError('Runtime/helper source changed')
            if task['family']=='aider-polyglot':
                import polyglot
                prepared=d/'prepared';manifest=polyglot.prepare('/tmp/solpi-polyglot-grader-source',ident,prepared)
                spec={'actor_image_id':S.IMAGE,'grader_image_id':S.IMAGE,'cpus':1,'memory_mb':2048,'mounts':[],'environment':{},'guidance':''}
                instruction=(prepared/'prompt.txt').read_text()
            else:
                if ident=='regex-log':
                    from regex_actor_inputs import recipe as regex_recipe
                    spec=regex_recipe(ident)
                else: spec=recipe(ident)
                instruction=(pathlib.Path(task['source'])/'instruction.md').read_text()
            prompt=instruction+'\n\n'+spec['guidance']+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. No skill is supplied.\n'
            (d/'prompt.txt').write_text(prompt);row['prompt_sha256']=sha(d/'prompt.txt');row['recipe']=spec
            name=prefix+'-'+str(index);owned.append(name)
            args=['create','--pull=never','--name',name,'--network',net,'--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=128m','-v',str(d/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-w','/app','--entrypoint','/bin/sh']
            for e in ['HOME=/root/solpi-home','CODEX_HOME=/root/solpi-home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']:args+=['-e',e]
            args+=docker_options(spec);argv=A.argv('codex',8000,d)
            docker(*args,spec['actor_image_id'],'-c','mkdir -p "$CODEX_HOME" && exec /opt/solpi/codex "$@"','g1',*argv[1:])
            inspect=json.loads(docker('inspect',name))[0];verify_actor_inspect(inspect,spec,net,{'/skills':str(d/'skills'),'/opt/solpi/codex':str(BINARY)})
            baseline=None
            if task['family']=='aider-polyglot':docker('cp',str(prepared/'workspace')+'/.',name+':/app')
            if ident=='overfull-hbox':
                from tex_protected_baseline import capture_before
                proof=capture_before(name,spec['actor_image_id'],d/'before');baseline=proof['protected_baseline']
            admission=Q.admit(d/'admission.json',deadline-7200)
            if time.monotonic()+7200>deadline:break
            session.begin(ident,admission[0]['load']);start=time.monotonic()
            session.raw_session.deadline=min(session.deadline,deadline)
            samples=[{'kind':'start','observations':admission}]; sampler_stop=threading.Event()
            def sample_load():
                while not sampler_stop.wait(30):
                    samples.append({'kind':'periodic','observations':Q.snapshot(session.deadline)})
                    save(d/'load-samples.json',samples)
            save(d/'load-samples.json',samples)
            sampler=threading.Thread(target=sample_load,daemon=True);sampler.start()
            try:
                with (d/'native.jsonl').open('wb') as out:
                    p=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT)
                    try:p.wait(timeout=max(.1,session.deadline-time.monotonic()-10))
                    except subprocess.TimeoutExpired:row['actor_deadline_interrupted']=True
                    docker('stop','-t','0',name);p.wait(timeout=5)
            finally:
                sampler_stop.set();sampler.join(timeout=5)
                if sampler.is_alive():raise RuntimeError('Load sampler cleanup uncertain')
            row['load_at_start']=admission;row['periodic_load_samples']=samples
            row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start,native_trace_sha256=sha(d/'native.jsonl'))
            until=time.monotonic()+240
            while server.workers and time.monotonic()<until:time.sleep(.2)
            if server.workers or session.connections:raise RuntimeError('Owned provider completion uncertain')
            requests=session.accounting_rows(ident)
            row.update(provider_POST=len(requests),unknown_cost_requests=[x['request'] for x in requests if not x.get('usage_complete')],provider_tokens_lower_bound=sum(x['usage_audit']['gross_tokens'] for x in requests if x.get('usage_complete')),cost_complete=bool(requests) and all(x.get('usage_complete') for x in requests),backends=[x['provider_backend'] for x in requests],queue_records=[x['observed_queue_before_request'] for x in requests])
            if any(x!=PEER for x in row['backends']):raise RuntimeError('Direct route mismatch; no fallback')
            if any(not x['stream_eof'] or x.get('error') for x in requests):raise RuntimeError('Provider completion uncertain; no further actor')
            try:
                if task['family']=='terminal-bench-2':terminal_grade(ident,name,spec,d,prefix+'-'+str(index),owned,row,baseline)
                else:
                    work=d/'final-work';work.mkdir();docker('cp',name+':/app/.',str(work))
                    grade=prefix+'-go-grade';owned.append(grade)
                    docker('create','--pull=never','--name',grade,'--network','none','--cpus','1','--memory','2g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-e','HOME=/tmp','-e','GOCACHE=/tmp/go-cache','-e','GOPROXY=off','-e','GOSUMDB=off','-e','GOTOOLCHAIN=local','-v',str(work)+':/workspace:ro','-v',str(prepared/'grader')+':/grader:ro','--entrypoint','python3',S.IMAGE,'/grader/grade.py')
                    with (d/'verifier.log').open('wb') as out:z=subprocess.run(['docker','start','-a',grade],stdout=out,stderr=subprocess.STDOUT,timeout=240)
                    docker('rm',grade);owned.remove(grade);row.update(verifier_exit=z.returncode,solved=z.returncode==0 if z.returncode in (0,1) else None)
            except Exception as e:row['grade_error']={'type':type(e).__name__,'message':str(e)[:300]}
            observed=row['queue_records']+[sample['observations'] for sample in samples]
            row['heavy_load']=any(any(r.get('num_waiting_reqs',0)>0 or r.get('num_reqs',0)>=6 for r in q[0].get('load',[]) if isinstance(r,dict)) for q in observed if isinstance(q[0].get('load'),list))
            row['contention_observed']=row['heavy_load']
            row['contention_exclusion']=False;row['wall_time_inflation']='Possible when contention observed; not causally identifiable from load alone'
            session.finish(True);docker('rm',name);owned.remove(name)
            save(E/'calibration-progress.json',{'rows':rows,'starts':session.starts,'POST':session.posts,'current_task':None})
    except Exception as e:error={'type':type(e).__name__,'message':str(e)[:500]}
    finally:
        proxy_journal=None;cleanup_errors=[]
        for name in owned:
            try:docker('rm','-f',name)
            except Exception as e:cleanup_errors.append(str(e)[:150])
        if session:session.abort_owned_connections()
        if server:
            try:server.cleanup()
            except Exception as e:cleanup_errors.append(str(e)[:150])
        try:docker('network','rm',net)
        except Exception as e:cleanup_errors.append(str(e)[:150])
        if proxy_spec:
            try:proxy_journal=collect_proxy(proxy_spec)
            except Exception as e:cleanup_errors.append(str(e)[:150])
        result={'contract_sha256':plan['contract_sha256'],'root':str(root),'rows':rows,'starts':session.starts if session else 0,'POST':session.posts if session else 0,'error':error,'cleanup_errors':cleanup_errors,'owned_containers_absent':all(absent(n) for n in owned),'proxy_journal':proxy_journal,'verified_solves':sum(r.get('solved') is True for r in rows),'budget_pass':sum(r.get('solved') is True for r in rows)>=5 and not cleanup_errors,'not_started':[t['id'] for t in contract['development_pool'] if t['id'] not in {r['task'] for r in rows if 'native_exit' in r}],'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Step 3 calibration only; no savings or confirmation claim'}
        save(E/'calibration-result.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
