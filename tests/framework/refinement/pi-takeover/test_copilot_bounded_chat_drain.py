import unittest,tempfile,pathlib,json,hashlib
from copilot_bounded_chat_drain import drain_chat
from copilot_owned_issuance_guard import IssuanceGuard
from copilot_provider_stream_fixture import MODEL,final_stream,encode,frame
class Tests(unittest.TestCase):
 def scope(self):return {'model':MODEL,'request_id':'synthetic-request','source_identity':'owned-synthetic-fixture','epoch':'frozen-epoch'}
 def run_case(self,read,emit=lambda b:None,now=lambda:0,deadline=10,scope=None,stop=None,limit=2097152):
  scope=scope or self.scope();calls=[];g=IssuanceGuard(1,stop or (lambda:calls.append('stop') or True),lambda r:None)
  with tempfile.TemporaryDirectory() as tmp:
   r=drain_chat(read,emit,MODEL,deadline,g,lambda:scope,pathlib.Path(tmp),now=now,max_bytes=limit);self.assertEqual(json.loads((pathlib.Path(tmp)/'drain-row.json').read_text()),r);raw=(pathlib.Path(tmp)/'provider-stream.sse').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),r['raw_receipt']['sha256']);self.assertEqual((pathlib.Path(tmp)/'provider-stream.sse').stat().st_mode&0o777,0o600);return r,raw,calls
 def test_consumer_detach_stops_before_next_read_retains_tail(self):
  body=final_stream();split=body.index(b'\n\n')+2;chunks=[body[:split],body[split:],b''];calls=[]
  def stop():calls.append('stop');return True
  def read(remaining):
   if len(chunks)<3:self.assertEqual(calls,['stop'])
   return chunks.pop(0)
  def emit(b):raise BrokenPipeError()
  r,raw,_=self.run_case(read,emit,stop=stop);self.assertTrue(r['receipt']['receipt_complete']);self.assertEqual(raw,body);self.assertEqual(r['receipt']['eligible_usage']['inclusive_gross_tokens'],18);self.assertTrue(r['owned_stop']['owned_stop_verified']);self.assertFalse(r['real_scored_eligible'])
 def test_deadline_expired_no_read_and_no_extension(self):
  r,raw,calls=self.run_case(lambda n:(_ for _ in ()).throw(AssertionError()),now=lambda:10);self.assertEqual(r['read_calls'],0);self.assertEqual(raw,b'');self.assertEqual(calls,['stop']);self.assertEqual(r['fixed_deadline'],10);self.assertIsNone(r['receipt']['eligible_usage'])
 def test_late_read_bytes_preserved_but_usage_ineligible(self):
  clock=[0]
  def read(n):clock[0]=11;return final_stream()
  r,raw,calls=self.run_case(read,now=lambda:clock[0]);self.assertEqual(raw,final_stream());self.assertIsNone(r['receipt']['eligible_usage']);self.assertEqual(r['transport_bytes_read'],len(raw));self.assertEqual(calls,['stop'])
 def test_source_change_no_further_reads(self):
  scope=self.scope()
  def read(n):scope['source_identity']='different';return final_stream()
  r,raw,calls=self.run_case(read,scope=scope);self.assertEqual(r['read_calls'],1);self.assertFalse(r['receipt']['receipt_complete']);self.assertEqual(calls,['stop']);self.assertEqual(r['scope']['source_identity'],'owned-synthetic-fixture')
 def test_read_failure_and_unverified_stop_remain_unknown(self):
  def read(n):raise TimeoutError('socket timeout')
  r,raw,_=self.run_case(read,stop=lambda:False);self.assertIsNone(r['receipt']['eligible_usage']);self.assertFalse(r['owned_stop']['owned_stop_verified']);self.assertTrue(r['drain_errors'])
 def test_missing_usage_stops_even_with_complete_EOF(self):
  chunks=[encode([frame({'content':'ACK'}),frame({},'stop')]),b''];r,raw,calls=self.run_case(lambda n:chunks.pop(0));self.assertFalse(r['receipt']['receipt_complete']);self.assertEqual(calls,['stop'])
 def test_duplicate_destination_rejected_before_read(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'provider-stream.sse').write_bytes(b'old');g=IssuanceGuard(1,lambda:True,lambda r:None)
   with self.assertRaises(FileExistsError):drain_chat(lambda n:(_ for _ in ()).throw(AssertionError()),lambda b:None,MODEL,10,g,self.scope,root,now=lambda:0)
   self.assertEqual((root/'provider-stream.sse').read_bytes(),b'old')
 def test_byte_overflow_transport_count_not_silently_dropped(self):
  r,raw,calls=self.run_case(lambda n:final_stream(),limit=2);self.assertEqual(r['transport_bytes_read'],len(final_stream()));self.assertIsNone(r['receipt']['eligible_usage']);self.assertEqual(calls,['stop']);self.assertLessEqual(len(raw),2)
if __name__=='__main__':unittest.main()
