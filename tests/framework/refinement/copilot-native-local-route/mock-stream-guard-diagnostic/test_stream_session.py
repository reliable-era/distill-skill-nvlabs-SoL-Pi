import unittest
from stream_session import FixtureSession
from provider_fixture import inspect_fixture,MODEL
class SessionTests(unittest.TestCase):
 def request(self):return {'model':MODEL,'stream':True,'messages':[{'role':'user','content':'fixture'}],'tools':[{'type':'function','function':{'name':'report_intent','parameters':{'required':['intent'],'properties':{'intent':{'type':'string'}}}}}]}
 def test_two_phase_followup_required(self):
  s=FixtureSession();self.assertEqual(inspect_fixture(s.response(self.request()))['finish'],'tool_calls')
  q=self.request();q['messages'].append({'role':'tool','tool_call_id':'synthetic-call-1','content':'intent reported'})
  self.assertEqual(inspect_fixture(s.response(q))['finish'],'stop');self.assertTrue(s.tool_result_seen)
  with self.assertRaises(ValueError):s.response(q)
 def test_no_tool_fallback(self):
  q=self.request();q['tools'][0]['function']['name']='bash'
  with self.assertRaises(ValueError):FixtureSession().response(q)
 def test_missing_followup_rejected(self):
  s=FixtureSession();s.response(self.request())
  with self.assertRaises(ValueError):s.response(self.request())
 def test_unknown_model_and_schema_rejected(self):
  q=self.request();q['model']='other-model'
  with self.assertRaises(ValueError):FixtureSession().response(q)
  q=self.request();q['tools'][0]['function']['parameters']['required']=['command']
  with self.assertRaises(ValueError):FixtureSession().response(q)
if __name__=='__main__':unittest.main()
