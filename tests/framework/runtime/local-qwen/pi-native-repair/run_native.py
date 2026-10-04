"""Guarded native readiness orchestration; requires frozen routing pass and root review."""
import contextlib,argparse,hashlib,importlib.util,json,os,pathlib,resource,subprocess,threading,time,uuid
R=pathlib.Path(__file__).resolve().parent
def module(name):
 s=importlib.util.spec_from_file_location(name,R/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
S=module('session');W=module('wrapper');B=module('server')
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
def validate(p,digest):
 if (p.get('maximum_native_starts'),p.get('seconds_per_actor'),p.get('retries'),p.get('maximum_provider_POST_total'),p.get('maximum_provider_POST_per_actor'))!=(1,90,0,4,4):raise RuntimeError('caps')
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
 mock=p['SDK_tunnel_mock_certificate']
 if sha(mock['path'])!=mock['sha256']:raise RuntimeError('SDKtunnelmockcertificatechanged')
 proof=json.loads(pathlib.Path(mock['path']).read_text());result=proof.get('result',{})
 if proof.get('diagnosis_category')!='SDK_CONNECT_Unix_mock_HTTP400' or proof.get('errors')!=[] or proof.get('cleanup_absence_verified') is not True or result.get('CONNECT_attempts')!=1 or result.get('POST')!=1 or result.get('sdk_status')!=400 or result.get('workers')!={'proxy':0,'broker':0} or result.get('socket_absent') is not True:raise RuntimeError('SDKtunnelmocknotproved')
 auth=json.loads((R/'execution-authorization.json').read_text())
 if auth.get('plan_sha256')!=digest or auth.get('maximum_starts')!=1:raise RuntimeError('root authorization missing')
 if p.get('hosthop_mode')!='reviewed_unix_proxy_only':raise RuntimeError('unproven hosthop mode')
def read_evidence(harness,events):
 import re
 pending={}
 for e in events:
  if harness=='pi':
   if e.get('type')=='tool_execution_start' and e.get('toolName')=='read' and pathlib.PurePosixPath(e.get('args',{}).get('path','')).name=='add.py':pending[e.get('toolCallId')]=True
   if e.get('type')=='tool_execution_end' and e.get('toolCallId') in pending and e.get('isError') is False:return True
  elif e.get('type')=='item.completed':
   item=e.get('item',{});command=item.get('command','')
   if item.get('type')=='command_execution' and item.get('exit_code')==0 and re.search(r'\bcat\s+(?:/work/|\./)?add\.py\b',command) and 'def add(' in item.get('aggregated_output',''):return True
 return None
def native_usage_audit(events,records):
 messages=[e.get('message',{}) for e in events if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant']
 requests=[z for z in records if z.get('actor')=='pi']
 if not requests or any(z.get('usage_complete') is not True for z in requests) or len(messages)!=len(requests) or not any(e.get('type')=='agent_end' for e in events):return {'complete':None,'gross_tokens':None}
 tokens=[m.get('usage',{}).get('totalTokens') for m in messages]
 if any(type(t) is not int or t<=0 for t in tokens) or any(m.get('stopReason') in ['error','aborted'] for m in messages):return {'complete':None,'gross_tokens':None}
 gross=sum(z['usage_audit']['gross_tokens'] for z in requests)
 if sum(tokens)!=gross:return {'complete':None,'gross_tokens':None}
 return {'complete':True,'gross_tokens':gross,'basis':'unique native assistant message_end usage totals match terminal provider request usage; native agent_end observed','cache_components_complete':False,'actual_dollars':None}
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-native-readiness',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args();digest=sha(R/'plan.json')
 if not x.execute_native_readiness or digest!=x.plan_sha256:raise SystemExit('explicit plan hash authorization required')
 p=json.loads((R/'plan.json').read_text());validate(p,digest)
 root=pathlib.Path('/tmp')/('solpi-qwennative-'+digest);root.mkdir(mode=0o700,exist_ok=False);(root/'launch.json').write_text(json.dumps({'plan':digest}))
 owned=[];nets=[];servers=[];errors=[];session=None;actors=[];proofs={'topology':None,'proxy':None,'actors':[],'cleanup':{'server_workers':None,'socket_absent':None,'containers':[],'networks':[]}};prefix='solpi-qwennative-'+uuid.uuid4().hex[:10];locks=contextlib.ExitStack()
 try:
  locks.enter_context(S.inference_locks(p['shared_inference_locks']))
  if True:
   S.fetch_idle(root/'load-before-topology.json')
   if cmd('image','inspect','--format','{{.Id}}',S.IMAGE)!=S.IMAGE:raise RuntimeError('image mismatch')
   n=prefix+'-actor';nets.append(n);cmd('network','create','--internal','--ipv6=false','--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated',n)
   actor=json.loads(cmd('network','inspect',n))[0]
   if actor.get('Internal') is not True or actor.get('EnableIPv6') is not False or actor.get('Options',{}).get('com.docker.network.bridge.gateway_mode_ipv4')!='isolated' or not actor['IPAM']['Config'] or any(z.get('Gateway') for z in actor['IPAM']['Config']):raise RuntimeError('topology mismatch')
   proofs['topology']={'internal':actor['Internal'],'ipv6':actor['EnableIPv6'],'gateway_mode':actor['Options']['com.docker.network.bridge.gateway_mode_ipv4'],'gateways':[x.get('Gateway') for x in actor['IPAM']['Config']]}
   topo={'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':n}
   session=S.Session(root/'transport',topo);handler=type('OwnedPost',(B.PostHandler,),{'session':session});sockdir=root/'broker';sockdir.mkdir(mode=0o700);sockpath=sockdir/'broker.sock';server=B.OwnedUnixServer(str(sockpath),handler);sockpath.chmod(0o600);servers.append(server);threading.Thread(target=server.serve_forever,daemon=True).start();port=8000
   proxy=prefix+'-proxy';owned.append(proxy)
   cmd('create','--pull=never','--name',proxy,'--network',n,'--user',str(os.getuid())+':'+str(os.getgid()),'--network-alias','proxy','--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-e','BROKER_SOCKET=/broker/broker.sock','-v',str(sockdir)+':/broker:ro','-v',str(R)+':/app:ro',S.IMAGE,'/app/tunnel_proxy.py')
   q=json.loads(cmd('inspect',proxy))[0]
   proxy_mounts=q['Mounts'];proxy_caps=q['HostConfig'];expected_sources={'/broker':str(sockdir),'/app':str(R)}
   proxy_ok=set(q['NetworkSettings']['Networks'])==set(nets) and proxy_caps.get('Memory')==536870912 and proxy_caps.get('NanoCpus')==1000000000 and proxy_caps.get('PidsLimit')==32 and q['Config'].get('User')==str(os.getuid())+':'+str(os.getgid()) and len(proxy_mounts)==2 and all(z.get('RW') is False and z.get('Source')==expected_sources.get(z.get('Destination')) for z in proxy_mounts)
   proofs['proxy']={'verified':proxy_ok,'user':q['Config'].get('User'),'nano_cpus':proxy_caps.get('NanoCpus'),'memory':proxy_caps.get('Memory'),'pids':proxy_caps.get('PidsLimit'),'mounts':[{'source':z['Source'],'destination':z['Destination'],'RW':z['RW']} for z in proxy_mounts],'networks':list(q['NetworkSettings']['Networks'])}
   if not proxy_ok:raise RuntimeError('proxy mounts/UID/resources/topology mismatch')
   cmd('start',proxy)
   for harness in ['pi']:
    session.begin(harness,S.fetch_idle(root/('load-before-'+harness+'.json')));d=W.prepare(root/harness,port);name=prefix+'-'+harness;owned.append(name)
    env=['HOME=/tmp/home','CODEX_HOME=/tmp/home/.codex','MOCK_KEY=dummy-not-a-real-secret','HTTP_PROXY=http://proxy:8080','HTTPS_PROXY=http://proxy:8080','http_proxy=http://proxy:8080','https_proxy=http://proxy:8080','NO_PROXY=','no_proxy=']
    args=['docker','create','--pull=never','--name',name,'--network',nets[0],'--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','64','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,size=64m','-v',str(d/'home')+':/tmp/home','-v',str(d/'work')+':/work','-w','/work','--entrypoint','/bin/sh']
    for e in env:args+=['-e',e]
    args +=[S.IMAGE,*W.shell(W.argv(harness,port))[1:]]
    row={'harness':harness,'availability':'started','usage_complete':None};actors.append(row)
    # Inspect inert container before any native executable runs.
    subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=remaining(session.deadline,8))
    inspect=json.loads(cmd('inspect',name,deadline=session.deadline))[0];h=inspect['HostConfig'];mounts=inspect['Mounts']
    destinations={z['Destination'] for z in mounts};environment=set(inspect['Config']['Env'])
    if inspect['Config'].get('User')!=str(os.getuid())+':'+str(os.getgid()) or h.get('NanoCpus')!=1000000000 or h.get('Memory')!=536870912 or h.get('PidsLimit')!=64 or set(inspect['NetworkSettings']['Networks'])!={nets[0]} or destinations!={'/tmp/home','/work'} or any('/broker' in z['Destination'] or str(sockdir) in z.get('Source','') for z in mounts) or not set(env).issubset(environment):raise RuntimeError('actor isolation/resources/env mismatch')
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
    aux=[z.get('type') for z in rows if any(k in str(z.get('type','')).lower() for k in ['compaction','subagent'])]
    # Read parser intentionally unknown until pinned native event schema observed.
    if process.returncode!=0:raise RuntimeError('native interrupted/error; quality unknown')
    assistant_errors=[e for e in rows if e.get('message',{}).get('role')=='assistant' and e.get('message',{}).get('stopReason')=='error']
    if assistant_errors:
     row['availability']='native_provider_error_before_grade';row['quality_evaluable']=False;raise RuntimeError('native assistant error; no behaviorqualityclaim')
    row['native_usage_audit']=native_usage_audit(rows,session.records);row['usage_complete']=row['native_usage_audit']['complete']
    grade=W.grade(d/'work',read_evidence(harness,rows));row['grade']=grade
    actor_requests=[z for z in session.records if z['actor']==harness]
    row['transport_pass']=bool(actor_requests) and all(z['error'] is None and z['provider_status']==200 for z in actor_requests)
    row['readiness_category']='full' if grade['solved'] else ('transport_only_read_TBD' if grade['behavior_pass'] else 'behavior_failed')
    if not grade['behavior_pass']:raise RuntimeError('behavior failure stops before next actor')
    session.finish(True,aux)
    if server.workers:raise RuntimeError('broker worker active after actor')
    if process.returncode!=0 or session.records and session.records[-1]['error']:raise RuntimeError('actor/transport failure stops next start')
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
  (root/'final-evidence.json').write_text(json.dumps({'plan_sha256':digest,'actual_proofs':proofs,'actors':actors,'errors':errors,'containers_remaining':owned,'networks_remaining':nets,'native_starts':session.starts if session else 0,'provider_POST':session.posts if session else 0,'usage_complete':None},indent=2)+'\n')
 if errors:raise SystemExit('failed: private evidence retained; no retries')
if __name__=='__main__':main()
