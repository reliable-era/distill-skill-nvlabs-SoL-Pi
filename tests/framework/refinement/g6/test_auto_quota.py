import contextlib,io,json,pathlib,tempfile,unittest
from unittest.mock import patch
from auto_quota import blocked_windows,reset_headroom
from running_quota import RunningQuota
from study_policy import RESET
from study_runner import StudyAdmissions

class AutoQuota(unittest.TestCase):
    def q(self):
        self.now=RESET-10
        return RunningQuota([dict(info=dict(rateLimitType='seven_day',utilization=.895,resetsAt=RESET),observed_epoch=RESET-20)],clock=lambda:self.now)
    def test_clock_and_same_window_drop_never_resume(self):
        q=self.q();w=blocked_windows(q.snapshot(2));self.now=RESET+1;self.assertFalse(reset_headroom(q,w,2));q.observe(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET),'stale-reset');self.assertFalse(reset_headroom(q,w,2));q.observe(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),'live-header');self.assertTrue(reset_headroom(q,w,2))
    def test_all_blocking_windows_need_actual_reset_and_projection(self):
        q=self.q();q.observe(dict(rateLimitType='five_hour',utilization=.90,resetsAt=RESET+100),'old');w=blocked_windows(q.snapshot(2));self.now=RESET+101;q.observe(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),'weekly-reset');self.assertFalse(reset_headroom(q,w,2));q.observe(dict(rateLimitType='five_hour',utilization=.89,resetsAt=RESET+18100),'five-hour-reset');self.assertTrue(reset_headroom(q,w,2));q.observe(dict(rateLimitType='seven_day',utilization=.699,resetsAt=RESET+604800),'no-projected-room');self.assertFalse(reset_headroom(q,w,2))
    def test_unknown_scopes_are_guard_failure_not_auto_wait(self):
        q=self.q();q.require_refresh()
        with self.assertRaises(RuntimeError):blocked_windows(q.snapshot(2))
    def test_real_weekly_sixty_requests_report_not_auto_resume(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota.observe(dict(rateLimitType='seven_day',utilization=.60,resetsAt=RESET+604800),'live',RESET+1);self.assertTrue(a.report_stop);self.assertTrue(a.pause_new_pairs);self.assertFalse(a.quota_paused);self.assertFalse(a.try_resume());self.assertFalse(a.stopped)
    def test_reporting_stop_blocks_new_pairs_but_fatal_blocks_promised_native(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota=self.q();a.quota.scopes['seven_day']['utilization']=.2;a.reserve_pair('task',['none','ours']);a.report_stop=True;a.pause_new_pairs=True
            with self.assertRaises(RuntimeError):a.reserve_pair('other',['none','ours'])
            a.reserve_native('task/none/1');a.quota.release('task/none/1');a.stop('fixture fatal')
            with self.assertRaises(RuntimeError):a.reserve_native('task/ours/1')
    def test_429_refresh_is_global_stop_not_auto_retry(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota=self.q();a.quota_pause('fixture',2)
            with patch('study_runner.refresh',return_value=dict(status=429)) as call:a.poll_quota(object());a.next_refresh=0;a.poll_quota(object())
            self.assertTrue(a.stopped);self.assertEqual(call.call_count,1)
    def test_refresh_five_server_errors_exhausts_and_records_no_model_calls(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota=self.q();a.quota_pause('fixture',2)
            with patch('study_runner.refresh',return_value=dict(status=503)):
                for _ in range(5):a.next_refresh=0;a.poll_quota(object())
            self.assertTrue(a.stopped);self.assertEqual(a.refresh_errors,5);self.assertTrue(a.adverse)
    def test_reserved_arm_wait_reuses_same_reservation_not_new_attempt(self):
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            a=StudyAdmissions(pathlib.Path(d),automatic=True);a.quota=self.q();a.quota.scopes['seven_day']['utilization']=.8;a.quota.reserve_pair('task',['none','ours']);a.quota.reserve('task/none/1');a.quota.release('task/none/1');a.quota.scopes['seven_day']['utilization']=.90;a.quota_pause('promised wait')
            self.now=RESET+1;a.quota.observe(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),'live-header');s=a.reserve_native('task/ours/1');self.assertFalse(a.quota_paused);self.assertEqual(len(a.quota.active),1);self.assertEqual(s['seven_day']['reserved_cells'],1);self.assertEqual(a.quota.pending['task'],[])
    def test_scheduler_resumes_after_drain_with_zero_model_refresh(self):
        import study_runner as sr
        from common import prereg
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);p=prereg();p['automatic_quota_resume']={'enabled':True};p['live_baseline_correction']={};p['study_issue_order']=['a'];p['arm_orders']={'a':['none','ours']};(root/'dataset.json').write_text(json.dumps([dict(instance_id='a')]))
            f=root/'smoke-explicit-v2/fake/none-a1';f.mkdir(parents=True);(f/'native.jsonl').write_text('');(f/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.895,resetsAt=RESET)]))))
            self.now=RESET-10;calls=[]
            def quota(seed,record):return RunningQuota(seed,record,clock=lambda:self.now)
            def probe(network):
                self.now=RESET+1
                return dict(status=200,scopes=[dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800)])
            def prep(data,base,path):path.mkdir();(path/'manifest.json').write_text('{}')
            def fake(task,arm,number,directory,baseline,image,base,network,a,phase):
                directory.mkdir();key=task+'/'+arm+'/'+str(number);a.reserve_native(key);a.quota.release(key);calls.append(arm);row=dict(task=task,arm=arm,attempt=number,native_started=True,grade_valid=True,solved=True,expansion=dict(command_expansion_verified=True),stream=dict(rate_limited=False,terminal_5xx=False,blocked_native=False,native_error_events=[]));(directory/'attempt-result.json').write_text(json.dumps(row));return row
            with patch.object(sr,'private_root',return_value=root),patch.object(sr,'guard',return_value=p),patch.object(sr,'Network'),patch.object(sr,'RunningQuota',side_effect=quota),patch.object(sr,'refresh',side_effect=probe) as refresh,patch.object(sr,'IssueImages'),patch.object(sr,'prepare',side_effect=prep),patch.object(sr,'attempt',side_effect=fake),patch.object(sr,'plugin_guard'),patch('study_analysis.main'):sr.main('offline-auto')
            self.assertEqual(calls,['none','ours']);self.assertEqual(refresh.call_count,1);events=[json.loads(x) for x in (root/'study-admission-events.jsonl').read_text().splitlines()];self.assertEqual(sum(e['kind']=='quota_pause' for e in events),1);self.assertEqual(sum(e['kind']=='quota_resume' for e in events),1)
    def test_credential_hit_callback_before_persisting_literal(self):
        from security import filtered_copy
        source=io.BytesIO(b'before secret-fixture after');output=io.BytesIO();hits=[];count=filtered_copy(source,output,b'secret-fixture',on_hit=lambda:hits.append(True));self.assertEqual(count,1);self.assertEqual(hits,[True]);self.assertNotIn(b'secret-fixture',output.getvalue())
    def test_live_usage_response_normalization_no_auth_persisted(self):
        import os,urllib.request
        from quota_refresh import CLIENT
        from unittest.mock import MagicMock
        body={k:dict(utilization=v,resets_at='2026-10-25T20:00:00+00:00') for k,v in [('five_hour',44),('seven_day',2)]};response=MagicMock();response.__enter__.return_value=response;response.read.return_value=json.dumps(body).encode();response.headers={};out=io.StringIO()
        with patch.dict(os.environ,{'CLAUDE_CODE_OAUTH_TOKEN':'fake-fixture-token'}),patch.object(urllib.request,'build_opener') as opener,contextlib.redirect_stdout(out):
            opener.return_value.open.return_value=response;exec(CLIENT,{})
        result=json.loads(out.getvalue());self.assertEqual(result['status'],200);self.assertEqual([s['utilization'] for s in result['scopes']],[.44,.02]);self.assertNotIn('fake-fixture-token',out.getvalue());self.assertEqual(opener.return_value.open.call_args.args[0].full_url,'https://api.anthropic.com/api/oauth/usage')
    def test_terminal_native_five_xx_stops_before_sixth_call_or_other_arm(self):
        import study_runner as sr
        from common import prereg
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=pathlib.Path(d);p=prereg();p['automatic_quota_resume']={'enabled':True};p['live_baseline_correction']={};p['study_issue_order']=['a'];p['arm_orders']={'a':['none','ours']};(root/'dataset.json').write_text(json.dumps([dict(instance_id='a')]))
            f=root/'smoke-explicit-v2/fake/none-a1';f.mkdir(parents=True);(f/'native.jsonl').write_text('');(f/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.1,resetsAt=RESET)]))))
            calls=[]
            def prep(data,base,path):path.mkdir();(path/'manifest.json').write_text('{}')
            def fake(task,arm,number,directory,baseline,image,base,network,a,phase):
                directory.mkdir();key=task+'/'+arm+'/'+str(number);a.reserve_native(key);a.quota.release(key);calls.append((arm,number));row=dict(task=task,arm=arm,attempt=number,native_started=True,grade_valid=False,solved=None,stream=dict(rate_limited=False,terminal_5xx=True,blocked_native=False,native_error_events=[]));(directory/'attempt-result.json').write_text(json.dumps(row));return row
            with patch.object(sr,'private_root',return_value=root),patch.object(sr,'guard',return_value=p),patch.object(sr,'Network'),patch.object(sr,'RunningQuota',side_effect=lambda seed,record:RunningQuota(seed,record,clock=lambda:RESET-10)),patch.object(sr,'IssueImages'),patch.object(sr,'prepare',side_effect=prep),patch.object(sr,'attempt',side_effect=fake),patch.object(sr.random,'uniform',return_value=-1),patch('study_analysis.main'):sr.main('offline-exhaust')
            self.assertEqual(calls,[('none',i) for i in range(1,6)]);self.assertIn('Terminal5xx exhaustion',json.loads((root/'STUDY-ADMISSIONS-STOP').read_text())['reason'])
    def test_refresh_client_is_non_inference_fixed_target_no_redirect(self):
        from quota_refresh import CLIENT
        self.assertIn('https://api.anthropic.com/api/oauth/usage',CLIENT);self.assertIn('http://127.0.0.1:3128',CLIENT);self.assertIn('NoRedirect',CLIENT);self.assertNotIn('/v1/messages',CLIENT)

if __name__=='__main__':unittest.main()
