import unittest
from usage_normalization import normalize_request as norm
U={'input_tokens':6400,'output_tokens':185,'total_tokens':6585,'input_tokens_details':{'cached_tokens':0,'cache_write_tokens':0},'output_tokens_details':{'reasoning_tokens':82}}
def terminal(u=U):return {'type':'response.completed','response':{'usage':u,'status':'completed'}}
class Normalization(unittest.TestCase):
 def test_first_observed_request(self):
  r=norm([{'type':'response.created','response':{}},terminal()],'responses',True);self.assertTrue(r['gross_usage_complete']);self.assertEqual(r['gross_tokens'],6585);self.assertEqual(r['reasoning_tokens_reported'],82);self.assertFalse(r['cache_components_complete'])
 def test_created_usage_cannot_replace_missing_terminal_usage(self):
  r=norm([{'type':'response.created','response':{'usage':U}},{'type':'response.completed','response':{}}],'responses',True);self.assertFalse(r['gross_usage_complete'])
 def test_duplicate_terminal_rejected(self):self.assertFalse(norm([terminal(),terminal()],'responses',True)['gross_usage_complete'])
 def test_zero_rejected(self):self.assertFalse(norm([terminal({'input_tokens':0,'output_tokens':0,'total_tokens':0})],'responses',True)['gross_usage_complete'])
 def test_partial_or_missing_fields_rejected(self):
  self.assertFalse(norm([terminal()],'responses',False)['gross_usage_complete']);self.assertFalse(norm([terminal({'input_tokens':2})],'responses',True)['gross_usage_complete'])
 def test_chat_final_usage_plus_done(self):
  r=norm([{'choices':[{'delta':{}}]},{'choices':[],'usage':{'prompt_tokens':10,'completion_tokens':3,'total_tokens':13}},'[DONE]'],'chat',True);self.assertEqual(r['gross_tokens'],13);self.assertIsNone(r['cache_read_tokens_reported'])
 def test_chat_without_done_or_duplicate_usage_rejected(self):
  e={'choices':[],'usage':{'prompt_tokens':10,'completion_tokens':3,'total_tokens':13}}
  self.assertFalse(norm([e],'chat',True)['gross_usage_complete']);self.assertFalse(norm([e,e,'[DONE]'],'chat',True)['gross_usage_complete'])
 def test_partial_chat_usage_not_final(self):
  e={'choices':[{'delta':{}}],'usage':{'prompt_tokens':10,'completion_tokens':3,'total_tokens':13}}
  self.assertFalse(norm([e,'[DONE]'],'chat',True)['gross_usage_complete'])
 def test_invalid_subsets_rejected(self):
  u={**U,'input_tokens_details':{'cached_tokens':6401}};self.assertFalse(norm([terminal(u)],'responses',True)['gross_usage_complete'])
if __name__=='__main__':unittest.main()
