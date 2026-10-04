"""Owned loopback broker. Fixed routes, two POST maximum; logs counts only."""
import http.server,http.client,threading,json
class Broker(http.server.BaseHTTPRequestHandler):
 count=0;lock=threading.Lock();posts_enabled=False
 def log_message(self,*args):pass
 def do_GET(self):self.forward()
 def do_POST(self):self.forward()
 def forward(self):
  paths={'GET':{'/v1/models'},'POST':{'/v1/responses','/v1/chat/completions'}}
  if self.path not in paths.get(self.command,set()):self.send_error(403);return
  if self.command=='POST':
   with self.lock:
    if not self.posts_enabled or Broker.count>=2:self.send_error(403);return
    Broker.count+=1
  n=int(self.headers.get('Content-Length','0'))
  if n>1048576 or self.headers.get('Transfer-Encoding'):self.send_error(413);return
  c=http.client.HTTPConnection('127.0.0.1',8000,timeout=15)
  try:
   c.request(self.command,self.path,self.rfile.read(n),{'Content-Type':'application/json'})
   z=c.getresponse();self.send_response(z.status)
   self.send_header('Content-Type',z.getheader('Content-Type','application/json'));self.end_headers()
   while True:
    b=z.read1(8192)
    if not b:break
    self.wfile.write(b);self.wfile.flush()
  finally:c.close()
