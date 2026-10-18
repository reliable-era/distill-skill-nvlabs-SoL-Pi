import contextlib,datetime,io,json,pathlib,tempfile,unittest
from unittest.mock import patch
from auto_quota import blocked_windows,reset_due
from running_quota import RunningQuota
from quota import QuotaHold
from study_policy import RESET
from study_runner import StudyAdmissions

class AutoQuota(unittest.TestCase):
    def setup_gate(self,root):
        self.now=RESET-10;a=StudyAdmissions(root,automatic=True);a.cell_order=[('a','none'),('a','ours'),('b','none'),('b','ours')]
        a.quota=RunningQuota([dict(info=dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),observed_epoch=RESET-20)],a.log,clock=lambda:self.now)
        a.quota_pause('fixture binding window',2);return a
    def finish(self,a,root,arm):
        a.quota.release('a/'+arm+'/1');f=root/'study/a'/(arm+'-a1')/'attempt-result.json';f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(dict(task='a',arm=arm,attempt=1,native_started=True,started_utc=datetime.datetime.fromtimestamp(self.now,datetime.timezone.utc).isoformat(),wall_seconds=0,grade_valid=True,solved=False,expansion=dict(command_expansion_verified=True),stream=dict(terminal_5xx=False,rate_limited=False,blocked_native=False,native_error_events=[]))))
        a.quota.completed_cell('a/'+arm);a.cell_completed('a/'+arm)
    def test_reset_plus120_allows_one_cell_not_numeric_zero(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+119;self.assertFalse(a.try_resume());self.now+=1;self.assertTrue(a.try_resume());self.assertEqual(a.reentry['cell'],'a/none');a.reserve_pair('a',['none','ours']);s=a.reserve_native('a/none/1');self.assertEqual(s['seven_day']['utilization'],.90);self.assertTrue(s['seven_day']['headroom_not_assumed']);self.assertEqual(len(a.quota.active),1)
            with self.assertRaises(RuntimeError):a.reserve_pair('b',['none','ours'])
            with self.assertRaises(QuotaHold):a.quota.reserve('b/none/1',reset_permit=a.quota_windows)
    def test_fresh_headers_then_partner_then_normal_scheduling(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+120;a.try_resume();a.reserve_pair('a',['none','ours']);a.reserve_native('a/none/1');a.observe_rate(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),'a/none/1');self.finish(a,root,'none');self.assertEqual(a.reentry['cell'],'a/ours');self.assertEqual(a.reentry['stage'],'partner');self.assertTrue(a.pause_new_pairs);a.reserve_native('a/ours/1');self.finish(a,root,'ours');self.assertFalse(a.quota_paused);self.assertFalse(a.pause_new_pairs);a.reserve_pair('b',['none','ours'])
    def test_no_headroom_rearms_next_reported_reset_no_repeat_old_reset(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+1;a.quota.observe(dict(rateLimitType='seven_day',utilization=.1,resetsAt=RESET+604800),'post-week-reset');a.quota.observe(dict(rateLimitType='five_hour',utilization=.91,resetsAt=RESET+100),'old');a.quota_pause('five hour',2);self.now=RESET+220;a.try_resume();a.reserve_pair('a',['none','ours']);a.reserve_native('a/none/1');a.observe_rate(dict(rateLimitType='five_hour',utilization=.91,resetsAt=RESET+18100),'a/none/1');self.finish(a,root,'none');self.assertTrue(a.quota_paused);self.assertIsNone(a.reentry);self.assertEqual(a.quota_windows,{'five_hour':RESET+18100});self.assertFalse(a.try_resume());self.now=RESET+18220;self.assertTrue(a.try_resume());self.assertEqual(a.reentry['cell'],'a/ours')
    def test_stale_reset_cannot_admit_second_cell_on_same_permission(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+120;a.try_resume();a.reserve_pair('a',['none','ours']);a.reserve_native('a/none/1');a.observe_rate(dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),'a/none/1');self.finish(a,root,'none');self.assertIsNone(a.reentry);self.assertFalse(a.try_resume());self.assertIn(('seven_day',RESET),a.used_resets)
    def test_used_reset_is_durable_across_restart(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+120;a.try_resume();a.reserve_pair('a',['none','ours']);a.reserve_native('a/none/1');a.observe_rate(dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),'a/none/1');self.finish(a,root,'none');b=StudyAdmissions(root,automatic=True);self.assertIn(('seven_day',RESET),b.used_resets)
    def test_missing_fresh_binding_header_is_reportable_guard_not_zero(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+120;a.try_resume();a.reserve_pair('a',['none','ours']);a.reserve_native('a/none/1');self.finish(a,root,'none');self.assertTrue(a.stopped);self.assertTrue(a.stop_file.exists())
    def test_unknown_or_unrelated_scope_never_bypassed(self):
        q=RunningQuota([dict(info=dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),observed_epoch=RESET-1)],clock=lambda:RESET+120)
        q.require_refresh()
        with self.assertRaises(QuotaHold):q.reserve('a/none/1',reset_permit={'seven_day':RESET})
        q.observe(dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),'old');q.observe(dict(rateLimitType='five_hour',utilization=.95,resetsAt=RESET+500),'other')
        with self.assertRaises(QuotaHold):q.reserve('a/none/1',reset_permit={'seven_day':RESET})
    def test_all_binding_windows_must_pass_plus120(self):
        now=[RESET+150];q=RunningQuota([],clock=lambda:now[0]);q.observe([dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET),dict(rateLimitType='five_hour',utilization=.95,resetsAt=RESET+100)],'last-headers');w=blocked_windows(q.snapshot());self.assertFalse(reset_due(q,w,set()));now[0]=RESET+220;self.assertTrue(reset_due(q,w,set()));self.assertFalse(reset_due(q,w,{('seven_day',RESET)}))
    def test_unresolved_native_or_grade_blocks_single_cell_gate(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);a=self.setup_gate(root);self.now=RESET+120;f=root/'study/b/none-a1/attempt-progress.json';f.parent.mkdir(parents=True);f.write_text('{}');self.assertFalse(a.try_resume());self.assertIsNone(a.reentry)
    def test_weekly_sixty_reporting_and_fatal_rules_unchanged(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota.observe(dict(rateLimitType='seven_day',utilization=.60,resetsAt=RESET+604800),'live',RESET+1);self.assertTrue(a.report_stop);self.assertTrue(a.pause_new_pairs);self.assertFalse(a.try_resume())
            with self.assertRaises(RuntimeError):a.reserve_pair('b',['none','ours'])
            a.observe_native(dict(type='system',subtype='api_retry',status_code=429),'a/none/1');self.assertTrue(a.stopped)
    def test_credential_hit_immediate_callback(self):
        from security import filtered_copy
        out=io.BytesIO();hits=[];n=filtered_copy(io.BytesIO(b'before secret-fixture after'),out,b'secret-fixture',on_hit=lambda:hits.append(True));self.assertEqual(n,1);self.assertEqual(hits,[True]);self.assertNotIn(b'secret-fixture',out.getvalue())
    def test_scheduler_single_cell_then_partner_then_frozen_queue_offline(self):
        import study_runner as sr
        from common import prereg
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);p=prereg();p['automatic_quota_resume']={'enabled':True};p['live_baseline_correction']={};p['study_issue_order']=['a','b'];p['arm_orders']={t:['none','ours'] for t in ('a','b')};(root/'dataset.json').write_text(json.dumps([dict(instance_id=t) for t in ('a','b')]))
            f=root/'smoke-explicit-v2/fake/none-a1';f.mkdir(parents=True);(f/'native.jsonl').write_text('');(f/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.90,resetsAt=RESET)]))))
            self.now=RESET-10;calls=[]
            def quota(seed,record):return RunningQuota(seed,record,clock=lambda:self.now)
            def sleep(seconds):self.now=max(self.now,RESET+120)
            def prep(data,base,path):path.mkdir();(path/'manifest.json').write_text('{}')
            def fake(task,arm,number,directory,baseline,image,base,network,a,phase):
                directory.mkdir();key=task+'/'+arm+'/'+str(number);before=a.reserve_native(key);calls.append((task,arm));a.observe_rate(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),key);a.quota.release(key)
                row=dict(task=task,arm=arm,attempt=number,native_started=True,grade_valid=True,solved=False,expansion=dict(command_expansion_verified=True),stream=dict(rate_limited=False,terminal_5xx=False,blocked_native=False,native_error_events=[]));(directory/'attempt-result.json').write_text(json.dumps(row));return row
            with patch.object(sr,'private_root',return_value=root),patch.object(sr,'guard',return_value=p),patch.object(sr,'Network'),patch.object(sr,'RunningQuota',side_effect=quota),patch.object(sr,'IssueImages'),patch.object(sr,'prepare',side_effect=prep),patch.object(sr,'attempt',side_effect=fake),patch.object(sr,'plugin_guard'),patch.object(sr.time,'sleep',side_effect=sleep),patch('study_analysis.main'):sr.main('offline-native-reset')
            self.assertEqual(calls,[('a','none'),('a','ours'),('b','none'),('b','ours')]);events=[json.loads(x) for x in (root/'study-admission-events.jsonl').read_text().splitlines()];entries=[e for e in events if e['kind']=='reset_reentry_admitted'];self.assertEqual(len(entries),1);self.assertEqual(entries[0]['cell'],'a/none');self.assertTrue(entries[0]['ordinary_study_cell']);self.assertTrue(any(e['kind']=='quota_resume' for e in events))
    def test_no_oauth_client_or_polling_in_runtime(self):
        import study_runner
        self.assertFalse(hasattr(study_runner,'refresh'));self.assertFalse(hasattr(StudyAdmissions,'poll_quota'));self.assertFalse((pathlib.Path(study_runner.__file__).parent/'quota_refresh.py').exists())

if __name__=='__main__':unittest.main()
