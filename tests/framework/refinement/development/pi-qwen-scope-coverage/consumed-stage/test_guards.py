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
 def test_request_uses_remaining_actor_budget(self):
  class Socket:
   def shutdown(self,*a):pass
  class Response:
   status=200
   def __init__(self):self.chunks=iter([b'data: {"choices":[],"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}}\n\ndata: [DONE]\n\n',b''])
   def read1(self,n):return next(self.chunks)
  seen=[]
  class Connection:
   def __init__(self,*a,**kw):seen.append(kw['timeout']);self.sock=Socket()
   def connect(self):pass
   def request(self,*a):pass
   def getresponse(self):return Response()
   def close(self):pass
  with tempfile.TemporaryDirectory() as tmp:
   session=S.Session(pathlib.Path(tmp)/'private',self.topology());session.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);session.deadline=260
   with mock.patch.object(S.time,'monotonic',return_value=100),mock.patch.object(S.threading,'Timer'):
    session.forward('/v1/chat/completions',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda b:None,Connection)
   self.assertEqual(seen,[150]);self.assertTrue(session.records[0]['usage_complete'])
 def test_idle_grace_bounded_and_logged(self):
  clock=[0];calls=[]
  def fake_load(path):
   calls.append(path);path.write_text('[{"num_reqs":1,"num_waiting_reqs":0}]');raise RuntimeError('busy')
  def sleep(seconds):clock[0]+=seconds
  with tempfile.TemporaryDirectory() as tmp,mock.patch.object(S,'fetch_idle',side_effect=fake_load),mock.patch.object(S.time,'monotonic',side_effect=lambda:clock[0]),mock.patch.object(S.time,'sleep',side_effect=sleep):
   with self.assertRaisesRegex(RuntimeError,'graceexhausted'):S.idle_grace(pathlib.Path(tmp)/'grace')
   self.assertLessEqual(len(calls),61);self.assertLessEqual(clock[0],300);self.assertEqual(json.loads((pathlib.Path(tmp)/'grace/grace.json').read_text())['models_during_grace'],0)
 def test_prepared_native_settings_full_budget(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);baseline=root/'baseline';baseline.mkdir();(baseline/'a.py').write_text('x=1');prompt=root/'prompt';prompt.write_text('task')
   private=W.prepare(root/'actor',8000,{'baseline':str(baseline),'prompt':str(prompt)},'none');agent=private/'home/.pi/agent';model=json.loads((agent/'models.json').read_text())['providers']['local-development']['models'][0];settings=json.loads((agent/'settings.json').read_text())
   self.assertEqual(model['contextWindow'],262144);self.assertEqual(model['maxTokens'],8192);self.assertFalse(model['reasoning']);self.assertEqual(settings['retry']['provider']['timeoutMs'],600000);self.assertEqual(settings['retry']['provider']['maxRetries'],0);self.assertFalse(settings['compaction']['enabled'])
 def test_topology_guard_uses_same_declared_grace(self):
  import ast
  source=(R/'run_screen.py').read_text();tree=ast.parse(source);calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='S']
  self.assertEqual(sum(n.func.attr=='idle_grace' for n in calls),2);self.assertFalse(any(n.func.attr=='fetch_idle' for n in calls));self.assertIn("idle-grace-before-topology",source)
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
