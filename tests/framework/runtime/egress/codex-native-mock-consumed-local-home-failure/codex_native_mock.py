"""Root-reviewed, exclusively two-start native mock routing diagnostic; no providers."""
import argparse,hashlib,json,pathlib,subprocess,time,uuid,os,signal,re
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate(p):
 if p['maximum_native_starts']!=2 or p['maximum_seconds_per_start']!=30 or len(p['controls'])!=2:raise ValueError('launch cap')
 cfg=p['provider_config']
 if cfg['model_providers.mock.base_url']!='http://provider.example:8000/v1' or cfg['model_provider']!='mock' or cfg['model_providers.mock.env_key']!='MOCK_KEY' or cfg['model_providers.mock.requires_openai_auth'] is not False or p['credentials'].split(';')[0]!='dummy MOCK_KEY only':raise ValueError('unsafe config')
 if p['controls'][0].get('base_url',cfg['model_providers.mock.base_url'])!='http://provider.example:8000/v1' or p['controls'][1].get('base_url')!='http://blocked.example:8000/v1':raise ValueError('unsafe control route')
 if any(v!='http://proxy:8080' for k,v in p['proxy_env'].items() if k.lower()!='no_proxy') or any(v for k,v in p['proxy_env'].items() if k.lower()=='no_proxy'):raise ValueError('unsafe proxy config')
 for f,h in p['source_hashes'].items():
  if sha(R/f)!=h:raise ValueError('source mismatch')
def cleanup_guard(result):
 if result.returncode:raise RuntimeError('cleanup uncertain; next actor prohibited')
def absence_verified(result,name):
 stderr=result.stderr.decode(errors='replace') if isinstance(result.stderr,bytes) else result.stderr or ''
 return result.returncode!=0 and name in stderr and bool(re.search(r'no such (?:object|container):',stderr,re.I))
def network_absence_verified(result,name):
 stderr=result.stderr.decode(errors='replace') if isinstance(result.stderr,bytes) else result.stderr or ''
 return result.returncode!=0 and bool(re.search(r'(?:no such network:\s*'+re.escape(name)+r'\b|network\s+'+re.escape(name)+r'\s+not found)',stderr,re.I))
def topology_ok(actor,provider):
 return all(n.get('Internal') is True and n.get('EnableIPv6') is False for n in (actor,provider)) and actor.get('Options',{}).get('com.docker.network.bridge.gateway_mode_ipv4')=='isolated' and bool(actor.get('IPAM',{}).get('Config')) and all(not c.get('Gateway') for c in actor['IPAM']['Config'])
def probe_ok(probes):
 return probes.get('direct_ip_blocked') is True and probes.get('nonallowed_denied') is True and probes.get('connect_denied') is True

def receipt_ok(index,decoded,native_log):
 return any(z.get('method')=='POST' and z.get('path')=='/v1/responses' for z in decoded) if index==0 else (not decoded and '403' in native_log and 'destination denied' in native_log.lower())
def remaining(deadline,limit):
 value=min(limit,deadline-time.monotonic())
 if value<=0:raise TimeoutError('native total30s deadline exhausted')
 return value

def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-mock-only',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args()
 if not x.execute_mock_only or sha(R/'codex-native-mock-plan.json')!=x.plan_sha256:raise SystemExit('authorization/hash guard')
 p=json.loads((R/'codex-native-mock-plan.json').read_text());validate(p)
 private=pathlib.Path('/tmp')/('solpi-codexmock-'+x.plan_sha256);private.mkdir(mode=0o700,exist_ok=False)
 (private/'launch.json').write_text(json.dumps({'plan_sha256':x.plan_sha256,'maximum_starts':2}))
 prefix='solpi-codexmock-'+uuid.uuid4().hex[:10];nets=[];owned=[];records=[];errors=[];starts=0;probes=None;network_evidence=None;receipt_evidence=[];runtime_verified=False;attachments_verified=False;native_processes=[]
 def cmd(*args,deadline=None):
  return subprocess.check_output(['docker',*args],text=True,timeout=remaining(deadline,15) if deadline else 15).strip()
 def remove(name,deadline=None):
  z=subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=remaining(deadline,8) if deadline else 8)
  if z.returncode and not absence_verified(z,name):cleanup_guard(z)
  check=subprocess.run(['docker','inspect',name],capture_output=True,timeout=remaining(deadline,3) if deadline else 3)
  if not absence_verified(check,name):raise RuntimeError('owned container absence not verified')
 def metadata_run(args):
  name=prefix+'-metadata-'+uuid.uuid4().hex[:6];owned.append(name)
  result=cmd('run','--rm','--pull=never','--name',name,'--network','none','--read-only','--tmpfs','/tmp:rw','-e','HOME=/tmp/home','-e','CODEX_HOME=/tmp/home/.codex',*args)
  remove(name);owned.remove(name);return result
 def persist():
  evidence={'plan_sha256':x.plan_sha256,'source_hashes':p['source_hashes'],'image_id':p['image_id'],'image_runtime_verified':runtime_verified,'network_attachments_verified':attachments_verified,'records':records,'native_starts':starts,'maximum_starts':2,'probes':probes,'network_topology':network_evidence,'mock_method_path_records':receipt_evidence,'errors':errors,'real_provider_calls':0,'model_benchmark':False,'private_native_logs':str(private),'final_cleanup_recorded':True,'owned_containers_remaining':len(owned),'owned_networks_remaining':len(nets)}
  (private/'final-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');os.chmod(private/'final-evidence.json',0o600)
 try:
  # All preflight containers are named/owned before launch and covered by finally.
  cmd('image','inspect',p['image_id'])
  for path,h in p['image_runtime']['file_sha256'].items():
   if metadata_run(['--entrypoint','sha256sum',p['image_id'],path]).split()[0]!=h:raise RuntimeError('image runtime hash mismatch')
  if metadata_run(['--entrypoint','codex',p['image_id'],'--version'])!='codex-cli '+p['expected_cli_version']:raise RuntimeError('image native version mismatch')
  runtime_verified=True
  for suffix in ['actor','provider']:
   n=prefix+'-'+suffix;nets.append(n);opts=['--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated'] if suffix=='actor' else []
   cmd('network','create','--internal','--ipv6=false',*opts,n)
  actor_network,provider_network=json.loads(cmd('network','inspect',*nets))
  if not topology_ok(actor_network,provider_network):raise RuntimeError('network topology invariants failed')
  network_evidence={'actor_internal':actor_network['Internal'],'provider_internal':provider_network['Internal'],'actor_ipv6':actor_network['EnableIPv6'],'provider_ipv6':provider_network['EnableIPv6'],'actor_gateway_mode':actor_network['Options']['com.docker.network.bridge.gateway_mode_ipv4'],'actor_gateways':[c.get('Gateway') for c in actor_network['IPAM']['Config']]}
  for suffix,script,network,extra in [('mock','codex_mock400.py',nets[1],[]),('proxy','proxy.py',nets[0],['-e','EGRESS_ALLOWLIST={"provider.example:8000":"mock"}'])]:
   name=prefix+'-'+suffix;owned.append(name)
   cmd('run','-d','--pull=never','--name',name,'--network',network,'--network-alias',suffix,'--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-v',str(R)+':/app:ro',*extra,p['image_id'],'/app/'+script)
  cmd('network','connect',nets[1],owned[1]);time.sleep(1)
  connected=json.loads(cmd('inspect',*owned));expected=[{nets[1]},{nets[0],nets[1]}]
  if any(set(c['NetworkSettings']['Networks'])!=e for c,e in zip(connected,expected)):raise RuntimeError('mock/proxy network attachments failed')
  attachments_verified=True
  for i,c in enumerate(p['controls']):
   if errors or starts>=2:raise RuntimeError('prior error or exclusive start cap')
   name=prefix+'-native-'+str(i);owned.append(name);cfg=dict(p['provider_config']);cfg['model_providers.mock.base_url']=c.get('base_url',cfg['model_providers.mock.base_url'])
   args=['docker','run','--pull=never','--name',name,'--network',nets[0],'--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw','-e','HOME=/tmp/home','-e','CODEX_HOME=/tmp/home/.codex','-e','MOCK_KEY=dummy-not-a-real-secret']
   for k,v in p['proxy_env'].items():args+=['-e',k+'='+v]
   args+=['--entrypoint','codex',p['image_id'],'exec','--skip-git-repo-check','--json']
   for k,v in cfg.items():args+=['-c',k+'='+json.dumps(v)]
   args+=['Transport diagnostic only. Reply OK.'];before=len(cmd('logs',owned[0]).splitlines());start=time.monotonic();deadline=start+30;starts+=1
   (private/'start-ledger.json').write_text(json.dumps({'native_starts':starts,'maximum':2,'current_control':c['id']}))
   row={'id':c['id'],'started':True,'receipt_expectation_met':False}
   try:
    with (private/(c['id']+'.log')).open('wb') as log:
     os.chmod(private/(c['id']+'.log'),0o600);actor=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);native_processes.append(actor)
     try:actor.wait(timeout=remaining(deadline,12))
     except subprocess.TimeoutExpired:
      z=subprocess.run(['docker','stop','-t','2',name],capture_output=True,timeout=remaining(deadline,5))
      if z.returncode:raise RuntimeError('owned native stop failed')
     remove(name,deadline);actor.wait(timeout=remaining(deadline,2));owned.remove(name)
    new=cmd('logs',owned[0],deadline=deadline).splitlines()[before:];decoded=[json.loads(l) for l in new if l.startswith('{')]
    native_log=(private/(c['id']+'.log')).read_text(errors='replace');passed=receipt_ok(i,decoded,native_log)
    row.update(exit=actor.returncode,mock_receipts=len(new),receipt_expectation_met=passed,deadline_met=time.monotonic()<=deadline)
    if not passed or not row['deadline_met']:raise RuntimeError('native receipt/deadline expectation failed')
   except BaseException as error:
    row['error_type']=type(error).__name__;row['error']=str(error);raise
   finally:
    row['seconds']=time.monotonic()-start;records.append(row);(private/'records.json').write_text(json.dumps(records,indent=2)+'\n')
  ip=json.loads(cmd('inspect',owned[0]))[0]['NetworkSettings']['Networks'][nets[1]]['IPAddress']
  code='import socket,urllib.request,json; r={};\ntry:socket.create_connection(("'+ip+'",8000),timeout=2);r["direct_ip_blocked"]=False\nexcept OSError:r["direct_ip_blocked"]=True\np=urllib.request.build_opener(urllib.request.ProxyHandler({"http":"http://proxy:8080"}));\ntry:p.open("http://blocked.example:8000/solution",timeout=2);r["nonallowed_denied"]=False\nexcept urllib.error.HTTPError as e:r["nonallowed_denied"]=e.code==403\ns=socket.create_connection(("proxy",8080),timeout=2);s.sendall(b"CONNECT blocked.example:8000 HTTP/1.1\\r\\nHost: blocked.example:8000\\r\\n\\r\\n");r["connect_denied"]=s.recv(1024).split(b"\\r\\n",1)[0].split()[1]==b"403";s.close();print(json.dumps(r))'
  probe_name=prefix+'-bypass';owned.append(probe_name)
  probes=json.loads(cmd('run','--rm','--pull=never','--name',probe_name,'--network',nets[0],'--entrypoint','python3',p['image_id'],'-c',code));remove(probe_name);owned.remove(probe_name)
  if not probe_ok(probes):raise RuntimeError('bypass denial controls failed')
  receipt_evidence=[json.loads(l) for l in cmd('logs',owned[0]).splitlines() if l.startswith('{')]
 except BaseException as error:
  errors.append({'phase':'primary','type':type(error).__name__,'message':str(error)})
 finally:
  for n in reversed(owned.copy()):
   try:remove(n);owned.remove(n)
   except Exception as error:errors.append({'phase':'container_cleanup','type':type(error).__name__,'message':str(error),'name':n})
  for process in native_processes:
   try:
    if process.poll() is None:process.terminate()
    try:process.wait(timeout=2)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=2)
   except Exception as error:errors.append({'phase':'owned_cli_cleanup','type':type(error).__name__,'message':str(error)})
  for n in reversed(nets.copy()):
   try:
    cmd('network','rm',n);check=subprocess.run(['docker','network','inspect',n],capture_output=True,text=True,timeout=3)
    if not network_absence_verified(check,n):raise RuntimeError('network absence not verified')
    nets.remove(n)
   except Exception as error:errors.append({'phase':'network_cleanup','type':type(error).__name__,'message':str(error),'name':n})
  persist()
  if not errors:
   (R/'codex-native-mock-evidence.json').write_text((private/'final-evidence.json').read_text())
  if errors:raise RuntimeError('mock diagnostic failed; durable private errors preserved')
if __name__=='__main__':main()
