"""Offline tests only; no Docker/provider execution."""
import unittest,pathlib,sys,tempfile,json,unittest.mock as mock
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'runtime'));sys.path.insert(0,str(R))
import session as S,wrapper as W,run_screen as Q
class Guards(unittest.TestCase):
 def topology(self):return {'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'owned'}
 def test_start_cap_no_replacement(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',self.topology())
   for i in range(4):s.begin(str(i),[{'num_reqs':0,'num_waiting_reqs':0}]);s.finish(True)
   with self.assertRaises(RuntimeError):s.begin('13',[{'num_reqs':0,'num_waiting_reqs':0}])
 def test_busy_and_aux_stop(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',self.topology())
   with self.assertRaises(RuntimeError):s.begin('a',[{'num_reqs':1,'num_waiting_reqs':0}])
   s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}])
   with self.assertRaises(RuntimeError):s.finish(True,['subagent'])
 def test_cap_before_upstream(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',self.topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.per_actor['a']=16
   with self.assertRaises(RuntimeError):s.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda *a:None,connect=lambda *a,**k:self.fail('upstream called'))
 def test_source_change_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'x';p.write_text('old');plan={'schedule':[{'family':f,'arm':a} for f in ['t','g','s'] for a in W.ARMS],'tasks':dict.fromkeys(['t','g','s']),'external_trees':{},'external_files':{str(p):W.sha(p)}};W.validate_inputs(plan);p.write_text('new')
   with self.assertRaises(RuntimeError):W.validate_inputs(plan)
 def test_missing_authorization_fails_offline(self):
  plan=json.loads((R/'plan.json').read_text())
  original=pathlib.Path.read_text
  def read(path,*args,**kwargs):
   if path==R/'execution-authorization.json':raise FileNotFoundError('offline missing authorization')
   return original(path,*args,**kwargs)
  with mock.patch.object(pathlib.Path,'read_text',read),self.assertRaises(FileNotFoundError):Q.validate(plan,Q.sha(R/'plan.json'))
 def test_exact_absence(self):
  with mock.patch.object(Q.subprocess,'run',return_value=type('Z',(),{'returncode':1,'stderr':'Error: No such object: different'})()):self.assertFalse(Q.absent('container','owned'))
 def test_shell_no_auth_and_binary_pin(self):
  argv=W.argv('codex',8000,type('P',(),{})()) if False else ['codex','exec']
  command=W.shell(argv);self.assertIn('12eb3e81',command[2]);self.assertNotIn('auth.json',str(command))

class Accounting(unittest.TestCase):
 def test_missing_native_is_incomplete(self):self.assertFalse(W.reconcile_native([],[])['complete'])
 def test_mismatch_not_savings(self):
  records=[{'usage_audit':{'gross_usage_complete':True,'input_tokens_inclusive':10,'output_tokens_inclusive':2}}]
  self.assertFalse(W.reconcile_native([{'type':'turn.completed','usage':{'input_tokens':9,'output_tokens':2}}],records)['complete'])
 def test_inclusive_cache_not_added(self):
  records=[{'usage_audit':{'gross_usage_complete':True,'input_tokens_inclusive':10,'output_tokens_inclusive':2,'cache_read_tokens_reported':8}}]
  self.assertTrue(W.reconcile_native([{'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':2,'cached_input_tokens':8}}],records)['complete'])

class OfficialChecks(unittest.TestCase):
 def test_expected_coverage_missing_rejected(self):
  from grade_validation import validate_report
  entry={'resolved':True,'patch_successfully_applied':True,'tests_status':{'FAIL_TO_PASS':{'success':['x'],'failure':[]},'PASS_TO_PASS':{'success':[],'failure':[]}}}
  with self.assertRaises(RuntimeError):validate_report(entry,{'FAIL_TO_PASS':['x'],'PASS_TO_PASS':['y']},{'x':'PASSED'},True,False,True)
 def test_pass_requires_actual_collection_and_application(self):
  from grade_validation import validate_report
  entry={'resolved':True,'patch_successfully_applied':True,'tests_status':{'FAIL_TO_PASS':{'success':['x'],'failure':[]},'PASS_TO_PASS':{'success':['y'],'failure':[]}}}
  refs={'FAIL_TO_PASS':['x'],'PASS_TO_PASS':['y']}
  with self.assertRaises(RuntimeError):validate_report(entry,refs,{},True,False,True)
  with self.assertRaises(RuntimeError):validate_report(entry,refs,{'x':'PASSED','y':'PASSED'},True,False,False)
  self.assertEqual(validate_report(entry,refs,{'x':'PASSED','y':'PASSED'},True,False,True)['PASS_TO_PASS']['success'],1)
 def test_worker_timeout_exact_owned_cleanup(self):
  import signal,subprocess
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'work').mkdir();process=mock.Mock(pid=12345);process.wait.side_effect=[subprocess.TimeoutExpired('worker',300),0];process.poll.return_value=0
   identifier=type('U',(),{'hex':'fixed'})();probe=type('Z',(),{'returncode':1,'stderr':'Error: No such object: sweb.eval.pallets__flask-5014.qwendev-fixed'})()
   with mock.patch.object(W.uuid,'uuid4',return_value=identifier),mock.patch.object(W.subprocess,'Popen',return_value=process),mock.patch.object(W.subprocess,'run',return_value=probe) as calls,mock.patch.object(W.os,'killpg') as kill:
    result=W.grade(root,{'family':'swe','python':'mock'})
    kill.assert_called_once_with(12345,signal.SIGTERM);self.assertTrue(result['grader_absence_verified']);self.assertEqual(calls.call_args_list[0].args[0],['docker','rm','-f','sweb.eval.pallets__flask-5014.qwendev-fixed'])

class DescriptiveTrace(unittest.TestCase):
 def test_item_dedup_and_return_bytes(self):
  item={'id':'same','type':'command_execution','command':'cat a && cat b','exit_code':0,'aggregated_output':'abc'}
  result=W.trace_metrics([{'type':'item.completed','item':item},{'type':'item.completed','item':item}])
  self.assertEqual(result['completed_command_calls'],1);self.assertEqual(result['read_like_command_calls'],1);self.assertEqual(result['command_return_bytes'],3);self.assertEqual(result['duplicate_completed_ids'],1)

class NegativeControls(unittest.TestCase):
 def grade(self):return {'solved':False,'infrastructure_error':None,'test_coverage':{'test_output_found':True,'official_resolved':False,'FAIL_TO_PASS':{'expected':2,'parsed_expected':2,'success':1,'failure':1},'PASS_TO_PASS':{'expected':3,'parsed_expected':3,'success':3,'failure':0}}}
 def test_uncollected_baseline_rejected(self):
  from grade_validation import validate_swe_control
  grade=self.grade();grade['test_coverage']['FAIL_TO_PASS']['parsed_expected']=0
  with self.assertRaises(RuntimeError):validate_swe_control(grade,'baseline')
 def test_forced_false_allpassing_baseline_rejected(self):
  from grade_validation import validate_swe_control
  grade=self.grade();grade['test_coverage']['FAIL_TO_PASS'].update(success=2,failure=0);grade['test_coverage']['official_resolved']=True
  with self.assertRaises(RuntimeError):validate_swe_control(grade,'baseline')
 def test_original_negative_and_gold_positive_controls(self):
  from grade_validation import validate_swe_control
  grade=self.grade();self.assertTrue(validate_swe_control(grade,'baseline'));grade['solved']=True;grade['test_coverage']['official_resolved']=True;grade['test_coverage']['FAIL_TO_PASS'].update(success=2,failure=0);self.assertTrue(validate_swe_control(grade,'gold'))

class TerminalValidation(unittest.TestCase):
 def test_permission_exit1_not_quality_failure(self):
  from grade_validation import validate_terminal_result
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp);(p/'stdout').write_text('PermissionError: Permission denied');(p/'stderr').write_text('')
   with self.assertRaises(RuntimeError):validate_terminal_result(p,1,3)
 def test_collection_exit2_rejected(self):
  from grade_validation import validate_terminal_result
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(RuntimeError):validate_terminal_result(pathlib.Path(tmp),2,3)
 def test_three_original_events_required_for_negative(self):
  from grade_validation import validate_terminal_result
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp);(p/'stdout').write_text('');(p/'stderr').write_text('');(p/'ctrf.json').write_text(json.dumps({'results':{'tests':[{'status':'passed'},{'status':'failed'},{'status':'passed'}]}}))
   self.assertTrue(validate_terminal_result(p,1,3)['functional_failure'])
   with self.assertRaises(RuntimeError):validate_terminal_result(p,1,4)
   (p/'ctrf.json').write_text(json.dumps({'results':{'tests':[{'status':'passed'}]*3}}))
   with self.assertRaises(RuntimeError):validate_terminal_result(p,1,3)

class RepairedDeadlines(unittest.TestCase):
 def test_remaining_actor_budget_not40(self):
  self.assertEqual(S.request_seconds(600,0),590)
  self.assertEqual(S.request_seconds(600,100),490)
  self.assertEqual(S.request_seconds(600,589),1)
  with self.assertRaises(RuntimeError):S.request_seconds(600,590)
 def test_idle_raw_saved_before_guard(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'idle.json';times=[0]
   def fetch(deadline):return {'status':200,'error':None,'raw_body':'metadata','load':[{'num_reqs':0,'num_waiting_reqs':0}]}
   original=S.idle
   def guard(load):self.assertTrue(p.exists());self.assertEqual(json.loads(p.read_text())['observations'][0]['raw_body'],'metadata');return original(load)
   with mock.patch.object(S,'idle',side_effect=guard):S.wait_idle(p,fetch=fetch,clock=lambda:times[0],sleep=lambda n:None)
   self.assertTrue(json.loads(p.read_text())['eligible'])
 def test_busy_grace_bounded_no_unknown_cancellation(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'idle.json';t=[0];calls=[]
   def fetch(deadline):calls.append(deadline);return {'status':200,'error':None,'raw_body':'busy','load':[{'num_reqs':1,'num_waiting_reqs':2}]}
   def sleep(n):t[0]+=n
   with self.assertRaises(RuntimeError):S.wait_idle(p,fetch=fetch,clock=lambda:t[0],sleep=sleep)
   evidence=json.loads(p.read_text());self.assertLessEqual(len(calls),61);self.assertLessEqual(t[0],300);self.assertFalse(evidence['eligible']);self.assertTrue(evidence['unknown_jobs_untouched'])
 def test_busy_then_idle_consumes_no_actor_budget(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'idle.json';t=[0];loads=iter([1,1,0])
   def fetch(deadline):return {'status':200,'error':None,'raw_body':'raw','load':[{'num_reqs':next(loads),'num_waiting_reqs':0}]}
   result=S.wait_idle(p,fetch=fetch,clock=lambda:t[0],sleep=lambda n:t.__setitem__(0,t[0]+n));self.assertTrue(S.idle(result));self.assertEqual(t[0],10)

class ActualDeadlineIntegration(unittest.TestCase):
 def test_forward_uses_remaining_reserve_deadline(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=S.Session(pathlib.Path(tmp)/'transport',Guards().topology());s.begin('a',[{'num_reqs':0,'num_waiting_reqs':0}]);s.deadline=600;received=[]
   class FakeConnection:
    sock=None
    def connect(self):raise RuntimeError('offline stop')
    def close(self):pass
   def connect(host,port,timeout):received.append(timeout);return FakeConnection()
   with mock.patch.object(S.time,'monotonic',return_value=100):
    with self.assertRaises(RuntimeError):s.forward('/v1/responses',b'{"model":"Qwen3.8-27B-FP8","stream":true}',lambda x:None,connect=connect)
   self.assertEqual(received,[490]);self.assertEqual(s.posts,1);self.assertFalse(s.records[0]['usage_complete'])
 def test_grace_rejects_malformed_zero_lookalike(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=[0]
   def fetch(deadline):return {'status':200,'error':None,'raw_body':'bad','load':[{'num_reqs':False,'num_waiting_reqs':0}]}
   with self.assertRaises(RuntimeError):S.wait_idle(pathlib.Path(tmp)/'idle.json',fetch=fetch,clock=lambda:t[0],sleep=lambda n:t.__setitem__(0,t[0]+n))

if __name__=='__main__':unittest.main()
