"""Explicit destination allowlist proxy. Never log paths, headers or bodies."""
import http.server,http.client,json,os,socket,select,urllib.parse
ALLOW=json.loads(os.environ['EGRESS_ALLOWLIST']) # authority -> trusted connection hostname
class Proxy(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def denied(self):self.send_error(403,'destination denied')
 def destination(self,host,port):return ALLOW.get(f'{host.lower()}:{port}')
 def do_CONNECT(self):
  try:host,port=self.path.rsplit(':',1);port=int(port)
  except ValueError:return self.denied()
  target=self.destination(host,port)
  if not target:return self.denied()
  try:s=socket.create_connection((target,port),timeout=5)
  except OSError:return self.send_error(502)
  self.send_response(200,'Connection established');self.end_headers()
  with s:
   while True:
    ready,_,_=select.select([s,self.connection],[],[],10)
    if not ready:return
    for src in ready:
     data=src.recv(65536)
     if not data:return
     (self.connection if src is s else s).sendall(data)
 def do_GET(self):self.forward()
 def do_POST(self):self.forward()
 def forward(self):
  u=urllib.parse.urlsplit(self.path)
  if u.scheme!='http' or u.username or u.password:return self.denied()
  try:port=u.port or 80
  except ValueError:return self.denied()
  target=self.destination(u.hostname or '',port)
  if not target:return self.denied()
  try:
   size=int(self.headers.get('Content-Length',0))
   if size>1048576 or self.headers.get('Transfer-Encoding'):return self.denied()
   conn=http.client.HTTPConnection(target,port,timeout=5)
   headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','proxy-authorization','proxy-connection','connection']};headers['Host']=u.netloc
   conn.request(self.command,urllib.parse.urlunsplit(('', '',u.path or '/',u.query,'')),self.rfile.read(size),headers)
   response=conn.getresponse();body=response.read();self.send_response(response.status)
   self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);conn.close()
  except (OSError,ValueError):self.send_error(502)
http.server.ThreadingHTTPServer(('0.0.0.0',8080),Proxy).serve_forever()
