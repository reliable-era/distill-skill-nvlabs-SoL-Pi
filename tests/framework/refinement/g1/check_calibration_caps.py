"""Offline cap checks only; no server, native actor, or provider invocation."""
import json, tempfile, pathlib, time
import run_calibration as C
from prospective_body_capacity import session_factory

def main():
    raw = session_factory(C.RT/'session.py', C.sha(C.RT/'session.py'))
    load = [{'num_reqs':7, 'num_waiting_reqs':3}]
    topology = {'verified':True,'image_id':C.S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'offline-rule-test-not-isolation-evidence'}
    with tempfile.TemporaryDirectory() as directory:
        s = raw.Session(pathlib.Path(directory)/'ledger',topology)
        before = time.monotonic();s.begin('unit',load)
        assert 7199 <= s.deadline-before <= 7201
        assert raw.idle(load) and not raw.idle([{'num_reqs':8,'num_waiting_reqs':0}])
        assert C.Q.eligible([{'port':18001,'status':200,'load':load}])
        assert not C.Q.eligible([{'port':18001,'status':200,'load':[{'num_reqs':8,'num_waiting_reqs':0}]}])
        body = json.dumps({'model':'Qwen3.8-27B-FP8','stream':True,'input':'unit'}).encode()
        def forbidden_connect(*args,**kwargs):raise AssertionError('No provider connection permitted in offline cap check')
        s.per_actor['unit']=60
        try:s.forward('/v1/responses',body,lambda _:None,connect=forbidden_connect)
        except raw.LocalBudgetExhaustion as e:assert e.reason=='per_actor_POST_cap'
        else:raise AssertionError('Per-run cap failed')
        s.per_actor['unit']=0;s.posts=600
        try:s.forward('/v1/responses',body,lambda _:None,connect=forbidden_connect)
        except raw.LocalBudgetExhaustion as e:assert e.reason=='global_POST_cap'
        else:raise AssertionError('Global cap failed')
        s.posts=0;s.deadline=time.monotonic()-1
        try:s.forward('/v1/responses',body,lambda _:None,connect=forbidden_connect)
        except raw.LocalBudgetExhaustion as e:assert e.reason=='actor_deadline_reserve'
        else:raise AssertionError('Wall cap failed')
        s.active=None;s.starts=10
        try:s.begin('eleventh',load)
        except RuntimeError:pass
        else:raise AssertionError('Start cap failed')
        assert not s.records and s.posts==0
        forwarded,policy=raw.transform(body)
        assert json.loads(forwarded)['max_output_tokens']==16384
    C.save(C.E/'calibration-cap-checks.json',{'status':'PASS_OFFLINE_RULES_ONLY','checks':['60 requests per run','600 global requests','10 native starts','7200-second wall cap','16384 output tokens','running below eight admitted with waiting; eight running rejected'],'model_POST':0,'isolation_or_performance_claim':False,'runtime_hashes':{p.name:C.sha(p) for p in C.RT.glob('*.py')}})
    print('Calibration cap checks passed; no model call.')

if __name__=='__main__':main()
