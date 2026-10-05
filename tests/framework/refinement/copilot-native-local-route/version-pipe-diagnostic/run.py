import pathlib,json,hashlib,subprocess,os
R=pathlib.Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def d(*a,timeout=5):
 z=subprocess.run(['docker',*a],capture_output=True,text=True,timeout=timeout)
 if z.returncode:raise RuntimeError('docker '+a[0]+' failed')
 return z.stdout.strip()
def absent(name):
 z=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
 return z.returncode!=0 and z.stderr.strip() in ['Error: No such object: '+name,'Error response from daemon: No such container: '+name]
if __name__=='__main__':
 p=json.loads((R/'plan.json').read_text());digest=sha(R/'plan.json');auth=json.loads((R/'execution-authorization.json').read_text());assert auth['authorized'] is True and auth['plan_sha256']==digest
 for n,h in p['source_hashes'].items():assert sha(R/n)==h
 root=pathlib.Path('/tmp/solpi-cpv-'+digest[:16]);root.mkdir(mode=0o700);out=root/'output';out.mkdir(mode=0o700);name='solpi-cpv-'+digest[:16];created=False;r={'errors':[],'prompt_starts':0}
 try:
  assert absent(name)
  d('create','--name',name,'--user','1003:1004','--network','none','--cpus','1','--memory','512m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=128m','--mount','type=bind,src='+str(R)+',dst=/probe,readonly','--mount','type=bind,src='+str(out)+',dst=/output','--entrypoint','python3',p['image_id'],'/probe/worker.py');created=True
  a=json.loads(d('inspect',name))[0];(root/'private-before.json').write_text(json.dumps(a))
  h=a['HostConfig'];assert a['Config']['User']=='1003:1004' and h['NetworkMode']=='none' and h['Memory']==536870912 and h['NanoCpus']==1000000000 and h['PidsLimit']==128 and h['ReadonlyRootfs'] and h['CapDrop']==['ALL'] and h['SecurityOpt']==['no-new-privileges']
  with open(root/'private-container.log','wb') as log:
   z=subprocess.run(['docker','start','-a',name],stdout=log,stderr=log,timeout=12);r['docker_exit']=z.returncode
  a=json.loads(d('inspect',name))[0];(root/'private-after.json').write_text(json.dumps(a));r['container_state']=a['State']
  v=json.loads((out/'version-result.json').read_text());r['version']=v;r['runtime_hashes_match']=v['runtime_hashes']==p['runtime_hashes']
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
 finally:
  if created:
   try:d('rm','-f',name,timeout=10);r['container_absent']=absent(name)
   except Exception as e:r['errors'].append('cleanup '+str(e))
  (root/'result.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({'private_result':str(root/'result.json'),'errors':r['errors']}))
