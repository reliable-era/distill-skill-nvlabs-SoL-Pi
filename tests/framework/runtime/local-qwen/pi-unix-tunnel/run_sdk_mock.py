"""Exclusive reviewed one-container mock-only probe. No model/provider endpoints."""
import argparse,pathlib,json,hashlib,subprocess,time,os,uuid
R=pathlib.Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def classify(result,exit_code):
 return 'SDK_CONNECT_Unix_mock_HTTP400' if exit_code==0 and result.get('CONNECT')==1 and result.get('CONNECT_attempts')==1 and result.get('POST')==1 and result.get('sdk_status')==400 and result.get('expectedMock400') is True and result.get('workers')=={'proxy':0,'broker':0} and result.get('socket_absent') is True and result.get('errors')==[] else None
def main():
 a=argparse.ArgumentParser();a.add_argument('--execute-mock-only',action='store_true');a.add_argument('--plan-sha256',required=True);x=a.parse_args();digest=sha(R/'plan.json');p=json.loads((R/'plan.json').read_text())
 if not x.execute_mock_only or digest!=x.plan_sha256 or p['maximum_mock_POST']!=1 or p['maximum_container_starts']!=1:raise SystemExit('explicit hash/cap authorization')
 for f,h in p['source_hashes'].items():
  if sha(R/f)!=h:raise SystemExit('source changed')
 private=pathlib.Path('/tmp')/('solpi-pi-unix-sdk-mock-'+digest);private.mkdir(mode=0o700,exist_ok=False);name='solpi-pi-unix-sdk-mock-'+uuid.uuid4().hex[:10];errors=[];result=None;started=False;absence=False;category=None;container_exit=None
 def cmd(*args):return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.PIPE,timeout=5).strip()
 try:
  if cmd('image','inspect','--format','{{.Id}}',p['image_id'])!=p['image_id']:raise RuntimeError('image mismatch')
  cmd('create','--pull=never','--name',name,'--network','none','--user',str(os.getuid())+':'+str(os.getgid()),'--cpus','1','--memory','512m','--pids-limit','32','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=16m','-v',str(R.parent)+':/app:ro','-v',str(private)+':/artifacts','--entrypoint','python3',p['image_id'],'/app/pi-unix-tunnel/mock_sdk.py')
  row=json.loads(cmd('inspect',name))[0];h=row['HostConfig'];mount=row['Mounts']
  if h['NetworkMode']!='none' or h['NanoCpus']!=1000000000 or h['Memory']!=536870912 or h['PidsLimit']!=32 or len(mount)!=2 or not any(x['Source']==str(R.parent) and x['Destination']=='/app' and x['RW'] is False for x in mount) or not any(x['Source']==str(private) and x['Destination']=='/artifacts' and x['RW'] is True for x in mount):raise RuntimeError('prestart isolation failed')
  started=True;(private/'start.json').write_text(json.dumps({'starts':1,'models':0}))
  with (private/'stdout').open('wb') as out,(private/'stderr').open('wb') as err:
   z=subprocess.run(['docker','start','-a',name],stdout=out,stderr=err,timeout=15)
  result=json.loads((private/'stdout').read_text());
  container_exit=z.returncode;category=classify(result,container_exit)
  if category is None:raise RuntimeError('unrecognized/incomplete transport diagnosis; SDKprivatecause retained')
 except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e)[:200]})
 finally:
  try:
   subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=5);q=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=3);absence=q.returncode!=0 and q.stderr.strip() in ['Error: No such object: '+name,'Error response from daemon: No such container: '+name]
   if not absence:raise RuntimeError('absence uncertain')
  except Exception:errors.append({'cleanup':'uncertain'})
  report={'plan_sha256':digest,'mock_starts':int(started),'result':result,'container_exit':container_exit,'diagnosis_category':category,'forwarded_POST_route_proved':category=='SDK_CONNECT_Unix_mock_HTTP400','cleanup_absence_verified':absence,'errors':errors,'models':0,'real_provider_calls':0};(private/'final-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
  if not errors:(R/'mock-proxy-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
 if errors:raise SystemExit('mock probe failed; no retry')
if __name__=='__main__':main()
