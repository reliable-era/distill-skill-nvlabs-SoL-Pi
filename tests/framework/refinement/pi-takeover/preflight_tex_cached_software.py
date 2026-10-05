"""Onegenericsoftwarecompatibilitypreflight:NOT officialgrader/thirdrepair."""
import hashlib,json,pathlib,subprocess,time,uuid,shutil
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'tex-cached-software-preflight.json').exists(),'one genericpreflight only'
 plan=json.loads((R/'16k-tex-r2-plan.json').read_text());inventory=json.loads((R/'tex-recovery-cache-inventory.json').read_text());root=pathlib.Path('/tmp/solpi-tex-software-preflight-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);wheels=root/'wheels';wheels.mkdir()
 for rec in inventory['verified_wheels'].values():
  source=pathlib.Path(rec['path']);assert sha(source)==rec['sha256'];shutil.copyfile(source,wheels/source.name)
 expanded=pathlib.Path('/tmp/solpi-tex-public-runtime-expanded');uv=expanded/'uv/uv-x86_64-unknown-linux-gnu';python=expanded/'cpython/python';assert sha(uv/'uv')=='d3dc3ca8e29337dd602a9a4df9e6edb15ebc52aed91461debeedb96939dc4ce0';name=root.name;deadline=time.monotonic()+90;created=False;out={'private_root':str(root),'software_only':True,'official_grader_attempts':0,'official_test_runs':0,'model_POST':0,'actor_starts':0,'generic_preflight_containers':1,'timeout_seconds':90,'network':'none','captured_outputs_mounted':False,'tests_or_solutions_mounted':False}
 def docker(*args):return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT,text=True,timeout=max(.1,deadline-time.monotonic())).strip()
 try:
  docker('create','--name',name,'--network','none','--memory','4096m','--cpus','1','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(wheels)+':/opt/public-wheels:ro','--entrypoint','/bin/sh',plan['image_id'],'-c','sleep infinity');created=True;docker('start',name);meta=json.loads(docker('inspect',name))[0];assert meta['Image']==plan['image_id'] and set(meta['NetworkSettings']['Networks'])=={'none'} and len(meta['Mounts'])==1 and meta['Mounts'][0]['Destination']=='/opt/public-wheels'
  docker('exec',name,'mkdir','-p','/root/.local/bin','/root/.local/share/uv/python');docker('cp',str(uv/'uv'),name+':/root/.local/bin/uv');docker('cp',str(uv/'uvx'),name+':/root/.local/bin/uvx');docker('cp',str(python),name+':/root/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu')
  script='''set -eu
export UV_OFFLINE=1 UV_PYTHON_DOWNLOADS=never UV_NO_INDEX=1 UV_FIND_LINKS=/opt/public-wheels
/root/.local/bin/uv --version
/root/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/bin/python3.13 --version
/root/.local/bin/uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version
'''
  log=docker('exec','-w','/',name,'/bin/sh','-c',script);(root/'preflight.log').write_text(log+'\n');assert 'uv 0.9.5' in log and 'Python 3.13.7' in log and 'pytest 8.4.1' in log;out['passed']=True;out['version_outputs']=log;out['original_image_id']=plan['image_id'];out['public_wheel_hashes']={p.name:sha(p) for p in wheels.iterdir()}
 except Exception as e:out.update(passed=False,error={'type':type(e).__name__,'message':str(e)[:600]})
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  out['cleanup_verified']=subprocess.run(['docker','inspect',name],capture_output=True,timeout=10).returncode!=0;out['seconds']=90-max(0,deadline-time.monotonic());out['official_recovery_authorized']=False;out['goal_complete']=False;out['artifact_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(R/'tex-cached-software-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
