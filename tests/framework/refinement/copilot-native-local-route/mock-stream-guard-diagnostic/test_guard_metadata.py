import unittest,importlib.util,pathlib
from stream_session import FixtureSession,GuardFailure
from guard_metadata import describe
from provider_fixture import MODEL
class Guards(unittest.TestCase):
 def req(self):return {'model':MODEL,'stream':True,'messages':[],'tools':[{'type':'function','function':{'name':'report_intent','parameters':{'required':['intent'],'properties':{'intent':{'type':'string'}}}}}]}
 def test_only_structural_types_and_no_payload(self):
  q=self.req();q['messages']=[{'content':'PRIVATE_SENTINEL'}];q['api_key']='PRIVATE_SENTINEL';m=describe(q);self.assertTrue(all(type(v) in [bool,int] for v in m.values()));self.assertNotIn('PRIVATE_SENTINEL',str(m))
 def test_fixed_guard_codes(self):
  for mutate,code in [(lambda q:q.update(model='other'),'ENVELOPE_MODEL_OR_STREAM'),(lambda q:q.update(messages=None),'MESSAGES_NOT_LIST'),(lambda q:q.update(tools=[]),'INTENT_DECLARATION_COUNT'),(lambda q:q['tools'][0]['function']['parameters'].update(required=[]),'INTENT_SCHEMA_UNRECOGNIZED')]:
   q=self.req();mutate(q)
   with self.assertRaises(GuardFailure) as e:FixtureSession().response(q)
   self.assertEqual(e.exception.guard_code,code)
 def test_same_acceptance_and_wire_as_predecessor(self):
  p=pathlib.Path(__file__).parent.parent/'mock-successful-stream-prepared/stream_session.py';spec=importlib.util.spec_from_file_location('predecessor_guard',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  q=self.req();a=old.FixtureSession();b=FixtureSession();self.assertEqual(a.response(q),b.response(q));q['messages']=[{'role':'tool','tool_call_id':'synthetic-call-1','content':'ok'}];self.assertEqual(a.response(q),b.response(q))
  q=self.req();q['tools']=[]
  for cls in [old.FixtureSession,FixtureSession]:
   with self.assertRaises(ValueError):cls().response(q)
if __name__=='__main__':unittest.main()
