import pathlib,importlib.util,http.server,socket,tempfile,threading,unittest,time
R=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('tunnel',R/'tunnel_proxy.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
s=importlib.util.spec_from_file_location('server',R.parent/'native-readiness/server.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class Mock(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  self.rfile.read(int(self.headers['Content-Length']));self.send_response(400);self.end_headers();self.wfile.write(b'owned mock')
class Tunnel(unittest.TestCase):
 def test_exact_unix_http_tunnel(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=str(pathlib.Path(tmp)/'broker.sock');broker=b.OwnedUnixServer(path,Mock);H=type('Owned',(m.TunnelProxy,),{'unix_socket':path,'stats':{'CONNECT':0,'denied':0,'completed':0,'errors':0}});proxy=b.OwnedServer(('127.0.0.1',0),H)
   for server in [broker,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
   client=socket.create_connection(proxy.server_address,timeout=2)
   try:
    client.sendall(b'CONNECT provider.example:8000 HTTP/1.1\r\nHost: provider.example:8000\r\n\r\n');head=client.recv(4096);self.assertIn(b'200 Connection Established',head)
    client.sendall(b'POST /v1/chat/completions HTTP/1.1\r\nHost: provider.example:8000\r\nContent-Length: 2\r\n\r\n{}');body=b''
    while True:
     chunk=client.recv(4096)
     if not chunk:break
     body+=chunk
    self.assertIn(b'400',body);self.assertIn(b'owned mock',body)
   finally:client.close();proxy.cleanup();broker.cleanup();self.assertEqual(proxy.workers,0)
 def test_tunnel_deadline_and_client_byte_cap(self):
  class Stall(http.server.BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def do_POST(self):time.sleep(.3)
  for cap in [1,262144]:
   with tempfile.TemporaryDirectory() as tmp:
    path=str(pathlib.Path(tmp)/'broker.sock');broker=b.OwnedUnixServer(path,Stall);H=type('Bounded',(m.TunnelProxy,),{'unix_socket':path,'max_tunnel_seconds':.15,'max_client_bytes':cap,'stats':{'CONNECT':0,'denied':0,'completed':0,'errors':0}});proxy=b.OwnedServer(('127.0.0.1',0),H)
    for server in [broker,proxy]:threading.Thread(target=server.serve_forever,daemon=True).start()
    c=socket.create_connection(proxy.server_address,timeout=2)
    try:
     c.sendall(b'CONNECT provider.example:8000 HTTP/1.1\r\n\r\n');self.assertIn(b'200',c.recv(4096));start=time.monotonic();c.sendall(b'POST /stall HTTP/1.1\r\nContent-Length: 0\r\n\r\n');self.assertEqual(c.recv(4096),b'');self.assertLess(time.monotonic()-start,.6);self.assertGreater(H.stats['errors'],0)
    finally:c.close();proxy.cleanup();broker.cleanup();self.assertEqual(proxy.workers,0)
 def test_foreign_numeric_denied(self):
  proxy=b.OwnedServer(('127.0.0.1',0),m.TunnelProxy);threading.Thread(target=proxy.serve_forever,daemon=True).start()
  try:
   for authority in ['127.0.0.1:8000','foreign.example:8000','provider.example:8001']:
    c=socket.create_connection(proxy.server_address,timeout=2);c.sendall(('CONNECT '+authority+' HTTP/1.1\r\n\r\n').encode());self.assertIn(b'403',c.recv(4096));c.close()
  finally:proxy.cleanup()
if __name__=='__main__':unittest.main()
