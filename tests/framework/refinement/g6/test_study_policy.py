from fractions import Fraction
import tempfile,pathlib,unittest
from unittest.mock import patch
from study_policy import RESET,RATE,RESERVE,forecast,capacity,weekly_threshold,concurrency_after_cells,notify_new_week_sixty
from quota import Quota,QuotaHold
class StudyPolicy(unittest.TestCase):
    def test_reset_boundary(self):
        self.assertEqual(weekly_threshold(RESET-1),Fraction(9,10));self.assertEqual(weekly_threshold(RESET),Fraction(7,10))
    def test_remaining_N_neither_single_window(self):
        f=forecast(.76,300,RESET-1);self.assertEqual(f['remaining_forecast_increment'],.75);self.assertEqual(f['current_window_full_N_projection'],1.51);self.assertFalse(f['current_window_full_N_fits']);self.assertFalse(f['fresh_new_week_full_N_fits'])
    def test_even_optimistic_two_windows_keep_reservation(self):
        f=forecast(.76,300,RESET-1);self.assertEqual(f['optimistic_current_week_capacity_with_existing_guard'],36);self.assertEqual(f['optimistic_fresh_new_week_capacity_with_existing_guard'],260);self.assertEqual(f['optimistic_two_window_capacity_with_existing_guard'],296);self.assertFalse(f['admissions_allowed'])
    def test_capacity_exact_last_admission_strictly_below_cap(self):
        for u,t in ((Fraction(76,100),Fraction(9,10)),(Fraction(0),Fraction(7,10))):
            n=capacity(u,t);self.assertLess(u+(n-1)*RATE+RESERVE,t);self.assertGreaterEqual(u+n*RATE+RESERVE,t)
    def test_new_week_no_old_headroom_assumed(self):
        f=forecast(.76,300,RESET);self.assertEqual(f['optimistic_current_week_capacity_with_existing_guard'],0);self.assertFalse(f['admissions_allowed']);self.assertTrue(f['fresh_zero_is_counterfactual_not_observed'])
    def test_threshold_applies_to_weekly_model_specific_scopes(self):
        q=Quota([],study_mode=True,clock=lambda:RESET);q.observe(dict(rateLimitType='seven_day_opus',utilization=.65),'actual')
        with self.assertRaises(QuotaHold):q.reserve('one')
        self.assertEqual(q.threshold('five_hour'),.9)
    def test_reset_does_not_zero_old_observation(self):
        q=Quota([dict(info=dict(rateLimitType='seven_day',utilization=.76),observed_epoch=RESET-10)],study_mode=True,clock=lambda:RESET)
        with self.assertRaises(QuotaHold):q.reserve('one')
        q.observe(dict(rateLimitType='seven_day',utilization=.10),'fresh');q.reserve('one')
    def test_ramp_requires_twenty_cells_and_no_adverse_events(self):
        self.assertEqual(concurrency_after_cells(19,0),2);self.assertEqual(concurrency_after_cells(20,0),4);self.assertEqual(concurrency_after_cells(20,1),2)
    def test_sixty_notice_uses_observation_week_not_clock_only(self):
        self.assertFalse(notify_new_week_sixty('seven_day',.76,RESET-1));self.assertTrue(notify_new_week_sixty('seven_day',.60,RESET));self.assertFalse(notify_new_week_sixty('five_hour',.80,RESET))
    def test_budget_guard_precedes_token_and_docker(self):
        import runner
        with tempfile.TemporaryDirectory() as d,patch.object(runner,'check_frozen',return_value=dict(supervisor_study_go=True)),patch.object(runner,'private_root',return_value=pathlib.Path(d)),patch('study_preflight.current_budget',return_value=dict(admissions_allowed=False)),patch.object(runner,'read_token') as token,patch.object(runner,'command') as command:
            with self.assertRaises(QuotaHold):runner.guard('unused','study')
            token.assert_not_called();command.assert_not_called()
if __name__=='__main__':unittest.main()
