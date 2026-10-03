import unittest
from collect import token_total

class CollectionTests(unittest.TestCase):
    def test_missing_counters_not_zero(self):
        self.assertIsNone(token_total('copilot',[])[0])
        self.assertIsNone(token_total('cursor',[{'type':'result','usage':{'inputTokens':100}}])[0])
    def test_agy_cache_and_thinking_not_added_again(self):
        event={'event':'result','result':{'status':'SUCCESS','usage':{'input_tokens':100,'output_tokens':20,'thinking_tokens':10,'cache_read_tokens':80,'total_tokens':120}}}
        self.assertEqual(token_total('agy',[event])[0],120)
        self.assertIsNone(token_total('agy',[event,event])[0])
    def test_inconsistent_total_rejected(self):
        event={'event':'result','result':{'status':'SUCCESS','usage':{'input_tokens':100,'output_tokens':20,'total_tokens':130}}}
        self.assertIsNone(token_total('agy',[event])[0])
