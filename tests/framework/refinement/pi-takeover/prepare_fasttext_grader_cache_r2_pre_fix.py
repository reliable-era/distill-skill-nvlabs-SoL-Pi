"""Publicdependency-closureONLYrepair;preserveoriginalcache/probefailure."""
import pathlib,json,hashlib,shutil,uuid,zipfile,email
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.markers import default_environment
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 assert not (R/'fasttext-public-grader-cache-r2.json').exists();prior=R/'fasttext-public-grader-cache.json';x=json.loads(prior.read_text());assert x['prepared'];root=pathlib.Path('/tmp/solpi-fasttext-public-grader-closure-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);wheels=root/'wheels';wheels.mkdir();original=pathlib.Path(x['root'])/'wheels';artifacts={}
 for n,v in x['artifacts'].items():assert sha(original/n)==v['sha256'];shutil.copyfile(original/n,wheels/n);artifacts[n]=v
 actor=json.loads((R/'public-fasttext-wheels-cache.json').read_text());p=pathlib.Path(actor['private_root'])/'wheels';added=[]
 for n,v in actor['artifacts'].items():
  if n.startswith(('pybind11-','setuptools-')):assert sha(p/n)==v['sha256'];shutil.copyfile(p/n,wheels/n);artifacts[n]={**v,'source_manifest':'public-fasttext-wheels-cache.json'};added.append(n)
 assert len(added)==2;env=default_environment();env.update(python_version='3.11',python_full_version='3.11.14',extra='',sys_platform='linux',platform_machine='x86_64',platform_python_implementation='CPython',implementation_name='cpython');versions={};required={}
 for p in wheels.iterdir():
  with zipfile.ZipFile(p) as z:
   names=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')];assert len(names)==1;meta=email.message_from_bytes(z.read(names[0]));name=canonicalize_name(meta['Name']);versions[name]=meta['Version'];required[name]=meta.get_all('Requires-Dist',[])
 checks=[]
 for name,requirements in required.items():
  for raw in requirements:
   req=Requirement(raw)
   if req.marker and not req.marker.evaluate(env):continue
   dependency=canonicalize_name(req.name);assert dependency in versions and req.specifier.contains(versions[dependency],prereleases=True),(name,str(req));checks.append({'package':name,'requirement':str(req),'resolved_version':versions[dependency]})
 report={**x,'root':str(root),'prior_cache_sha256':sha(prior),'failed_probe_sha256':sha(R/'fasttext-cached-software-probe.json'),'artifacts':artifacts,'HTTP_requests_including_redirects':0,'network_bytes':0,'requests':[],'repair_scope':'addONLYpublicpybind11/setuptoolsalreadycached;metadata-wheelclosureprovenCP31114;no originalfailuremutation/model/target/test/data','added_wheels':added,'dependency_closure':checks,'versions_closed':versions,'original_cache_unchanged':all(sha(original/n)==v['sha256'] for n,v in x['artifacts'].items()),'runtime_imports_verified':False};(R/'fasttext-public-grader-cache-r2.json').write_text(json.dumps(report,indent=2)+'\n');print({'root':str(root),'added_wheels':added,'closed_dependencies':len(checks),'network_requests':0,'old_failure_preserved':True})
