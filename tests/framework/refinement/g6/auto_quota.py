"""Native-only reset admission:one normal frozen cell,no fabricated headroom."""
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

def reset_due(quota,windows,used):
    return bool(windows) and not quota.active and all(quota.clock()>=reset+120 and (name,reset) not in used for name,reset in windows.items())
