"""Quota-only auto-resume;never use a reset clock as numeric headroom."""
import math
from quota import QuotaHold

def blocked_windows(snapshot):
    if not snapshot:raise RuntimeError('Missing quota observations')
    blocked={}
    for name,s in snapshot.items():
        if s['unknown'] or s['projected'] is None:raise RuntimeError('Unknown/rejected quota scope requires supervisor')
        if s['observation_window_expired'] or s['projected']>=s['threshold']-1e-12:
            reset=s.get('reset')
            if type(reset) not in (int,float) or not math.isfinite(reset):raise RuntimeError('Quota reset unavailable;cannot authorize automatic resume')
            blocked[name]=reset
    if not blocked:raise RuntimeError('Quota hold has no explainable blocking window')
    return blocked

def reset_headroom(quota,windows,extra=0):
    snapshot=quota.snapshot(extra)
    for name,old_reset in windows.items():
        s=snapshot.get(name,{})
        if s.get('observed_epoch',0)<old_reset or not isinstance(s.get('reset'),(int,float)) or s['reset']<=old_reset:return False
    try:quota.check(extra)
    except QuotaHold:return False
    return True
