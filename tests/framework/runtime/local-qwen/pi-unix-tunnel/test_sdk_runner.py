import unittest,pathlib,importlib.util
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('runner',R/'run_sdk_mock.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class SDKGuard(unittest.TestCase):
 def test_complete_receipt_and_no_false_success(self):
  p={'CONNECT':1,'CONNECT_attempts':1,'POST':1,'sdk_status':400,'expectedMock400':True,'workers':{'proxy':0,'broker':0},'socket_absent':True,'errors':[]}
  self.assertEqual(m.classify(p,0),'SDK_CONNECT_Unix_mock_HTTP400')
  for key,value in [('sdk_status',None),('CONNECT_attempts',2),('POST',0),('socket_absent',False),('errors',['failure'])]:
   bad=dict(p);bad[key]=value;self.assertIsNone(m.classify(bad,0))
  self.assertIsNone(m.classify(p,1))
if __name__=='__main__':unittest.main()
