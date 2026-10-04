#!/usr/bin/env python3
import argparse,json,pathlib,hashlib,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(p,x):pathlib.Path(p).write_text(json.dumps(x,indent=2)+'\n')
def guards():
 p=load(OUT/'bootstrap-plan.json');auth=load(OUT/'bootstrap-authorization.json')
 assert auth.get('authorized') is True and auth['plan_sha256']==sha(OUT/'bootstrap-plan.json')
 assert sha(__file__)==p['runner_sha256'] and sha(p['private_prefix'])==p['prefix_sha256']
 assert p['bootstrap_cap']==1 and p['outer_seconds']==300 and p['memory']==8589934592 and p['nano_cpus']==4000000000
 for f,h in p['wheel_sha256'].items():assert sha(pathlib.Path(p['readonly_wheelhouse'])/f)==h
 return p
def clean(cid,work):
 rm=subprocess.run(['docker','rm','-f',cid],capture_output=True,timeout=30);r=subprocess.run(['docker','container','inspect',cid],capture_output=True,timeout=10)
 absent=r.returncode!=0 and (b'No such container' in r.stderr or b'No such object' in r.stderr);dump(work/'cleanup.json',{'container_id':cid,'remove_exit':rm.returncode,'absence_verified':absent})
 if not absent:raise RuntimeError('cleanup unverified')
def worker():
 p=guards();work=pathlib.Path(p['private_output_root']);assert (work/'bootstrap-start.json').exists()
 with (work/'worker-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'bootstrap-plan.json')},f)
 import docker
 c=docker.from_env(timeout=20);container=None
 python='/opt/miniconda3/envs/testbed/bin/python'
 before=python+" -c \"import json,importlib.metadata as m;print(json.dumps({'numpy':m.version('numpy')}))\" > /output/numpy-before.json"
 after=before.replace('before','after')
 command=['bash','-c',before+'; bash /official-bootstrap-prefix.sh; status=$?; '+after+'; exit $status']
 try:
  image=c.images.get(p['image']);assert p['image'] in image.attrs.get('RepoDigests',[])
  container=c.containers.create(image=p['image'],name='solpi-astropy-offline-bootstrap-1',command=command,network_mode='none',network_disabled=False,mem_limit=p['memory'],nano_cpus=p['nano_cpus'],environment=p['environment'],volumes={p['readonly_wheelhouse']:{'bind':'/wheelhouse','mode':'ro'},p['private_prefix']:{'bind':'/official-bootstrap-prefix.sh','mode':'ro'},str(work):{'bind':'/output','mode':'rw'}})
  dump(work/'container.json',{'container_id':container.id});container.reload();h=container.attrs['HostConfig'];config=container.attrs['Config'];caps={'memory':h['Memory'],'nano_cpus':h['NanoCpus'],'network_mode':h['NetworkMode'],'network_disabled':config.get('NetworkDisabled',False)};dump(work/'caps.json',caps)
  assert caps=={'memory':8589934592,'nano_cpus':4000000000,'network_mode':'none','network_disabled':False}
  container.start();c.api.timeout=295;status=container.wait(timeout=290);(work/'private-bootstrap.log').write_bytes(container.logs());dump(work/'worker-result.json',{'exit_code':status['StatusCode']})
 finally:
  if container:clean(container.id,work)
  c.close()
def launch():
 p=guards();work=pathlib.Path(p['private_output_root'])
 with (work/'bootstrap-start.json').open('x') as f:json.dump({'plan_sha256':sha(OUT/'bootstrap-plan.json'),'time':time.time()},f)
 start=time.monotonic();error=None
 try:
  with (work/'private-worker.log').open('wb') as f:r=subprocess.run([sys.executable,str(OUT/'run_bootstrap.py'),'--worker'],stdout=f,stderr=subprocess.STDOUT,timeout=300)
  if r.returncode:raise RuntimeError('bootstrap worker error')
 except Exception as e:
  error=type(e).__name__;cidfile=work/'container.json'
  if cidfile.exists():clean(load(cidfile)['container_id'],work)
 finally:
  record={'status':'error' if error else 'complete','error_type':error,'elapsed_seconds':time.monotonic()-start,'models':0,'graders':0,'pulls':0,'docker_builds':0,'package_setup_attempts':1}
  for name in ['worker-result','caps','cleanup','numpy-before','numpy-after']:
   f=work/(name+'.json')
   if f.exists():record[name]=load(f)
  record['bootstrap_ready']=not error and record.get('worker-result',{}).get('exit_code')==0 and record.get('numpy-before',{}).get('numpy')=='1.25.2' and record.get('numpy-after',{}).get('numpy')=='1.25.2' and record.get('cleanup',{}).get('absence_verified') is True
  record['private_log_hashes']={f.name:sha(f) for f in work.glob('*.log')};dump(OUT/'bootstrap-result.json',record)
 if error:raise RuntimeError('bootstrap stopped')
 if record['worker-result']['exit_code']!=0 or record['numpy-before']['numpy']!='1.25.2' or record['numpy-after']['numpy']!='1.25.2':raise RuntimeError('bootstrap failed or runtime NumPy changed')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--launch',action='store_true');parser.add_argument('--worker',action='store_true');args=parser.parse_args()
 if args.worker:worker()
 elif args.launch:launch()
 else:print('prepared only; no bootstrap')
