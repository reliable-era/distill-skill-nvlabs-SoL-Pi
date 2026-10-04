"""Tracked, bounded native POST broker server; fixed Session upstream only."""
import http.server,socket,threading,time
class OwnedServer(http.server.ThreadingHTTPServer):
 daemon_threads=True;block_on_close=False
 def __init__(self,*a,**kw):
  self.sockets=set();self.workers=0;self.guard=threading.Lock();self.busy=threading.Semaphore(1);self.slots=threading.Semaphore(2)
  super().__init__(*a,**kw)
 def get_request(self):
  s,a=super().get_request();s.settimeout(180)
  with self.guard:self.sockets.add(s)
  return s,a
 def process_request(self,s,a):
  if not self.slots.acquire(False):
   self.shutdown_request(s)
   with self.guard:self.sockets.discard(s)
   return
  try:super().process_request(s,a)
  except BaseException:
   self.slots.release();raise
 def process_request_thread(self,s,a):
  with self.guard:self.workers+=1
  try:super().process_request_thread(s,a)
  finally:
   with self.guard:self.workers-=1;self.sockets.discard(s)
   self.slots.release()
 def cleanup(self):
  t=threading.Thread(target=self.shutdown,daemon=True);t.start();t.join(2)
  with self.guard:connections=list(self.sockets)
  for s in connections:
   try:s.shutdown(socket.SHUT_RDWR)
   except OSError:pass
  self.server_close();until=time.monotonic()+3
  while self.workers and time.monotonic()<until:time.sleep(.01)
  if t.is_alive() or self.workers:raise RuntimeError('server workers cleanup uncertain')
class PostHandler(http.server.BaseHTTPRequestHandler):
 session=None;protocol_version='HTTP/1.0'
 def log_message(self,*a):pass
 def do_GET(self):self.send_error(403)
 def do_CONNECT(self):self.send_error(403)
 def do_POST(self):
  if self.path not in ['/v1/responses','/v1/chat/completions'] or self.headers.get('Transfer-Encoding'):self.send_error(403);return
  try:n=int(self.headers.get('Content-Length','-1'))
  except ValueError:self.send_error(413);return
  if not 0<=n<=262144:self.send_error(413);return
  if not self.server.busy.acquire(False):self.send_error(429);return
  timer=threading.Timer(180,lambda:self.cutoff(self.connection));timer.start();headers_sent=False
  try:
   body=self.rfile.read(n)
   if len(body)!=n:raise ValueError('incomplete body')
   def emit(chunk):
    nonlocal headers_sent
    if not headers_sent:
     self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers();headers_sent=True
    self.wfile.write(chunk);self.wfile.flush()
   self.session.forward(self.path,body,emit)
   if not headers_sent:self.send_error(502)
  except Exception:
   if not headers_sent:self.send_error(502)
   # Session persists exact exception category privately; no provider body exposure.
  finally:timer.cancel();timer.join(1);self.server.busy.release();self.close_connection=True
 @staticmethod
 def cutoff(s):
  try:s.shutdown(socket.SHUT_RDWR)
  except OSError:pass

class OwnedUnixServer(OwnedServer):
 address_family=socket.AF_UNIX
 def server_bind(self):
  self.socket.bind(self.server_address);self.server_name='owned-unix';self.server_port=0
