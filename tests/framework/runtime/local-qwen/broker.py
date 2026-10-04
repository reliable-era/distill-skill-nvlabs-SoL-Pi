"""GET-only metadata broker; fixed loopback upstream and absolute read deadline."""
import http.server,http.client,threading,socket,time,socketserver
class Broker(http.server.BaseHTTPRequestHandler):
 posts=0;get_count=0;upstream_connect=0;upstream_status=0;completed=0;upstream_error=0;active=0;lock=threading.Lock();busy=threading.Semaphore(1)
 def log_message(self,*args):pass
 def do_POST(self):
  with self.lock:Broker.posts+=1
  self.send_error(403)
 def do_CONNECT(self):self.send_error(403)
 def do_GET(self):
  self.connection.settimeout(5)
  if self.path!='/v1/models' or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length','0')!='0':self.send_error(403);return
  with self.lock:
   if Broker.get_count>=4:self.send_error(429);return
   Broker.get_count+=1
  if not self.busy.acquire(blocking=False):self.send_error(429);return
  with self.lock:Broker.active+=1
  c=http.client.HTTPConnection('127.0.0.1',8000,timeout=5);timer=None
  try:
   c.connect();Broker.upstream_connect+=1;sock=c.sock
   def cutoff():
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   timer=threading.Timer(5,cutoff);timer.start()
   c.request('GET','/v1/models');z=c.getresponse();Broker.upstream_status+=1;body=z.read(1024*1024+1)
   if len(body)>1024*1024:raise ValueError('metadata size cap')
   self.send_response(z.status);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);Broker.completed+=1
  except Exception:
   Broker.upstream_error+=1;raise
  finally:
   if timer:timer.cancel();timer.join(timeout=1)
   c.close();self.busy.release()
   with self.lock:Broker.active-=1

class OwnedServer(http.server.ThreadingHTTPServer):
 daemon_threads=False;block_on_close=False
 def __init__(self,*a,**k):
  self.connections=set();self.connection_lock=threading.Lock();self.workers=0
  super().__init__(*a,**k)
 def get_request(self):
  sock,addr=super().get_request();sock.settimeout(5)
  with self.connection_lock:self.connections.add(sock)
  return sock,addr
 def process_request_thread(self,request,client_address):
  with self.connection_lock:self.workers+=1
  try:super().process_request_thread(request,client_address)
  finally:
   with self.connection_lock:self.workers-=1;self.connections.discard(request)
 def terminate_connections(self):
  with self.connection_lock:sockets=list(self.connections)
  for sock in sockets:
   try:sock.shutdown(socket.SHUT_RDWR)
   except OSError:pass

class OwnedUnixServer(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
 daemon_threads=False;block_on_close=False
 def __init__(self,*a,**k):
  self.connections=set();self.connection_lock=threading.Lock();self.workers=0
  super().__init__(*a,**k)
 def get_request(self):
  sock,addr=socketserver.UnixStreamServer.get_request(self);sock.settimeout(5)
  with self.connection_lock:self.connections.add(sock)
  return sock,addr
 def process_request_thread(self,request,client_address):
  with self.connection_lock:self.workers+=1
  try:socketserver.ThreadingMixIn.process_request_thread(self,request,client_address)
  finally:
   with self.connection_lock:self.workers-=1;self.connections.discard(request)
 terminate_connections=OwnedServer.terminate_connections
