import unittest,json
from copilot_provider_stream_fixture import tool_stream,final_stream,inspect_fixture,encode,frame,FAKE_USAGE
class Fixtures(unittest.TestCase):
 def test_fragmented_arguments_roundtrip(self):
  args={'message':'quote " and unicode 测试'};v=inspect_fixture(tool_stream('fixture_echo',args,{'fixture_echo'}));self.assertEqual(v['tool_arguments'],args);self.assertEqual(v['finish'],'tool_calls');self.assertIsNone(v['real_model_tokens'])
 def test_final_and_subset_accounting(self):
  v=inspect_fixture(final_stream());self.assertEqual(v['finish'],'stop');self.assertEqual(v['inclusive_gross_fixture_tokens'],18);self.assertTrue(v['cache_and_reasoning_SUBSETS_NOT_added']);self.assertTrue(v['native_compatibility_NOT_established'])
 def test_no_undeclared_tool(self):
  with self.assertRaises(ValueError):tool_stream('unknown',{},set())
 def test_cutoff_not_zero_complete(self):
  with self.assertRaises(ValueError):inspect_fixture(final_stream().replace(b'data: [DONE]\n\n',b''))
  with self.assertRaises(ValueError):inspect_fixture(encode([frame({'content':'ACK'},'stop')]))
 def test_duplicate_usage_rejected(self):
  u={'model':'Qwen3.8-27B-FP8','choices':[],'usage':FAKE_USAGE}
  with self.assertRaises(ValueError):inspect_fixture(encode([frame({},'stop'),u,u]))
 def test_total_and_post_terminal_guard(self):
  u={**FAKE_USAGE,'total_tokens':22}
  with self.assertRaises(ValueError):inspect_fixture(encode([frame({},'stop'),{'model':'Qwen3.8-27B-FP8','choices':[],'usage':u}]))
  with self.assertRaises(ValueError):inspect_fixture(final_stream()+b'data: {}\n\n')
if __name__=='__main__':unittest.main()
