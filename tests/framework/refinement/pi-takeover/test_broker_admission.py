import http.client,json,pathlib,tempfile,threading,time,types,unittest
from prospective_broker_admission import admission,factory,AdmissionJournal,WAIT_CAP_SECONDS
from private_rejection_journal import RejectionJournal
R=pathlib.Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def handler(self,deadline=700,active='a',acquire=True,mutation=None):
  reject=[];statuses=[];args=[];released=[];session=types.SimpleNamespace(active=active,deadline=deadline)
  class Busy:
   def acquire(self,**kw):
    args.append(kw)
    if mutation:mutation(session)
    return acquire
   def release(self):released.append(True)
  h=types.SimpleNamespace(session=session,server=types.SimpleNamespace(busy=Busy()),send_error=statuses.append);return h,reject,statuses,args,released
 def test_idle_no_deadline_change(self):
  h,r,s,a,f=self.handler();self.assertTrue(admission(h,r.append,clock=lambda:100));self.assertEqual(a,[{'timeout':WAIT_CAP_SECONDS}]);self.assertEqual(h.session.deadline,700);self.assertEqual(f,[]);self.assertEqual(r,[])
 def test_expired_no_acquire(self):h,r,s,a,f=self.handler(deadline=109);self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(a,[]);self.assertEqual(r[0]['reason'],'actor_cleanup_reserve')
 def test_exact_cleanup_reserve(self):h,r,s,a,f=self.handler(deadline=110);self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(a,[])
 def test_missing_epoch(self):h,r,s,a,f=self.handler(active=None);self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(r[0]['reason'],'missing_actor_epoch')
 def test_busy_cap_no_forward(self):h,r,s,a,f=self.handler(acquire=False);self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(r[0]['reason'],'busy_wait_cap');self.assertFalse(r[0]['provider_forwarded']);self.assertEqual(r[0]['provider_POST'],0)
 def test_deadline_limits_wait(self):h,r,s,a,f=self.handler(deadline=110.25,acquire=False);admission(h,r.append,clock=lambda:100);self.assertEqual(a,[{'timeout':.25}])
 def test_epoch_changed_release_once(self):h,r,s,a,f=self.handler(mutation=lambda s:setattr(s,'active','b'));self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(f,[True]);self.assertEqual(r[0]['reason'],'actor_epoch_changed')
 def test_same_actor_new_deadline_is_different_epoch(self):h,r,s,a,f=self.handler(mutation=lambda s:setattr(s,'deadline',701));self.assertFalse(admission(h,r.append,clock=lambda:100));self.assertEqual(f,[True])
 def test_actual_actor_deadline_bound(self):
  h,r,s,a,f=self.handler(deadline=time.monotonic()+10.03);h.server.busy=threading.Semaphore(0);start=time.monotonic();self.assertFalse(admission(h,r.append));self.assertLess(time.monotonic()-start,.2);self.assertEqual(r[0]['reason'],'actor_cleanup_reserve')
 def test_journal_private_metadata_only_and_cap(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'journal.json';j=AdmissionJournal(path);record={'reason':'busy_wait_cap','status':429,'provider_forwarded':False,'provider_POST':0,'wait_seconds':0.01}
   for _ in range(128):j(record)
   self.assertRaises(ValueError,j,record);self.assertEqual(path.stat().st_mode&0o777,0o600);x=json.loads(path.read_text());self.assertEqual(len(x['records']),128);self.assertEqual(set(x['records'][0]),set(record));self.assertRaises(ValueError,j,{**record,'payload':'SECRET'})
 def test_source_fail_closed(self):
  p=R.parent/'development/pi-takeover-qwen-source-backed-16k/runtime/server.py';self.assertRaises(ValueError,factory,p,'0'*64,lambda r:None,lambda r:None)
 def test_8MiB_guard_still_precedes_admission(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);byte=RejectionJournal(root/'byte.json');denied=AdmissionJournal(root/'admit.json');plan=json.loads((R/'16k-regex-plan.json').read_text());m=factory(R.parent/'development/pi-takeover-qwen-source-backed-16k/runtime/server.py',plan['runtime_hashes']['server.py'],byte,denied)
   class Fake:
    active='fake';deadline=time.monotonic()+600;calls=0
    def forward(self,*args):self.calls+=1;raise AssertionError('oversizedbodyforwarded')
   f=Fake();h=type('TestHandler',(m.PostHandler,),{'session':f});server=m.OwnedServer(('127.0.0.1',0),h);threading.Thread(target=server.serve_forever,daemon=True).start();c=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=2)
   try:c.request('POST','/v1/responses',b'',{'Content-Length':'8388609'});response=c.getresponse();response.read();self.assertEqual(response.status,413);self.assertEqual(f.calls,0);self.assertEqual(denied.records,[]);self.assertEqual(byte.records[0]['declared_body_bytes'],8388609)
   finally:c.close();server.cleanup()
if __name__=='__main__':unittest.main()
