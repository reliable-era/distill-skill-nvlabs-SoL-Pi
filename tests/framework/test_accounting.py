import unittest
from accounting import summarize, price_attempt, terminal_usage

class AccountingTests(unittest.TestCase):
    def test_failed_attempts_in_cost(self):
        records=[dict(solved=True,cost_usd=1,elapsed_seconds=2),dict(solved=False,cost_usd=3,elapsed_seconds=4)]
        s=summarize(records)
        self.assertEqual(s['dollars_per_solve'],4)
        self.assertEqual(s['seconds_per_solve'],6)
    def test_missing_usage_not_free(self):
        s=summarize([dict(solved=True,cost_usd=None)])
        self.assertIsNone(s['dollars_per_solve'])
        self.assertFalse(s['tokens_complete'])
        self.assertIsNone(s['observed_tokens'])
        self.assertIsNone(s['tokens_per_solve'])
    def test_caches_exclusive_price(self):
        r=dict(input_tokens=10, output_tokens=20,cache_read_tokens=30,cache_write_tokens=40,usage_complete=True,token_semantics='exclusive')
        p=dict(input_tokens=1,output_tokens=2,cache_read_tokens=3,cache_write_tokens=4)
        self.assertAlmostEqual(price_attempt(r,p),300/1e6)
        r['token_semantics']='unknown'
        self.assertIsNone(price_attempt(r,p))
    def test_cumulative_not_double_counted(self):
        event=dict(type='turn.completed',usage=dict(input_tokens=100,cached_input_tokens=20,output_tokens=30))
        self.assertEqual(terminal_usage([event], 'codex')['input_tokens'],80)
        self.assertIsNone(terminal_usage([event,event], 'codex')['input_tokens'])
    def test_unknown_grades_do_not_inflate_quality(self):
        s=summarize([dict(solved=True),dict(solved=None)])
        self.assertIsNone(s["solve_rate"])
        self.assertEqual(s["solve_rate_lower_bound"],.5)
        self.assertEqual(s["solve_rate_upper_bound"],1)

    def test_ungraded_and_zero_solves(self):
        s=summarize([dict(status='timeout',solved=None)])
        self.assertEqual(s['ungraded'],1)
        self.assertIsNone(s['solve_rate'])
        self.assertIsNone(s['tokens_per_solve'])

    def test_codex_explicit_no_write_cache(self):
        e=dict(type='turn.completed',usage=dict(input_tokens=100,cached_input_tokens=20,
               cache_write_input_tokens=0,output_tokens=30,reasoning_output_tokens=10))
        r=terminal_usage([e], 'codex')
        self.assertTrue(r['usage_complete'])
        self.assertEqual(r['output_tokens'],30)  # reasoning is already included
        del e['usage']['cache_write_input_tokens']
        self.assertFalse(terminal_usage([e], 'codex')['usage_complete'])

    def test_pi_terminal_snapshot_not_stream_duplicates(self):
        m=dict(role='assistant',stopReason='stop',usage=dict(input=10,output=20,
               cacheRead=30,cacheWrite=40,totalTokens=100))
        events=[dict(type='message_end',message=m),dict(type='turn_end',message=m),
                dict(type='agent_end',messages=[dict(role='user'),m,m])]
        r=terminal_usage(events, 'pi')
        self.assertTrue(r['usage_complete'])
        self.assertEqual(r['input_tokens'],20)
        self.assertEqual(r['cache_write_tokens'],80)
        # Equal usage on separate calls must not be deduplicated by token count.
        self.assertIsNone(terminal_usage(events[:-1], 'pi')['input_tokens'])

    def test_pi_compaction_cannot_be_silently_omitted(self):
        message = dict(role='assistant', stopReason='stop',
                       usage=dict(input=10, output=20, cacheRead=30, cacheWrite=0, totalTokens=60))
        for kind in ('compaction_start', 'compaction_end', 'branch_summary'):
            with self.subTest(kind=kind):
                result = terminal_usage([dict(type=kind), dict(type='agent_end', messages=[message])], 'pi')
                self.assertFalse(result['usage_complete'])
                self.assertEqual(result['input_tokens'], 10)
                self.assertIn('auxiliary scope unresolved', result['usage_source'])

    def test_pi_nested_tool_usage_requires_scope_reconciliation(self):
        message = dict(role='assistant', stopReason='stop',
                       usage=dict(input=10, output=20, cacheRead=30, cacheWrite=0, totalTokens=60))
        tool = dict(role='toolResult', usage=dict(input=2, output=3))
        result = terminal_usage([dict(type='agent_end', messages=[message, tool])], 'pi')
        self.assertFalse(result['usage_complete'])
        self.assertEqual(result['output_tokens'], 20)

    def test_pi_ordinary_tool_result_keeps_verified_main_scope(self):
        message = dict(role='assistant', stopReason='stop',
                       usage=dict(input=10, output=20, cacheRead=30, cacheWrite=0, totalTokens=60))
        result = terminal_usage([dict(type='agent_end', messages=[message, dict(role='toolResult', content='ok')])], 'pi')
        self.assertTrue(result['usage_complete'])

    def test_pi_placeholder_or_missing_usage_not_complete(self):
        m=dict(role='assistant',stopReason='stop',usage=dict(input=0,output=0,
               cacheRead=0,cacheWrite=0,totalTokens=0))
        self.assertFalse(terminal_usage([dict(type='agent_end',messages=[m])], 'pi')['usage_complete'])
        m['usage']=dict(input=1,output=2,cacheRead=0,totalTokens=3)
        self.assertFalse(terminal_usage([dict(type='agent_end',messages=[m])], 'pi')['usage_complete'])

    def test_claude_terminal_models_only(self):
        u=dict(inputTokens=10,outputTokens=20,cacheReadInputTokens=30,cacheCreationInputTokens=40)
        e=dict(type='result',modelUsage={'main':u,'aux':u},usage={'input_tokens':999})
        r=terminal_usage([dict(type='assistant',usage=u),e], 'claude')
        self.assertTrue(r['usage_complete'])
        self.assertEqual(r['input_tokens'],20)
        self.assertEqual(r['cache_read_tokens'],60)

    def test_unknown_and_malformed_remain_unknown(self):
        for agent in ('gemini','copilot','opencode','cursor','hermes','openclaw'):
            self.assertFalse(terminal_usage([dict(type='result',tokens=42)],agent)['usage_complete'])
        e=dict(type='turn.completed',usage=dict(input_tokens=True,cached_input_tokens=0,output_tokens=1))
        self.assertIsNone(terminal_usage([e],'codex')['input_tokens'])
