import pathlib,unittest,json
R=pathlib.Path(__file__).resolve().parent
class MockControls(unittest.TestCase):
 def test_connect_denial_receipt_and_limit(self):
  # Load handler declarations only; exclude all server/client execution.
  scope={};exec(compile((R/'mock_probe.py').read_text().split('\nmock=http.server.HTTPServer')[0],str(R/'mock_probe.py'),'exec'),scope)
  p=object.__new__(scope['Proxy']);p.path='provider.example:8000';status=[];p.send_error=status.append;p.do_CONNECT();p.do_CONNECT()
  self.assertEqual(status,[403,429]);self.assertEqual(scope['counts']['CONNECT'],2);self.assertEqual(scope['receipts'][0],{'method':'CONNECT','authority':'provider.example:8000','status':403});self.assertEqual(scope['counts']['mock_POST'],0)
 def test_distinct_success_and_connect_diagnosis(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('runner',R/'run_probe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  forwarded={'counts':{'proxy_POST':1,'mock_POST':1,'CONNECT':0},'sdk_status':400,'expectedMock400':True,'failure':None}
  self.assertEqual(m.classify(forwarded,0),'forwarded_mock_POST_HTTP400')
  wrong=dict(forwarded);wrong.pop('sdk_status');wrong['status']=400;self.assertIsNone(m.classify(wrong,0))
  denied={'counts':{'proxy_POST':0,'mock_POST':0,'CONNECT':1},'method_receipts':[{'method':'CONNECT','authority':'provider.example:8000','status':403}],'sdk_status':None,'expectedMock400':False,'sdk_exit':3,'failure':None}
  self.assertEqual(m.classify(denied,1),'CONNECT_denied_transport_diagnosis');self.assertIsNone(m.classify(denied,0));denied['counts']['CONNECT']=2;self.assertIsNone(m.classify(denied,1))
 def test_no_real_routes(self):
  s=(R/'probe.mjs').read_text();self.assertIn("baseURL:'http://provider.example:8000/v1'",s);self.assertIn('maxRetries:0',s);self.assertIn('error.cause',s)
if __name__=='__main__':unittest.main()
