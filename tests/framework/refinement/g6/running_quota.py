"""Running quota amendment:observations,not a remaining-N veto or5pp floor.
Reserve both arms at issue admission. Native cells consume those reservations;
retries need additional headroom. Unexpected external jumps/reset uncertainty
can still stop a reserved arm:never override a live quota/auth/isolation guard.
"""
import threading,time
from quota import QuotaHold
from study_policy import RESET,weekly_threshold
class RunningQuota:
    def __init__(self,seed,record=lambda e:None,clock=time.time):
        self.lock=threading.RLock();self.clock=clock;self.record=record;self.scopes={};self.active={};self.pending={};self.completed=0;self.seen_cells=set();self.notices=set()
        for event in seed:
            if event.get('require_refresh'):self.require_refresh()
            else:self.observe(event['info'],'retained-native-stream',event['observed_epoch'],learning=False)
        self.begin_study()
    def begin_study(self):
        for s in self.scopes.values():s.update(anchor_utilization=None,anchor_completed=self.completed,last_step=0,observed_delta=0.,learning_active=False,last_live_utilization=None)
    def observe(self,event,origin,observed_epoch=None,learning=True):
        if isinstance(event,list):
            for item in event:self.observe(item,origin,observed_epoch,learning)
            return
        if not isinstance(event,dict):return
        scope=event.get('rateLimitType') or event.get('rate_limit_type');rejected=event.get('status') in ('rejected','denied')
        if rejected and not scope:scope='provider_rejected_unscoped'
        if scope:
            with self.lock:
                value=event.get('utilization');numeric=type(value) in (int,float) and 0<=value<=1;reset=event.get('resetsAt',event.get('reset_at'));epoch=observed_epoch if observed_epoch is not None else self.clock()
                old=self.scopes.get(scope,dict(utilization=None,rate=.0025,unknown=True,anchor_utilization=None,anchor_completed=self.completed,last_step=0,observed_delta=0.,learning_active=False,last_live_utilization=None))
                if numeric:
                    new_window=reset!=old.get('reset') or old['utilization'] is not None and value<old['utilization']
                    if learning and self.active:
                        if old['anchor_utilization'] is None or new_window:
                            old.update(anchor_utilization=value,anchor_completed=self.completed,last_step=0,observed_delta=0.,last_live_utilization=value)
                            self.record(dict(kind='first_live_learning_anchor',scope=scope,utilization=value,completed_cells=self.completed,observed_epoch=epoch))
                        elif old['learning_active']:
                            old['observed_delta']+=max(0,value-old['last_live_utilization'])
                        elif value!=old['last_live_utilization']:
                            self.record(dict(kind='idle_counter_gap_excluded_from_rate',scope=scope,previous=old['last_live_utilization'],current=value))
                        old.update(learning_active=True,last_live_utilization=value)
                    elif new_window:
                        old.update(anchor_utilization=None,learning_active=False)
                    old.update(utilization=float(value),reset=reset,observed_epoch=epoch,origin=origin,unknown=rejected)
                elif rejected:old['unknown']=True
                self.scopes[scope]=old;self.record(dict(kind='quota_observation',scope=scope,**old))
                if rejected:self.record(dict(kind='subscription_rejection',scope=scope))
                week=int((epoch-RESET)//604800)
                if numeric and 'seven_day' in scope and epoch>=RESET and isinstance(reset,(int,float)) and reset>RESET and value>=.60 and (scope,week) not in self.notices:
                    self.notices.add((scope,week));self.record(dict(kind='supervisor_notice',scope=scope,utilization=value,observed_epoch=epoch,reason='actual new-week weekly utilization >=0.60'))
        for key,child in event.items():
            if isinstance(child,dict) and 'utilization' in child and not child.get('rateLimitType') and any(w in key for w in ('hour','day','opus','sonnet')):child=dict(child,rateLimitType=key)
            if isinstance(child,(list,dict)):self.observe(child,origin,observed_epoch,learning)
    def require_refresh(self):
        with self.lock:
            for s in self.scopes.values():s['unknown']=True
    def completed_cell(self,key):
        with self.lock:
            if key in self.seen_cells:return
            self.seen_cells.add(key);self.completed+=1
            for name,s in self.scopes.items():
                if s['unknown'] or s['anchor_utilization'] is None:continue
                delta=s['observed_delta'];steps=int((delta+1e-10)*100);count=self.completed-s['anchor_completed']
                if steps>s['last_step'] and count>0:
                    s.update(rate=min(.01,delta/count),uncapped_rate=delta/count,last_step=steps);self.record(dict(kind='running_rate_update',scope=name,completed_cells=self.completed,delta=delta,denominator_completed_cells=count,rate=s['rate']))
    def snapshot(self,extra=0):
        with self.lock:
            reserved=len(self.active)+sum(len(a) for a in self.pending.values())+extra
            return {name:dict(s,observation_window_expired=(isinstance(s.get('reset'),(int,float)) and s['reset']<=self.clock()) or ('seven_day' in name and self.clock()>=RESET and s.get('observed_epoch',0)<RESET),threshold=float(weekly_threshold(self.clock())) if 'seven_day' in name else .90,projected=None if s['utilization'] is None else s['utilization']+reserved*s['rate'],inflight_native=len(self.active),reserved_cells=reserved,completed_study_cells=self.completed,observation_age_seconds=self.clock()-s.get('observed_epoch',self.clock())) for name,s in self.scopes.items()}
    def check(self,extra):
        snap=self.snapshot(extra)
        if not snap or not any('seven_day' in s for s in snap) or any(s['unknown'] or s['observation_window_expired'] or s['projected'] is None or s['projected']>=s['threshold']-1e-12 for s in snap.values()):
            self.record(dict(kind='quota_hold',projections=snap));raise QuotaHold('Next admission reaches quota threshold or actual headroom is unknown')
        return snap
    def admission_check(self,extra,reset_permit=None):
        if reset_permit is None:return self.check(extra)
        snap=self.snapshot(extra)
        if self.active or not snap or not any('seven_day' in s for s in snap):raise QuotaHold('Single-cell reset admission requires drained native work')
        for name,s in snap.items():
            if s['unknown'] or s['projected'] is None:raise QuotaHold('Reset admission never overrides unknown/rejected counters')
            if s['observation_window_expired'] or s['projected']>=s['threshold']-1e-12:
                reset=reset_permit.get(name)
                if reset is None or s.get('reset')!=reset or self.clock()<reset+120:raise QuotaHold('Binding reset+120s not established for this scope')
        return {name:dict(s,single_cell_reset_admission=True,headroom_not_assumed=True) for name,s in snap.items()}
    def reserve_pair(self,task,arms,reset_permit=None):
        with self.lock:
            assert task not in self.pending;snap=self.admission_check(len(arms),reset_permit);self.pending[task]=list(arms);self.record(dict(kind='pair_reservation',task=task,arms=list(arms),projections=snap));return snap
    def reserve(self,key,reset_permit=None):
        with self.lock:
            task,arm,number=key.split('/');promised=arm in self.pending.get(task,[]);snap=self.admission_check(0 if promised else 1,reset_permit)
            assert key not in self.active
            if promised:
                assert self.pending[task][0]==arm,'Frozen sequential arm order required'
                self.pending[task].remove(arm)
            self.active[key]=self.clock();self.record(dict(kind='native_reservation',run=key,pre_reserved_pair_arm=promised,projections=snap));return snap
    def release(self,key):
        with self.lock:
            self.active.pop(key,None)
            if not self.active:
                for s in self.scopes.values():s['learning_active']=False
            return self.snapshot()
    def close_pair(self,task):
        with self.lock:self.pending.pop(task,None)
