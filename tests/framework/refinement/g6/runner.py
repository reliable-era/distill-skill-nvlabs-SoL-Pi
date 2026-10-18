"""G6 paired smoke/study scheduler. Study gate defaults CLOSED.
Only runtime docker-exec receives the dedicated token;streams are redacted first.
"""
import argparse,collections,concurrent.futures,datetime,json,pathlib,random,subprocess,threading,time,uuid
from common import H,R,check_frozen,command,private_root,prereg,save,sha
from docker_runtime import Network,IssueImages,actor,remove
from prepare_source import prepare
from capture_patch import capture
from security import read_token,env_file,filtered_copy
from stream import parse
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def native_argv(name,credential_file,arm):
    return ['docker','exec','-i','--env-file',credential_file,name,'python3','/opt/g6/entry.py','run',arm]

class Admissions:
    def __init__(self,root):self.root=root;self.lock=threading.RLock();self.until=0;self.stopped=False;self.recent=collections.deque(maxlen=16)
    def log(self,event):
        with self.lock:
            with (self.root/'admission-events.jsonl').open('a') as f:f.write(json.dumps(dict(utc=utc(),**event))+'\n')
    def wait(self):
        while True:
            with self.lock:
                if self.stopped or (self.root/'ADMISSIONS-STOP').exists():raise RuntimeError('G6 admissions paused;retained costs require supervisor input')
                delay=self.until-time.time()
            if delay<=0:return
            time.sleep(min(delay,1))
    def finished(self,metadata,cell,number):
        with self.lock:
            for event in metadata['native_error_events']:self.log(dict(kind='native_error',cell=cell,attempt=number,**event))
            if metadata['rate_limited']:
                reset=metadata['reset_epoch'];self.log(dict(kind='rate_limit_pause',cell=cell,attempt=number,reset_epoch=reset))
                if reset is None:self.stopped=True;save(self.root/'ADMISSIONS-STOP',dict(reason='rate-limit reset unavailable',cell=cell))
                else:self.until=max(self.until,reset)
            else:
                self.recent.append(metadata['terminal_5xx'])
                if len(self.recent)==16 and sum(self.recent)>=8:
                    self.until=max(self.until,time.time()+600);self.log(dict(kind='circuit_pause',pause_seconds=600))
            if metadata['blocked_native']:
                self.stopped=True;save(self.root/'ADMISSIONS-STOP',dict(reason='native authentication/model access error',cell=cell))

def attempt(task,arm,number,directory,baseline,image,base_image,network,admissions,phase):
    root=private_root();p=prereg();directory.mkdir();name='solpi-g6-actor-'+uuid.uuid4().hex[:16]
    result=dict(task=task,arm=arm,phase=phase,attempt=number,actor=name,plugin_commit=p['plugin_commit'],cli_version=p['agent']['cli_version'],requested_model=p['agent']['requested_model'],native_started=False,grade_valid=False,solved=None,timeout=False,wall_seconds=None,error=None)
    token=None;process=None;reader=None
    try:
        template=json.loads((root/'grader-template.json').read_text());actor(name,image,baseline,directory,network,arm,template['wheelhouse'])
        prompt=(baseline/'prompt.txt').read_bytes();assert sha(baseline/'prompt.txt')==json.loads((baseline/'manifest.json').read_text())['prompt_sha256'];(directory/'prompt.txt').write_bytes(prompt)
        admissions.wait();token=read_token();start=time.monotonic();result.update(native_started=True,started_utc=utc(),prompt_sha256=sha(directory/'prompt.txt'));save(directory/'attempt-progress.json',result)
        with env_file(token) as credential_file,(directory/'prompt.txt').open('rb') as source,(directory/'native.jsonl').open('wb') as output:
            process=subprocess.Popen(native_argv(name,credential_file,arm),stdin=source,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            redactions=[]
            def drain():redactions.append(filtered_copy(process.stdout,output,token))
            reader=threading.Thread(target=drain,daemon=True);reader.start()
            try:process.wait(timeout=7200)
            except subprocess.TimeoutExpired:result['timeout']=True;command(['docker','stop','-t','10',name]);process.wait(timeout=30)
            reader.join(timeout=30)
            if reader.is_alive():raise RuntimeError('Native stream reader did not finish')
        result.update(wall_seconds=time.monotonic()-start,native_exit=process.returncode,native_secret_redactions=sum(redactions),native_sha256=sha(directory/'native.jsonl'))
        metadata=parse(directory/'native.jsonl');result['stream']=metadata
        if metadata['cli_version'] and metadata['cli_version']!=p['agent']['cli_version']:raise RuntimeError('Stream CLI version drift')
        if any(not m.startswith('claude-opus-5-5') for m in metadata['main_provider_model_ids']):raise RuntimeError('Unexpected primary provider model;no fallback authorized')
        if arm=='none' and (metadata['plugins'] or metadata['loaded_skills']):raise RuntimeError('Control customization contamination')
        if not metadata['final_result_present'] and not result['timeout'] and not metadata['terminal_5xx'] and not metadata['rate_limited'] and not metadata['blocked_native']:raise RuntimeError('Native exited without final result;not an ordinary model outcome')
        command(['docker','stop','-t','10',name])
        with (directory/'captured.tar').open('wb') as output:
            cp=subprocess.Popen(['docker','cp',name+':/testbed/.','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            redacted=filtered_copy(cp.stdout,output,token);stderr=cp.stderr.read();code=cp.wait(timeout=120)
            (directory/'capture.stderr').write_bytes(stderr.replace(token,b'X'*len(token)))
            if redacted:raise RuntimeError('Credential content quarantined from capture;stop,do not grade altered source')
            if code:raise RuntimeError('Docker source capture failed')
        proof=capture(directory/'captured.tar',baseline,directory);result['patch_sha256']=proof['patch_sha256']
        if not metadata['rate_limited'] and not metadata['terminal_5xx'] and not metadata['blocked_native']:
            plan=dict(template,images={task:base_image},private_dataset=str(root/'dataset.json'),private_dataset_sha256=sha(root/'dataset.json'));save(directory/'grader-plan.json',plan)
            with (directory/'grader.log').open('wb') as out:graded=subprocess.run([PYTHON,str(H/'grade_swe.py'),str(directory/'grade'),task,str(directory/'model.patch'),str(directory/'grader-plan.json')],stdout=out,stderr=subprocess.STDOUT,timeout=950)
            if graded.returncode:raise RuntimeError('Official grader process failed')
            grade=json.loads((directory/'grade/grade-result.json').read_text());assert grade['owned_containers_absent'];result.update(solved=grade['solved'],grade_valid=grade['grade_valid'],grade_sha256=sha(directory/'grade/grade-result.json'))
            if not result['grade_valid']:raise RuntimeError('Official Boolean outcome unavailable')
    except Exception as e:
        # No exception can interpolate credentials:only fixed runner messages/type.
        result['error']=dict(type=type(e).__name__,message='G6 attempt stopped;see sanitized per-attempt metadata')
        admissions.stopped=True;save(root/'ADMISSIONS-STOP',dict(reason='harness/cleanup uncertainty',cell=task+'/'+arm,attempt=number))
        raise
    finally:
        try:remove(name,root.name);result['owned_actor_absent']=True
        except Exception:result['owned_actor_absent']=False;admissions.stopped=True
        owned=directory/'grade/owned.json'
        try:
            if owned.exists():
                for grader in json.loads(owned.read_text())['names']:
                    assert grader.startswith('sweb.eval.'+task.lower()+'.g6-grade-')
                    exists=subprocess.run(['docker','inspect',grader],capture_output=True)
                    if exists.returncode==0:command(['docker','rm','-f',grader])
                    after=subprocess.run(['docker','inspect',grader],capture_output=True);assert after.returncode and b'No such' in after.stderr
            result['owned_graders_absent']=True
        except Exception:
            result['owned_graders_absent']=False;admissions.stopped=True;save(root/'ADMISSIONS-STOP',dict(reason='owned grader cleanup uncertain'))
        if reader and reader.is_alive():reader.join(timeout=30)
        if 'stream' not in result and (directory/'native.jsonl').exists():result['stream']=parse(directory/'native.jsonl')
        save(directory/'attempt-result.json',result)
    return result

def guard(commit,phase):
    p=check_frozen();root=private_root();stage=json.loads((H/'runner-stage.json').read_text());relative=str((H/'runner-stage.json').relative_to(R))
    assert command(['git','show',commit+':'+relative]).stdout==(H/'runner-stage.json').read_bytes(),'Committed allowance required'
    assert sha(H/'preregistration.json')==stage['preregistration_sha256'];assert phase in stage['authorized_phases'],'Study waits for explicit supervisor go'
    assert stage['no_model_plumbing_passed'] and sha(H/'plumbing-summary.json')==stage['plumbing_summary_sha256']
    assert set(stage['source_sha256'])=={f.name for f in H.glob('*.py')}
    assert sha(root/'tool-image.json')==stage['tool_image_manifest_sha256']
    tools=json.loads((root/'tool-image.json').read_text())
    for name in ('entry.py','egress_proxy.py'):assert sha(H/name)==tools['context_sha256'][name]
    actual={str(f.relative_to(root/'marketplace')):sha(f) for f in (root/'marketplace').rglob('*') if f.is_file()}
    assert actual==stage['plugin_tree_sha256']
    for f,d in stage['source_sha256'].items():assert sha(H/f)==d,'Frozen G6 runner changed'
    assert not (root/'ADMISSIONS-STOP').exists();read_token() # No Docker/model work if missing/unsafe.
    return p

def main(commit,phase):
    p=guard(commit,phase);root=private_root();launch=root/(phase+'-launch.json')
    with launch.open('x') as out:json.dump(dict(utc=utc(),allowance_commit=commit,pid=__import__('os').getpid()),out)
    tasks=p['smoke_sample'] if phase=='smoke' else p['study_issue_order'];network=Network();admissions=Admissions(root);results=[];lock=threading.RLock()
    def issue(task):
        directory=root/phase/task;directory.mkdir(parents=True);images=IssueImages(task,directory)
        try:
            actor_image=images.acquire();dataset=json.loads((root/'dataset.json').read_text());taskdata=next(t for t in dataset if t['instance_id']==task);baseline=directory/'source';prepare(taskdata,images.base,baseline)
            for arm in p['arm_orders'][task]:
                admissions.wait();rows=[];budget=0
                while budget<5:
                    admissions.wait();number=len(rows)+1;d=directory/(arm+'-a'+str(number));row=attempt(task,arm,number,d,baseline,actor_image,images.base,network,admissions,phase);rows.append(row);save(directory/(arm+'-all-attempts.json'),rows);m=row['stream'];admissions.finished(m,task+'/'+arm,number)
                    if m['rate_limited']:admissions.wait();continue
                    budget+=1
                    if not m['terminal_5xx']:break
                    if budget<5:
                        delay=min(900,60*2**(budget-1)*(1+random.uniform(0,.2)));admissions.log(dict(kind='backoff',cell=task+'/'+arm,next_attempt=number+1,seconds=delay));end=time.monotonic()+delay
                        while time.monotonic()<end:
                            admissions.wait();time.sleep(min(1,max(0,end-time.monotonic())))
                last=rows[-1];exhausted=last['stream']['terminal_5xx'] and budget==5
                summary=dict(task=task,arm=arm,phase=phase,scored_attempt=len(rows),solved=False if exhausted else last['solved'],grade_valid=last['grade_valid'],infra_exhausted=exhausted,attempts=rows,plugin_commit=p['plugin_commit'],cli_version=p['agent']['cli_version'])
                with lock:results.append(summary);save(root/(phase+'-summary.json'),results);print(phase,'completed',len(results),'of',2*len(tasks),flush=True)
        finally:images.close()
    try:
        network.start()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(issue,t) for t in tasks]
            for f in concurrent.futures.as_completed(futures):f.result()
        save(root/(phase+'-complete.json'),dict(cells=len(results),study_authorized=False if phase=='smoke' else True))
    finally:network.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--allowance-commit',required=True);parser.add_argument('--phase',choices=('smoke','study'),default='smoke');a=parser.parse_args();main(a.allowance_commit,a.phase)
