import json,types,unittest
from regex_output_presence import stopped_output_present
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def fake(self,status=200,changes=None,identity='owned',mounts=None):
  v={'Id':'owned','Image':'image','State':{'Running':False},'Mounts':mounts or []};v.update(changes or {});rows=[(200,json.dumps(v).encode()),(status,b'')]
  if status==404:rows.append((200,json.dumps({**v,'Id':identity}).encode()))
  requests=[]
  class Conn:
   def request(self,*a):requests.append(a)
   def getresponse(self):
    code,body=rows.pop(0);return types.SimpleNamespace(status=code,read=lambda *a:body)
   def close(self):pass
  return Conn,requests
 def test_present_exact_regexpath(self):
  c,requests=self.fake();self.assertTrue(stopped_output_present('owned','image',c));self.assertIn('regex.txt',requests[1][1]);self.assertNotIn('out.html',requests[1][1])
 def test_verified_absence(self):self.assertFalse(stopped_output_present('owned','image',self.fake(404)[0]))
 def test_changed_identity(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(404,identity='changed')[0])
 def test_wrong_image(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(changes={'Image':'other'})[0])
 def test_running(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(changes={'State':{'Running':True}})[0])
 def test_paused(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(changes={'State':{'Running':False,'Paused':True}})[0])
 def test_unknown(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(500)[0])
 def test_trusted_mount(self):self.assertRaises(CaptureError,stopped_output_present,'owned','image',self.fake(mounts=[{'Destination':'/tests'}])[0])
if __name__=='__main__':unittest.main()
