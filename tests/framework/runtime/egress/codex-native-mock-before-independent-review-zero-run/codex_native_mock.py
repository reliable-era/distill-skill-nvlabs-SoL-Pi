"""Requires root-reviewed plan hash and explicit mock-only execution authorization."""
import argparse,hashlib,json,pathlib,subprocess,time,uuid,os
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate(p):
 if p['maximum_native_starts']!=2 or p['maximum_seconds_per_start']!=30 or len(p['controls'])!=2:raise ValueError('launch cap')
 if p['provider_config']['model_providers.mock.base_url']!='http://provider.example:8000/v1' or p['credentials'].split(';')[0]!='dummy MOCK_KEY only':raise ValueError('unsafe config')
 for f,h in p['source_hashes'].items():
  if sha(R/f)!=h:raise ValueError('source mismatch')
def cleanup_guard(result):
 if result.returncode:raise RuntimeError("cleanup uncertain; next actor prohibited")

def receipt_ok(index,decoded,native_log):
 return any(z.get('method')=='POST' and z.get('path')=='/v1/responses' for z in decoded) if index==0 else (not decoded and '403' in native_log)

def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-mock-only',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args()
 if not x.execute_mock_only or sha(R/'codex-native-mock-plan.json')!=x.plan_sha256:raise SystemExit('authorization/hash guard')
 p=json.loads((R/'codex-native-mock-plan.json').read_text());validate(p)
 private=pathlib.Path('/tmp')/('solpi-codexmock-'+x.plan_sha256);private.mkdir(mode=0o700,exist_ok=False) # exclusive plan-bound launch marker
 (private/'launch.json').write_text(json.dumps({'plan_sha256':x.plan_sha256,'maximum_starts':2}))
 for path,h in p['image_runtime']['file_sha256'].items():
  observed=subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','sha256sum',p['image_id'],path],text=True,timeout=15).split()[0]
  if observed!=h:raise SystemExit('image runtime hash mismatch')
 version=subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','codex',p['image_id'],'--version'],text=True,timeout=15).strip()
 if version!='codex-cli '+p['expected_cli_version']:raise SystemExit('image native version mismatch')
 prefix='solpi-codexmock-'+uuid.uuid4().hex[:10];nets=[];owned=[];records=[];errors=[]
 def cmd(*args):return subprocess.check_output(['docker',*args],text=True,timeout=15).strip()
 def remove(name):
  z=subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=8)
  cleanup_guard(z)
  check=subprocess.run(['docker','inspect',name],capture_output=True,timeout=3)
  if check.returncode==0:raise RuntimeError('owned container still present after cleanup')
 try:
  for suffix in ['actor','provider']:
   n=prefix+'-'+suffix;opts=['--opt','com.docker.network.bridge.gateway_mode_ipv4=isolated'] if suffix=='actor' else []
   cmd('network','create','--internal','--ipv6=false',*opts,n);nets.append(n)
  for suffix,script,network,extra in [('mock','codex_mock400.py',nets[1],[]),('proxy','proxy.py',nets[0],['-e','EGRESS_ALLOWLIST={"provider.example:8000":"mock"}'])]:
   name=prefix+'-'+suffix;cmd('run','-d','--name',name,'--network',network,'--network-alias',suffix,'--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-v',str(R)+':/app:ro',*extra,p['image_id'],'/app/'+script);owned.append(name)
  cmd('network','connect',nets[1],owned[1]);time.sleep(1)
  # Dummy key and empty tmpfs home only; source mounts exclude all host credentials.
  for i,c in enumerate(p['controls']):
   if errors:raise RuntimeError('prior cleanup uncertain')
   name=prefix+'-native-'+str(i);owned.append(name)
   cfg=dict(p['provider_config']);cfg['model_providers.mock.base_url']=c.get('base_url',cfg['model_providers.mock.base_url'])
   args=['docker','run','--name',name,'--network',nets[0],'--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw','-e','HOME=/tmp/home','-e','CODEX_HOME=/tmp/home/.codex','-e','MOCK_KEY=dummy-not-a-real-secret']
   for k,v in p['proxy_env'].items():args+=['-e',k+'='+v]
   args+=['--entrypoint','codex',p['image_id'],'exec','--skip-git-repo-check','--json']
   for k,v in cfg.items():args+=['-c',k+'='+json.dumps(v)]
   args+=['Transport diagnostic only. Reply OK.']
   before=len(cmd('logs',owned[0]).splitlines());start=time.monotonic();log=open(private/(c['id']+'.log'),'wb');actor=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
   try:actor.wait(timeout=12)
   except subprocess.TimeoutExpired:
    z=subprocess.run(['docker','stop','-t','2',name],capture_output=True,timeout=5)
    if z.returncode:errors.append('owned native stop failed')
   try:remove(name);actor.wait(timeout=2);owned.remove(name)
   except Exception:errors.append('owned native cleanup uncertain');raise
   log.close()
   new=cmd('logs',owned[0]).splitlines()[before:]
   decoded=[json.loads(l) for l in new if l.startswith('{')]
   native_log=(private/(c['id']+'.log')).read_text(errors='replace')
   passed=receipt_ok(i,decoded,native_log)
   records.append({'id':c['id'],'exit':actor.returncode,'seconds':time.monotonic()-start,'mock_receipts':len(new),'receipt_expectation_met':passed})
   if not passed:raise RuntimeError('native receipt expectation failed; no inference certification')
  # Relevant bypass probes are separate from the two native starts.
  ip=json.loads(cmd('inspect',owned[0]))[0]['NetworkSettings']['Networks'][nets[1]]['IPAddress']
  code='import socket,urllib.request,json; r={};\ntry:socket.create_connection(("'+ip+'",8000),timeout=2);r["direct_ip_blocked"]=False\nexcept OSError:r["direct_ip_blocked"]=True\np=urllib.request.build_opener(urllib.request.ProxyHandler({"http":"http://proxy:8080"}));\ntry:p.open("http://blocked.example:8000/solution",timeout=2);r["nonallowed_denied"]=False\nexcept urllib.error.HTTPError as e:r["nonallowed_denied"]=e.code==403\nprint(json.dumps(r))'
  probes=cmd('run','--rm','--network',nets[0],'--entrypoint','python3',p['image_id'],'-c',code)
  receipts=cmd('logs',owned[0]);(R/'codex-native-mock-evidence.json').write_text(json.dumps({'records':records,'probes':json.loads(probes),'mock_method_path_records':[json.loads(l) for l in receipts.splitlines() if l.startswith('{')],'errors':errors,'real_provider_calls':0,'model_benchmark':False},indent=2)+'\n')
 finally:
  for n in reversed(owned):
   try:remove(n)
   except Exception:errors.append('cleanup uncertain '+n)
  for n in reversed(nets):
   try:cmd('network','rm',n)
   except Exception:errors.append('network cleanup uncertain '+n)
  evidence={'records':records,'errors':errors,'real_provider_calls':0,'model_benchmark':False,'private_native_logs':str(private),'final_cleanup_recorded':True}
  (private/'final-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
  if errors:raise RuntimeError('; '.join(errors))
if __name__=='__main__':main()
