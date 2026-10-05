import unittest
from response_receipt import inspect_response
from stream_session import FixtureSession
from provider_fixture import MODEL,final_stream
class Tests(unittest.TestCase):
 def test_terminal_without_usage_is_not_complete(self):
  r=inspect_response(FixtureSession().response({'model':MODEL,'stream':True,'messages':[]}));self.assertTrue(r['done_seen']);self.assertEqual(r['terminal_count'],1);self.assertIsNone(r['usage']);self.assertFalse(r['usage_complete'])
 def test_reference_complete_usage(self):self.assertTrue(inspect_response(final_stream())['usage_complete'])
 def test_post_done_and_size_rejected(self):
  for body in [final_stream()+b'data: {}\n\n',b'x'*65537]:
   with self.assertRaises(ValueError):inspect_response(body)
if __name__=='__main__':unittest.main()
