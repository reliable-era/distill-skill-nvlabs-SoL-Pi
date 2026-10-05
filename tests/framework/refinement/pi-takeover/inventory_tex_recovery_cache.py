"""Read-onlypublicrunnercacheinventory;NO downloads/model/containers/graders."""
import email,hashlib,json,pathlib,zipfile
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.markers import default_environment
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 cache=json.loads((R/'cython-grader-wheels-cache.json').read_text());wheels=pathlib.Path(cache['private_root'])/'wheels';verified={}
 for name,rec in cache['artifacts'].items():
  p=wheels/name;assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'];verified[name]={'path':str(p),'bytes':rec['bytes'],'sha256':rec['sha256'],'public_url':rec['url']}
 p=pathlib.Path('/tmp/solpi-public-cython-wheels-1ef8377ad8/wheels/packaging-26.3-py3-none-any.whl');manifest=json.loads((R/'public-cython-wheels-cache.json').read_text());assert p.name in manifest['artifacts'];rec=manifest['artifacts'][p.name];assert sha(p)==rec['sha256'] and p.stat().st_size==rec['bytes'];verified[p.name]={'path':str(p),'bytes':rec['bytes'],'sha256':rec['sha256'],'public_url':rec.get('url'),'public_cache_manifest':'public-cython-wheels-cache.json'}
 metadata={}
 for name,rec in verified.items():
  with zipfile.ZipFile(rec['path']) as z:
   names=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')];assert len(names)==1;msg=email.message_from_bytes(z.read(names[0]));metadata[name]={'name':msg['Name'],'version':msg['Version'],'requires_python':msg['Requires-Python'],'requires_dist':msg.get_all('Requires-Dist',[])}
 versions={canonicalize_name(m['name']):m['version'] for m in metadata.values()};env=default_environment();env.update(python_version='3.13',python_full_version='3.13.7',implementation_version='3.13.7',implementation_name='cpython',os_name='posix',sys_platform='linux',platform_system='Linux',extra='');dependencies=[]
 for m in metadata.values():
  assert '3.13.7' in SpecifierSet(m['requires_python'] or ''),'pythonversionincompatible'
  for line in m['requires_dist']:
   req=Requirement(line)
   if req.marker and not req.marker.evaluate(env):continue
   key=canonicalize_name(req.name);assert key in versions and versions[key] in req.specifier,('missing/incompatible',line);dependencies.append({'package':m['name'],'requirement':line,'resolved_version':versions[key]})
 report={'static_dependency_resolution':dependencies,'status':'partial_public_cache_inventory_not_readiness','read_only':True,'network_requests':0,'model_POST':0,'grader_attempts':0,'Docker_creates':0,'verified_wheels':verified,'metadata':metadata,'total_wheel_bytes':sum(r['bytes'] for r in verified.values()),'available_host_uv_version':'0.11.7','required_uv_version':'0.9.5','uv_095_cached_verified':False,'required_cpython':'3.13.7','host_cpython_variants_observed':['3.10.20','3.11.15','3.13.3'],'cpython_3137_cache_verified':False,'six_generic_package_wheels_available':True,'static_package_requirement_closure_verified':True,'trusted_package_closure_fully_verified':False,'closure_compatibility_execution_verified':False,'matching_all_transitive_versions_to_prior_fresh_graders_verified':False,'public_software_only':True,'benchmark_solutions_or_target_outputs_included':False,'offline_bootstrap_ready':False,'need_before_recovery':['Explicitseparatefinitegraderphaseauthorization;oldone-repaircapexhausted','Pinnedpublicuv0.9.5+CPython3.13.7archiveswithoriginalsource/checksums;do not substitutehostversions','VerifygenericrunnerclosureinoriginalUbuntuimagebeforecountinganyofficialgradingattempt','Preloadgenericsandrununchangedoriginaltest.shdisconnectedonEXACTsavedKcapture;preserveallhistoricalfailures'],'goal_complete':False};(R/'tex-recovery-cache-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['metadata','verified_wheels']},indent=2))
