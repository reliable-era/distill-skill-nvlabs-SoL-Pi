"""Original Terminal verifier on stopped native filesystem capture; no model.
Original G1 control resources/network/test.sh/reward semantics, hidden tests
mounted only after native execution. New owned grader/container/logs only.
"""
import hashlib,json,os,pathlib,subprocess,time,uuid
H=pathlib.Path(__file__).resolve().parent
SOURCE=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def grade(root,task,capture_image,metadata):
 root=pathlib.Path(root);root.mkdir(mode=0o700);logs=root/'logs';(logs/'verifier').mkdir(parents=True);logs.chmod(0o777);(logs/'verifier').chmod(0o777);source=SOURCE/task
 for p,d in metadata['source_hashes'].items():
  if sha(source/p)!=d:raise RuntimeError('Original task source changed')
 name='solpi-g4-B-grade-'+uuid.uuid4().hex[:16];record=dict(task=task,image_id=capture_image,container_name=name,solved=None,grade_valid=False,model_calls=0,errors=[],timeout=False);created=False;start=time.monotonic()
 try:
  e=metadata['environment'];cmd=['docker','create','--pull=never','--name',name,'--cpus',str(e['cpus']),'--memory',str(e['memory_mb'])+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(source/'tests')+':/tests:ro','-v',str(logs)+':/logs','--entrypoint','/bin/sh',capture_image,'-c','sleep infinity'];subprocess.run(cmd,capture_output=True,check=True,timeout=30);created=True;subprocess.run(['docker','start',name],capture_output=True,check=True,timeout=30);ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0];h=ins['HostConfig'];assert ins['Image']==capture_image and not h['Privileged'] and not h.get('DeviceRequests') and h['NanoCpus']==int(e['cpus']*1e9) and h['Memory']==e['memory_mb']*1024**2;assert any(m['Destination']=='/tests' and m['RW'] is False for m in ins['Mounts']);(root/'container-inspect.json').write_text(json.dumps(ins,indent=2))
  # Snapshotting necessarily loses daemon processes. Restart only the task's
  # existing configured services in its OWN container (not shared nginx/SSH).
  if task=='git-multibranch':
   with (root/'service-start.private.log').open('xb') as out:subprocess.run(['docker','exec',name,'sh','-c','mkdir -p /run/sshd; /usr/sbin/sshd; nginx'],stdout=out,stderr=subprocess.STDOUT,timeout=30)
  with (root/'verifier.private.log').open('xb') as out:
   try:r=subprocess.run(['docker','exec',name,'bash','/tests/test.sh'],stdout=out,stderr=subprocess.STDOUT,timeout=metadata['verifier']['timeout_sec']);record['verifier_exit']=r.returncode
   except subprocess.TimeoutExpired:record['timeout']=True
  reward=logs/'verifier/reward.txt';record['reward']=reward.read_text().strip() if reward.exists() else None;ctrf=logs/'verifier/ctrf.json'
  if ctrf.exists():
   tests=json.loads(ctrf.read_text()).get('results',{}).get('tests',[]);record['test_events']=len(tests);record['test_statuses']=[t.get('status') for t in tests];expected=metadata['gold_original_test_events']
   if len(tests)!=expected or any(t.get('status') not in ('passed','failed') for t in tests):raise RuntimeError('Original verifier collection incomplete')
  else:raise RuntimeError('Original CTRF evidence missing')
  if record['timeout'] or record['reward'] not in ('0','1'):raise RuntimeError('Original verifier timeout/reward unavailable')
  solved=record['reward']=='1'
  if solved!=all(t['status']=='passed' for t in tests):raise RuntimeError('Original reward/test status disagreement')
  record.update(solved=solved,grade_valid=True)
 except Exception as e:record['errors'].append(dict(type=type(e).__name__,message=str(e)[:500]))
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
  gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);record['owned_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr;record['seconds']=time.monotonic()-start;record['artifacts']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};(root/'grade-result.json').write_text(json.dumps(record,indent=2)+'\n')
 return record
