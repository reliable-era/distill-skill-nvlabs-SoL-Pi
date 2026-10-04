"""Offline Pi screen controls; no Docker/provider calls."""
import unittest,pathlib,sys,tempfile,json,importlib.util,unittest.mock as mock
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'runtime'));sys.path.insert(0,str(R))
import session as S,wrapper as W,run_screen as Q
class Guards(unittest.TestCase):
 def topology(self):return {'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'}
 def test_caps(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',self.topology())
   for i in range(12):s.begin(str(i),[{'num_reqs':0,'num_waiting_reqs':0}]);s.finish(True)
   with self.assertRaises(RuntimeError):s.begin('13',[{'num_reqs':0,'num_waiting_reqs':0}])
 def test_POST_before_upstream(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',self.topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.per_actor['a']=16
   with self.assertRaises(RuntimeError):s.forward('/v1/chat/completions',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda *a:None,connect=lambda *a,**k:self.fail('called'))
 def test_native_usage_dedup(self):
  message={'id':'one','role':'assistant','usage':{'totalTokens':5},'stopReason':'stop'};events=[{'type':'message_end','message':message}]*2+[{'type':'agent_end'}];req=[{'usage_audit':{'gross_usage_complete':True,'gross_tokens':5}}]
  result=W.reconcile_native(events,req);self.assertTrue(result['complete']);self.assertEqual(result['duplicates'],1);message['usage']['totalTokens']=0;self.assertFalse(W.reconcile_native(events,req)['complete'])
 def test_tool_outputs_dedup(self):
  events=[{'type':'tool_execution_start','toolCallId':'x','toolName':'read'},{'type':'tool_execution_end','toolCallId':'x','result':{'content':[{'type':'text','text':'abc'}]}}];result=W.trace_metrics(events+[events[-1]]);self.assertEqual(result['read_output_bytes'],3);self.assertEqual(result['duplicate_tool_ends'],1)
 def test_missing_auth_and_matched_inputs(self):
  p=json.loads((R/'plan.json').read_text());W.validate_inputs(p)
  with self.assertRaises(FileNotFoundError):Q.validate(p,Q.sha(R/'plan.json'))
 def test_shared_grade_certificate_full_validation(self):
  p=json.loads((R/'plan.json').read_text());digest=Q.sha(R/'plan.json');original=pathlib.Path.read_text
  def read(path,*a,**kw):
   if path==R/'execution-authorization.json':return json.dumps({'plan_sha256':digest,'maximum_starts':12})
   return original(path,*a,**kw)
  with mock.patch.object(pathlib.Path,'read_text',read):Q.validate(p,digest)
 def test_explicit_native_proxy_and_noambient(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'prompt.txt').write_text('task');args=W.argv('pi',8000,root);self.assertEqual(args[:3],['/opt/eval-node','--use-env-proxy','/opt/eval-pi/dist/bundle/cli.js']);self.assertIn('--no-skills',args);self.assertIn('--no-extensions',args);self.assertIn('e0e46d3a',W.shell(args)[2])
if __name__=='__main__':unittest.main()
