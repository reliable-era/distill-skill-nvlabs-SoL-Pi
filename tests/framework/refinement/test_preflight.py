import unittest
from preflight import check_swe, check_terminal

class PreflightTests(unittest.TestCase):
    def test_swe_infra_failure_never_counts_as_negative_control(self):
        r = dict(completed_instances=1, resolved_instances=0, infra_failure_instances=1,
                 ambiguous_failure_instances=0, empty_patch_instances=0, error_instances=0)
        with self.assertRaises(ValueError):
            check_swe(r, 0)
        r['infra_failure_instances'] = 0
        check_swe(r, 0)
        with self.assertRaises(ValueError):
            check_swe(r, 1)

    def test_terminal_wrong_or_missing_reward_rejected(self):
        r = {'n_total_trials': 1, 'stats': {'n_completed_trials': 1,
             'n_errored_trials': 0, 'n_retries': 0, 'evals': {'oracle': {
             'n_errors': 0, 'reward_stats': {'reward': {'0.0': ['trial']}}}}}}
        with self.assertRaises(ValueError):
            check_terminal(r, 1)
        check_terminal(r, 0)
        r['stats']['evals']['oracle']['reward_stats']['reward'] = {}
        with self.assertRaises(ValueError):
            check_terminal(r, 0)
