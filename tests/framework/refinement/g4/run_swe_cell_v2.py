"""One G4 C attempt: scoped G3 actor/broker lifecycle + official SWE adapter.
Scheduler owns16-slot admission/retry decisions. This file never reschedules.
All provider receipts, native output, captured patch, raw grade and cleanup stay.
"""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,tarfile,threading,time,uuid
from native import authorized,create_args,argv,H
from source_archive import archive_source
from transport import Broker,save,metadata,waiting_zero
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def command(args,**kw):return subprocess.run(args,check=True,capture_output=True,timeout=120,**kw)
def absent(name):
 r=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);return r.returncode!=0 and 'No such' in r.stderr

def attempt(cell,number,root,plan,window,start_callback):
 authorized(cell,plan,window)
 if cell['part']!='C':raise RuntimeError('SWE runner is Part C only')
 root=pathlib.Path(root);root.mkdir(mode=0o700);(root/'skills').mkdir();baseline=pathlib.Path(plan['prepared_tasks'][cell['task']]);manifest=json.loads((baseline/'manifest.json').read_text());assert manifest['prepared'] and manifest['gold_in_actor'] is False;assert sha(baseline/'prompt.txt')==manifest['prompt_sha256'];prompt=(baseline/'prompt.txt').read_text()+'\nRun budget:60 model requests/7200s wall/16384 output tokens per request. Work only on this task; no network retrieval or subagents. Supplied resources are in /skills.\n'
 for skill in plan['arm_skills'][cell['arm']]:
  source=pathlib.Path(plan['skills'][skill]['path']);assert sha(source/'SKILL.md')==plan['skills'][skill]['SKILL_sha256'];shutil.copytree(source,root/'skills'/skill);prompt+='\n'+(source/'SKILL.md').read_text()
 if not plan['arm_skills'][cell['arm']]:prompt+='\nNo skill is supplied.\n'
 (root/'prompt.txt').write_text(prompt);name='solpi-g4-C-'+uuid.uuid4().hex[:16];row=dict(cell_id=cell['cell_id'],part='C',task=cell['task'],arm=cell['arm'],round=cell['round'],attempt=number,root=str(root),actor=name,native_started=False,solved=None,grade_valid=False,timeout=False,grader_timeout=False,error=None,phase='setup');broker=None;process=None;started=None;stop=threading.Event();sampler=None
 try:
  broker=Broker(root/'transport',time.monotonic()+7200,cell['arm']);broker.start();image=plan['images'][cell['task']];command(create_args(name,image,root,'C',8192,'/testbed',plan['wheelhouse']));command(['docker','start',name]);ins=json.loads(command(['docker','inspect',name]).stdout);assert ins[0]['Image']==image;save(root/'actor-inspect.json',ins[0]);command(['docker','exec',name,'sh','-c','rm -rf /testbed; mkdir /testbed']);archive_source(baseline/'workspace',root/'starter.tar')
  with (root/'starter.tar').open('rb') as source_tar:command(['docker','cp','-',name+':/'],stdin=source_tar)
  head=command(['docker','exec',name,'git','-C','/testbed','rev-parse','HEAD']).stdout.decode().strip();assert head==manifest['snapshot_commit'];save(root/'source-proof.json',dict(snapshot_commit=head,original_base_commit=manifest['base_commit'],gold_in_actor=False,upstream_history_in_actor=False))
  row['phase']='native';admission=start_callback(cell,number)
  if not waiting_zero(admission.get('load',{})) or type(admission.get('occupied_slots_after_admission')) is not int or not 1<=admission['occupied_slots_after_admission']<=16:raise RuntimeError('Fresh zero-wait/16-slot admission proof required before native start')
  save(root/'admission.json',admission);started=time.monotonic();broker.deadline=started+7200;row.update(native_started=True,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(root/'attempt-progress.json',row);samples=[dict(kind='start',observation=admission)]
  def sample():
   while not stop.wait(30):
    try:v=metadata('/get_load')
    except Exception as e:v=dict(error=type(e).__name__,message=str(e))
    samples.append(dict(kind='periodic',observation=v));save(root/'load-samples.json',samples)
  save(root/'load-samples.json',samples);sampler=threading.Thread(target=sample,daemon=True);sampler.start();shell='source /opt/miniconda3/bin/activate; conda activate testbed; python3 /opt/solpi/relay.py & relay=$!; trap "kill $relay 2>/dev/null || true" EXIT; sleep 0.2; "$@"'
  with (root/'native.jsonl').open('xb') as out:
   process=subprocess.Popen(['docker','exec',name,'bash','-lc',shell,'g4',*argv(prompt)],stdout=out,stderr=subprocess.STDOUT)
   try:process.wait(timeout=max(.1,broker.deadline-time.monotonic()-10))
   except subprocess.TimeoutExpired:row['timeout']=True
   subprocess.run(['docker','stop','-t','0',name],capture_output=True,timeout=30);process.wait(timeout=30)
  row.update(native_exit=process.returncode,wall_seconds=time.monotonic()-started,native_sha256=sha(root/'native.jsonl'));stop.set();sampler.join(timeout=15);broker.close();broker=None
  # Never extract candidate symlinks outside the owned capture root.
  row['phase']='capture';archive=root/'captured.tar';work=root/'captured';work.mkdir()
  with archive.open('xb') as out:subprocess.run(['docker','cp',name+':/testbed/.','-'],stdout=out,stderr=subprocess.PIPE,check=True,timeout=120)
  with tarfile.open(archive) as tar:tar.extractall(work,filter='data')
  git=work/'.git'
  if git.is_symlink() or git.is_file():git.unlink()
  elif git.exists():shutil.rmtree(git)
  shutil.copytree(baseline/'workspace/.git',git)
  # Native commits/config/hooks are not trusted by host Git. New source files
  # are intent-added against the original single snapshot, not actor history.
  new=[str(p.relative_to(work)) for p in work.rglob('*') if p.is_file() and '.git' not in p.relative_to(work).parts and str(p.relative_to(work)) not in manifest['source_tree']]
  env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null')
  if new:command(['git','-C',str(work),'add','-N','--force','--',*new],env=env)
  patch=command(['git','-C',str(work),'diff','--binary','HEAD'],env=env).stdout;(root/'model.patch').write_bytes(patch);row['patch_sha256']=sha(root/'model.patch')
  # The unchanged official adapter creates its root. Never precreate it.
  if (root/'grade').exists():raise RuntimeError('Fresh grader root required')
  row['phase']='grader'
  with (root/'grader.private.log').open('xb') as log:graded=subprocess.run([plan['grader_python'],str(H/'grade_swe.py'),str(root/'grade'),cell['task'],str(root/'model.patch'),plan['grader_plan']],stdout=log,stderr=subprocess.STDOUT,timeout=900)
  result=root/'grade/grade-result.json'
  if graded.returncode or not result.exists():raise RuntimeError('Original grader worker failed; retain cost and reconcile owned grader')
  g=json.loads(result.read_text());row.update(solved=g['solved'],grade_valid=g['grade_valid'],grader_sha256=sha(result),grader_owned_containers_absent=g['owned_containers_absent'])
 except Exception as e:
  row['error']=dict(type=type(e).__name__,message=str(e)[:500]);row['grader_timeout']=row['phase']=='grader' and isinstance(e,subprocess.TimeoutExpired)
 finally:
  stop.set()
  if sampler:sampler.join(timeout=15)
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);row['actor_absent']=absent(name)
  owned=root/'grade/owned.json';grade_cleanup=[]
  if owned.exists():
   for grader in json.loads(owned.read_text())['names']:
    if not grader.startswith('sweb.eval.'+cell['task'].lower()+'.g4-grade-'):grade_cleanup.append('unverified grader ownership');continue
    subprocess.run(['docker','rm','-f',grader],capture_output=True,timeout=30)
    if not absent(grader):grade_cleanup.append(grader)
  row['grader_cleanup_errors']=grade_cleanup
  if process and process.poll() is None:
   try:process.wait(timeout=30)
   except subprocess.TimeoutExpired:row['actor_process_uncertain']=True
  if broker:
   try:broker.close()
   except Exception as e:row['broker_cleanup_error']=str(e)
  ledger=json.loads((root/'transport/ledger.json').read_text()) if (root/'transport/ledger.json').exists() else dict(provider_POST=0,records=[]);records=ledger['records'];row['owned_cleanup_verified']=row['actor_absent'] and not grade_cleanup and not row.get('actor_process_uncertain') and not row.get('broker_cleanup_error');row.update(requests=ledger['provider_POST'],recorded_receipts=len(records),known_tokens_lower_bound=sum(r['tokens_lower_bound'] for r in records),cost_complete=len(records)==ledger['provider_POST'] and all(r['cost_complete'] for r in records),connection_infra_failure=any(r.get('connection_infra_failure') for r in records),backend='127.0.0.1:8000');save(root/'attempt-result.json',row)
 return row
