"""Capture-only projection: omit only proved untracked/ignored non-file links.
Original tar/attempt/cost untouched. Remaining members always use data_filter.
No model/actor/grader calls. Mirrors frozen v2 patch construction exactly.
"""
import hashlib,json,os,pathlib,shutil,subprocess,tarfile

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def run(args,**kw):return subprocess.run(args,check=True,capture_output=True,timeout=120,**kw)
def name(member):
 p=pathlib.PurePosixPath(member.name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe member path')
 return str(p)

def project(archive,baseline,destination):
 archive=pathlib.Path(archive);baseline=pathlib.Path(baseline);destination=pathlib.Path(destination)
 if os.path.lexists('/testbed'):raise ValueError('Host /testbed exists: original is_file semantics not proved')
 manifest=json.loads((baseline/'manifest.json').read_text());source=baseline/'workspace'
 if not manifest['prepared'] or manifest['gold_in_actor'] is not False:raise ValueError('trusted sanitized snapshot required')
 destination.mkdir(mode=0o700);work=destination/'captured';work.mkdir();omitted=[]
 with tarfile.open(archive) as tar:
  members=tar.getmembers();byname={name(m):m for m in members}
  if len(byname)!=len(members):raise ValueError('duplicate normalized paths')
  expected={str(p.relative_to(source)):p.read_bytes() for p in source.rglob('.gitignore')}
  actual={n:tar.extractfile(m).read() for n,m in byname.items() if pathlib.PurePosixPath(n).name=='.gitignore' and m.isfile() and '.git' not in pathlib.PurePosixPath(n).parts}
  if any(actual.get(n)!=b for n,b in expected.items()):raise ValueError('frozen ignore rules changed/missing')
  for n,m in byname.items():
   if not (m.issym() and pathlib.PurePosixPath(m.linkname).is_absolute()):continue
   if not n.startswith('result_images/') or pathlib.PurePosixPath(n).suffix not in {'.png','.pdf','.eps'} or not m.linkname.startswith('/testbed/') or '..' in pathlib.PurePosixPath(m.linkname).parts or n in manifest['source_tree']:raise ValueError('absolute link not eligible for projection')
   ancestors={str(p) for p in pathlib.PurePosixPath(n).parents}
   if any(str(pathlib.PurePosixPath(extra).parent) in ancestors for extra in actual.keys()-expected.keys()):raise ValueError('new relevant ignore rules')
   ignored=subprocess.run(['git','--no-optional-locks','-C',str(source),'check-ignore','--',n],capture_output=True,timeout=20)
   tracked=subprocess.run(['git','--no-optional-locks','-C',str(source),'ls-files','--error-unmatch','--',n],capture_output=True,timeout=20)
   if ignored.returncode!=0 or tracked.returncode==0:raise ValueError('link is not proven ignored+untracked')
   omitted.append(dict(name=n,target=m.linkname,frozen_ignored=True,untracked=True,original_host_is_file=False))
  if not omitted:raise ValueError('No eligible links; no recovery required')
  skip={r['name'] for r in omitted}
  tar.extractall(work,members=[m for m in members if name(m) not in skip],filter='data')
 git=work/'.git'
 if git.is_symlink() or git.is_file():git.unlink()
 elif git.exists():shutil.rmtree(git)
 shutil.copytree(source/'.git',git)
 new=[str(p.relative_to(work)) for p in work.rglob('*') if p.is_file() and '.git' not in p.relative_to(work).parts and str(p.relative_to(work)) not in manifest['source_tree']]
 env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null')
 if new:run(['git','-C',str(work),'add','-N','--force','--',*new],env=env)
 patch=run(['git','-C',str(work),'diff','--binary','HEAD'],env=env).stdout;(destination/'model.patch').write_bytes(patch)
 proof=dict(captured_tar_sha256=sha(archive),snapshot_commit=manifest['snapshot_commit'],omitted=omitted,patch_sha256=sha(destination/'model.patch'),retained_members=len(members)-len(omitted),new_intent_added_paths=new,unchanged_existing_ignore_rules=True,no_new_relevant_ignore_rules=True,host_testbed_absent=True,data_filter_preserved=True,original_patch_rule='v2: force intent-add only new is_file paths, then binary diff HEAD; ignored untracked absolute /testbed links would not be intent-added or diffed',model_calls=0,actor_reruns=0,auditor_sha256=sha(__file__))
 (destination/'projection-proof.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
