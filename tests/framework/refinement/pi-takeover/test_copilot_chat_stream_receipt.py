import unittest,json,tempfile,pathlib,threading,socketserver,http.server,importlib.util
from copilot_chat_stream_receipt import ChatReceipt
from copilot_provider_stream_fixture import MODEL,final_stream,tool_stream,frame,encode,FAKE_USAGE
class Tests(unittest.TestCase):
 def collect(self,body,emit=lambda b:None,eof=True):
  c=ChatReceipt(emit,MODEL)
  for b in body:c.feed(bytes([b]))
  return c.finish(eof)
 def test_fragmented_raw_and_cache_reasoning_subsets(self):
  b=final_stream();r=self.collect(b.replace(b'\n',b'\r\n'));self.assertTrue(r['receipt_complete']);self.assertEqual(r['eligible_usage']['inclusive_gross_tokens'],18);self.assertEqual(r['eligible_usage']['cache_read_tokens'],4);self.assertEqual(r['raw_bytes'],b.replace(b'\n',b'\r\n'))
 def test_detached_consumer_does_not_drop_upstream_tail(self):
  calls=[]
  def emit(b):calls.append(b);raise BrokenPipeError()
  r=self.collect(final_stream(),emit);self.assertTrue(r['receipt_complete']);self.assertTrue(r['consumer_detached']);self.assertEqual(len(calls),1);self.assertEqual(r['raw_bytes'],final_stream())
 def test_missing_usage_or_DONE_or_EOF_unavailable(self):
  for body,eof in [(encode([frame({'content':'ACK'}),frame({},'stop')]),True),(final_stream().replace(b'data: [DONE]\n\n',b''),True),(final_stream(),False)]:
   r=self.collect(body,eof=eof);self.assertFalse(r['receipt_complete']);self.assertIsNone(r['eligible_usage'])
 def test_duplicate_usage_and_post_DONE_rejected(self):
  u={'id':'synthetic-chat-1','object':'chat.completion.chunk','model':MODEL,'choices':[],'usage':FAKE_USAGE}
  b=encode([frame({},'stop'),u,u]);self.assertFalse(self.collect(b)['receipt_complete']);self.assertFalse(self.collect(final_stream()+b'data: [DONE]\n\n')['receipt_complete'])
 def test_bad_subset_and_bool_total_rejected(self):
  for mutate in [lambda u:u.update(total_tokens=True),lambda u:u['completion_tokens_details'].update(reasoning_tokens=7)]:
   u=json.loads(json.dumps(FAKE_USAGE));mutate(u);r=self.collect(encode([frame({},'stop'),{'id':'synthetic-chat-1','object':'chat.completion.chunk','model':MODEL,'choices':[],'usage':u}]));self.assertIsNone(r['eligible_usage'])
 def test_missing_optional_detail_not_zero(self):
  u={k:v for k,v in FAKE_USAGE.items() if not k.endswith('details')};r=self.collect(encode([frame({},'stop'),{'id':'synthetic-chat-1','object':'chat.completion.chunk','model':MODEL,'choices':[],'usage':u}]));self.assertTrue(r['receipt_complete']);self.assertIsNone(r['eligible_usage']['reasoning_tokens']);self.assertIsNone(r['eligible_usage']['cache_read_tokens'])
 def test_bounds_and_finalize_once(self):
  c=ChatReceipt(lambda b:None,MODEL,max_bytes=2)
  with self.assertRaises(ValueError):c.feed(b'123')
  c=ChatReceipt(lambda b:None,MODEL);c.feed(final_stream());c.finish(True)
  with self.assertRaises(ValueError):c.feed(b'')
 def test_overflow_after_valid_DONE_cannot_be_ignored(self):
  body=final_stream();c=ChatReceipt(lambda b:None,MODEL,max_bytes=len(body));c.feed(body)
  with self.assertRaises(ValueError):c.feed(b'overflow')
  r=c.finish(True);self.assertFalse(r['receipt_complete']);self.assertIn('collector_feed_error',r['reasons']);self.assertIsNone(r['eligible_usage'])
 def test_response_identity_mismatch_rejected(self):
  b=final_stream().replace(b'"id":"synthetic-chat-1"',b'"id":"other"',1);self.assertFalse(self.collect(b)['receipt_complete'])
 def test_real_Unix_HTTP_chunked_tail_after_consumer_detach(self):
  path=pathlib.Path(__file__).resolve().parent.parent/'copilot-native-local-route/mock-owned-cutoff-guard/stream_proxy.py';spec=importlib.util.spec_from_file_location('saved_chat_proxy',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  body=final_stream();errors=[]
  class Handler(http.server.BaseHTTPRequestHandler):
   protocol_version='HTTP/1.1'
   def log_message(self,*args):pass
   def do_POST(self):
    try:
     self.rfile.read(int(self.headers['Content-Length']));self.send_response(200);self.send_header('Transfer-Encoding','chunked');self.send_header('Connection','close');self.end_headers()
     for i in range(0,len(body),13):
      chunk=body[i:i+13];self.wfile.write(('%x\r\n'%len(chunk)).encode()+chunk+b'\r\n');self.wfile.flush()
     self.wfile.write(b'0\r\n\r\n');self.wfile.flush();self.close_connection=True
    except Exception as e:errors.append(type(e).__name__)
  with tempfile.TemporaryDirectory(prefix='solpi-chatr-') as tmp:
   class Server(socketserver.UnixStreamServer):pass
   s=Server(str(pathlib.Path(tmp)/'broker.sock'),Handler);t=threading.Thread(target=s.serve_forever);t.start();conn=module.UnixHTTPConnection(s.server_address,3)
   try:
    conn.request('POST','/v1/chat/completions',b'{}');response=conn.getresponse();self.assertIsNone(response.length)
    def detached(b):raise BrokenPipeError()
    c=ChatReceipt(detached,MODEL)
    while True:
     b=response.read1(7)
     if not b:break
     c.feed(b)
    r=c.finish(True);self.assertTrue(r['receipt_complete']);self.assertTrue(r['consumer_detached']);self.assertEqual(r['raw_bytes'],body);self.assertEqual(r['eligible_usage']['inclusive_gross_tokens'],18);self.assertEqual(errors,[])
   finally:conn.close();s.shutdown();t.join(3);s.server_close();self.assertFalse(t.is_alive())
if __name__=='__main__':unittest.main()
