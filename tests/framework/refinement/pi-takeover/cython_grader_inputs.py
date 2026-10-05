"""Pinned offline trusted dependency setup;never install/build the target."""
import hashlib,json,pathlib,re,subprocess
from actor_public_inputs import recipe
from public_artifact_cache import verify_artifact_directory
from artifact_capture import CaptureError
R=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
 spec=recipe('build-cython-ext');binding=json.loads((R/'public-cython-wheels-binding.json').read_text());manifest=R/'public-cython-wheels-cache.json'
 if sha(manifest)!=binding['cache_sha256']:raise CaptureError('grader cache manifest changed')
 cache=json.loads(manifest.read_text());root=pathlib.Path(cache['private_root']);verify_artifact_directory(root/'wheels',cache['artifacts'])
 req=root/'requirements.txt'
 if req.is_symlink() or sha(req)!=binding['requirements_sha256']:raise CaptureError('grader requirements changed')
 for line in req.read_text().splitlines():
  if not re.fullmatch(r'[A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+',line) or re.split(r'==',line)[0].lower().replace('_','-')=='pyknotid':raise CaptureError('unsupported or target dependency requirement')
 if any('pyknotid' in k.lower() for k in cache['artifacts']):raise CaptureError('target artifact in public software cache')
 supplement=json.loads((R/'cython-grader-wheels-cache.json').read_text());verify_artifact_directory(pathlib.Path(supplement['private_root'])/'wheels',supplement['artifacts'])
 if supplement['actor_delivery'] or set(supplement['versions'])!={'pytest','pytest-json-ctrf','iniconfig','pluggy','pygments'} or supplement['versions']['pytest']!='8.4.1' or supplement['versions']['pytest-json-ctrf']!='0.3.5':raise CaptureError('unexpected trusted runner cache')
 for name,record in supplement['metadata'].items():
  path=pathlib.Path(supplement['private_root'])/(name+'-metadata.json')
  if sha(path)!=record['sha256']:raise CaptureError('runner public metadata changed')
  if name in ['iniconfig','pluggy','pygments'] and any(f['upload_time_iso_8601']>='2025-11-01' for f in json.loads(path.read_text())['urls']):raise CaptureError('runner dependency outside declared epoch')
 env={**binding['environment'],'PIP_FIND_LINKS':'/opt/public-wheels /opt/grader-wheels'}
 return {'image_id':spec['grader_image_id'],'mounts':binding['mounts']+[supplement['mount']],'environment':env,'requirements_sha256':binding['requirements_sha256'],'cache_manifest_sha256':binding['cache_sha256'],'runner_cache_sha256':sha(R/'cython-grader-wheels-cache.json')}

def docker_options(spec):
 out=[]
 for mount in spec['mounts']:out+=['-v',mount]
 for key,value in sorted(spec['environment'].items()):out+=['-e',key+'='+value]
 return out

def prepare(container,image_id,installation_absent=False,run=subprocess.run):
 spec=inputs();x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(x)!=1 or image_id!=spec['image_id'] or x[0]['Image']!=image_id or not x[0]['State']['Running'] or x[0]['State'].get('Paused'):raise CaptureError('wrong trusted running grader')
 if x[0]['Config'].get('Entrypoint')!=['/bin/sh'] or x[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise CaptureError('unexpected grader entrypoint')
 expected={m.rsplit(':',2)[1]:m.rsplit(':',2)[0] for m in spec['mounts']};actual={m['Destination']:m for m in x[0].get('Mounts',[])}
 if any(d not in actual or actual[d]['Source']!=s or actual[d]['RW'] for d,s in expected.items()):raise CaptureError('grader cache mount changed')
 env=dict(v.split('=',1) for v in x[0]['Config']['Env'])
 if any(env.get(k)!=v for k,v in spec['environment'].items()):raise CaptureError('grader dependency environment changed')
 run(['docker','exec',container,'python','-m','pip','install','--no-index','--find-links','/opt/public-wheels','--find-links','/opt/grader-wheels','-r','/opt/public-requirements.txt','pytest==8.4.1','pytest-json-ctrf==0.3.5'],capture_output=True,text=True,check=True,timeout=300)
 # Private grader witness,not actor guidance. Never imports actor target code.
 program="import json,importlib.metadata as m,numpy;print(json.dumps({'numpy':numpy.__version__,'planarity':m.version('planarity'),'target_metadata_present':any(d.metadata.get('Name','').lower()=='pyknotid' for d in m.distributions())}))"
 p=run(['docker','exec','-w','/',container,'python','-c',program],capture_output=True,text=True,check=True,timeout=20);w=json.loads(p.stdout)
 if w['numpy']!='2.3.0' or w['planarity']!='0.6' or (installation_absent and w['target_metadata_present']):raise CaptureError('dependency versions or preserved target absence violated')
 return {'dependency_setup_complete':True,'requirements_sha256':spec['requirements_sha256'],'witness':w,'target_builds':0,'target_installs':0,'network_required':False}
