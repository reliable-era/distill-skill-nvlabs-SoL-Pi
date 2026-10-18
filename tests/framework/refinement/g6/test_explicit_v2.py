import json,pathlib,tempfile,time,unittest
from activation import PREFIX,prompt_bytes,input_bytes,plugin_guard,expansion_evidence
from quota import Quota,QuotaHold
H=pathlib.Path(__file__).parent
class Explicit(unittest.TestCase):
    def quota(self,value=.75):return Quota([dict(info=dict(rateLimitType='seven_day',utilization=value,resetsAt=123),observed_epoch=time.time()-100)])
    def test_exact_task_suffix_and_json_roundtrip(self):
        task=b'<issue>\nutf8 \xc3\xa9\n</issue>\n';self.assertEqual(prompt_bytes(task,'ours'),PREFIX+task);self.assertEqual(prompt_bytes(task,'none'),task);self.assertEqual(json.loads(input_bytes(task,'ours'))['message']['content'].encode(),PREFIX+task)
    def test_three_reservations_at75_rejected(self):
        q=self.quota();q.reserve('a');q.reserve('b')
        with self.assertRaises(QuotaHold):q.reserve('c')
        q.release('a');q.reserve('c');self.assertEqual(len(q.active),2)
    def test_threshold_and_shorter_model_scope(self):
        q=self.quota();q.observe(dict(rateLimitType='five_hour_opus',utilization=.86,resetsAt=999),'live')
        with self.assertRaises(QuotaHold):q.reserve('a')
    def test_unknown_scope_not_zero(self):
        q=self.quota();q.observe(dict(rateLimitType='five_hour',status='allowed'),'live')
        with self.assertRaises(QuotaHold):q.reserve('a')
    def test_reset_clock_not_headroom(self):
        q=self.quota(.9)
        with self.assertRaises(QuotaHold):q.reserve('a')
        q.observe(dict(rateLimitType='seven_day',utilization=.3,resetsAt=456),'new actual');q.reserve('a')
    def test_inflight_and_adaptive_reservation(self):
        q=self.quota();q.reserve('a');q.observe(dict(rateLimitType='seven_day',utilization=.83,resetsAt=123),'live')
        with self.assertRaises(QuotaHold):q.reserve('b')
        self.assertGreaterEqual(q.scopes['seven_day']['reservation'],.159)
    def test_rejected_missing_counter_needs_actual_refresh(self):
        q=self.quota();q.observe(dict(rateLimitType='seven_day',status='rejected',resetsAt=1),'rejected')
        with self.assertRaises(QuotaHold):q.reserve('a')
        q.observe(dict(rateLimitType='seven_day',status='allowed',utilization=.4,resetsAt=2),'actual');q.reserve('a')
        q.require_refresh()
        with self.assertRaises(QuotaHold):q.reserve('b')
    def test_restart_seeds_study_observations_and_requires_refresh(self):
        from runner import Admissions
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);a=root/'study/task/none-a1';a.mkdir(parents=True);(a/'native.jsonl').write_text('');(a/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.88,resetsAt=1)],rate_limited=True))))
            quota=Admissions(root).quota
            with self.assertRaises(QuotaHold):quota.reserve('new')
            quota.observe(dict(rateLimitType='seven_day',utilization=.2,resetsAt=2),'fresh actual');quota.reserve('new')
    def test_nested_model_scope(self):
        q=self.quota();q.observe(dict(seven_day_opus=dict(utilization=.89,resetsAt=1)),'actual')
        with self.assertRaises(QuotaHold):q.reserve('a')
    def test_stale_seed_disclosed(self):self.assertGreater(self.quota().snapshot()['seven_day']['observation_age_seconds'],90)
    def test_plugin_ids_versions_extras_and_stock(self):
        a=json.loads((H/'preregistration.json').read_text())['amendment_explicit_v2'];m=dict(plugins=a['builtin_plugins'],loaded_skills=a['stock_skills']);plugin_guard(m,'none',a)
        m['plugins']=m['plugins']+[dict(name='bad',path='builtin')]
        with self.assertRaises(RuntimeError):plugin_guard(m,'none',a)
        m['plugins']=a['builtin_plugins'];m['loaded_skills']=[]
        with self.assertRaises(RuntimeError):plugin_guard(m,'none',a)
    def test_advertisement_or_literal_command_not_expansion(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'s';f.write_text(json.dumps(dict(type='user',message=dict(content='/distill-sol-pi:efficient-coding TASK')))+'\n'+json.dumps(dict(type='assistant'))+'\n');e=expansion_evidence(f,b'TASK',b'BODY','ours');self.assertFalse(e['command_expansion_verified'])
            f.write_text(json.dumps(dict(type='user',message=dict(content='BODY\nTASK')))+'\n'+json.dumps(dict(type='assistant'))+'\n');self.assertTrue(expansion_evidence(f,b'TASK',b'BODY','ours')['command_expansion_verified'])
    def test_post_assistant_echo_not_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'s';f.write_text(json.dumps(dict(type='assistant'))+'\n'+json.dumps(dict(type='user',message=dict(content='BODY TASK'))));self.assertFalse(expansion_evidence(f,b'TASK',b'BODY','ours')['command_expansion_verified'])
if __name__=='__main__':unittest.main()
