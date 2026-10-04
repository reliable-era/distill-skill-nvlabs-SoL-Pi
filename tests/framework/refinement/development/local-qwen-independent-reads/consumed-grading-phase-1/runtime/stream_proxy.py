"""Future separately reviewed streaming proxy component; no launch entrypoint."""
import http.server,http.client,socket,threading,time,urllib.parse
class UnixHTTPConnection(http.client.HTTPConnection):
 def __init__(self,path,timeout):super().__init__('owned-unix',timeout=timeout);self.path=path
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(self.path)
class StreamingProxy(http.server.BaseHTTPRequestHandler):
 # Orchestrator must set exact authority and owned broker destination, never client selected.
 authority=None;broker_host=None;broker_port=None;unix_socket=None
 protocol_version='HTTP/1.0'
 def log_message(self,*args):pass
 def do_CONNECT(self):self.send_error(403)
 def do_GET(self):self.send_error(403)
 def do_POST(self):
  deadline=time.monotonic()+45;self.connection.settimeout(45)
  u=urllib.parse.urlsplit(self.path)
  if u.scheme!='http' or u.netloc!=self.authority or u.path not in ['/v1/responses','/v1/chat/completions'] or u.query or u.fragment or self.headers.get('Transfer-Encoding'):self.send_error(403);return
  try:n=int(self.headers.get('Content-Length','-1'))
  except ValueError:self.send_error(413);return
  if not 0<=n<=262144:self.send_error(413);return
  timer=threading.Timer(45,lambda:self.cutoff(self.connection));timer.start();c=None
  try:
   body=self.rfile.read(n)
   if len(body)!=n:raise RuntimeError('incomplete body')
   timeout=max(.01,deadline-time.monotonic())
   c=UnixHTTPConnection(self.unix_socket,timeout) if self.unix_socket else http.client.HTTPConnection(self.broker_host,self.broker_port,timeout=timeout)
   c.connect();upstream=c.sock
   upstream_timer=threading.Timer(max(.01,deadline-time.monotonic()),lambda:self.cutoff(upstream));upstream_timer.start()
   try:
    c.request('POST',u.path,body,{'Content-Type':'application/json'});z=c.getresponse()
    self.send_response(z.status);self.send_header('Content-Type',z.getheader('Content-Type','application/octet-stream'));self.send_header('Connection','close');self.end_headers();size=0
    while True:
     chunk=z.read1(8192)
     if not chunk:break
     size+=len(chunk)
     if size>2097152 or time.monotonic()>deadline:raise RuntimeError('stream bound')
     self.wfile.write(chunk);self.wfile.flush()
   finally:upstream_timer.cancel();upstream_timer.join(timeout=1)
  finally:
   if c:c.close()
   timer.cancel();timer.join(timeout=1);self.close_connection=True
 @staticmethod
 def cutoff(sock):
  try:sock.shutdown(socket.SHUT_RDWR)
  except OSError:pass

if __name__=='__main__':
 import os,signal
 from server import OwnedServer
 path=os.environ['BROKER_SOCKET']
 if path!='/broker/broker.sock':raise SystemExit('fixed broker socket')
 handler=type('OwnedProxy',(StreamingProxy,),{'authority':'provider.example:8000','unix_socket':path})
 server=OwnedServer(('0.0.0.0',8080),handler)
 def stop(*a):threading.Thread(target=server.shutdown,daemon=True).start()
 signal.signal(signal.SIGTERM,stop)
 try:server.serve_forever()
 finally:server.cleanup()
