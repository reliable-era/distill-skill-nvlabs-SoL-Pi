import unittest
from stream_session import FixtureSession
from response_receipt import inspect_response
from provider_fixture import MODEL
class Tests(unittest.TestCase):
 def test_cutoff_missing_every_terminal_signal(self):
  r=inspect_response(FixtureSession().response({'model':MODEL,'stream':True,'messages':[]}));self.assertFalse(r['done_seen']);self.assertEqual(r['terminal_count'],0);self.assertEqual(r['usage_event_count'],0);self.assertIsNone(r['usage']);self.assertFalse(r['usage_complete'])
if __name__=='__main__':unittest.main()
