"""GET-only owned metadata broker; no model POST route exists."""
import http.server,http.client,threading,time
class Broker(http.server.BaseHTTPRequestHandler):
 posts=0;get_count=0;lock=threading.Lock();busy=threading.Semaphore(1)
 def log_message(self,*args):pass
 def do_POST(self):
  with self.lock:Broker.posts+=1
  self.send_error(403)
 def do_CONNECT(self):self.send_error(403)
 def do_GET(self):
  self.connection.settimeout(5)
  if self.path!='/v1/models' or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length','0')!='0':self.send_error(403);return
  with self.lock:
   if Broker.get_count>=2:self.send_error(429);return
   Broker.get_count+=1
  if not self.busy.acquire(blocking=False):self.send_error(429);return
  c=http.client.HTTPConnection('127.0.0.1',8000,timeout=5)
  try:
   c.request('GET','/v1/models');z=c.getresponse();body=z.read(1024*1024+1)
   if len(body)>1024*1024:raise ValueError('metadata size cap')
   self.send_response(z.status);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  finally:c.close();self.busy.release()
