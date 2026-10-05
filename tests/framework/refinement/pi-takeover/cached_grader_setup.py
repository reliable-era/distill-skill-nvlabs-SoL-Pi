"""GenericpublicrunnercachepreloadfororiginalUbuntu;no taskoutputs/testsrun."""
import hashlib,json,pathlib,subprocess,time
R=pathlib.Path(__file__).resolve().parent
ENV=['-e','UV_OFFLINE=1','-e','UV_PYTHON_DOWNLOADS=never','-e','UV_NO_INDEX=1','-e','UV_FIND_LINKS=/opt/public-wheels']
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def inputs():
 inv=json.loads((R/'tex-recovery-cache-inventory.json').read_text());proof=json.loads((R/'tex-cached-software-preflight.json').read_text());assert proof['passed'] and proof['cleanup_verified'];wheelroot=pathlib.Path(proof['private_root'])/'wheels'
 assert {p.name:sha(p) for p in wheelroot.iterdir()}=={pathlib.Path(v['path']).name:v['sha256'] for v in inv['verified_wheels'].values()}
 root=pathlib.Path('/tmp/solpi-tex-public-runtime-expanded');uv=root/'uv/uv-x86_64-unknown-linux-gnu';assert sha(uv/'uv')=='d3dc3ca8e29337dd602a9a4df9e6edb15ebc52aed91461debeedb96939dc4ce0' and sha(uv/'uvx')=='421b1bb58429180a04ade98da066b5a5b6763e8ed74edef97359701c4cb42db8';python=root/'cpython/python';assert python.is_dir()
 return {'software_scope':'publicuv0.9.5/CP3137/pytest8.4.1/plugin0.3.5;notarget/test/solution','uv_root':str(uv),'python_root':str(python),'mounts':[str(wheelroot)+':/opt/public-wheels:ro'],'wheel_hashes':proof['public_wheel_hashes'],'setup_module_sha256':sha(pathlib.Path(__file__)),'proof_sha256':sha(R/'tex-cached-software-preflight.json')}
def prepare(container,image_id,root,run=subprocess.run):
 spec=inputs();root=pathlib.Path(root);deadline=time.monotonic()+90
 def call(*a):return run(['docker',*a],capture_output=True,text=True,check=True,timeout=max(.1,deadline-time.monotonic())).stdout
 x=json.loads(call('inspect',container))[0]
 if x['Image']!=image_id or not x['State']['Running'] or x['State'].get('Paused') or set(x['NetworkSettings']['Networks'])!={'none'} or x['Config']['Entrypoint']!=['/bin/sh'] or x['Config']['Cmd']!=['-c','sleep infinity']:raise ValueError('original disconnected idle grader required')
 mounts=[m for m in x['Mounts'] if m['Destination']=='/opt/public-wheels'];assert len(mounts)==1 and not mounts[0]['RW'] and mounts[0]['Source']==spec['mounts'][0].split(':')[0]
 call('exec',container,'mkdir','-p','/root/.local/bin','/root/.local/share/uv/python');call('cp',spec['uv_root']+'/uv',container+':/root/.local/bin/uv');call('cp',spec['uv_root']+'/uvx',container+':/root/.local/bin/uvx');call('cp',spec['python_root'],container+':/root/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu');call('exec',container,'/bin/sh','-c','printf \'%s\\n\' \'export PATH="/root/.local/bin:$PATH"\' > /root/.local/bin/env')
 text=call('exec',*ENV,'-w','/',container,'/bin/sh','-c','set -eu; /root/.local/bin/uv --version; /root/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/bin/python3.13 --version; /root/.local/bin/uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version');assert 'uv 0.9.5' in text and 'Python 3.13.7' in text and 'pytest 8.4.1' in text;(root/'trusted-setup.log').write_text(text+'\n')
 return {'trusted_software_preload_complete':True,'test_network_disconnected':True,'network':'none','seconds':90-max(0,deadline-time.monotonic()),'setup_log_sha256':sha(root/'trusted-setup.log'),'target_builds':0,'target_installs':0,'original_test_script_unchanged':True,'cache_inputs':spec}
def grade_argv(container):return ['docker','exec','-w','/app',*ENV,container,'bash','/tests/test.sh']
