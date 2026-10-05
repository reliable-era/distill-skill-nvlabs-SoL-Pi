"""Guarded native readiness orchestration; requires frozen routing pass and root review."""
import sys
import contextlib,argparse,hashlib,importlib.util,json,os,pathlib,resource,subprocess,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'runtime'))
def module(name):
 s=importlib.util.spec_from_file_location(name,R/'runtime'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
S=module('session');W=module('wrapper');B=module('server');A=module('actor_profile')
sha=lambda f:hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
def remaining(deadline,cap):
 value=min(cap,deadline-time.monotonic()) if deadline else cap
 if value<=0:raise TimeoutError('actor deadline exhausted')
 return value
def cmd(*args,deadline=None):return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.PIPE,timeout=remaining(deadline,8)).strip()
def absent(kind,name,deadline=None):
 z=subprocess.run(['docker',*(['inspect',name] if kind=='container' else ['network','inspect',name])],capture_output=True,text=True,timeout=remaining(deadline,3))
 expected=('Error: No such object: '+name,'Error response from daemon: No such container: '+name) if kind=='container' else ('Error: No such network: '+name,'Error response from daemon: network '+name+' not found')
 return z.returncode!=0 and z.stderr.strip() in expected
def remove(name,deadline=None):
 subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=remaining(deadline,5))
 if not absent('container',name,deadline):raise RuntimeError('container absence uncertain')
def certificate_ok(report,cert):
 if report.get('status')!='PASS_GET_only_transport' or report.get('exit_code')!=0 or report.get('plan_sha256')!=cert['route_plan_sha256']:return False
 e=report.get('evidence',{});routing=e.get('routing',{})
 if e.get('errors')!=[] or e.get('POST')!=0 or e.get('native_starts')!=0 or e.get('broker_socket_absent') is not True or e.get('broker_workers_remaining')!=0:return False
 if routing.get('models')!='Qwen3.8-27B-FP8' or any(routing.get(k) is not True for k in ['authority','path']):return False
 if report.get('independent_remaining_owned')!={'containers':[],'networks':[]}:return False
 nets=report.get('actual_network_inspect',[])
 if len(nets)!=1 or nets[0]!={'internal':True,'ipv6':False,'gateway_present':False}:return False
 actors=report.get('actual_container_inspect',[])
 if len(actors)!=2 or any(a.get('nano_cpus')!=1000000000 or a.get('memory')!=536870912 or len(a.get('networks',[]))!=1 for a in actors):return False
 proxy=next((a for a in actors if a.get('name','').endswith('-proxy')),None);probe=next((a for a in actors if a.get('name','').endswith('-probe')),None)
 if proxy is None or probe is None or probe.get('mounts')!=[] or proxy['networks']!=probe['networks']:return False
 mounts=proxy.get('mounts',[])
 if len(mounts)!=2 or any(m.get('RW') is not False for m in mounts):return False
 socket=next((m for m in mounts if m.get('destination')=='/broker'),{})
 if not socket.get('source','').startswith('/tmp/solpi-qwenroute-'+cert['route_plan_sha256']+'/socket'):return False
 proofs=e.get('absence_proofs',[])
 return len(proofs)==3 and all(p.get('absence_verified') is True for p in proofs) and sorted(p.get('kind') for p in proofs)==['container','container','network']
def actor_transport_error(requests,expected_POSTs,upstream_drained,actor_removed):
 if not upstream_drained or not actor_removed:return 'owned cleanup not verified'
 if len(requests)!=expected_POSTs or len({z.get('request') for z in requests})!=len(requests):return 'provider request observability uncertain'
 if any(z.get('error') and not z.get('actor_budget_exhaustion') for z in requests):return 'non-budget provider/transport error'
 return None
def validate(p,digest):
 if p.get('combined_maximum_native_starts')!=18 or p.get('combined_maximum_provider_POST_total')!=244 or p['prior_consumed_attempts']['native_starts']!=6 or p['prior_consumed_attempts']['provider_POST']!=52:raise RuntimeError('combined attempt caps')
 if (p.get('maximum_native_starts'),p.get('seconds_per_actor'),p.get('retries'),p.get('maximum_provider_POST_total'),p.get('maximum_provider_POST_per_actor'))!=(12,600,0,192,16):raise RuntimeError('caps')
 W.validate_inputs(p)
 for f,h in p['source_hashes'].items():
  if sha(R/f)!=h:raise RuntimeError('source mismatch')
 cert=p.get('routing_certificate',{})
 if not cert.get('path') or not cert.get('sha256') or sha(cert['path'])!=cert['sha256']:raise RuntimeError('routing pass unbound')
 report=json.loads(pathlib.Path(cert['path']).read_text())
 if not certificate_ok(report,cert):raise RuntimeError('routing certificate invalid')
 route_plan=pathlib.Path(cert['route_plan_path'])
 if sha(route_plan)!=cert['route_plan_sha256']:raise RuntimeError('routing plan changed')
 frozen=json.loads(route_plan.read_text())
 if frozen['source_hashes']!=cert['route_source_hashes']:raise RuntimeError('routing source bindings changed')
 for name,h in cert['route_source_hashes'].items():
  if sha(route_plan.parent/name)!=h:raise RuntimeError('routing source changed')
 auth=json.loads((R/'execution-authorization.json').read_text())
 if auth.get('plan_sha256')!=digest or auth.get('maximum_starts')!=12:raise RuntimeError('root authorization missing')
 cert=auth.get('grading_certificate',{})
 if cert.get('sha256')!=p['grading_reuse']['certificate_sha256'] or sha(R/'grading-plan.json')!=p['grading_reuse']['grading_plan_sha256']:raise RuntimeError('grading reuse provenance changed')
 if sha(p['prior_consumed_attempts']['audit_path'])!=p['prior_consumed_attempts']['audit_sha256']:raise RuntimeError('prior consumed audit changed')
 if not cert.get('path') or not cert.get('sha256') or sha(cert['path'])!=cert['sha256']:raise RuntimeError('independent grading certificate absent')
 control=json.loads((R/'grading-plan.json').read_text());report=json.loads(pathlib.Path(cert['path']).read_text())
 if control['screen_plan_sha256']!=p['grading_reuse']['origin_screen_plan_sha256'] or auth.get('grading_plan_sha256')!=p['grading_reuse']['grading_plan_sha256'] or report.get('plan_sha256')!=sha(R/'grading-plan.json'):raise RuntimeError('grading certificate plan mismatch')
 for name,h in p['grading_reuse']['adapter_source_hashes'].items():
  if sha(R/name)!=h:raise RuntimeError('reused grading adapter changed')
 if report.get('success') is not True or report.get('errors')!=[] or report.get('native_starts')!=0 or report.get('POST')!=0 or len(report.get('controls',[]))!=6 or any(x.get('expected_matched') is not True for x in report['controls']):raise RuntimeError('independent grading controls not passed')
 if p.get('hosthop_mode')!='reviewed_unix_proxy_only':raise RuntimeError('unproven hosthop mode')
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-development-screen',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args();digest=sha(R/'plan.json')
 if not x.execute_development_screen or digest!=x.plan_sha256:raise SystemExit('explicit plan hash authorization required')
 p=json.loads((R/'plan.json').read_text());validate(p,digest)
 root=pathlib.Path('/tmp')/('solpi-qwendev-'+digest);root.mkdir(mode=0o700,exist_ok=False);(root/'launch.json').write_text(json.dumps({'plan':digest}))
 owned=[];nets=[];servers=[];errors=[];session=None;actors=[];proofs={'topology':None,'proxy':None,'actors':[],'cleanup':{'server_workers':None,'socket_absent':None,'containers':[],'networks':[]}};prefix='solpi-qwendev-'+uuid.uuid4().hex[:10];locks=contextlib.ExitStack()
 try:
  locks.enter_context(S.inference_locks(p['shared_inference_locks']))
  if True:
   S.wait_idle(root/'idle'/'topology.json')
   if cmd('image','inspect','--format','{{.Id}}',S.IMAGE)!=S.IMAGE:raise RuntimeError('image mismatch')
   n=prefix+'-actor';nets.append(n);cmd('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',n)
   actor=json.loads(cmd('network','inspect',n))[0]
   if actor.get('Internal') is not True or actor.get('EnableIPv6') is not False or actor.get('Options',{}).get('com.docker.network.bridge.gateway_mode_ipv4')!='isolated' or not actor['IPAM']['Config'] or any(z.get('Gateway') for z in actor['IPAM']['Config']):raise RuntimeError('topology mismatch')
   proofs['topology']={'internal':actor['Internal'],'ipv6':actor['EnableIPv6'],'gateway_mode':actor['Options']['com.docker.network.bridge.gateway_mode_ipv4'],'gateways':[x.get('Gateway') for x in actor['IPAM']['Config']]}
   topo={'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':n}
   session=S.Session(root/'transport',topo);handler=type('OwnedPost',(B.PostHandler,),{'session':session});sockdir=root/'broker';sockdir.mkdir(mode=0o700);sockpath=sockdir/'broker.sock';server=B.OwnedUnixServer(str(sockpath),handler);sockpath.chmod(0o600);servers.append(server);threading.Thread(target=server.serve_forever,daemon=True).start();port=8000
   proxy=prefix+'-proxy';owned.append(proxy)
   cmd('create','--pull=never','--name',proxy,'--network',n,'--user',str(os.getuid())+':'+str(os.getgid()),'--network-alias','proxy','--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',str(R)+':/app:ro',S.IMAGE,'/app/runtime/stream_proxy.py')
   q=json.loads(cmd('inspect',proxy))[0]
   proxy_mounts=q['Mounts'];proxy_caps=q['HostConfig'];expected_sources={'/broker':str(sockdir),'/app':str(R)}
   proxy_ok=set(q['NetworkSettings']['Networks'])==set(nets) and proxy_caps.get('Memory')==536870912 and proxy_caps.get('NanoCpus')==1000000000 and proxy_caps.get('PidsLimit')==32 and q['Config'].get('User')==str(os.getuid())+':'+str(os.getgid()) and len(proxy_mounts)==2 and all(z.get('RW') is False and z.get('Source')==expected_sources.get(z.get('Destination')) for z in proxy_mounts)
   proofs['proxy']={'verified':proxy_ok,'user':q['Config'].get('User'),'nano_cpus':proxy_caps.get('NanoCpus'),'memory':proxy_caps.get('Memory'),'pids':proxy_caps.get('PidsLimit'),'mounts':[{'source':z['Source'],'destination':z['Destination'],'RW':z['RW']} for z in proxy_mounts],'networks':list(q['NetworkSettings']['Networks'])}
   if not proxy_ok:raise RuntimeError('proxy mounts/UID/resources/topology mismatch')
   cmd('start',proxy)
   for cell in p['schedule']:
    harness=cell['id'];task=p['tasks'][cell['family']];image=task['image_id']
    session.begin(harness,S.wait_idle(root/'idle'/(harness+'.json')));d=W.prepare(root/harness,port,task,cell['arm']);name=prefix+'-'+harness;owned.append(name)
    env=['HOME=/tmp/home','CODEX_HOME=/tmp/home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']
    args=['docker','create','--pull=never','--name',name,'--network',nets[0],'--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','64','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,size=64m','-v',str(d/'home')+':/tmp/home','-v',str(d/'work')+':'+task['actor_workdir'],'-v',str(d/'skills')+':/skills:ro','-w',task['actor_workdir'],'--entrypoint','/bin/sh']
    for e in env:args+=['-e',e]
    args +=[image,*W.shell(A.argv('codex',port,d))[1:]]
    row={'id':harness,'family':cell['family'],'arm':cell['arm'],'availability':'started','usage_complete':None};actors.append(row)
    # Inspect inert container before any native executable runs.
    if cmd('image','inspect','--format','{{.Id}}',image)!=image:raise RuntimeError('task actor image mismatch')
    subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=remaining(session.deadline,8))
    inspect=json.loads(cmd('inspect',name,deadline=session.deadline))[0];h=inspect['HostConfig'];mounts=inspect['Mounts']
    destinations={z['Destination'] for z in mounts};environment=set(inspect['Config']['Env'])
    expected_mounts={'/tmp/home':(str(d/'home'),True),task['actor_workdir']:(str(d/'work'),True),'/skills':(str(d/'skills'),False)}
    if any((z.get('Source'),z.get('RW'))!=expected_mounts.get(z.get('Destination')) for z in mounts):raise RuntimeError('actor mount source/RW mismatch')
    if inspect.get('Image')!=image or inspect['Config'].get('User')!=str(os.getuid())+':'+str(os.getgid()) or h.get('NanoCpus')!=1000000000 or h.get('Memory')!=536870912 or h.get('PidsLimit')!=64 or h.get('ReadonlyRootfs') is not True or h.get('Privileged') is not False or h.get('CapDrop')!=['ALL'] or set(inspect['NetworkSettings']['Networks'])!={nets[0]} or destinations!={'/tmp/home',task['actor_workdir'],'/skills'} or next(z for z in mounts if z['Destination']=='/skills')['RW'] is not False or any('/broker' in z['Destination'] or str(sockdir) in z.get('Source','') for z in mounts) or not set(env).issubset(environment):raise RuntimeError('actor isolation/resources/env mismatch')
    proofs['actors'].append({'harness':harness,'prestart_verified':True,'user':inspect['Config']['User'],'nano_cpus':h['NanoCpus'],'memory':h['Memory'],'pids':h['PidsLimit'],'mounts':[{'source':z['Source'],'destination':z['Destination'],'RW':z['RW']} for z in mounts],'networks':list(inspect['NetworkSettings']['Networks'])})
    row['prestart_inspection_verified']=True;log=d/'native.jsonl';start=time.monotonic()
    def bound():resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152))
    with log.open('wb') as out:
     log.chmod(0o600);process=subprocess.Popen(['docker','start','-a',name],stdout=out,stderr=subprocess.STDOUT,preexec_fn=bound)
     try:process.wait(timeout=remaining(session.deadline, max(.01,session.deadline-time.monotonic()-10)))
     except subprocess.TimeoutExpired:row['availability']='deadline_interrupted'
     finally:
      remove(name,session.deadline);proofs['cleanup']['containers'].append({'name':name,'absence_verified':True});owned.remove(name);process.wait(timeout=remaining(session.deadline,2));row.update(exit=process.returncode,native_phase_seconds=time.monotonic()-start,native_log_sha256=sha(log))
    rows=[]
    for line in log.read_text(errors='replace').splitlines():
     try:rows.append(json.loads(line))
     except ValueError:pass
    row['diagnostic_trace_metrics']=W.trace_metrics(rows)
    aux=[z.get('type') for z in rows if any(k in str(z.get('type','')).lower() for k in ['compaction','subagent'])]
    # Read parser intentionally unknown until pinned native event schema observed.
    session.abort_owned_connections()
    until=time.monotonic()+3
    while server.workers and time.monotonic()<until:time.sleep(.01)
    if server.workers:raise RuntimeError('owned upstream drain uncertain before grading')
    row['upstream_drained_before_grade']=True
    row['actor_removed_verified']=name not in owned
    W.capture(d,task);grade=W.grade(d,task);row['grade']=grade
    actor_requests=[z for z in session.records if z['actor']==harness]
    normalized=[z['usage_audit'] for z in actor_requests if z.get('usage_complete')]
    row['observed_gross_tokens_lower_bound']=sum(z['gross_tokens'] for z in normalized)
    row['native_usage_reconciliation']=W.reconcile_native(rows,actor_requests)
    row['native_reconciled']=row['native_usage_reconciliation']['complete']
    row['provider_cost_complete']=bool(actor_requests) and len(actor_requests)==session.per_actor[harness] and all(z.get('usage_complete') and z.get('provider_status')==200 and z.get('error') is None for z in actor_requests) and not aux and row['upstream_drained_before_grade']
    row['usage_complete']=row['provider_cost_complete']
    row['protocol_valid']=all(z.get('usage_audit',{}).get('protocol_valid') is True for z in actor_requests) if row['provider_cost_complete'] else False if any(z.get('usage_audit',{}).get('protocol_valid') is False for z in actor_requests) else None
    row['protocol_violations']=[{'request':z['request'],'violations':z['usage_audit']['protocol_violations']} for z in actor_requests if z.get('usage_audit',{}).get('protocol_valid') is False]
    row['accounting_scope']='All this actor broker-observed Responses POSTs only; native reconciliation separately reported; helpers/account-wide traffic/dollars TBD'
    row['transport_pass']=bool(actor_requests) and all(z['error'] is None and z['provider_status']==200 for z in actor_requests)
    row['local_budget_denials']=[z for z in session.budget_denials if z['actor']==harness]
    row['actor_budget_exhaustion']=row.get('availability')=='deadline_interrupted' or any(z.get('actor_budget_exhaustion') for z in actor_requests) or any(z['reason'] in ('per_actor_POST_cap','actor_deadline_reserve') for z in row['local_budget_denials'])
    row['quality_status']='pass' if grade['solved'] is True else 'fail' if grade['solved'] is False else 'ungraded'
    row['scope']='reused development fixture; no readiness/confirmation certification'
    session.finish(True,aux)
    (root/'partial-evidence.json').write_text(json.dumps({'actors':actors,'native_starts':session.starts,'POST':session.posts},indent=2))
    if server.workers:raise RuntimeError('broker worker active after actor')
    if row['protocol_valid'] is False:raise RuntimeError('provider protocol violation; reported traffic cost retained')
    if grade.get('infrastructure_error'):raise RuntimeError('official grader infrastructure failure')
    transport_error=actor_transport_error(actor_requests,session.per_actor[harness],row['upstream_drained_before_grade'],row['actor_removed_verified'])
    if transport_error:raise RuntimeError(transport_error)
 except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e)[:300]})
 finally:
  # Terminate our actor/proxy clients before draining owned broker workers.
  for name in reversed(owned.copy()):
   try:remove(name);proofs['cleanup']['containers'].append({'name':name,'absence_verified':True});owned.remove(name)
   except Exception:errors.append({'cleanup':'container','name':name})
  if session:proofs['cleanup']['aborted_owned_upstreams']=session.abort_owned_connections()
  for server in reversed(servers):
   try:server.cleanup();proofs['cleanup']['server_workers']=server.workers
   except Exception as e:errors.append({'cleanup':'server','type':type(e).__name__})
  for name in reversed(owned.copy()):
   try:remove(name);proofs['cleanup']['containers'].append({'name':name,'absence_verified':True});owned.remove(name)
   except Exception:errors.append({'cleanup':'container','name':name})
  for n in reversed(nets.copy()):
   try:cmd('network','rm',n)
   except Exception:pass
   try:
    if absent('network',n):proofs['cleanup']['networks'].append({'name':n,'absence_verified':True});nets.remove(n)
    else:errors.append({'cleanup':'network','name':n})
   except Exception:errors.append({'cleanup':'network_inspect','name':n})
  if 'sockpath' in locals():
   try:
    sockpath.unlink(missing_ok=True);proofs['cleanup']['socket_absent']=not sockpath.exists()
    if not proofs['cleanup']['socket_absent']:raise RuntimeError('socket remains')
   except Exception:errors.append({'cleanup':'unix_socket'})
  locks.close()
  (root/'final-evidence.json').write_text(json.dumps({'plan_sha256':digest,'actual_proofs':proofs,'actors':actors,'errors':errors,'containers_remaining':owned,'networks_remaining':nets,'native_starts':session.starts if session else 0,'provider_POST':session.posts if session else 0,'combined_native_starts':6+(session.starts if session else 0),'combined_provider_POST':52+(session.posts if session else 0),'prior_consumed_attempts':p['prior_consumed_attempts'],'usage_complete':None},indent=2)+'\n')
 if errors:raise SystemExit('failed: private evidence retained; no retries')
if __name__=='__main__':main()
