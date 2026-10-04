"""Owned GET-only diagnostic proxy. Counters only, no headers/body/path logs."""
import http.server,http.client,json,os,urllib.parse,threading,socket
ALLOW=json.loads(os.environ['EGRESS_ALLOWLIST'])
class Proxy(http.server.BaseHTTPRequestHandler):
 counters={'accepted':0,'forward':0,'connect':0,'status':0,'completed':0,'timeout':0,'denied':0};lock=threading.Lock()
 def log_message(self,*args):pass
 def bump(self,key):
  with self.lock:self.counters[key]+=1
 def do_CONNECT(self):self.bump('denied');self.send_error(403)
 def do_POST(self):self.bump('denied');self.send_error(403)
 def do_GET(self):
  self.connection.settimeout(5)
  if self.path=='/_health':
   data=json.dumps(self.counters).encode();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  self.bump('accepted');u=urllib.parse.urlsplit(self.path)
  authority=(u.hostname or '')+':'+str(u.port or 80);target=ALLOW.get(authority)
  if u.scheme!='http' or u.username or u.password or not target or u.path!='/v1/models' or u.query:self.bump('denied');self.send_error(403);return
  self.bump('forward');c=http.client.HTTPConnection(target,u.port or 80,timeout=3);timer=None
  try:
   c.connect();self.bump('connect');sock=c.sock
   def cutoff():
    try:sock.shutdown(socket.SHUT_RDWR)
    except OSError:pass
   timer=threading.Timer(4,cutoff);timer.start();c.request('GET','/v1/models');z=c.getresponse();self.bump('status');body=z.read(1048577)
   if len(body)>1048576:raise ValueError('metadata cap')
   self.send_response(z.status);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);self.bump('completed')
  except (OSError,ValueError):self.bump('timeout');self.send_error(502)
  finally:
   if timer:timer.cancel();timer.join(timeout=1)
   c.close()
if __name__=='__main__':http.server.ThreadingHTTPServer(('0.0.0.0',8080),Proxy).serve_forever()
