"""Owned localhost mocks only, never connects to real provider."""
import importlib.util,pathlib,threading,http.server,http.client,time,unittest
R=pathlib.Path(__file__).resolve().parent
def load(n):
 s=importlib.util.spec_from_file_location(n,R/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
B=load('server');P=load('stream_proxy')
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  self.rfile.read(int(self.headers['Content-Length']));self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
  for chunk in [b'data: {"usa',b'ge":{"output_tokens":2}}\n\n',b'data: [DONE]\n\n']:
   self.wfile.write(chunk);self.wfile.flush();time.sleep(.02)
class Live(unittest.TestCase):
 def test_actual_proxy_stream_and_cleanup(self):
  upstream=B.OwnedServer(('127.0.0.1',0),Mock);port=upstream.server_address[1]
  H=type('Proxy',(P.StreamingProxy,),{'authority':'provider.example:'+str(port),'broker_host':'127.0.0.1','broker_port':port})
  proxy=B.OwnedServer(('127.0.0.1',0),H)
  for server in [upstream,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   c=http.client.HTTPConnection('127.0.0.1',proxy.server_address[1],timeout=2);c.request('POST','http://provider.example:'+str(port)+'/v1/responses',b'{}');z=c.getresponse();self.assertEqual(z.getheader('Content-Type'),'text/event-stream');body=z.read();self.assertIn(b'"output_tokens":2',body);self.assertTrue(body.endswith(b'data: [DONE]\n\n'));c.close()
   c=http.client.HTTPConnection('127.0.0.1',proxy.server_address[1],timeout=2);c.request('POST','http://blocked.example/v1/responses',b'{}');self.assertEqual(c.getresponse().status,403);c.close()
  finally:
   proxy.cleanup();upstream.cleanup();self.assertEqual(proxy.workers,0);self.assertEqual(upstream.workers,0)
 def test_unix_broker_proxy_stream(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   path=str(pathlib.Path(tmp)/'broker.sock');upstream=B.OwnedUnixServer(path,Mock)
   H=type('UnixProxy',(P.StreamingProxy,),{'authority':'provider.example:8000','unix_socket':path})
   proxy=B.OwnedServer(('127.0.0.1',0),H)
   for server in [upstream,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
   try:
    c=http.client.HTTPConnection('127.0.0.1',proxy.server_address[1],timeout=2);c.request('POST','http://provider.example:8000/v1/chat/completions',b'{}');z=c.getresponse();self.assertEqual(z.status,200);self.assertIn(b'[DONE]',z.read());c.close()
   finally:proxy.cleanup();upstream.cleanup();self.assertEqual(upstream.workers,0)
 def test_owned_upstream_abort_drains_workers(self):
  import tempfile,socket,json
  S=load('session');T={'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'mock'}
  entered=threading.Event();left,right=socket.socketpair()
  class Stalled:
   status=200
   def read1(self,n):entered.set();return left.recv(n)
  class Connection:
   def __init__(self,*a,**kw):self.sock=left
   def connect(self):pass
   def request(self,*a):pass
   def getresponse(self):return Stalled()
   def close(self):left.close()
  with tempfile.TemporaryDirectory() as tmp:
   session=S.Session(pathlib.Path(tmp)/'private',T);session.begin('codex',[{'num_reqs':0,'num_waiting_reqs':0}])
   class Adapter:
    def forward(self,path,body,emit):return session.forward(path,body,emit,Connection)
   H=type('OwnedStall',(B.PostHandler,),{'session':Adapter()});server=B.OwnedServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
   client=http.client.HTTPConnection('127.0.0.1',server.server_address[1],timeout=2)
   def request():
    try:client.request('POST','/v1/responses',json.dumps({'model':'Qwen3.8-27B-FP8','stream':True}));client.getresponse().read()
    except OSError:pass
   worker=threading.Thread(target=request);worker.start()
   try:
    self.assertTrue(entered.wait(1));start=time.monotonic();self.assertEqual(session.abort_owned_connections(),1);server.cleanup();worker.join(1);self.assertEqual(server.workers,0);self.assertLess(time.monotonic()-start,3);self.assertEqual(len(session.connections),0)
   finally:client.close();right.close()
 def test_real_http10_detached_body_abort(self):
  import tempfile,json
  S=load('session');T={'verified':True,'image_id':S.IMAGE,'actor_internal':True,'unix_proxy_only':True,'ipv6':False,'actor_gateway_empty':True,'proxy_attachments_verified':True,'actor_network':'mock'}
  entered=threading.Event();release=threading.Event()
  class Stall(http.server.BaseHTTPRequestHandler):
   protocol_version='HTTP/1.0'
   def log_message(self,*a):pass
   def do_POST(self):
    self.rfile.read(int(self.headers['Content-Length']));self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers();self.wfile.flush();entered.set();release.wait(3)
  upstream=B.OwnedServer(('127.0.0.1',0),Stall);threading.Thread(target=upstream.serve_forever,daemon=True).start()
  captured=[]
  def connection(*a,**kw):
   c=http.client.HTTPConnection('127.0.0.1',upstream.server_address[1],**kw);captured.append(c);return c
  with tempfile.TemporaryDirectory() as tmp:
   session=S.Session(pathlib.Path(tmp)/'private',T);session.begin('codex',[{'num_reqs':0,'num_waiting_reqs':0}])
   class Adapter:
    def forward(self,path,body,emit):return session.forward(path,body,emit,connection)
   H=type('Http10Stall',(B.PostHandler,),{'session':Adapter()});server=B.OwnedServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
   client=http.client.HTTPConnection('127.0.0.1',server.server_address[1],timeout=2)
   def request():
    try:client.request('POST','/v1/responses',json.dumps({'model':'Qwen3.8-27B-FP8','stream':True}));client.getresponse().read()
    except OSError:pass
   worker=threading.Thread(target=request);worker.start()
   try:
    self.assertTrue(entered.wait(1));until=time.monotonic()+1
    while captured[0].sock is not None and time.monotonic()<until:time.sleep(.01)
    self.assertIsNone(captured[0].sock);self.assertTrue(any(sock is not None for sock in session.connections.values()));start=time.monotonic();session.abort_owned_connections();server.cleanup();worker.join(1);self.assertEqual(server.workers,0);self.assertLess(time.monotonic()-start,3)
   finally:release.set();client.close();upstream.cleanup()
 def test_handler_failure_cleanup(self):
  class Failed:
   def forward(self,*a):raise RuntimeError('owned mock failure')
  H=type('Fail',(B.PostHandler,),{'session':Failed()});server=B.OwnedServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   c=http.client.HTTPConnection('127.0.0.1',server.server_address[1],timeout=2);c.request('POST','/v1/responses',b'{}');self.assertEqual(c.getresponse().status,502);c.close()
  finally:server.cleanup();self.assertEqual(server.workers,0)
if __name__=='__main__':unittest.main()
