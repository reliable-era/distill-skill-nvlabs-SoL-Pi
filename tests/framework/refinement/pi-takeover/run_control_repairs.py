"""Prospective changed-adapter controls only;reuse original worker,retain originals."""
import argparse,ast,hashlib,json,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--task',choices=['train-fasttext','make-doom-for-mips','build-cython-ext','build-pmars'],required=True);p.add_argument('--cython-epoch-controls',action='store_true');a=p.parse_args();task=a.task
assert not a.cython_epoch_controls or task=='build-cython-ext'
base=(R/'run_first_terminal_controls.py').read_text();parent=ast.parse((R/'run_remaining_terminal_controls.py').read_text());function=next(x for x in parent.body if isinstance(x,ast.FunctionDef) and x.name=='generated');ns={'template':base};exec(compile(ast.Module(body=[function],type_ignores=[]),'reuse-control-generation','exec'),ns)
t=next(x for x in json.loads((R/'terminal-readiness-inventory.json').read_text())['tasks'] if x['id']==task);code=ns['generated'](t).replace('/tmp/solpi-controls-'+task+'-v1','/tmp/solpi-controls-'+task+'-repair-v1').replace('control-'+task+'-','repaired-control-'+task+'-')
changes=[]
if task=='train-fasttext':
 code=code.replace('import datetime,hashlib,json,pathlib,subprocess,time,uuid','import datetime,hashlib,json,pathlib,subprocess,time,uuid,shutil')
 code=code.replace("  try:\n   subprocess.run", "  shutil.copytree(SOURCE/'tests',d/'tests-copy')\n  try:\n   subprocess.run",1).replace("str(SOURCE/'tests')+':/tests:ro'","str(d/'tests-copy')+':/tests'")
 changes=['Trusted grader gets fresh private writable copy of tests for official archive extraction;original source immutable andneveractor-visible']
elif task=='build-cython-ext' and a.cython_epoch_controls:
 constraint=pathlib.Path('/tmp/solpi-cython-epoch-constraints.txt');constraint.write_text('planarity==0.6\n')
 code=code.replace('-repair-v1','-epoch-v1').replace('repaired-control-build-cython-ext-','epoch-control-build-cython-ext-')
 code=code.replace("'-v',str(SOURCE/'tests')+':/tests:ro'","'-e','PIP_CONSTRAINT=/opt/epoch-constraints.txt','-e','UV_CONSTRAINT=/opt/epoch-constraints.txt','-v',"+repr(str(constraint)+':/opt/epoch-constraints.txt:ro')+",'-v',str(SOURCE/'tests')+':/tests:ro'")
 changes=['Freeze planarity at0.6,newest releasebefore declaredimage20251031;major1.0.0released2026changesgraphAPI;bothbaseline/goldconstraintidentical;originaltests/oracleunchanged']
elif task=='build-cython-ext':
 code=code.replace("'controls':['baseline','gold']","'controls':['gold']").replace("['docker','exec',name,'bash','/tests/test.sh']","['docker','exec','-e','PYTEST_ADDOPTS=-vv --showlocals',name,'bash','/tests/test.sh']")
 changes=['Gold-only diagnostic with full pytest verbosity;unchanged oracle/tests/dependencies;not a new baseline/gold certificate or retry-to-pass']
elif task=='build-pmars':
 archive=pathlib.Path('/tmp/solpi-pmars-archive-probe-v1/snapshot-debian.sources');assert archive.exists()
 code=code.replace("'-v',str(SOURCE/'tests')+':/tests:ro'","'-v','/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro','-v',str(SOURCE/'tests')+':/tests:ro'")
 needle="   if kind=='gold':"
 replacement="   subprocess.run(['docker','cp',"+repr(str(archive))+",name+':/etc/apt/sources.list.d/debian.sources'],check=True,capture_output=True,timeout=15)\n   with (d/'archive-metadata-refresh.log').open('wb') as f:\n    refresh=subprocess.run(['docker','exec',name,'apt-get','-o','Acquire::Retries=0','-o','Acquire::https::Timeout=15','update'],stdout=f,stderr=subprocess.STDOUT,timeout=120)\n   if refresh.returncode:raise RuntimeError('signed archive metadata refresh failed')\n"+needle
 assert code.count(needle)==1;code=code.replace(needle,replacement)
 changes=['Identical signed Debian snapshot repositories dated20251031(image tag) beforebaseline/gold;preserve original sources-filelayout;no packagepreinstallation ororacle/test edits']
else:
 needle="   if kind=='gold':"
 replacement="   with (d/'apt-metadata-refresh.log').open('wb') as f:\n    refresh=subprocess.run(['docker','exec',name,'apt-get','update'],stdout=f,stderr=subprocess.STDOUT,timeout=120)\n   if refresh.returncode:raise RuntimeError('apt metadata refresh failed')\n"+needle
 assert code.count(needle)==1;code=code.replace(needle,replacement);changes=['Refresh expired apt indexes identically before baseline andgold;no packageinstall,oracle/test/task edit orpresolvedbaseline']
record={'task':task,'old_result_sha256':hashlib.sha256((R/('control-'+task+'-result.json')).read_bytes()).hexdigest(),'generated_worker_sha256':hashlib.sha256(code.encode()).hexdigest(),'changes':changes,'oracle_seconds':300,'verifier_seconds':600,'apt_refresh_seconds':120 if task in ['make-doom-for-mips','build-pmars'] else 0,'maximum_worker_seconds':2100,'model_POSTs':0,'retries':0,'candidate_changed':False,'task_substituted':False};
if task=='build-pmars':record['archive_sources_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest();record['public_ca_sha256']=hashlib.sha256(pathlib.Path('/etc/ssl/certs/ca-certificates.crt').read_bytes()).hexdigest()
authorization_name=('epoch-' if a.cython_epoch_controls else 'repair-')+task+'-authorization.json'
if a.cython_epoch_controls:record['constraint_sha256']=hashlib.sha256(constraint.read_bytes()).hexdigest();record['selection_rule']='Latest planarity releasebefore20251031,chosenfromrelease metadata'
(R/authorization_name).write_text(json.dumps(record,indent=2)+'\n');launch="exec(compile("+repr(code)+",'changed-adapter-control','exec'),{'__name__':'__main__','__file__':"+repr(str(R/'run_first_terminal_controls.py'))+"})"
with pathlib.Path('/tmp/solpi-repair-'+task+('-epoch' if a.cython_epoch_controls else '')+'.log').open('wb') as out:result=subprocess.run([sys.executable,'-c',launch],stdout=out,stderr=subprocess.STDOUT,timeout=2100)
print(json.dumps({'task':task,'worker_exit':result.returncode,'model_POSTs':0}))
