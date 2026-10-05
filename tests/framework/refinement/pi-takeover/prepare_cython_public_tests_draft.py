"""Prospective generic public-repository test software;never changes active recipes."""
import hashlib,json,pathlib,shutil,uuid
from public_artifact_cache import verify_artifact_directory
R=pathlib.Path(__file__).resolve().parent
if __name__=='__main__':
 source=json.loads((R/'cython-grader-wheels-cache.json').read_text());old=pathlib.Path(source['private_root'])/'wheels';verify_artifact_directory(old,source['artifacts']);root=pathlib.Path('/tmp/solpi-public-cython-tests-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o755);wheels=root/'wheels';wheels.mkdir(mode=0o755);artifacts={}
 for name,rec in source['artifacts'].items():
  if name.startswith('pytest_json_ctrf-'):continue # grader-specific plugin not needed by public package tests.
  shutil.copyfile(old/name,wheels/name);artifacts[name]=rec
 assert len(artifacts)==4;verify_artifact_directory(wheels,artifacts)
 report={'private_root':str(root),'artifacts':artifacts,'bytes':sum(r['bytes'] for r in artifacts.values()),'packages':{k:v for k,v in source['versions'].items() if k!='pytest-json-ctrf'},'mount':str(wheels)+':/opt/public-test-wheels:ro','public_task_basis':'instruction explicitly permits source-package tests;generic test software only,no hidden assertions/solutions/logs','source_cache_sha256':hashlib.sha256((R/'cython-grader-wheels-cache.json').read_bytes()).hexdigest(),'active_recipe_changed':False,'prospective_only':True,'scoring_ready':False,'native_starts':0,'provider_POST':0,'target_builds':0,'target_installs':0};(R/'public-cython-tests-cache-draft.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
