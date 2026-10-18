"""Admission projections,not a guarantee against unrelated account usage.
Only actual rate observations lower utilization;clock reset alone never does.
"""
import threading,time
class QuotaHold(RuntimeError):pass
class Quota:
    def __init__(self,seed,record=lambda x:None):
        self.lock=threading.RLock();self.scopes={};self.active={};self.record=record;self.seen=set()
        for event in seed:
            if event.get('require_refresh'):self.require_refresh()
            else:self.observe(event['info'],'prior-retained-native-stream',event['observed_epoch'])
    def observe(self,event,origin,observed_epoch=None):
        # Native versions can expose additional named scopes in nested arrays/maps.
        if isinstance(event,list):
            for item in event:self.observe(item,origin)
            return
        if not isinstance(event,dict):return
        scope=event.get('rateLimitType') or event.get('rate_limit_type')
        rejected=event.get('status') in ('rejected','denied')
        if rejected and not scope:scope='provider_rejected_unscoped'
        if scope:
            value=event.get('utilization');reset=event.get('resetsAt',event.get('reset_at'))
            with self.lock:
                old=self.scopes.get(scope,{});prior=old.get('utilization');numeric=isinstance(value,(int,float)) and not isinstance(value,bool) and 0<=value<=1
                # An unquantified observation cannot establish returned headroom.
                if numeric:
                    delta=max(0,value-prior) if prior is not None and reset==old.get('reset') else 0
                    old.update(utilization=float(value),reset=reset,observed_epoch=observed_epoch or time.time(),origin=origin,reservation=max(.05,old.get('reservation',.05),2*delta),unknown=rejected)
                elif not old:old=dict(utilization=None,reservation=.05,unknown=True,origin=origin,reset=reset)
                elif rejected:old.update(unknown=True,origin=origin)
                self.scopes[scope]=old;self.record(dict(kind='quota_observation',scope=scope,**old))
        for key,child in event.items():
            if isinstance(child,dict) and 'utilization' in child and not child.get('rateLimitType') and any(w in key for w in ('hour','day','opus','sonnet')):child=dict(child,rateLimitType=key)
            if isinstance(child,(list,dict)):self.observe(child,origin)
    def require_refresh(self):
        with self.lock:
            for v in self.scopes.values():v['unknown']=True
    def snapshot(self,extra=0):
        with self.lock:
            return {s:dict(v,projected=None if v.get('utilization') is None else v['utilization']+(len(self.active)+extra)*v['reservation'],inflight=len(self.active),observation_age_seconds=time.time()-v.get('observed_epoch',time.time())) for s,v in self.scopes.items()}
    def reserve(self,key):
        with self.lock:
            projection=self.snapshot(extra=1)
            if not projection or any(v.get('unknown') or v['projected'] is None or v['projected']>=.90-1e-12 for v in projection.values()):
                self.record(dict(kind='quota_hold',projections=projection));raise QuotaHold('Projected quota >=0.90 or actual utilization unavailable;wait for actual headroom')
            assert key not in self.active;self.active[key]=time.time();self.record(dict(kind='quota_reservation',run=key,projections=projection));return projection
    def release(self,key):
        with self.lock:
            self.active.pop(key,None);return self.snapshot()
