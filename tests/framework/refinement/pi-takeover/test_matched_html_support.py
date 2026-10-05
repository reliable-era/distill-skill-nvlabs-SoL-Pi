import json,types,unittest
from matched_html_support import stopped_output_present,PanelSession
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def connection(self,status,missing_actor=False,changed_actor=False):
  rows=[(404,b'{}')] if missing_actor else [(200,json.dumps({'Id':'owned','Image':'image','State':{'Running':False}}).encode()),(status,b'')]
  if status==404 and not missing_actor:rows.append((200,json.dumps({'Id':'other' if changed_actor else 'owned','Image':'image','State':{'Running':False}}).encode()))
  class Conn:
   def request(self,*args):pass
   def getresponse(self):
    code,body=rows.pop(0);return types.SimpleNamespace(status=code,read=lambda *a:body)
   def close(self):pass
  return Conn
 def test_present(self):self.assertTrue(stopped_output_present('owned','image',self.connection(200)))
 def test_missing_output_valid(self):self.assertFalse(stopped_output_present('owned','image',self.connection(404)))
 def test_missing_actor_not_quality_failure(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.connection(404,missing_actor=True))
 def test_identity_race(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.connection(404,changed_actor=True))
 def test_unknown_status(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.connection(500))
 def test_numeric_view_does_not_modify_raw(self):
  raw=types.SimpleNamespace(records=[{'request':1,'actor':'a','usage_audit':{'error':'invalid_reasoning_subset'},'usage_complete':False}]);session=PanelSession(raw);session.prospective_records=[{'request':1,'actor':'a','accounting_view':{'derived_cost':{'provider_cost_complete':True,'gross_tokens':10},'correction_applied':True,'raw_provider_protocol_valid':False}}];r=session.accounting_rows('a');self.assertTrue(r[0]['usage_complete']);self.assertFalse(raw.records[0]['usage_complete']);self.assertFalse(r[0]['raw_provider_protocol_valid'])
 def test_unmatched_receipt(self):session=PanelSession(types.SimpleNamespace(records=[{'request':1,'actor':'a'}]));self.assertRaises(RuntimeError,session.accounting_rows,'a')
if __name__=='__main__':unittest.main()
