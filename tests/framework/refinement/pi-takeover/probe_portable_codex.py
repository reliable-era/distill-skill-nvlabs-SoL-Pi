"""Verify exact already-certified static CLI in selected images,zero inference."""
import datetime,hashlib,json,pathlib,subprocess,uuid
R=pathlib.Path(__file__).resolve().parent;binary=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex');expected='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
assert hashlib.sha256(binary.read_bytes()).hexdigest()==expected
cache=json.loads((R/'terminal-selected-image-cache.json').read_text());resources={x['id']:x for x in json.loads((R/'terminal-readiness-inventory.json').read_text())['tasks']};rows=[]
for task in cache['tasks']:
 meta=resources[task['task']];name='solpi-tb-cli-'+uuid.uuid4().hex[:10];row={'task':task['task'],'image_id':task['image']['image_id'],'binary_sha256':expected};created=False
 try:
  subprocess.run(['docker','create','--pull=never','--name',name,'--network','none','--cpus',str(meta['declared_cpus']),'--memory',str(meta['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,size=64m','-e','HOME=/tmp','-e','CODEX_HOME=/tmp/codex-home','-v',str(binary)+':/opt/solpi/codex:ro','--entrypoint','/opt/solpi/codex',task['image']['image_id'],'--version'],capture_output=True,check=True,timeout=10);created=True
  p=subprocess.run(['docker','start','-a',name],capture_output=True,text=True,timeout=30);row.update(exit=p.returncode,version=p.stdout.strip(),passed=p.returncode==0 and p.stdout.strip()=='codex-cli 0.160.0')
 except Exception as e:row.update(passed=False,error_type=type(e).__name__)
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)
  p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);row['owned_container_absent']=p.returncode!=0 and ('No such object: '+name in p.stderr or 'No such container: '+name in p.stderr)
 rows.append(row)
 if not row['owned_container_absent']:break
out={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Native binary/runtime compatibility only;no actor generation,SDK networking,oracle or official test execution','model_POSTs':0,'grader_calls':0,'host_config_or_credentials_mounted':False,'task_instructions_tests_solutions_read':False,'binary_sha256':expected,'tasks':rows};(R/'terminal-portable-codex-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
