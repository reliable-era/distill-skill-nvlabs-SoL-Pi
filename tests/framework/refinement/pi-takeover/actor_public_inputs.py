"""Uniform public input delivery;does not authorize inference or grant grading eligibility."""
import hashlib,json,pathlib
from public_artifact_cache import verify_artifact_directory
R=pathlib.Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((R/name).read_text())
def verify_git_cache(binding):
 cache=load('public-pyknotid-source-cache.json')
 if sha(R/'public-pyknotid-source-cache.json')!=binding['cache_manifest_sha256']:raise ValueError('source cache manifest changed')
 root=pathlib.Path(cache['private_root'])/'pyknotid.git';observed={}
 if root.is_symlink():raise ValueError('linked public source root')
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('linked public source member')
  if p.is_file():observed[p.relative_to(root).as_posix()]=sha(p)
 if observed!=cache['cache_hashes']:raise ValueError('public Git cache changed')
 config=pathlib.Path(cache['private_root'])/'clone.gitconfig'
 if config.is_symlink() or sha(config)!=binding['git_config_sha256']:raise ValueError('source rewrite config changed')

def recipe(task):
 base=next(t for t in load('selected-environment-control-bindings.json')['tasks'] if t['task']==task);result={'task':task,'actor_image_id':base['image']['image_id'],'grader_image_id':base['image']['image_id'],'cpus':base['cpus'],'memory_mb':base['memory_mb'],'mounts':[],'environment':{},'guidance':'','all_arms_uniform_required':True,'inference_authorized':False}
 if task=='build-cython-ext':
  source=load('public-pyknotid-source-binding.json');verify_git_cache(source);wheels=load('public-cython-wheels-cache.json');binding=load('public-cython-wheels-binding.json');root=pathlib.Path(wheels['private_root']);verify_artifact_directory(root/'wheels',wheels['artifacts']);
  if sha(root/'requirements.txt')!=binding['requirements_sha256']:raise ValueError('Cython requirements changed')
  result['mounts']=source['mounts']+binding['mounts'];result['environment']={**source['environment'],**binding['environment']};result['guidance']='Public task source is available through the exact instructed Git URL via a read-only local mirror. Python dependency artifacts are cached at /opt/public-wheels;index access is disabled and versions are constrained. Target source modification,compilation and installation remain your responsibility.'
 elif task=='build-pmars':
  source=load('public-pmars-source-cache.json');tools=load('public-pmars-tools-cache.json');root=pathlib.Path(source['private_root']);verify_artifact_directory(root/'downloads',source['artifacts']);verify_artifact_directory(root/'tool-archives',tools['artifacts'],True);binding=load('public-pmars-source-binding.json');result['mounts']=binding['mounts'];result['guidance']='Original public Debian source artifacts are cached at /opt/public-source and generic prerequisite packages at /opt/public-debs. External package access is disabled. Local APT installation can use sandbox=root and fresh temporary cache/list directories. No target binary or build recipe is provided.'
 elif task=='make-doom-for-mips':
  prep=load('doom-dependency-actor-image.json')
  if not prep['prepared'] or not prep['app_source_inputs_unchanged'] or not prep['target_binary_absent'] or prep['base_image_id']!=result['grader_image_id']:raise ValueError('unverified Doom preparation')
  result['actor_image_id']=prep['prepared_actor_image_id'];result['guidance']='A generic MIPS crosscompiler is preinstalled. Original task source/runtime inputs are unchanged;no target executable is supplied.'
 elif task=='train-fasttext':
  cache=load('public-fasttext-wheels-cache.json');root=pathlib.Path(cache['private_root']);verify_artifact_directory(root/'wheels',cache['artifacts']);
  if (root/'requirements.txt').is_symlink() or (root/'requirements.txt').read_text()!=''.join(k+'=='+v+'\n' for k,v in cache['versions'].items()):raise ValueError('fastText requirements changed')
  bindings=load('doom-fasttext-public-input-bindings.json')['train-fasttext'];result['mounts']=bindings['mounts'];result['environment']=bindings['environment'];result['guidance']='Public training-software dependencies are cached at /opt/public-wheels;index access is disabled and versions are constrained. No trained model is provided.'
 return result

def docker_options(spec):
 result=[]
 for mount in spec['mounts']:result+=['-v',mount]
 for key,value in sorted(spec['environment'].items()):result+=['-e',key+'='+value]
 return result

def verify_actor_inspect(metadata,spec,network,required_mounts):
 if metadata['Image']!=spec['actor_image_id'] or metadata['State'].get('Running'):raise ValueError('actor image/state changed before start')
 host=metadata['HostConfig']
 if set(metadata['NetworkSettings']['Networks'])!={network} or host['NanoCpus']!=spec['cpus']*1000000000 or host['Memory']!=spec['memory_mb']*1048576 or host['PidsLimit']!=128 or set(host.get('CapDrop') or [])!={'ALL'} or host.get('CapAdd'):raise ValueError('actor isolation/resources changed')
 if 'no-new-privileges' not in host.get('SecurityOpt',[]):raise ValueError('actor privilege policy changed')
 if set(required_mounts)-{'/opt/solpi/codex','/skills'}:raise ValueError('only pinned binary/skills may supplement public inputs')
 expected=dict(required_mounts)
 for mount in spec['mounts']:
  source,destination,mode=mount.rsplit(':',2)
  if mode!='ro' or destination in expected:raise ValueError('invalid or overlapping public mount')
  expected[destination]=source
 observed=metadata.get('Mounts',[])
 if len(observed)!=len(expected) or any(m['Destination'] not in expected or m['Source']!=expected[m['Destination']] or m['RW'] or m['Type']!='bind' for m in observed):raise ValueError('unexpected/writable actor mounts')
 if any(d=='/' or d in ['/tests','/solution','/logs','/broker'] or any(d.startswith(p+'/') for p in ['/tests','/solution','/logs','/broker']) for d in expected):raise ValueError('trusted materials exposed to actor')
 env=dict(value.split('=',1) for value in metadata['Config']['Env'])
 if any(env.get(k)!=v for k,v in spec['environment'].items()):raise ValueError('public input environment changed')
 return {'verified':True,'public_input_mounts':len(spec['mounts']),'original_grader_image_id':spec['grader_image_id'],'actor_image_id':spec['actor_image_id']}
