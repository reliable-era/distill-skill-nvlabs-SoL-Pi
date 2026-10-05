import unittest
from stream_session import FixtureSession,GuardFailure
from provider_fixture import MODEL,inspect_fixture
class Tests(unittest.TestCase):
 def req(self):return {'model':MODEL,'stream':True,'messages':[],'tools':[]}
 def test_final_without_tools(self):
  s=FixtureSession();self.assertEqual(inspect_fixture(s.response(self.req()))['finish'],'stop')
  with self.assertRaises(GuardFailure):s.response(self.req())
 def test_envelope_failclosed(self):
  q=self.req();q['model']='other'
  with self.assertRaises(GuardFailure):FixtureSession().response(q)
  q=self.req();q['messages']=None
  with self.assertRaises(GuardFailure):FixtureSession().response(q)
if __name__=='__main__':unittest.main()
