"""One G4 B Codex attempt using scoped G3 lifecycle and original Terminal tests.
No scheduler/retries here; hidden verifier added only to stopped FS capture.
"""
import datetime,json,pathlib,shutil,subprocess,threading,time,uuid
from native import H,authorized,create_args,argv,capture_image,sha
from transport import Broker,save,metadata,waiting_zero
from grade_terminal import grade

def absent(name):
 p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);return p.returncode!=0 and 'No such' in p.stderr

def attempt(cell,number,root,plan,window,start_callback):
 authorized(cell,plan,window)
 if cell['part']!='B':raise RuntimeError('Terminal runner is Part B only')
 root=pathlib.Path(root);root.mkdir(mode=0o700);(root/'skills').mkdir();task=plan['terminal_tasks'][cell['task']];source=pathlib.Path(plan['terminal_source'])/cell['task']
 for p,d in task['source_hashes'].items():
  if sha(source/p)!=d:raise RuntimeError('Frozen Terminal task changed')
 prompt=(source/'instruction.md').read_text()+'\n\nRun budget:60 model requests/7200s wall/16384 output tokens per request. Work only on this task; no network retrieval or subagents. Supplied resources are in /skills.\n'
 for skill in plan['arm_skills'][cell['arm']]:
  skillroot=pathlib.Path(plan['skills'][skill]['path']);assert sha(skillroot/'SKILL.md')==plan['skills'][skill]['SKILL_sha256'];shutil.copytree(skillroot,root/'skills'/skill);prompt+='\n'+(skillroot/'SKILL.md').read_text()
 if not plan['arm_skills'][cell['arm']]:prompt+='\nNo skill is supplied.\n'
 (root/'prompt.txt').write_text(prompt);name='solpi-g4-B-'+uuid.uuid4().hex[:16];row=dict(cell_id=cell['cell_id'],part='B',task=cell['task'],arm=cell['arm'],round=cell['round'],attempt=number,root=str(root),actor=name,solved=None,grade_valid=False,native_started=False,timeout=False,grader_timeout=False,error=None,phase='setup');broker=None;process=None;stop=threading.Event();sampler=None;started=None
 try:
  original=json.loads(subprocess.check_output(['docker','image','inspect',task['image_id']],timeout=20))[0];workdir=original['Config'].get('WorkingDir') or '/app';row['original_workdir']=workdir
  broker=Broker(root/'transport',time.monotonic()+7200,cell['arm']);broker.start();args=create_args(name,task['image_id'],root,'B',task['environment']['memory_mb'],workdir);subprocess.run(args,check=True,capture_output=True,timeout=30);subprocess.run(['docker','start',name],check=True,capture_output=True,timeout=30);ins=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0];assert ins['Image']==task['image_id'];save(root/'actor-inspect.json',ins)
  admission=start_callback(cell,number)
  if not waiting_zero(admission.get('load',{})) or type(admission.get('occupied_slots_after_admission')) is not int or not 1<=admission['occupied_slots_after_admission']<=16:raise RuntimeError('Fresh zero-wait/16-slot admission proof required')
  save(root/'admission.json',admission);started=time.monotonic();broker.deadline=started+7200;row.update(native_started=True,phase='native',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(root/'attempt-progress.json',row);samples=[dict(kind='start',observation=admission)]
  def sample():
   while not stop.wait(30):
    try:v=metadata('/get_load')
    except Exception as e:v=dict(error=type(e).__name__,message=str(e))
    samples.append(dict(kind='periodic',observation=v));save(root/'load-samples.json',samples)
  save(root/'load-samples.json',samples);sampler=threading.Thread(target=sample,daemon=True);sampler.start();shell='python3 /opt/solpi/relay.py & relay=$!; trap "kill $relay 2>/dev/null || true" EXIT; sleep 0.2; "$@"'
  with (root/'native.jsonl').open('xb') as out:
   process=subprocess.Popen(['docker','exec','-w',workdir,name,'sh','-c',shell,'g4',*argv(prompt)],stdout=out,stderr=subprocess.STDOUT)
   try:process.wait(timeout=max(.1,broker.deadline-time.monotonic()-10))
   except subprocess.TimeoutExpired:row['timeout']=True
   subprocess.run(['docker','stop','-t','0',name],capture_output=True,timeout=30);process.wait(timeout=30)
  row.update(native_exit=process.returncode,wall_seconds=time.monotonic()-started,native_sha256=sha(root/'native.jsonl'));stop.set();sampler.join(timeout=15);broker.close();broker=None;row['phase']='capture';tag='solpi-g4-capture:'+uuid.uuid4().hex;image=capture_image(name,tag);row.update(capture_image_id=image,capture_tag=tag);save(root/'capture.json',dict(image_id=image,tag=tag,original_image_id=task['image_id']));row['phase']='grader';g=grade(root/'grade',cell['task'],image,task);row.update(solved=g['solved'],grade_valid=g['grade_valid'],grader_timeout=g['timeout'],grader_owned_container_absent=g['owned_container_absent'],grader_sha256=sha(root/'grade/grade-result.json'))
 except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e)[:500])
 finally:
  stop.set()
  if sampler:sampler.join(timeout=15)
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);row['actor_absent']=absent(name)
  if process and process.poll() is None:
   try:process.wait(timeout=30)
   except subprocess.TimeoutExpired:row['actor_process_uncertain']=True
  if broker:
   try:broker.close()
   except Exception as e:row['broker_cleanup_error']=str(e)
  ledger=json.loads((root/'transport/ledger.json').read_text()) if (root/'transport/ledger.json').exists() else dict(provider_POST=0,records=[]);records=ledger['records'];row.update(requests=ledger['provider_POST'],recorded_receipts=len(records),known_tokens_lower_bound=sum(r['tokens_lower_bound'] for r in records),cost_complete=len(records)==ledger['provider_POST'] and all(r['cost_complete'] for r in records),connection_infra_failure=any(r.get('connection_infra_failure') for r in records),backend='127.0.0.1:8000');row['owned_cleanup_verified']=row['actor_absent'] and not row.get('actor_process_uncertain') and not row.get('broker_cleanup_error') and (row.get('grader_owned_container_absent') is True or row['phase']!='grader');save(root/'attempt-result.json',row)
 return row
