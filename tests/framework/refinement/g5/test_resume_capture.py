"""Offline real-Docker resumed-path lifecycle,zero provider calls.
Set G5_DOCKER_CAPTURE_IMAGE to an already-owned SWE image;never pulls images.
"""
import hashlib,json,os,pathlib,subprocess,tempfile,time,unittest
from unittest.mock import patch
import run_swe_cell as runner
from transport import Broker
from five_xx import budget_attempts
IMAGE=os.environ.get('G5_DOCKER_CAPTURE_IMAGE')
class Budget(unittest.TestCase):
 def test_shared_safety_stop_prevents_any_provider_call(self):
  from transport import MODEL
  with tempfile.TemporaryDirectory(prefix='g5-stop-test-') as tmp:
   t=pathlib.Path(tmp);stop=t/'ADMISSIONS-STOP';stop.write_text('capture failure');b=Broker(t/'transport',time.monotonic()+60,'none',admission_stop_file=stop);statuses=[]
   class Client:
    def send_error(self,status):statuses.append(status)
   b.forward('/v1/responses',json.dumps(dict(model=MODEL,stream=True)).encode(),Client(),connect=lambda *a,**kw:self.fail('No provider connection permitted'))
   self.assertEqual(statuses,[409]);self.assertEqual(b.posts,0);self.assertEqual(b.denials[0]['reason'],'admission_safety_stop')
 def test_harness_rows_keep_cost_but_not_five_attempt_budget(self):
  rows=[dict(harness_failure=False,known_tokens_lower_bound=10),dict(harness_failure=True,known_tokens_lower_bound=25),dict(harness_failure=False,known_tokens_lower_bound=30)];self.assertEqual(budget_attempts(rows),2);self.assertEqual(sum(r['known_tokens_lower_bound'] for r in rows),65)
@unittest.skipUnless(IMAGE,'explicit already-owned offline Docker image required')
class ResumedCapture(unittest.TestCase):
 def exercise(self,fail_capture=False,fail_copy=False,empty=False):
  with tempfile.TemporaryDirectory(prefix='g5-resume-capture-e2e-') as tmp:
   t=pathlib.Path(tmp);baseline=t/'source';w=baseline/'workspace';w.mkdir(parents=True);(w/'probe.py').write_text('before\n')
   def git(*args):return subprocess.check_output(['git','-C',str(w),*args]).decode().strip()
   git('init','-q');git('config','user.email','offline@example.invalid');git('config','user.name','Offline');git('add','.');git('commit','-qm','snapshot');head=git('rev-parse','HEAD');(baseline/'prompt.txt').write_text('Offline lifecycle fixture,no model.');(baseline/'manifest.json').write_text(json.dumps(dict(prepared=True,gold_in_actor=False,prompt_sha256=hashlib.sha256((baseline/'prompt.txt').read_bytes()).hexdigest(),snapshot_commit=head,base_commit=head,source_tree=['probe.py'])))
   grader=t/'offline_grader.py';grader.write_text('import sys,pathlib,json\nr=pathlib.Path(sys.argv[1]);r.mkdir();(r/"grade-result.json").write_text(json.dumps(dict(solved=True,grade_valid=True,owned_containers_absent=True)))\n');stop=t/'ADMISSIONS-STOP';cell=dict(cell_id='g5-offline-Both',task='offline',arm='Both',part='C',round=1);root=t/'models-resume-v2'/'offline'/'g5-offline-Both-a4';root.parent.mkdir(parents=True);plan=dict(prepared_tasks={'offline':str(baseline)},arm_skills={'Both':[]},images={'offline':IMAGE},wheelhouse=str(t),admission_stop_file=str(stop),grader_python=__import__('sys').executable,grader_plan=str(t/'unused.json'));events=[];brokers=[]
   class CheckedBroker(Broker):
    def start(b):super().start();brokers.append(b)
    def close(b):
     if fail_capture or fail_copy:self.assertTrue(stop.exists(),'Shared stop must precede actor/bind cleanup')
     self.assertTrue(runner.absent(json.loads((root/'actor-inspect.json').read_text())['Name'].lstrip('/')));self.assertTrue(b.short_socket_dir.exists());events.append('actor_absent_before_broker_cleanup');super().close()
   from capture_patch import capture as real_capture
   def checked_capture(*args):
    self.assertTrue(brokers[0].short_socket_dir.exists());events.append('capture_with_live_bind_source')
    if fail_capture:raise RuntimeError('injected capture failure after successful native exit')
    return real_capture(*args)
   real_run=subprocess.run
   def run(args,**kw):
    if fail_copy and args[:2]==['docker','cp'] and args[-1]=='-':
     kw['stderr'].write(b'injected docker cp mount-source error\n');kw['stderr'].flush();raise subprocess.CalledProcessError(1,args)
    if len(args)>1 and args[1]==str(runner.H/'grade_swe.py'):args=[args[0],str(grader),*args[2:]];events.append('grade_with_live_bind_source');self.assertTrue(brokers[0].short_socket_dir.exists())
    return real_run(args,**kw)
   with patch.object(runner,'authorized',return_value=True),patch.object(runner,'Broker',CheckedBroker),patch.object(runner,'argv',return_value=['sh','-c',('' if empty else 'printf "after\\n" > /testbed/probe.py; ')+'mkdir -p /testbed/__pycache__; printf bytecode > /testbed/__pycache__/probe.cpython-36.pyc; printf \'{"type":"turn.completed"}\\n\'']),patch('capture_patch.capture',side_effect=checked_capture),patch.object(runner.subprocess,'run',side_effect=run):
    row=runner.attempt(cell,4,root,plan,dict(cells=[cell['cell_id']]),lambda *a:dict(occupied_slots_after_admission=1))
   self.assertEqual(row['native_exit'],0);self.assertTrue(row['actor_absent']);self.assertTrue(row['owned_cleanup_verified']);self.assertEqual(row['requests'],0);self.assertEqual((root/'capture.stderr').read_bytes(),b'injected docker cp mount-source error\n' if fail_copy else b'');self.assertIsNone(brokers[0].short_socket_dir)
   if fail_copy:self.assertTrue(stop.exists());self.assertTrue(row['safety_stop']);self.assertEqual(events,['actor_absent_before_broker_cleanup']);self.assertEqual(row['error']['type'],'CalledProcessError')
   elif fail_capture:self.assertTrue(stop.exists());self.assertTrue(row['safety_stop']);self.assertTrue(row['harness_failure']);self.assertEqual(events,['capture_with_live_bind_source','actor_absent_before_broker_cleanup'])
   elif empty:self.assertIsNone(row['error']);self.assertTrue(row['grade_valid']);self.assertFalse(row['solved']);self.assertFalse(row['grader_invoked']);self.assertEqual((root/'model.patch').read_bytes(),b'');self.assertEqual(events,['capture_with_live_bind_source','actor_absent_before_broker_cleanup'])
   else:self.assertIsNone(row['error']);self.assertTrue(row['grade_valid']);self.assertTrue(row['solved']);self.assertEqual((root/'delta-replay/probe.py').read_text(),'after\n');self.assertNotIn(b'__pycache__',(root/'model.patch').read_bytes());self.assertIn(b'__pycache__',(root/'model.raw.patch').read_bytes());self.assertEqual(events,['capture_with_live_bind_source','grade_with_live_bind_source','actor_absent_before_broker_cleanup'])
 def test_resumed_attempt_through_capture_grade_actor_removal_socket_cleanup(self):self.exercise()
 def test_native_success_capture_failure_sets_shared_stop_before_cleanup(self):self.exercise(True)
 def test_docker_cp_stderr_retained_and_safety_stop(self):self.exercise(fail_copy=True)
 def test_empty_source_projection_is_valid_unsolved_without_grader(self):self.exercise(empty=True)
if __name__=='__main__':unittest.main()
