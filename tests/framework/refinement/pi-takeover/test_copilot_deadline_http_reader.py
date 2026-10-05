import unittest,time,pathlib,tempfile,threading,socketserver,http.server,importlib.util,json,hashlib
from copilot_deadline_http_reader import DeadlineHTTPReader
from copilot_bounded_chat_drain import drain_chat
from copilot_owned_issuance_guard import IssuanceGuard
from copilot_provider_stream_fixture import MODEL,final_stream
P=pathlib.Path(__file__).resolve().parent.parent/'copilot-native-local-route/mock-owned-cutoff-guard/stream_proxy.py';spec=importlib.util.spec_from_file_location('deadline_saved_proxy',P);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Tests(unittest.TestCase):
 def scope(self):return {'model':MODEL,'source_identity':'local-Unix-synthetic-fixture','request_id':'one-request','epoch':'one-epoch'}
 def socket_case(self,stall):
  with tempfile.TemporaryDirectory(prefix='solpi-deadliner-') as tmp:
   root=pathlib.Path(tmp);release=threading.Event();ready=threading.Event();errors=[];body=final_stream();first=body.index(b'\n\n')+2;stops=[]
   class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*a):pass
    def do_POST(self):
     try:
      self.rfile.read(int(self.headers['Content-Length']));self.send_response(200);self.send_header('Transfer-Encoding','chunked');self.send_header('Connection','close');self.end_headers()
      for index,part in enumerate([body[:first],body[first:]]):
       if index==1 and stall:ready.set();release.wait(2)
       self.wfile.write(('%x\r\n'%len(part)).encode()+part+b'\r\n');self.wfile.flush()
      self.wfile.write(b'0\r\n\r\n');self.wfile.flush();self.close_connection=True
     except (BrokenPipeError,ConnectionResetError):pass
     except Exception as e:errors.append(type(e).__name__)
   class Server(socketserver.UnixStreamServer):pass
   server=Server(str(root/'broker.sock'),Handler);thread=threading.Thread(target=server.serve_forever);thread.start();conn=module.UnixHTTPConnection(server.server_address,3)
   try:
    conn.connect();sock=conn.sock;conn.request('POST','/v1/chat/completions',b'{}');response=conn.getresponse();deadline=time.monotonic()+(.08 if stall else 2)
    reader=DeadlineHTTPReader(response,sock,deadline)
    def stop():stops.append('stop');release.set();return True
    guard=IssuanceGuard(1,stop,lambda r:None)
    def emit(b):
     if not stall:raise BrokenPipeError()
    start=time.monotonic();row=drain_chat(reader,emit,MODEL,deadline,guard,self.scope,root);elapsed=time.monotonic()-start
    self.assertLess(elapsed,1);self.assertEqual(row['fixed_deadline'],deadline);self.assertFalse(row['real_scored_eligible']);self.assertEqual(json.loads((root/'drain-row.json').read_text()),row);raw=(root/'provider-stream.sse').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['raw_receipt']['sha256'])
    if stall:
     self.assertTrue(ready.is_set());self.assertFalse(row['receipt']['receipt_complete']);self.assertIsNone(row['receipt']['eligible_usage']);self.assertTrue(row['drain_errors']);self.assertEqual(stops,['stop']);self.assertTrue(raw.startswith(body[:first]));self.assertLessEqual(len(raw),len(body))
    else:
     self.assertTrue(row['receipt']['receipt_complete']);self.assertEqual(raw,body);self.assertTrue(row['receipt']['consumer_detached']);self.assertEqual(stops,['stop']);self.assertEqual(row['receipt']['eligible_usage']['inclusive_gross_tokens'],18)
   finally:release.set();conn.close();server.shutdown();thread.join(3);server.server_close();self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
 def test_real_socket_stall_deadline_persists_unknown_partial(self):self.socket_case(True)
 def test_real_chunked_socket_detach_complete_tail(self):self.socket_case(False)
 def test_expired_deadline_no_read(self):
  class R:
   def isclosed(self):raise AssertionError('no read after deadline')
  reader=DeadlineHTTPReader(R(),None,1,now=lambda:2)
  with self.assertRaises(TimeoutError):reader(10)
 def test_remaining_cannot_extend_absolute_deadline(self):
  calls=[]
  class R:
   def isclosed(self):return False
   def read1(self,n):calls.append(n);return b'x'
  class S:
   def settimeout(self,n):calls.append(n)
  reader=DeadlineHTTPReader(R(),S(),5,now=lambda:4);self.assertEqual(reader(100),b'x');self.assertEqual(calls,[1,8192])
if __name__=='__main__':unittest.main()
