import json,pathlib,tempfile,unittest
from running_quota import RunningQuota
from quota import QuotaHold
from study_policy import RESET
class Running(unittest.TestCase):
    def q(self,u=.76,now=RESET-10):return RunningQuota([dict(info=dict(rateLimitType='seven_day',utilization=u,resetsAt=RESET),observed_epoch=RESET-20)],clock=lambda:now)
    def start_learning(self,q):
        q.active['fixture/none/1']=q.clock();q.observe(dict(rateLimitType='seven_day',utilization=q.scopes['seven_day']['utilization'],resetsAt=RESET),'live-baseline')
    def test_stale_seed_first_live_is_baseline_not_rate_delta(self):
        q=self.q();q.active['fixture/none/1']=q.clock();q.observe(dict(rateLimitType='seven_day',utilization=.79,resetsAt=RESET),'first-live');q.completed_cell('first');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.0025);self.assertEqual(q.scopes['seven_day']['anchor_utilization'],.79)
        q.observe(dict(rateLimitType='seven_day',utilization=.80,resetsAt=RESET),'later-live');q.completed_cell('second');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.005)
    def test_outside_idle_usage_changes_headroom_not_learning_delta(self):
        q=self.q();self.start_learning(q);q.observe(dict(rateLimitType='seven_day',utilization=.77,resetsAt=RESET),'running');q.completed_cell('one');q.release('fixture/none/1');q.observe(dict(rateLimitType='seven_day',utilization=.85,resetsAt=RESET),'outside');q.active['fixture/ours/1']=q.clock();q.observe(dict(rateLimitType='seven_day',utilization=.86,resetsAt=RESET),'next-live');self.assertAlmostEqual(q.scopes['seven_day']['observed_delta'],.01);self.assertEqual(q.scopes['seven_day']['utilization'],.86)
    def test_rate_capped_at_one_pp_for_external_noise_while_active(self):
        q=self.q();self.start_learning(q);q.observe(dict(rateLimitType='seven_day',utilization=.84,resetsAt=RESET),'external-contaminated-live');q.completed_cell('one');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.01);self.assertGreater(q.scopes['seven_day']['uncapped_rate'],.01)
    def test_five_hour_actual_ninety_and_expired_window_hold(self):
        q=self.q();q.observe(dict(rateLimitType='five_hour',utilization=.90,resetsAt=RESET+100),'actual')
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['none','ours'])
        q.observe(dict(rateLimitType='five_hour',utilization=.2,resetsAt=RESET-20),'expired')
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['none','ours'])
        q.observe(dict(rateLimitType='five_hour',utilization=.0,resetsAt=RESET+18000),'actual-reset');q.reserve_pair('task',['none','ours'])
    def test_no_five_pp_or_full_N_veto(self):
        q=self.q(.88);s=q.reserve_pair('task',['ours','none']);self.assertAlmostEqual(s['seven_day']['projected'],.885)
    def test_pair_stop_before_first_not_half_pair(self):
        q=self.q(.895)
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['ours','none'])
        self.assertFalse(q.pending);self.assertFalse(q.active)
    def test_second_arm_consumes_existing_pair_reservation(self):
        q=self.q();q.reserve_pair('task',['ours','none']);q.reserve('task/ours/1');self.assertEqual(q.snapshot()['seven_day']['reserved_cells'],2);q.release('task/ours/1');q.reserve('task/none/1');self.assertEqual(q.snapshot()['seven_day']['reserved_cells'],1);q.release('task/none/1');q.close_pair('task');self.assertEqual(q.snapshot()['seven_day']['reserved_cells'],0)
    def test_running_rate_at_one_pp_step_completed_cells(self):
        q=self.q();self.start_learning(q)
        for i in range(3):q.completed_cell(str(i))
        q.observe(dict(rateLimitType='seven_day',utilization=.77,resetsAt=RESET),'actual');q.completed_cell('3');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.0025)
        q.completed_cell('3');self.assertEqual(q.completed,4)
        for i in range(4,7):q.completed_cell(str(i))
        q.observe(dict(rateLimitType='seven_day',utilization=.78,resetsAt=RESET),'actual');q.completed_cell('7');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.0025)
    def test_rate_has_no_five_pp_floor(self):
        q=self.q();self.start_learning(q)
        for i in range(19):q.completed_cell(str(i))
        q.observe(dict(rateLimitType='seven_day',utilization=.77,resetsAt=RESET),'actual');q.completed_cell('19');self.assertAlmostEqual(q.scopes['seven_day']['rate'],.0005)
    def test_reset_clock_alone_is_not_headroom(self):
        q=self.q(now=RESET+1)
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['ours','none'])
        q.observe(dict(rateLimitType='seven_day',utilization=.01,resetsAt=RESET+604800),'fresh');q.reserve_pair('task',['ours','none'])
    def test_rejection_holds_until_actual_numeric_refresh(self):
        q=self.q();q.observe(dict(status='rejected',rateLimitType='seven_day'),'rejected')
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['ours','none'])
        q.observe(dict(rateLimitType='seven_day',utilization=.2,resetsAt=RESET),'actual');q.reserve_pair('task',['ours','none'])
    def test_every_shorter_model_scope_is_guarded(self):
        q=self.q();q.observe(dict(five_hour_opus=dict(utilization=.899,resetsAt=1)),'actual')
        with self.assertRaises(QuotaHold):q.reserve_pair('task',['ours','none'])
    def test_additional_retry_needs_headroom_not_free_second_slot(self):
        q=self.q();q.reserve_pair('task',['ours','none']);q.reserve('task/ours/1');q.release('task/ours/1');q.reserve('task/ours/2');self.assertEqual(q.snapshot()['seven_day']['reserved_cells'],2)
    def test_sixty_notice_is_actual_new_week_only(self):
        records=[];q=RunningQuota([],records.append,clock=lambda:RESET+1);q.observe(dict(rateLimitType='seven_day',utilization=.76),'old',RESET-1);self.assertFalse(any(e['kind']=='supervisor_notice' for e in records));q.observe(dict(rateLimitType='seven_day',utilization=.6,resetsAt=RESET+604800),'new',RESET+1);self.assertTrue(any(e['kind']=='supervisor_notice' for e in records))
    def test_running_amendment_skips_retired_preflight(self):
        import hashlib
        from unittest.mock import patch
        from types import SimpleNamespace
        import runner
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/'preregistration.json').write_text('{}');stage=dict(preregistration_sha256=hashlib.sha256(b'{}').hexdigest(),authorized_phases=['smoke']);raw=json.dumps(stage).encode();(root/'runner-stage.json').write_bytes(raw)
            with patch.object(runner,'check_frozen',return_value=dict(supervisor_study_go=True,running_quota_amendment=dict(enabled=True))),patch.object(runner,'private_root',return_value=root),patch.object(runner,'H',root),patch.object(runner,'R',root),patch.object(runner,'command',return_value=SimpleNamespace(stdout=raw)),patch.object(runner,'read_token') as token,patch('study_preflight.current_budget') as retired:
                with self.assertRaises(AssertionError):runner.guard('unused','study')
                retired.assert_not_called();token.assert_not_called()
    def test_live429_stops_even_before_terminal_parse(self):
        from study_runner import StudyAdmissions
        with tempfile.TemporaryDirectory() as d:
            a=StudyAdmissions(pathlib.Path(d));a.observe_native(dict(type='system',subtype='api_retry',status_code=429),'task/ours/1');self.assertTrue(a.stopped);self.assertTrue(a.stop_file.exists())
    def test_live_overload_prevents_ramp_without_discarding_attempt(self):
        from study_runner import StudyAdmissions
        with tempfile.TemporaryDirectory() as d:
            a=StudyAdmissions(pathlib.Path(d));a.observe_native(dict(type='error',error='API Error:503 overloaded'),'task/ours/1');self.assertGreater(a.adverse,0);self.assertFalse(a.stopped)
    def test_soft_pause_drains_second_arm_offline(self):
        import io,contextlib
        from unittest.mock import patch,MagicMock
        import study_runner as sr
        from common import prereg
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=prereg();p['live_baseline_correction']={};p['study_issue_order']=['fixture'];p['arm_orders']={'fixture':['ours','none']};(root/'dataset.json').write_text(json.dumps([dict(instance_id='fixture')]))
            f=root/'smoke-explicit-v2/fixture/ours-a1';f.mkdir(parents=True);(f/'native.jsonl').write_text('');(f/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.76,resetsAt=RESET)]))))
            calls=[]
            def prep(data,base,path):path.mkdir();(path/'manifest.json').write_text('{}')
            def fake(task,arm,number,directory,baseline,image,base,network,a,phase):
                directory.mkdir();key=task+'/'+arm+'/'+str(number);a.quota.reserve(key);a.quota.release(key);calls.append(arm)
                if len(calls)==1:a.pause('fixture quota stop on NEW pairs only')
                row=dict(task=task,arm=arm,attempt=number,native_started=True,grade_valid=True,solved=True,expansion=dict(command_expansion_verified=True),stream=dict(rate_limited=False,terminal_5xx=False,blocked_native=False,native_error_events=[]));(directory/'attempt-result.json').write_text(json.dumps(row));return row
            with patch.object(sr,'private_root',return_value=root),patch.object(sr,'guard',return_value=p),patch.object(sr,'Network'),patch.object(sr,'RunningQuota',side_effect=lambda seed,record:RunningQuota(seed,record,clock=lambda:RESET-10)),patch.object(sr,'IssueImages'),patch.object(sr,'prepare',side_effect=prep),patch.object(sr,'attempt',side_effect=fake),patch.object(sr,'plugin_guard'),patch('study_analysis.main'),contextlib.redirect_stdout(io.StringIO()):sr.main('offline-fixture')
            self.assertEqual(calls,['ours','none']);status=json.loads((root/'study-status.json').read_text());self.assertEqual(status['cells_done'],2);self.assertEqual(status['completed_pairs'],1);self.assertEqual(status['state'],'paused')
    def test_resume_priority_missing_arm_before_other_issues_offline(self):
        import io,contextlib,datetime,time
        from unittest.mock import patch
        import study_runner as sr
        from common import prereg
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=prereg();p['study_issue_order']=['priority','later'];p['arm_orders']={t:['none','ours'] for t in p['study_issue_order']};p['live_baseline_correction']={'complete_first_task':'priority'};(root/'dataset.json').write_text(json.dumps([dict(instance_id=t) for t in p['study_issue_order']]))
            smoke=root/'smoke-explicit-v2/fixture/none-a1';smoke.mkdir(parents=True);(smoke/'native.jsonl').write_text('');(smoke/'attempt-result.json').write_text(json.dumps(dict(stream=dict(rate_limit_events=[dict(rateLimitType='seven_day',utilization=.76,resetsAt=RESET)]))))
            def row(task,arm):return dict(task=task,arm=arm,attempt=1,native_started=True,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=0.,grade_valid=True,solved=True,expansion=dict(command_expansion_verified=True),stream=dict(rate_limited=False,terminal_5xx=False,blocked_native=False,native_error_events=[]))
            old=root/'study/priority/none-a1';old.mkdir(parents=True);(old/'attempt-result.json').write_text(json.dumps(row('priority','none')));calls=[]
            def prep(data,base,path):path.mkdir();(path/'manifest.json').write_text('{}')
            def fake(task,arm,number,directory,baseline,image,base,network,a,phase):
                directory.mkdir();key=task+'/'+arm+'/'+str(number);a.quota.reserve(key);a.quota.release(key);calls.append((task,arm));r=row(task,arm);r['attempt']=number;(directory/'attempt-result.json').write_text(json.dumps(r));return r
            with patch.object(sr,'private_root',return_value=root),patch.object(sr,'guard',return_value=p),patch.object(sr,'Network'),patch.object(sr,'RunningQuota',side_effect=lambda seed,record:RunningQuota(seed,record,clock=lambda:RESET-10)),patch.object(sr,'IssueImages'),patch.object(sr,'prepare',side_effect=prep),patch.object(sr,'attempt',side_effect=fake),patch.object(sr,'plugin_guard'),patch('study_analysis.main'),contextlib.redirect_stdout(io.StringIO()):sr.main('offline-priority')
            self.assertEqual(calls,[('priority','ours'),('later','none'),('later','ours')]);self.assertEqual(json.loads((root/'study-status.json').read_text())['cells_done'],4)
    def test_interim_analysis_all_attempts_and_unknowns(self):
        from study_analysis import analyze
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=dict(study_issue_order=['a','b'],analysis=dict(bootstrap_seed=2026101704))
            for task in ('a','b'):
                for arm in ('none','ours'):
                    f=root/'study'/task/(arm+'-a1')/'attempt-result.json';f.parent.mkdir(parents=True);f.write_text(json.dumps(dict(task=task,arm=arm,attempt=1,native_started=True,grade_valid=True,solved=arm=='ours',expansion=dict(command_expansion_verified=True),stream=dict(usage_complete=True,token_volume_lower_bound=100,cache_adjusted_volume_5m_proxy=50))))
            a=analyze(root,p);self.assertEqual(a['native_attempts'],4);self.assertEqual(a['study_reported_token_volume_lower_bound'],400);self.assertEqual(a['exact_mcnemar_p'],.5);self.assertEqual(a['paired_solve_difference'],1);self.assertIsNone(a['paired_all_cost_TPS_ratio'])
if __name__=='__main__':unittest.main()
