"""Fixed150 paired study;bounded admission,drain and explicit pause checkpoints."""
import concurrent.futures,datetime,json,random,re,threading,time
from common import H,private_root,prereg,save,sha
from runner import Admissions,attempt,guard,utc,PYTHON
from running_quota import RunningQuota
from quota import QuotaHold
from study_policy import concurrency_after_cells
from docker_runtime import Network,IssueImages
from prepare_source import prepare
from activation import plugin_guard

def attempts(root,task,arm):
    return [json.loads(f.read_text()) for f in sorted((root/'study'/task).glob(arm+'-a*/attempt-result.json'),key=lambda f:int(f.parent.name.rsplit('-a',1)[1]))]
def valid(row):
    m=row.get('stream',{})
    return bool(row.get('grade_valid') and not row.get('error') and not row.get('configuration_guard_failed') and row.get('expansion',{}).get('command_expansion_verified') and not m.get('terminal_5xx') and not m.get('rate_limited') and not m.get('blocked_native'))
def finished_cell(rows):
    return bool(rows and (valid(rows[-1]) or rows[-1].get('stream',{}).get('terminal_5xx') and sum(bool(r.get('native_started') and not r.get('stream',{}).get('rate_limited')) for r in rows)>=5))
class StudyAdmissions(Admissions):
    def __init__(self,root):
        self.root=root;self.lock=threading.RLock();self.log_lock=threading.RLock();self.stop_lock=threading.RLock();self.until=0;self.stopped=False;self.recent=__import__('collections').deque(maxlen=16);self.stop_file=root/'STUDY-ADMISSIONS-STOP';self.adverse=0;self.pause_new_pairs=False;self.pause_reason=None
        seed=[]
        for phase in ('smoke','smoke-explicit-v2'):
            for f in sorted((root/phase).glob('*/*/attempt-result.json'),key=lambda f:f.stat().st_mtime):
                for e in json.loads(f.read_text()).get('stream',{}).get('rate_limit_events',[]):seed.append(dict(info=e,observed_epoch=(f.parent/'native.jsonl').stat().st_mtime))
        history_path=root/'study-admission-events.jsonl';history=[json.loads(x) for x in history_path.read_text().splitlines()] if history_path.exists() else []
        self.quota=RunningQuota(seed,self.log)
        # Replay actual observations during retained native intervals,not old
        # smoke-to-study gaps. Keep original timestamps and all completed cells.
        replay=[];native_keys=set()
        for f in sorted((root/'study').glob('*/*/attempt-result.json'),key=lambda f:f.stat().st_mtime):
            row=json.loads(f.read_text());m=row.get('stream',{});self.note_errors(m)
            if not row.get('native_started'):continue
            key=row['task']+'/'+row['arm']+'/'+str(row['attempt']);native_keys.add(key)
            start=datetime.datetime.fromisoformat(row['started_utc']).timestamp();end=start+row['wall_seconds'];replay.extend([(start,0,'start',key),(end,2,'end',key)])
            retained=attempts(root,row['task'],row['arm'])
            if row['attempt']==retained[-1]['attempt'] and finished_cell(retained):replay.append((f.stat().st_mtime,3,'complete',row['task']+'/'+row['arm']))
            if m.get('rate_limited'):replay.append((f.stat().st_mtime,4,'reject',key))
            self.recent.append(m.get('terminal_5xx',False))
        for event in history:
            if event.get('kind')=='quota_observation' and event.get('origin') in native_keys:replay.append((event['observed_epoch'],1,'observe',event))
        for epoch,_,kind,value in sorted(replay,key=lambda e:e[:2]):
            if kind=='start':self.quota.active[value]=epoch
            elif kind=='end':self.quota.release(value)
            elif kind=='complete':self.quota.completed_cell(value)
            elif kind=='reject':self.quota.require_refresh()
            else:self.quota.observe(dict(rateLimitType=value['scope'],utilization=value['utilization'],resetsAt=value.get('reset'),status='rejected' if value.get('unknown') else 'allowed'),'replayed-study-native-stream',epoch)
        assert not self.quota.active
        self.log(dict(kind='study_rate_history_replayed',completed_cells=self.quota.completed,native_attempts=len(native_keys)))
    def stop(self,reason):
        with self.stop_lock:self.stopped=True;save(self.stop_file,dict(utc=utc(),reason=reason))
    def log(self,event):
        with self.log_lock:
            with (self.root/'study-admission-events.jsonl').open('a') as f:f.write(json.dumps(dict(utc=utc(),**event))+'\n')
            if event.get('kind')=='supervisor_notice':save(self.root/'STUDY-SUPERVISOR-NOTICE.json',dict(utc=utc(),**event))
            if event.get('kind')=='subscription_rejection':self.stop('429/subscription rejection;drain and await reset/headroom plus supervisor input')
    def note_errors(self,m):
        if any(e['overloaded'] or e['rate_limited'] or any(s==429 or s>=500 for s in e['statuses']) for e in m.get('native_error_events',[])):self.adverse=1
    def observe_native(self,event,key):
        is_error=event.get('type')=='error' or event.get('type')=='assistant' and event.get('error') or event.get('type')=='result' and event.get('is_error') or event.get('type')=='system' and event.get('subtype')=='api_retry'
        if is_error:
            text=json.dumps({k:event[k] for k in ('error','errors','result','message','status','status_code') if k in event}).lower()
            if re.search(r'(?:api error|http|status(?:_code)?)[\s\"\x27:=]+429(?!\d)',text) or any(x in text for x in ('rate_limit','rate limit','hit your limit','out of extra usage')):self.stop('Live429/subscription rejection;drain and await explicit continuation')
            if 'overloaded' in text or re.search(r'(?:api error|http|status(?:_code)?)[\s\"\x27:=]+5\d\d(?!\d)',text):self.adverse=1
    def finished(self,m,cell,number):
        self.note_errors(m)
        for event in m['native_error_events']:self.log(dict(kind='native_error',cell=cell,attempt=number,**event))
        if m['rate_limited'] or any(e['rate_limited'] or 429 in e['statuses'] for e in m['native_error_events']):
            self.quota.require_refresh();self.stop('429/subscription rejection;all charges retained;supervisor continuation required')
        if m['blocked_native']:self.stop('Native authentication/model access guard')
        with self.lock:
            self.recent.append(m['terminal_5xx'])
            if len(self.recent)==16 and sum(self.recent)>=8:self.until=max(self.until,time.time()+600);self.log(dict(kind='circuit_pause',pause_seconds=600))
    def pause(self,reason):self.pause_new_pairs=True;self.pause_reason=reason;self.log(dict(kind='pause_new_pairs',reason=reason))

def main(commit):
    p=guard(commit,'study');root=private_root();phase='study';continuation=(root/'study-launch.json').exists();launch=root/('study-continuation-'+str(time.time_ns())+'-launch.json' if continuation else 'study-launch.json')
    with launch.open('x') as f:json.dump(dict(utc=utc(),allowance_commit=commit,pid=__import__('os').getpid(),supervisor_running_quota_amendment=True),f)
    # Do not silently reconcile an interrupted native stream/unknown spend.
    for f in (root/'study').glob('*/*/attempt-progress.json'):
        if not (f.parent/'attempt-result.json').exists():raise RuntimeError('Interrupted study native attempt;reconcile costs before restarting')
    admissions=StudyAdmissions(root);admissions.allowance_commit=commit;network=Network();lock=threading.RLock();results=[];dataset={t['instance_id']:t for t in json.loads((root/'dataset.json').read_text())};tasks=p['study_issue_order'];index=0;failures=[]
    priority=p.get('live_baseline_correction',{}).get('complete_first_task');priority_pending=bool(priority and not all(finished_cell(attempts(root,priority,a)) for a in p['arm_orders'][priority]))
    if priority_pending:assert all(all(finished_cell(attempts(root,t,a)) for a in p['arm_orders'][t]) for t in tasks[:tasks.index(priority)]),'Priority continuation must not reorder unfinished earlier issues'
    def write_status(state):
        with lock:
            status=dict(utc=utc(),state=state,cells_done=len(results),target_cells=300,completed_pairs=sum(all(any(r['task']==t and r['arm']==a for r in results) for a in ('none','ours')) for t in tasks),quota=admissions.quota.snapshot(),adverse_api_event_seen=bool(admissions.adverse),issue_workers_limit=concurrency_after_cells(len(results),admissions.adverse),next_issue_index=index,pause_reason=admissions.pause_reason,hard_stop=admissions.stopped,errors=failures)
            save(root/'study-status.json',status);save(root/'study-summary.json',results)
    def issue(task):
        directory=root/'study'/task;directory.mkdir(parents=True,exist_ok=True);resources=directory/('resources-'+str(time.time_ns()));resources.mkdir();images=IssueImages(task,resources,safety_workers=4)
        try:
            image=images.acquire();baseline=directory/'source'
            if not (baseline/'manifest.json').exists():prepare(dataset[task],images.base,baseline)
            for arm in p['arm_orders'][task]:
                rows=attempts(root,task,arm)
                budget=sum(bool(r.get('native_started') and not r.get('stream',{}).get('rate_limited')) for r in rows)
                if finished_cell(rows):last=rows[-1]
                else:
                    while budget<5:
                        admissions.wait();number=max([r['attempt'] for r in rows]+[0])+1
                        row=attempt(task,arm,number,directory/(arm+'-a'+str(number)),baseline,image,images.base,network,admissions,phase);rows.append(row);save(directory/(arm+'-all-attempts.json'),rows);m=row['stream'];admissions.finished(m,task+'/'+arm,number)
                        if m['rate_limited']:admissions.wait() # Stops globally;no reset-clock retry.
                        budget+=1
                        if not m['terminal_5xx']:break
                        if budget<5:
                            delay=min(900,60*2**(budget-1)*(1+random.uniform(0,.2)));admissions.log(dict(kind='backoff',cell=task+'/'+arm,next_attempt=number+1,seconds=delay));end=time.monotonic()+delay
                            while time.monotonic()<end:admissions.wait();time.sleep(min(1,max(0,end-time.monotonic())))
                    last=rows[-1]
                if valid(last):plugin_guard(last['stream'],arm,p['amendment_explicit_v2'])
                elif not (last.get('stream',{}).get('terminal_5xx') and budget==5):raise RuntimeError('No valid latest quality;admission/activation/harness guard')
                summary=dict(task=task,arm=arm,phase=phase,scored_attempt=last['attempt'],solved=last.get('solved'),grade_valid=last.get('grade_valid',False),infra_exhausted=last.get('stream',{}).get('terminal_5xx',False) and budget==5 if not valid(last) else False,attempts=rows)
                with lock:
                    results.append(summary);admissions.quota.completed_cell(task+'/'+arm);write_status('running');print('study completed',len(results),'of300',task,arm,flush=True)
        except QuotaHold:
            admissions.pause('Next native admission blocked by live quota;reserved pair may require supervisor reconciliation after unexpected counter/reset change');raise
        except Exception:
            admissions.stop('Study issue harness/cleanup/native guard;drain all in-flight work');raise
        finally:
            try:images.close()
            except Exception:admissions.stop('Owned image cleanup uncertain');raise
            finally:admissions.quota.close_pair(task)
    try:
        network.start()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            active={}
            while index<len(tasks) or active:
                limit=concurrency_after_cells(len(results),admissions.adverse)
                while index<len(tasks) and len(active)<limit and not admissions.pause_new_pairs and not admissions.stopped:
                    if priority_pending and active:break # Complete missing Django treatment BEFORE new issue admission.
                    task=tasks[index];remaining=[a for a in p['arm_orders'][task] if not finished_cell(attempts(root,task,a))]
                    if not remaining:
                        for arm in p['arm_orders'][task]:
                            rows=attempts(root,task,arm);last=rows[-1];results.append(dict(task=task,arm=arm,phase=phase,scored_attempt=last['attempt'],solved=last.get('solved'),grade_valid=last.get('grade_valid',False),infra_exhausted=not valid(last),attempts=rows))
                        index+=1;continue
                    try:admissions.wait();admissions.quota.reserve_pair(task,remaining)
                    except QuotaHold:admissions.pause('Next whole pair reaches quota threshold;drain reserved pairs then await reset and supervisor decision');break
                    except RuntimeError:break
                    index+=1;active[pool.submit(issue,task)]=task;write_status('running')
                if not active:break
                done,_=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED,timeout=2)
                for future in done:
                    task=active.pop(future)
                    try:
                        future.result()
                        if priority_pending and task==priority:priority_pending=False
                    except Exception as e:failures.append(dict(task=task,type=type(e).__name__,detail='Sanitized per-attempt evidence retained;no credential exception text'));admissions.pause('Issue quota/native/isolation/cleanup guard;supervisor input required')
                write_status('draining' if admissions.pause_new_pairs or admissions.stopped else 'running')
    finally:
        try:network.close()
        except Exception:admissions.stop('Network/proxy cleanup uncertain');failures.append(dict(type='cleanup',detail='Owned network/proxy reconciliation required'))
        done=len(results)==300 and not failures and not admissions.stopped
        write_status('complete' if done else 'paused')
        save(root/('study-complete.json' if done else 'study-pause.json'),dict(utc=utc(),cells=len(results),target=300,N=150,supervisor_decision_required=not done,quota=admissions.quota.snapshot(),reason=admissions.pause_reason,errors=failures))
        from study_analysis import main as analyze
        analyze()
