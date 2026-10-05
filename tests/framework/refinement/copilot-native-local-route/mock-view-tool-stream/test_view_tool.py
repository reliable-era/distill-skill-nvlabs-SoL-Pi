import unittest
from stream_session import FixtureSession,GuardFailure,MARKER,PATH
from provider_fixture import MODEL,inspect_fixture
class ViewTests(unittest.TestCase):
 def req(self):return {'model':MODEL,'stream':True,'messages':[],'tools':[{'type':'function','function':{'name':'view','parameters':{'required':['path'],'properties':{'path':{'type':'string'}}}}}]}
 def test_exact_owned_path_and_marker(self):
  s=FixtureSession();q=self.req();v=inspect_fixture(s.response(q));self.assertEqual(v['tool_arguments'],{'path':PATH});q['messages']=[{'role':'tool','tool_call_id':'synthetic-call-1','content':MARKER}];self.assertEqual(inspect_fixture(s.response(q))['finish'],'stop');self.assertTrue(s.tool_result_seen)
 def test_no_other_tool_fallback(self):
  q=self.req();q['tools'][0]['function']['name']='bash'
  with self.assertRaises(GuardFailure):FixtureSession().response(q)
 def test_extra_required_argument_rejected(self):
  q=self.req();q['tools'][0]['function']['parameters']['required'].append('command')
  with self.assertRaises(GuardFailure):FixtureSession().response(q)
 def test_result_without_marker_rejected(self):
  s=FixtureSession();q=self.req();s.response(q);q['messages']=[{'role':'tool','tool_call_id':'synthetic-call-1','content':'error'}]
  with self.assertRaises(GuardFailure):s.response(q)
if __name__=='__main__':unittest.main()
