import unittest
from provider_failures import interpret_codex_terminal


class ProviderFailures(unittest.TestCase):
    def test_routing_failure_stops_stage(self):
        result = interpret_codex_terminal([
            {'type': 'error', 'message': 'Reconnecting 1/5'},
            {'type': 'turn.failed', 'error': {'message': 'workspace routing discovery failed'}}])
        self.assertFalse(result['actor_available'])
        self.assertEqual(result['stage_stop_reason'], 'workspace_routing_unavailable')

    def test_benign_tool_output_is_not_provider_failure(self):
        result = interpret_codex_terminal([
            {'type': 'item.completed', 'item': {'aggregated_output': 'Unauthorized; workspace routing discovery failed'}},
            {'type': 'turn.completed', 'usage': {'input_tokens': 12}}])
        self.assertTrue(result['actor_available'])
        self.assertIsNone(result['stage_stop_reason'])

    def test_recovered_error_does_not_replace_success(self):
        result = interpret_codex_terminal([
            {'type': 'error', 'message': 'workspace routing discovery failed'},
            {'type': 'turn.completed'}])
        self.assertTrue(result['actor_available'])
        self.assertEqual(result['recovered_errors'], 1)
        self.assertIsNone(result['provider_failure'])

    def test_auth_and_quota_have_distinct_stop_reasons(self):
        for message, reason in [('invalid_grant', 'authentication_unavailable'),
                                ('insufficient_quota', 'quota_unavailable')]:
            with self.subTest(message=message):
                result = interpret_codex_terminal([{'type': 'turn.failed', 'error': {'message': message}}])
                self.assertEqual(result['stage_stop_reason'], reason)

    def test_unknown_terminal_failure_requires_stop(self):
        self.assertEqual(interpret_codex_terminal([{'type': 'turn.failed', 'error': {'message': 'unknown native failure'}}])['stage_stop_reason'], 'native_turn_failed')

    def test_missing_terminal_is_unknown_not_measured_failure(self):
        result = interpret_codex_terminal([{'type': 'item.completed'}])
        self.assertIsNone(result['actor_available'])
        self.assertIsNone(result['provider_failure'])
